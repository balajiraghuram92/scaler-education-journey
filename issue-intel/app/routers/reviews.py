"""Review routers: approve/post, need-info, wrong, notify owner, request access."""
from __future__ import annotations

from typing import Any

from fastapi import APIRouter, HTTPException, Request
from pydantic import BaseModel
from sqlalchemy import select

from app.adapters.fake_chat import CHAT
from app.adapters.fake_tracker import TRACKER
from app.governance.rls import service_session
from app.models.g1 import EvalCase
from app.models.g2 import Review, Run, Writeback
from app.pipeline.render import render_for_viewer
from app.routers.runs import _viewer_entitlements  # noqa: F401 (shared helper)

router = APIRouter()

DECISIONS = ("APPROVED", "NEED_INFO", "WRONG", "NOTIFY_OWNER")


class ReviewPayload(BaseModel):
    reviewer: str
    decision: str
    edits: dict[str, Any] = {}
    reason: str = ""


@router.post("/runs/{run_id}/review")
async def submit_review(run_id: str, payload: ReviewPayload, request: Request) -> dict[str, Any]:
    if payload.decision not in DECISIONS:
        raise HTTPException(status_code=400, detail=f"decision must be one of {DECISIONS}")
    async with service_session() as session:
        run = (
            await session.execute(select(Run).where(Run.id == run_id))
        ).scalar_one_or_none()
        if run is None:
            raise HTTPException(status_code=404, detail="unknown run")
        review = Review(run_id=run_id, reviewer=payload.reviewer,
                        decision=payload.decision, edits=payload.edits,
                        reason=payload.reason)
        session.add(review)
        await session.flush()
        result: dict[str, Any] = {"review_id": review.id, "decision": payload.decision}
        if payload.decision == "APPROVED":
            ent = await _viewer_entitlements(request)
            view = await render_for_viewer(run_id, ent)
            text = view["answer_text"] or "(no synthesis)"
            ref = TRACKER.post_comment(run.ticket_key, payload.reviewer, text)
            session.add(
                Writeback(run_id=run_id, review_id=review.id, channel="tracker",
                          payload={"ticket": run.ticket_key, "text": text},
                          external_ref=ref)
            )
            result["posted_ref"] = ref
        if payload.decision == "WRONG" or payload.edits:
            session.add(
                EvalCase(kind="review_feedback",
                         payload={"run_id": run_id, "ticket": run.ticket_key},
                         expected={"decision": payload.decision, "edits": payload.edits})
            )
            result["eval_case"] = True
        await session.commit()
        return result


@router.post("/runs/{run_id}/notify-owner")
async def notify_owner(run_id: str, request: Request) -> dict[str, Any]:
    reviewer = request.headers.get("x-user-id", "reviewer")
    async with service_session() as session:
        run = (
            await session.execute(select(Run).where(Run.id == run_id))
        ).scalar_one_or_none()
        if run is None:
            raise HTTPException(status_code=404, detail="unknown run")
        view = await render_for_viewer(run_id, await _viewer_entitlements(request))
        owner = str(view.get("synthesis", {}).get("who_to_ask", "module-owner"))
        ref = CHAT.post_message(
            f"owner-{owner}", reviewer,
            f"Ticket {run.ticket_key} needs your module: please review run {run_id}.",
        )
        session.add(
            Writeback(run_id=run_id, review_id=None, channel="chat",
                      payload={"owner": owner}, external_ref=ref)
        )
        await session.commit()
        return {"notified": owner, "ref": ref}


@router.post("/runs/{run_id}/request-access")
async def request_access(run_id: str, request: Request) -> dict[str, Any]:
    reviewer = request.headers.get("x-user-id", "reviewer")
    async with service_session() as session:
        run = (
            await session.execute(select(Run).where(Run.id == run_id))
        ).scalar_one_or_none()
        if run is None:
            raise HTTPException(status_code=404, detail="unknown run")
        session.add(
            Writeback(run_id=run_id, review_id=None, channel="access",
                      payload={"requested_by": reviewer,
                               "ticket": run.ticket_key}, external_ref="")
        )
        await session.commit()
        return {"requested": True}
