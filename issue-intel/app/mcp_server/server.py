"""MCP server with read-only investigation tools.

Transport: stdio (`python -m app.mcp_server.server`). The host authenticates
the caller and passes the verified user id to every tool; tools resolve the
same entitlements as the HTTP API and reuse the same code paths.

Connect a local MCP client (example Claude Desktop config):
{"mcpServers": {"issue-intel": {"command": "python", "args": ["-m",
"app.mcp_server.server"], "cwd": "<repo>/issue-intel"}}.
"""
from __future__ import annotations

import json
from typing import Any

from mcp.server import NotificationOptions, Server
from mcp.server.models import InitializationOptions
import mcp.server.stdio
import mcp.types as types
from sqlalchemy import select

from app.gateway.gateway import ModelGateway
from app.governance.entitlements import resolve_entitlements
from app.governance.rls import rls_session, service_session
from app.models.g1 import Case
from app.models.g2 import Run
from app.pipeline.render import render_for_viewer
from app.search.hybrid import SearchMode, hybrid_search
from app.search.lineage import change_summary, expand_lineage

server = Server("issue-intel")


async def _entitlements_for(user_id: int):  # type: ignore[no-untyped-def]
    async with service_session() as session:
        return await resolve_entitlements(session, user_id)


@server.list_tools()
async def list_tools() -> list[types.Tool]:
    return [
        types.Tool(
            name="get_ticket_intelligence",
            description="Latest investigation of a ticket, rendered for the caller.",
            inputSchema={"type": "object", "properties": {
                "ticket_key": {"type": "string"},
                "user_id": {"type": "integer", "description": "host-verified caller id"},
            }, "required": ["ticket_key", "user_id"]},
        ),
        types.Tool(
            name="search_archives",
            description="Hybrid search over past cases, threads and changes.",
            inputSchema={"type": "object", "properties": {
                "query": {"type": "string"},
                "user_id": {"type": "integer"},
                "mode": {"type": "string", "enum": ["fulltext", "vector", "fused"],
                         "default": "fused"},
            }, "required": ["query", "user_id"]},
        ),
        types.Tool(
            name="get_change_lineage",
            description="Change summary plus cases linked to it.",
            inputSchema={"type": "object", "properties": {
                "change_ref": {"type": "string"},
                "user_id": {"type": "integer"},
            }, "required": ["change_ref", "user_id"]},
        ),
        types.Tool(
            name="publish_status",
            description="Post the investigation answer to the ticket. Needs token.",
            inputSchema={"type": "object", "properties": {
                "run_id": {"type": "string"},
                "text": {"type": "string"},
                "token": {"type": "string"},
                "user_id": {"type": "integer"},
            }, "required": ["run_id", "text", "token", "user_id"]},
        ),
        types.Tool(
            name="request_fix",
            description="Request a fix attempt for a run. Needs token.",
            inputSchema={"type": "object", "properties": {
                "run_id": {"type": "string"},
                "token": {"type": "string"},
                "user_id": {"type": "integer"},
            }, "required": ["run_id", "token", "user_id"]},
        ),
        types.Tool(
            name="approve_backport",
            description="Merge a backport PR. Needs a merge_pr token.",
            inputSchema={"type": "object", "properties": {
                "pr_id": {"type": "integer"},
                "token": {"type": "string"},
                "user_id": {"type": "integer"},
            }, "required": ["pr_id", "token", "user_id"]},
        ),
    ]


async def _ticket_intelligence(args: dict[str, Any]) -> str:
    ent = await _entitlements_for(int(args["user_id"]))
    async with service_session() as session:
        run = (
            await session.execute(
                select(Run).where(Run.ticket_key == args["ticket_key"])
                .order_by(Run.created_at.desc()).limit(1)
            )
        ).scalar_one_or_none()
        if run is None:
            return json.dumps({"error": f"no run for {args['ticket_key']}"})
        run_id = run.id
    return json.dumps(await render_for_viewer(run_id, ent), default=str)


async def _search_archives(args: dict[str, Any]) -> str:
    ent = await _entitlements_for(int(args["user_id"]))
    mode: SearchMode = args.get("mode", "fused")
    gateway = ModelGateway()
    vectors = await gateway.embed([str(args["query"])])
    async with rls_session(ent) as session:
        hits = await hybrid_search(session, str(args["query"]), vectors[0], mode=mode)
        return json.dumps(
            [{"owner": h.owner_type, "key": h.owner_key, "score": h.score,
              "text": h.text[:300]} for h in hits]
        )


async def _change_lineage(args: dict[str, Any]) -> str:
    ent = await _entitlements_for(int(args["user_id"]))
    async with rls_session(ent) as session:
        summary = await change_summary(session, str(args["change_ref"]))
        cases = (
            await session.execute(
                select(Case.source_key).where(
                    Case.fixed_change == str(args["change_ref"])
                ).limit(20)
            )
        ).scalars().all()
        lineage = await expand_lineage(session, list(cases))
        _ = ent
        return json.dumps({"change": summary, "cases": lineage}, default=str)


