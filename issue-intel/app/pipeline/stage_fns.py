"""Stage functions S1..S8. Each takes a RunContext, returns a JSON dict."""
from __future__ import annotations

from collections.abc import Awaitable, Callable
from typing import Any

from sqlalchemy import select

from app.adapters.fake_docs import search_docs
from app.gateway.tasks import TaskType
from app.ingest.normalise import get_or_create_acl
from app.ingest.ownership import current_owner
from app.models.g1 import Case, Change, Link, Message, Thread
from app.pipeline.stages import (
    CUST_RE,
    S1_SYSTEM,
    S2_SYSTEM,
    S5_SYSTEM,
    S7_SYSTEM,
    CitationError,
    LeakageError,
    RunContext,
    SchemaValidationError,
    add_evidence,
    parse_json_or_raise,
)
from app.search import citations
from app.search.hybrid import hybrid_search
from app.search.rerank import parse_relevance, rerank


async def s1_ticket_parse(ctx: RunContext) -> dict[str, Any]:
    result = await ctx.gateway.complete(
        TaskType.TICKET_PARSE, system=S1_SYSTEM,
        user=f"Ticket {ctx.ticket.source_key}: {ctx.ticket.title}",
        data={"body": ctx.ticket.body}, run_id=ctx.run.id,
    )
    payload = parse_json_or_raise(result.text)
    return {
        "module": str(payload.get("module", "")),
        "version": str(payload.get("version", ctx.ticket.version)),
        "error_strings": [str(x) for x in payload.get("error_strings", [])],
        "stack_frames": [str(x) for x in payload.get("stack_frames", [])],
        "legacy_ids": [str(x) for x in payload.get("legacy_ids", [])],
    }


async def s2_module_check(ctx: RunContext) -> dict[str, Any]:
    s1 = ctx.outputs["S1"]
    result = await ctx.gateway.complete(
        TaskType.MODULE_CHECK, system=S2_SYSTEM,
        user=f"Filed module: {ctx.ticket.filed_module}",
        data={"parsed": str(s1), "title": ctx.ticket.title},
        run_id=ctx.run.id,
    )
    payload = parse_json_or_raise(result.text)
    predicted = str(payload.get("predicted_module", ctx.ticket.filed_module))
    confidence = float(payload.get("confidence", 0.0))
    return {
        "filed_module": ctx.ticket.filed_module,
        "predicted_module": predicted,
        "confidence": confidence,
        "wrong_module": bool(predicted != ctx.ticket.filed_module and confidence >= 0.5),
    }


async def _case_and_thread_maps(ctx: RunContext) -> tuple[dict[str, Case], dict[str, Thread]]:
    cases = {
        c.source_key: c for c in (await ctx.session.execute(select(Case))).scalars().all()
    }
    threads = {
        t.key: t for t in (await ctx.session.execute(select(Thread))).scalars().all()
    }
    return cases, threads


async def s3_ticket_retrieval(ctx: RunContext) -> dict[str, Any]:
    query = f"{ctx.ticket.title}\n{ctx.ticket.body}"
    vectors = await ctx.gateway.embed([query], run_id=ctx.run.id)
    hits = await hybrid_search(ctx.session, query, vectors[0], limit=10)
    ranked = await rerank(ctx.gateway, query, hits, run_id=ctx.run.id)
    cases, threads = await _case_and_thread_maps(ctx)
    added: list[str] = []
    for item in ranked[:8]:
        if item.hit.owner_type == "thread":
            thread = threads.get(item.hit.owner_key)
            case_key = thread.case_key if thread else item.hit.owner_key
        elif item.hit.owner_type == "case":
            case_key = item.hit.owner_key
        else:
            continue
        if case_key == ctx.ticket.source_key:
            continue
        case = cases.get(case_key)
        added.append(
            await add_evidence(
                ctx, "case", case_key, case.title if case else case_key,
                item.hit.text, case.outcome if case else "",
                case.acl_id if case else ctx.ticket.acl_id, {"score": item.score},
            )
        )
    return {"evidence": added}


async def s4_chat_retrieval(ctx: RunContext) -> dict[str, Any]:
    query = f"{ctx.ticket.title}\n{ctx.ticket.body}"
    vectors = await ctx.gateway.embed([query], run_id=ctx.run.id)
    hits = await hybrid_search(ctx.session, query, vectors[0], limit=15, mode="vector")
    thread_hits = [h for h in hits if h.owner_type == "thread"]
    ranked = await rerank(ctx.gateway, query, thread_hits, run_id=ctx.run.id)
    _, threads = await _case_and_thread_maps(ctx)
    added: list[str] = []
    for item in ranked[:5]:
        thread = threads.get(item.hit.owner_key)
        if thread is None:
            continue
        messages = (
            await ctx.session.execute(
                select(Message).where(Message.thread_id == thread.id)
                .order_by(Message.seq)
            )
        ).scalars().all()
        full = "\n".join(f"{m.author}: {m.text}" for m in messages)
        added.append(
            await add_evidence(
                ctx, "chat", thread.key, f"Thread {thread.key}", full,
                "", thread.acl_id,
                {"score": item.score, "case_key": thread.case_key},
            )
        )
    return {"evidence": added, "threads_considered": len(thread_hits)}


