"""Fix candidates: a ticket qualifies only via allow-list, confidence, opt-in."""
from __future__ import annotations

from sqlalchemy import select

from app.governance.rls import service_session
from app.ingest.ownership import current_owner
from app.models.g2 import Run, RunStage
from app.models.g3 import DeveloperProfile, FixCandidate
from app.settings import Settings


def candidate_eligible(
    module: str, confidence: float, owner_opt_in: bool,
    allowlist: list[str], threshold: float,
) -> bool:
    return module in allowlist and confidence >= threshold and owner_opt_in


async def consider_run(settings: Settings, run_id: str) -> FixCandidate:
    """Create (or return the existing) fix candidate for a DONE run."""
    async with service_session() as session:
        run = (
            await session.execute(select(Run).where(Run.id == run_id))
        ).scalar_one()
        existing: FixCandidate | None = (
            await session.execute(
                select(FixCandidate).where(FixCandidate.run_id == run_id)
            )
        ).scalar_one_or_none()
        if existing is not None:
            return existing
        from app.models.g1 import Case

        ticket = (
            await session.execute(
                select(Case).where(Case.source_key == run.ticket_key)
            )
        ).scalar_one()
        s7 = (
            await session.execute(
                select(RunStage).where(
                    RunStage.run_id == run_id, RunStage.stage == "S7"
                )
            )
        ).scalar_one_or_none()
        confidence = float((s7.output_json if s7 else {}).get("confidence", 0.0))
        owner = await current_owner(session, ticket.module)
        profile = None
        if owner:
            profile = (
                await session.execute(
                    select(DeveloperProfile).where(DeveloperProfile.handle == owner)
                )
            ).scalar_one_or_none()
        opt_in = bool(profile.opt_in_fix) if profile else False
        eligible = candidate_eligible(
            ticket.module, confidence, opt_in,
            settings.fix_allowlist, settings.fix_confidence_threshold,
        )
        candidate = FixCandidate(
            run_id=run_id, ticket_key=run.ticket_key, module=ticket.module,
            confidence=confidence, owner_opt_in=opt_in,
            status="PENDING" if eligible else "REJECTED",
        )
        session.add(candidate)
        await session.commit()
        return candidate


async def ensure_opt_in(handle: str, modules: str, opt_in: bool = True) -> None:
    """Seed helper used by evals and local setup."""
    async with service_session() as session:
        profile = (
            await session.execute(
                select(DeveloperProfile).where(DeveloperProfile.handle == handle)
            )
        ).scalar_one_or_none()
        if profile is None:
            session.add(
                DeveloperProfile(handle=handle, modules=modules, opt_in_fix=opt_in)
            )
        else:
            profile.modules = modules
            profile.opt_in_fix = opt_in
        await session.commit()
