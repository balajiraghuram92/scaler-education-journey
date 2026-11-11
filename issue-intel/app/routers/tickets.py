"""POST /tickets/{key}/similar: ranked past cases + cited synthesised answer."""
from __future__ import annotations

import json

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.gateway.gateway import ModelGateway
from app.gateway.tasks import TaskType
from app.governance.rls import rls_session_dep
from app.models.g1 import Case, Thread
from app.schemas.tickets import Claim, EvidenceItem, LineageItem, SimilarResponse
from app.search import citations
from app.search.hybrid import hybrid_search
from app.search.lineage import expand_lineage
from app.search.rerank import rerank

router = APIRouter(prefix="/tickets", tags=["tickets"])

SYNTHESIS_SYSTEM = (
    "Answer the support question from the evidence only. Every claim must cite "
    'its evidence ids. Reply with JSON only: {"claims": [{"text": "...", '
    '"cites": ["E1"]}]}. Cite ids as [E1] inside the text as well.'
)


async def _synthesise(
    gateway: ModelGateway, ticket: Case, evidence: list[EvidenceItem]
) -> tuple[str, list[Claim]]:
    data = {
        e.id: f"[{e.kind}:{e.key}] {e.title}\n{e.snippet}\nOutcome: {e.outcome}"
        for e in evidence
    }
    result = await gateway.complete(
        TaskType.SYNTHESIS, system=SYNTHESIS_SYSTEM,
        user=f"Ticket {ticket.source_key}: {ticket.title}\n{ticket.body}", data=data,
    )
    try:
        payload = json.loads(result.text)
        claims = [Claim(**c) for c in payload.get("claims", [])]
    except (ValueError, TypeError):
        return result.text, []
    return result.text, claims


@router.post("/{key}/similar", response_model=SimilarResponse)
async def similar_cases(
    key: str,
    session: AsyncSession = Depends(rls_session_dep),  # noqa: B008
) -> SimilarResponse:
    gateway = ModelGateway()
    ticket = (
        await session.execute(select(Case).where(Case.source_key == key))
    ).scalar_one_or_none()
    if ticket is None:
        raise HTTPException(status_code=404, detail=f"unknown ticket {key}")
    query = f"{ticket.title}\n{ticket.body}"
    vectors = await gateway.embed([query])
    hits = await hybrid_search(session, query, vectors[0], limit=10)
    ranked = await rerank(gateway, query, hits)

    evidence: list[EvidenceItem] = []
    case_keys: list[str] = []
    threads = {
        t.key: t for t in (await session.execute(select(Thread))).scalars().all()
    }
    cases = {
        c.source_key: c
        for c in (await session.execute(select(Case))).scalars().all()
    }
    for i, item in enumerate(ranked, start=1):
        hit = item.hit
        if hit.owner_type == "thread":
            thread = threads.get(hit.owner_key)
            case_key = thread.case_key if thread else hit.owner_key
        else:
            case_key = hit.owner_key
        if case_key == key:
            continue  # never cite the queried ticket itself
        case = cases.get(case_key)
        title = case.title if case else hit.owner_key
        outcome = case.outcome if case else ""
        evidence.append(
            EvidenceItem(id=f"E{i}", kind=hit.owner_type, key=case_key,
                         title=title, snippet=hit.text[:400], outcome=outcome)
        )
        if case_key not in case_keys:
            case_keys.append(case_key)

    answer_text, claims = await _synthesise(gateway, ticket, evidence)
    report = citations.check_citations(answer_text, [e.id for e in evidence])
    if not report.ok:
        raise HTTPException(
            status_code=500,
            detail=f"citation check failed: unknown ids {report.unknown}",
        )
    lineage = await expand_lineage(session, case_keys)
    return SimilarResponse(
        ticket=key, evidence=evidence, claims=claims,
        lineage=[
            LineageItem(key=k, outcome=v.outcome, duplicates=v.duplicates,
                        fixed_by=v.fixed_by, owner=v.owner)
            for k, v in lineage.items()
        ],
        answer_text=answer_text,
    )
