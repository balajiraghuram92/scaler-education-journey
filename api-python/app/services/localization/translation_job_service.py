"""Ported from api/Services/Localization/TranslationJobService.cs."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import UTC, datetime

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from ...models.localization.localization_locale import LocalizationLocale
from ...models.localization.localization_project import LocalizationProject
from ...models.localization.localization_string import LocalizationString
from ...models.localization.localization_translation import LocalizationTranslation
from ...models.localization.service_agreement import ServiceAgreement
from ...models.localization.service_tiers import ServiceTiers
from ...models.localization.team_assignment import TeamAssignment
from ...models.localization.translation_job import TranslationJob
from ...models.localization.vendor import Vendor
from ...schemas.localization_dtos import (
    AgreementTeamDto,
    OpsAgreementTeamDto,
    OpsServiceAgreementDto,
    SaveAgreementRequest,
    ServiceAgreementDto,
    TranslationJobRowDto,
)
from .job_scope import JobScope
from .localization_exceptions import (
    InvalidJobStateException,
    LocalizationLocaleNotFoundException,
    LocalizationProjectNotFoundException,
    MarketplaceJobNotFoundException,
)


@dataclass
class _AssignedTeam:
    vendor_id: int
    alias: str
    member_count: int


class TranslationJobService:
    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def get_jobs_for_project_async(
        self, project_slug: str
    ) -> list[TranslationJobRowDto]:
        project = (
            await self._session.execute(
                select(LocalizationProject)
                .options(
                    selectinload(LocalizationProject.locales),
                    selectinload(LocalizationProject.strings).selectinload(
                        LocalizationString.translations
                    ),
                )
                .where(LocalizationProject.slug == project_slug)
            )
        ).scalar_one_or_none()
        if project is None:
            raise LocalizationProjectNotFoundException(project_slug)

        jobs = (
            await self._session.execute(
                select(TranslationJob)
                .options(selectinload(TranslationJob.vendor))
                .where(TranslationJob.project_id == project.id)
            )
        ).scalars().all()

        teams = await self._assigned_teams_async(project.id)

        rows: list[TranslationJobRowDto] = []
        for locale in sorted(project.locales, key=lambda item: item.id):
            job = next(
                (
                    j
                    for j in sorted(jobs, key=lambda j: j.id, reverse=True)
                    if j.locale_code == locale.locale_code
                ),
                None,
            )
            team = teams.get(locale.locale_code)
            if job is None:
                open_strings = [
                    s
                    for s in project.strings
                    if JobScope.is_open(s, locale.locale_code)
                ]
                rows.append(
                    TranslationJobRowDto(
                        id=None,
                        project_id=project.id,
                        locale_code=locale.locale_code,
                        status="NotCreated",
                        string_count=len(open_strings),
                        word_count=_count_words(open_strings),
                        completed_percent=0,
                        vendor_team_alias=team.alias if team else None,
                        member_count=team.member_count if team else None,
                        created_at=None,
                        submitted_at=None,
                        approved_at=None,
                    )
                )
            else:
                rows.append(
                    TranslationJobRowDto(
                        id=job.id,
                        project_id=project.id,
                        locale_code=job.locale_code,
                        status=job.status,
                        string_count=job.string_count,
                        word_count=job.word_count,
                        completed_percent=JobScope.completed_percent(
                            project.strings,
                            job.locale_code,
                            job.string_count,
                            job.status,
                        ),
                        vendor_team_alias=job.vendor.alias if job.vendor else None,
                        member_count=team.member_count if team else None,
                        created_at=job.created_at,
                        submitted_at=job.submitted_at,
                        approved_at=job.approved_at,
                    )
                )
        return rows

    async def create_job_async(
        self, project_slug: str, locale_code: str
    ) -> TranslationJobRowDto:
        project = (
            await self._session.execute(
                select(LocalizationProject)
                .options(
                    selectinload(LocalizationProject.locales),
                    selectinload(LocalizationProject.strings).selectinload(
                        LocalizationString.translations
                    ),
                )
                .where(LocalizationProject.slug == project_slug)
            )
        ).scalar_one_or_none()
        if project is None:
            raise LocalizationProjectNotFoundException(project_slug)

        if not any(
            locale.locale_code == locale_code for locale in project.locales
        ):
            raise LocalizationLocaleNotFoundException(locale_code)

        teams = await self._assigned_teams_async(project.id)
        team = teams.get(locale_code)
        if team is None:
            raise InvalidJobStateException(
                f"NO_TEAM_FOR_LOCALE: the agreement assigns no team to locale '{locale_code}'."
            )

        most_recent_job = (
            await self._session.execute(
                select(TranslationJob)
                .where(
                    TranslationJob.project_id == project.id,
                    TranslationJob.locale_code == locale_code,
                )
                .order_by(TranslationJob.id.desc())
            )
        ).scalar_one_or_none()
        if (
            most_recent_job is not None
            and most_recent_job.status != "Approved"
            and most_recent_job.status != "Closed"
        ):
            raise InvalidJobStateException(
                f"Cannot create a new job for locale '{locale_code}' while job "
                f"{most_recent_job.id} is in status '{most_recent_job.status}'."
            )

        # The session may already hold this project's strings from an earlier
        # load in the same request (e.g. the workflow action posts after a
        # direct create); refresh them so the count sees fresh rows, as the
        # C# relationship fixup would.
        await self._session.refresh(project, ["strings"])
        for item in project.strings:
            await self._session.refresh(item, ["translations"])
        open_strings = [
            s for s in project.strings if JobScope.is_open(s, locale_code)
        ]
        if not open_strings:
            raise InvalidJobStateException(
                f"There is nothing left to translate for locale '{locale_code}'."
            )

        job = TranslationJob(
            project_id=project.id,
            locale_code=locale_code,
            status="Assigned",
            string_count=len(open_strings),
            word_count=_count_words(open_strings),
            vendor_id=team.vendor_id,
            created_at=datetime.now(UTC),
        )
        self._session.add(job)
        await self._session.flush()
        return await self._job_row_async(job.id)

    async def approve_async(self, job_id: int) -> TranslationJobRowDto:
        job = (
            await self._session.execute(
                select(TranslationJob).where(TranslationJob.id == job_id)
            )
        ).scalar_one_or_none()
        if job is None:
            raise MarketplaceJobNotFoundException(job_id)
        if job.status != "SubmittedForReview":
            raise InvalidJobStateException(
                f"Cannot approve job {job_id} because it is in status "
                f"'{job.status}'. Expected 'SubmittedForReview'."
            )

        now = datetime.now(UTC)
        job.status = "Approved"
        job.approved_at = now

        translations = (
            await self._session.execute(
                select(LocalizationTranslation)
                .join(
                    LocalizationString,
                    LocalizationString.id == LocalizationTranslation.string_id,
                )
                .where(
                    LocalizationString.project_id == job.project_id,
                    LocalizationTranslation.locale_code == job.locale_code,
                )
            )
        ).scalars().all()
        for trans in translations:
            if not _is_blank(trans.target_text):
                trans.stage = "Approved"
                trans.updated_at = now

        await self._session.flush()
        return await self._job_row_async(job.id)

    async def send_back_async(self, job_id: int) -> TranslationJobRowDto:
        job = (
            await self._session.execute(
                select(TranslationJob).where(TranslationJob.id == job_id)
            )
        ).scalar_one_or_none()
        if job is None:
            raise MarketplaceJobNotFoundException(job_id)
        if job.status != "SubmittedForReview":
            raise InvalidJobStateException(
                f"Cannot send back job {job_id} because it is in status "
                f"'{job.status}'. Expected 'SubmittedForReview'."
            )

        job.status = "NeedsRevision"
        await self._session.flush()
        return await self._job_row_async(job.id)

    async def get_agreement_async(
        self, project_slug: str, for_operations: bool
    ) -> ServiceAgreementDto | OpsServiceAgreementDto | None:
        project = (
            await self._session.execute(
                select(LocalizationProject).where(
                    LocalizationProject.slug == project_slug
                )
            )
        ).scalar_one_or_none()
        if project is None:
            raise LocalizationProjectNotFoundException(project_slug)

        agreement = (
            await self._session.execute(
                select(ServiceAgreement).where(
                    ServiceAgreement.project_id == project.id
                )
            )
        ).scalar_one_or_none()
        if agreement is None:
            return None

        teams = (
            await self._session.execute(
                select(TeamAssignment)
                .options(selectinload(TeamAssignment.vendor))
                .where(TeamAssignment.agreement_id == agreement.id)
                .order_by(TeamAssignment.locale_code)
            )
        ).scalars().all()

        if for_operations:
            return OpsServiceAgreementDto(
                tier=agreement.tier,
                members_per_team=ServiceTiers.members_for(agreement.tier),
                valid_from=agreement.valid_from,
                valid_to=agreement.valid_to,
                client_alias=project.client_alias,
                teams=[
                    OpsAgreementTeamDto(
                        locale_code=t.locale_code,
                        vendor_team_alias=t.vendor.alias if t.vendor else "",
                        member_count=t.member_count,
                        vendor_team_id=t.vendor_id,
                        vendor_team_real_name=t.vendor.name if t.vendor else "",
                    )
                    for t in teams
                ],
            )
        return ServiceAgreementDto(
            tier=agreement.tier,
            members_per_team=ServiceTiers.members_for(agreement.tier),
            valid_from=agreement.valid_from,
            valid_to=agreement.valid_to,
            teams=[
                AgreementTeamDto(
                    locale_code=t.locale_code,
                    vendor_team_alias=t.vendor.alias if t.vendor else "",
                    member_count=t.member_count,
                )
                for t in teams
            ],
        )

    async def save_agreement_async(
        self, project_slug: str, request: SaveAgreementRequest
    ) -> OpsServiceAgreementDto:
        project = (
            await self._session.execute(
                select(LocalizationProject).where(
                    LocalizationProject.slug == project_slug
                )
            )
        ).scalar_one_or_none()
        if project is None:
            raise LocalizationProjectNotFoundException(project_slug)

        tiers = (ServiceTiers.SILVER, ServiceTiers.GOLD, ServiceTiers.PLATINUM)
        if request.tier is None or not request.tier.strip() or request.tier not in tiers:
            # The detail embeds .NET's Message suffix verbatim; the C# names
            # the whole request ("request") as the parameter.
            raise ValueError(
                f"Unknown service tier '{request.tier or ''}'. (Parameter 'request')"
            )
        tier = request.tier

        teams = request.teams or []
        locale_codes = (
            await self._session.execute(
                select(LocalizationLocale.locale_code).where(
                    LocalizationLocale.project_id == project.id
                )
            )
        ).scalars().all()
        vendors = {
            v.id: v
            for v in (
                await self._session.execute(select(Vendor))
            )
            .scalars()
            .all()
        }

        seen: set[str] = set()
        for team in teams:
            if team.locale_code is None or not team.locale_code.strip() or team.locale_code not in locale_codes:
                raise ValueError(
                    f"Locale '{team.locale_code or ''}' is not a locale of "
                    f"project '{project_slug}'. (Parameter 'request')"
                )
            if team.locale_code in seen:
                raise ValueError(
                    f"Locale '{team.locale_code}' is listed twice. (Parameter 'request')"
                )
            seen.add(team.locale_code)
            if team.vendor_team_id is None or team.vendor_team_id not in vendors:
                vendor_id = "" if team.vendor_team_id is None else team.vendor_team_id
                raise ValueError(
                    f"Unknown vendor team '{vendor_id}'. (Parameter 'request')"
                )

        agreement = (
            await self._session.execute(
                select(ServiceAgreement).where(
                    ServiceAgreement.project_id == project.id
                )
            )
        ).scalar_one_or_none()
        if agreement is None:
            agreement = ServiceAgreement(
                project_id=project.id,
                tier=tier,
                valid_from=request.valid_from or datetime.now(UTC),
                valid_to=request.valid_to,
                created_at=datetime.now(UTC),
            )
            self._session.add(agreement)
        else:
            agreement.tier = tier
            if request.valid_from is not None:
                agreement.valid_from = request.valid_from
            agreement.valid_to = request.valid_to
            stale = (
                await self._session.execute(
                    select(TeamAssignment).where(
                        TeamAssignment.agreement_id == agreement.id
                    )
                )
            ).scalars().all()
            for row in stale:
                await self._session.delete(row)
            # Flush the DELETEs first: the unit of work would
            # otherwise emit the INSERTs below before them and
            # collide on ux_localization_team_assignments_agreement_locale.
            await self._session.flush()

        member_count = ServiceTiers.members_for(tier)
        for team in teams:
            # Validated above: both fields are present and the vendor exists.
            assert team.locale_code is not None and team.vendor_team_id is not None
            self._session.add(
                TeamAssignment(
                    agreement=agreement,
                    vendor_id=team.vendor_team_id,
                    locale_code=team.locale_code,
                    member_count=member_count,
                )
            )

        await self._session.flush()
        saved_teams: list[OpsAgreementTeamDto] = []
        for team in teams:
            assert team.locale_code is not None and team.vendor_team_id is not None
            vendor = vendors[team.vendor_team_id]
            saved_teams.append(
                OpsAgreementTeamDto(
                    locale_code=team.locale_code,
                    vendor_team_alias=vendor.alias,
                    member_count=member_count,
                    vendor_team_id=team.vendor_team_id,
                    vendor_team_real_name=vendor.name,
                )
            )
        return OpsServiceAgreementDto(
            tier=agreement.tier,
            members_per_team=member_count,
            valid_from=agreement.valid_from,
            valid_to=agreement.valid_to,
            client_alias=project.client_alias,
            teams=saved_teams,
        )

    async def _job_row_async(self, job_id: int) -> TranslationJobRowDto:
        job = (
            await self._session.execute(
                select(TranslationJob)
                .options(selectinload(TranslationJob.vendor))
                .where(TranslationJob.id == job_id)
            )
        ).scalar_one_or_none()
        if job is None:
            raise MarketplaceJobNotFoundException(job_id)

        strings = (
            await self._session.execute(
                select(LocalizationString)
                .options(
                    selectinload(LocalizationString.translations.and_(
                        LocalizationTranslation.locale_code == job.locale_code
                    ))
                )
                .where(LocalizationString.project_id == job.project_id)
            )
        ).scalars().all()

        teams = await self._assigned_teams_async(job.project_id)
        team = teams.get(job.locale_code)
        return TranslationJobRowDto(
            id=job.id,
            project_id=job.project_id,
            locale_code=job.locale_code,
            status=job.status,
            string_count=job.string_count,
            word_count=job.word_count,
            completed_percent=JobScope.completed_percent(
                strings, job.locale_code, job.string_count, job.status
            ),
            vendor_team_alias=job.vendor.alias if job.vendor else None,
            member_count=team.member_count if team else None,
            created_at=job.created_at,
            submitted_at=job.submitted_at,
            approved_at=job.approved_at,
        )

    async def _assigned_teams_async(self, project_id: int) -> dict[str, _AssignedTeam]:
        agreement = (
            await self._session.execute(
                select(ServiceAgreement).where(
                    ServiceAgreement.project_id == project_id
                )
            )
        ).scalar_one_or_none()
        if agreement is None:
            return {}
        rows = (
            await self._session.execute(
                select(TeamAssignment)
                .options(selectinload(TeamAssignment.vendor))
                .where(TeamAssignment.agreement_id == agreement.id)
            )
        ).scalars().all()
        return {
            t.locale_code: _AssignedTeam(
                vendor_id=t.vendor_id,
                alias=t.vendor.alias if t.vendor else "",
                member_count=t.member_count,
            )
            for t in rows
        }


def _is_blank(value: str | None) -> bool:
    return value is None or not value.strip()


def _count_words(strings: list[LocalizationString]) -> int:
    # C# splits on the space character only (not tabs/newlines) and drops
    # empty entries; str.split(" ") with the truthiness filter matches it.
    return sum(1 for s in strings for part in s.source_text.split(" ") if part)
