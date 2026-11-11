"""Final check over the whole package: evidence, synthesis, diff, tests."""
from __future__ import annotations

import json
from typing import Any

from sqlalchemy import select

from app.gateway.gateway import ModelGateway
from app.gateway.tasks import TaskType
from app.models.g2 import Evidence, RunStage
from app.models.g3 import FinalCheck

QUALITY_SYSTEM = (
    "Screen the fix package cheaply. Reply with JSON only: "
    '{"pass": true|false, "reason": "..."}. Fail it only for obvious scope, '
    "safety or evidence problems."
)
FINAL_SYSTEM = (
    "Review the fix package. Reply with JSON only: "
    '{"verdict": "OK"|"NEED_MORE_INFO"|"BLOCK", "reason": "..."}. '
    "BLOCK only for safety, scope or evidence problems."
)
VERDICTS = ("OK", "NEED_MORE_INFO", "BLOCK")
FILTERED_PREFIX = "filtered by quality_verify: "


async def run_final_check(
    session: Any, gateway: ModelGateway, run_id: str,
    attempt_id: int | None = None, diff: str = "", test_output: str = "",
) -> FinalCheck:
    rows = (
        await session.execute(select(Evidence).where(Evidence.run_id == run_id))
    ).scalars().all()
    s7 = (
        await session.execute(
            select(RunStage).where(RunStage.run_id == run_id, RunStage.stage == "S7")
        )
    ).scalar_one_or_none()
    evidence = "\n".join(f"[{r.evid} {r.kind}:{r.key}] {r.snippet[:500]}" for r in rows)
    screen = await gateway.complete(
        TaskType.QUALITY_VERIFY, system=QUALITY_SYSTEM,
        user="Screen this fix package.",
        data={"diff": diff[-4000:], "tests": test_output[-2000:]},
    )
    try:
        screened = json.loads(screen.text)
        screen_pass = bool(screened.get("pass", True))
        screen_reason = str(screened.get("reason", ""))
    except ValueError:
        screen_pass, screen_reason = True, ""
    if not screen_pass:
        row = FinalCheck(run_id=run_id, attempt_id=attempt_id,
                         verdict="NEED_MORE_INFO",
                         reason=f"{FILTERED_PREFIX}{screen_reason}")
        session.add(row)
        await session.commit()
        return row
    result = await gateway.complete(
        TaskType.FINAL_CHECK, system=FINAL_SYSTEM,
        user="Review this fix package.",
        data={
            "evidence": evidence[:8000],
            "synthesis": str((s7.output_json if s7 else {}).get("answer_text", "")),
            "diff": diff[-8000:],
            "test_output": test_output[-4000:],
        },
    )
    try:
        payload = json.loads(result.text)
        verdict = str(payload.get("verdict", "NEED_MORE_INFO"))
        reason = str(payload.get("reason", ""))
    except ValueError:
        verdict, reason = "NEED_MORE_INFO", "final check reply unparseable"
    if verdict not in VERDICTS:
        verdict, reason = "NEED_MORE_INFO", f"unknown verdict {verdict!r}"
    row = FinalCheck(run_id=run_id, attempt_id=attempt_id, verdict=verdict,
                     reason=reason)
    session.add(row)
    await session.commit()
    return row
