"""Outcome classification for legacy cases, in batches via the gateway."""
from __future__ import annotations

import json

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.gateway.gateway import ModelGateway
from app.gateway.tasks import TaskType
from app.models.g1 import Case

OUTCOME_LABELS = (
    "WONT_FIX", "BY_DESIGN", "HW_LIMITATION", "DUPLICATE",
    "REGRESSION", "FIXED", "UNKNOWN",
)
BATCH_SIZE = 25
SYSTEM = (
    "Classify the bug-tracker resolution into exactly one label: "
    + ", ".join(OUTCOME_LABELS)
    + '. Reply with JSON only: {"outcome": "<LABEL>"}.'
)


def parse_outcome(text: str) -> str:
    try:
        label = str(json.loads(text).get("outcome", "")).strip().upper()
    except (ValueError, AttributeError):
        return "UNKNOWN"
    return label if label in OUTCOME_LABELS else "UNKNOWN"


async def classify_legacy_outcomes(
    session: AsyncSession, gateway: ModelGateway, run_id: str | None = None
) -> int:
    """Classify every legacy case still labelled UNKNOWN. Returns count set."""
    pending = (
        await session.execute(
            select(Case).where(Case.source == "LEGACY", Case.outcome == "UNKNOWN")
        )
    ).scalars().all()
    done = 0
    for i in range(0, len(pending), BATCH_SIZE):
        batch = pending[i : i + BATCH_SIZE]
        for case in batch:
            result = await gateway.complete(
                TaskType.OUTCOME_CLASSIFY, system=SYSTEM,
                user=f"Title: {case.title}",
                data={"resolution": case.raw_resolution}, run_id=run_id,
            )
            case.outcome = parse_outcome(result.text)
            done += 1
        await session.flush()
    return done
