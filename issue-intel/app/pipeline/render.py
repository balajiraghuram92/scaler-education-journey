"""Per-viewer rendering of a cached run under the viewer's entitlements.

Evidence the viewer may not see is removed; synthesis claims citing removed
evidence are withheld. When S2 says the ticket belongs to a module the viewer
cannot access, the viewer sees only the alert and the two actions.
"""
from __future__ import annotations

from typing import Any

from sqlalchemy import select

from app.governance.entitlements import Entitlements, is_visible
from app.governance.redaction import redact
from app.governance.rls import service_session
from app.models.g1 import Acl
from app.models.g2 import Evidence, Run, RunStage


def withhold_claims(
    claims: list[dict[str, Any]], visible: set[str]
) -> tuple[list[dict[str, Any]], int]:
    kept = [c for c in claims if set(c.get("cites", [])) <= visible]
    return kept, len(claims) - len(kept)


def wrong_module_alert(
    s2: dict[str, Any], viewer_modules: set[str]
) -> dict[str, Any] | None:
    if not s2.get("wrong_module"):
        return None
    predicted = str(s2.get("predicted_module", ""))
    if predicted in viewer_modules:
        return None
    return {
        "predicted_module": predicted,
        "confidence": float(s2.get("confidence", 0.0)),
        "actions": ["request_access", "notify_owner"],
    }


async def render_for_viewer(run_id: str, ent: Entitlements) -> dict[str, Any]:
    async with service_session() as session:
        run = (
            await session.execute(select(Run).where(Run.id == run_id))
        ).scalar_one()
        rows = (
            await session.execute(select(Evidence).where(Evidence.run_id == run_id))
        ).scalars().all()
        stages = (
            await session.execute(select(RunStage).where(RunStage.run_id == run_id))
        ).scalars().all()
        acls = {
            a.id: a for a in (await session.execute(select(Acl))).scalars().all()
        }
    by_name = {s.stage: s.output_json for s in stages}
    alert = wrong_module_alert(by_name.get("S2", {}), ent.modules)
    if alert is not None:
        return {
            "run_id": run_id, "ticket": run.ticket_key, "status": run.status,
            "evidence": [], "claims": [], "withheld": 0, "answer_text": "",
            "wrong_module_alert": alert,
        }
    visible_rows = [
        r for r in rows
        if (a := acls.get(r.acl_id)) is not None
        and is_visible(a.modules, a.departments, a.restriction, ent)
    ]
    visible_ids = {r.evid for r in visible_rows}
    claims = list(by_name.get("S7", {}).get("claims", []))
    kept, withheld = withhold_claims(claims, visible_ids)
    lines = [f"{c.get('text', '')} " + "".join(f"[{x}]" for x in c.get("cites", []))
             for c in kept]
    return {
        "run_id": run_id, "ticket": run.ticket_key, "status": run.status,
        "trigger": run.trigger, "cost_usd": run.cost_usd,
        "evidence": [
            {"id": r.evid, "kind": r.kind, "key": r.key, "title": r.title,
             "snippet": redact(r.snippet, ent), "outcome": r.outcome}
            for r in visible_rows
        ],
        "claims": kept, "withheld": withheld,
        "answer_text": "\n".join(lines),
        "synthesis": {
            k: by_name.get("S7", {}).get(k)
            for k in ("seen_before", "outcomes", "likely_cause",
                      "fix_or_workaround", "who_to_ask", "confidence")
        },
        "wrong_module_alert": None,
    }