async def _publish_status(args: dict[str, Any]) -> str:
    from app.adapters.fake_tracker import TRACKER
    from app.governance.tokens import validate_token
    from app.models.g2 import Writeback

    run_id = str(args["run_id"])
    async with service_session() as session:
        run = await session.get(Run, run_id)
        if run is None:
            return json.dumps({"error": "unknown run"})
        ticket_key = run.ticket_key
    ok = await validate_token(
        str(args["token"]), "publish_status", run_id, ticket_key,
        {"text": str(args["text"])},
    )
    if not ok:
        return json.dumps({"error": "invalid approval token: nothing posted"})
    ref = TRACKER.post_comment(ticket_key, f"user-{args['user_id']}", str(args["text"]))
    async with service_session() as session:
        session.add(
            Writeback(run_id=run_id, review_id=None, channel="tracker",
                      payload={"ticket": ticket_key, "text": str(args["text"])},
                      external_ref=ref)
        )
        await session.commit()
    return json.dumps({"posted_ref": ref})


async def _request_fix_mcp(args: dict[str, Any]) -> str:
    from app.agents.candidates import consider_run
    from app.governance.tokens import validate_token
    from app.models.g2 import Job
    from app.settings import get_settings

    run_id = str(args["run_id"])
    async with service_session() as session:
        run = await session.get(Run, run_id)
        if run is None:
            return json.dumps({"error": "unknown run"})
        ticket_key = run.ticket_key
    ok = await validate_token(str(args["token"]), "request_fix", run_id,
                              ticket_key, {})
    if not ok:
        return json.dumps({"error": "invalid approval token: nothing queued"})
    candidate = await consider_run(get_settings(), run_id)
    if candidate.status == "PENDING":
        async with service_session() as session:
            session.add(Job(kind="fix", payload={"candidate_id": candidate.id}))
            await session.commit()
    return json.dumps({"candidate_id": candidate.id, "status": candidate.status})


async def _approve_backport(args: dict[str, Any]) -> str:
    import hashlib
    from pathlib import Path

    from app.adapters.fake_codehost import CODEHOST
    from app.agents.sandbox import run_cmd
    from app.governance.tokens import validate_token
    from app.models.g3 import FixAttempt, FixCandidate, FixPr
    from app.settings import get_settings

    pr_id = int(args["pr_id"])
    async with service_session() as session:
        pr = await session.get(FixPr, pr_id)
        if pr is None or pr.kind != "BACKPORT":
            return json.dumps({"error": "unknown backport PR"})
        attempt = await session.get(FixAttempt, pr.attempt_id)
        assert attempt is not None
        candidate = await session.get(FixCandidate, attempt.candidate_id)
        assert candidate is not None
        diff_sha = hashlib.sha256(pr.diff.encode()).hexdigest()
        branch, base = pr.branch, pr.base
    ok = await validate_token(
        str(args["token"]), "merge_pr", candidate.run_id, candidate.ticket_key,
        {"pr_id": pr_id, "diff_sha": diff_sha},
    )
    if not ok:
        return json.dumps({"error": "invalid approval token: nothing merged"})
    repo = Path(get_settings().sample_repo_path)
    checkout = await run_cmd(["git", "checkout", base], cwd=repo, timeout_s=120)
    if checkout.returncode != 0:
        return json.dumps({"error": "checkout failed"})
    merged = await run_cmd(["git", "merge", "--no-ff", branch], cwd=repo,
                           timeout_s=180)
    if merged.returncode != 0:
        await run_cmd(["git", "merge", "--abort"], cwd=repo, timeout_s=60)
        return json.dumps({"error": "merge conflict in git"})
    sha = await run_cmd(["git", "rev-parse", "HEAD"], cwd=repo, timeout_s=60)
    async with service_session() as session:
        row = await session.get(FixPr, pr_id)
        assert row is not None
        row.status = "MERGED"
        await session.commit()
    CODEHOST.record_merge(pr_id, branch, base, f"user-{args['user_id']}",
                          sha.stdout.strip())
    return json.dumps({"merged": True, "commit": sha.stdout.strip()})


@server.call_tool()
async def call_tool(name: str, args: dict[str, Any]) -> list[types.TextContent]:
    if name == "get_ticket_intelligence":
        return [types.TextContent(type="text", text=await _ticket_intelligence(args))]
    if name == "search_archives":
        return [types.TextContent(type="text", text=await _search_archives(args))]
    if name == "get_change_lineage":
        return [types.TextContent(type="text", text=await _change_lineage(args))]
    if name == "publish_status":
        return [types.TextContent(type="text", text=await _publish_status(args))]
    if name == "request_fix":
        return [types.TextContent(type="text", text=await _request_fix_mcp(args))]
    if name == "approve_backport":
        return [types.TextContent(type="text", text=await _approve_backport(args))]
    raise ValueError(f"unknown tool {name}")


async def run_stdio() -> None:
    async with mcp.server.stdio.stdio_server() as (read, write):
        await server.run(
            read, write,
            InitializationOptions(
                server_name="issue-intel", server_version="0.2.0",
                capabilities=server.get_capabilities(
                    notification_options=NotificationOptions(), experimental_capabilities={},
                ),
            ),
        )


def main() -> None:
    import asyncio

    asyncio.run(run_stdio())


if __name__ == "__main__":
    main()