async def s5_code_lineage(ctx: RunContext) -> dict[str, Any]:
    s1 = ctx.outputs["S1"]
    implicated = {t.lower() for t in s1["stack_frames"] + s1["error_strings"] if len(t) > 2}
    case_keys = [e.key for e in ctx.evidence if e.kind == "case"]
    case_keys += [
        str(e.data.get("case_key", "")) for e in ctx.evidence
        if e.kind == "chat" and e.data.get("case_key")
    ]
    links = (
        await ctx.session.execute(
            select(Link).where(
                Link.from_type == "case", Link.from_key.in_(case_keys),
                Link.to_type == "change",
            )
        )
    ).scalars().all() if case_keys else []
    changes = {
        c.ref: c for c in (await ctx.session.execute(select(Change))).scalars().all()
    }
    scored: dict[str, tuple[float, str]] = {}
    for link in links:
        if link.to_key in changes:
            scored[link.to_key] = (1.0, f"{link.kind} from {link.from_key}")
    for ref, change in changes.items():
        haystack = f"{change.message}\n{change.files}".lower()
        if any(token in haystack for token in implicated):
            scored.setdefault(ref, (0.7, "mentions implicated file or token"))
    ordered = sorted(scored.items(), key=lambda kv: kv[1][0], reverse=True)[:5]
    kept: list[dict[str, Any]] = []
    for ref, (_base, reason) in ordered:
        change = changes[ref]
        result = await ctx.gateway.complete(
            TaskType.RELEVANCE, system=S5_SYSTEM,
            user=f"Issue: {ctx.ticket.title}",
            data={"change": f"{ref}: {change.message}\nFiles: {change.files}"},
            run_id=ctx.run.id,
        )
        relevant, score = parse_relevance(result.text)
        if relevant and score >= 0.5:
            kept.append({"ref": ref, "score": score, "reason": reason,
                         "files": change.files})
            await add_evidence(
                ctx, "change", ref, ref,
                f"{change.message}\nFiles: {change.files}", "",
                change.acl_id, {"score": score},
            )
    kept.sort(key=lambda c: float(c["score"]), reverse=True)
    strong = [c for c in kept if float(c["score"]) >= 0.7]
    multi = False
    if len(strong) >= 2:
        first_files = set(str(strong[0]["files"]).split(","))
        second_files = set(str(strong[1]["files"]).split(","))
        multi = not (first_files & second_files)
    version = s1.get("version", "")
    return {
        "candidates": kept, "multi_change": multi,
        "version_window": [version] if version else [],
    }


async def s6_docs(ctx: RunContext) -> dict[str, Any]:
    docs = search_docs(f"{ctx.ticket.title} {ctx.ticket.body}")
    acl = await get_or_create_acl(
        ctx.session, "VersionControl,Localization,UiState,AssetImport",
        "SE,Support,Partner", "OPEN",
    )
    added = []
    for doc in docs:
        added.append(
            await add_evidence(
                ctx, "docs", doc.module, doc.title, doc.snippet, "",
                acl.id, {"score": doc.score},
            )
        )
    return {"evidence": added}


async def s7_synthesis(ctx: RunContext) -> dict[str, Any]:
    data = {
        e.evid: f"[{e.kind}:{e.key}] {e.title}\n{e.snippet}\nOutcome: {e.outcome}"
        for e in ctx.evidence
    }
    result = await ctx.gateway.complete(
        TaskType.SYNTHESIS, system=S7_SYSTEM,
        user=f"Ticket {ctx.ticket.source_key}: {ctx.ticket.title}\n{ctx.ticket.body}",
        data=data, run_id=ctx.run.id,
    )
    payload = parse_json_or_raise(result.text)
    claims = [
        {"text": str(c.get("text", "")), "cites": [str(x) for x in c.get("cites", [])]}
        for c in payload.get("claims", [])
    ]
    answer_text = "\n".join(
        f"{c['text']} " + "".join(f"[{x}]" for x in c["cites"]) for c in claims
    )
    who = str(payload.get("who_to_ask", ""))
    if not who:
        who = await current_owner(ctx.session, ctx.ticket.module) or ""
    return {
        "seen_before": bool(payload.get("seen_before", False)),
        "outcomes": [str(x) for x in payload.get("outcomes", [])],
        "likely_cause": str(payload.get("likely_cause", "")),
        "fix_or_workaround": str(payload.get("fix_or_workaround", "")),
        "who_to_ask": who,
        "confidence": float(payload.get("confidence", 0.0)),
        "claims": claims,
        "answer_text": answer_text,
    }


async def s8_checks(ctx: RunContext) -> dict[str, Any]:
    s7 = ctx.outputs["S7"]
    required = ("seen_before", "outcomes", "likely_cause", "fix_or_workaround",
                "who_to_ask", "claims", "answer_text")
    missing = [k for k in required if k not in s7]
    if missing:
        raise SchemaValidationError(f"S7 output missing keys: {missing}")
    report = citations.check_citations(
        str(s7["answer_text"]), [e.evid for e in ctx.evidence]
    )
    if not report.ok:
        raise CitationError(f"cited ids not retrieved: {report.unknown}")
    for match in CUST_RE.findall(str(s7["answer_text"])):
        if not any(match in e.snippet for e in ctx.evidence):
            raise LeakageError(f"answer contains ungrounded customer ref {match}")
    return {"ok": True}


StageFn = Callable[[RunContext], Awaitable[dict[str, Any]]]

STAGES: list[tuple[str, StageFn]] = [
    ("S1", s1_ticket_parse),
    ("S2", s2_module_check),
    ("S3", s3_ticket_retrieval),
    ("S4", s4_chat_retrieval),
    ("S5", s5_code_lineage),
    ("S6", s6_docs),
    ("S7", s7_synthesis),
    ("S8", s8_checks),
]
