"""Translated from TranslationJobServiceTests.cs."""

from __future__ import annotations

from datetime import UTC, datetime, timedelta

import pytest
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.localization.localization_locale import LocalizationLocale
from app.models.localization.localization_project import LocalizationProject
from app.models.localization.localization_string import LocalizationString
from app.models.localization.localization_translation import LocalizationTranslation
from app.models.localization.service_agreement import ServiceAgreement
from app.models.localization.service_tiers import ServiceTiers
from app.models.localization.team_assignment import TeamAssignment
from app.models.localization.translation_job import TranslationJob
from app.models.localization.vendor import Vendor
from app.schemas.localization_dtos import (
    AgreementTeamDto,
    AgreementTeamRequest,
    SaveAgreementRequest,
    ServiceAgreementDto,
    TranslationJobRowDto,
    VendorStringRowDto,
)
from app.services.localization.localization_exceptions import InvalidJobStateException

from .localization_fixture import jobs, seed_project, vendor_portal


async def _seed_vendor(
    db: AsyncSession,
    alias: str = "Vendor Team Test",
    languages: str = "de-DE,fr-FR",
) -> Vendor:
    vendor = Vendor(name="Test Team", alias=alias, languages=languages)
    db.add(vendor)
    await db.flush()
    return vendor


async def _seed_agreement(
    db: AsyncSession, project_id: int, vendor_id: int, *locale_codes: str
) -> None:
    now = datetime.now(UTC)
    agreement = ServiceAgreement(
        project_id=project_id,
        tier=ServiceTiers.SILVER,
        valid_from=now - timedelta(days=1),
        created_at=now,
    )
    db.add(agreement)
    await db.flush()
    for locale_code in locale_codes:
        db.add(
            TeamAssignment(
                agreement_id=agreement.id,
                vendor_id=vendor_id,
                locale_code=locale_code,
                member_count=ServiceTiers.members_for(ServiceTiers.SILVER),
            )
        )
    await db.flush()


@pytest.mark.asyncio
async def test_create_job_picks_team_from_agreement(
    scratch_session: AsyncSession,
) -> None:
    db = scratch_session
    seed = await seed_project(db)
    vendor = await _seed_vendor(db)
    await _seed_agreement(db, seed.project.id, vendor.id, "de-DE", "fr-FR")
    job_service = jobs(db)

    row = await job_service.create_job_async(seed.project.slug, "de-DE")

    assert row.status == "Assigned"
    assert row.vendor_team_alias == "Vendor Team Test"
    assert row.member_count == 3
    assert row.string_count == 2
    assert row.created_at is not None

    stored = (await db.execute(select(TranslationJob))).scalar_one()
    assert stored.vendor_id == vendor.id


@pytest.mark.asyncio
async def test_create_job_locale_without_team_throws_no_team(
    scratch_session: AsyncSession,
) -> None:
    db = scratch_session
    seed = await seed_project(db)
    vendor = await _seed_vendor(db)
    await _seed_agreement(db, seed.project.id, vendor.id, "de-DE")
    job_service = jobs(db)

    with pytest.raises(InvalidJobStateException, match="NO_TEAM_FOR_LOCALE"):
        await job_service.create_job_async(seed.project.slug, "fr-FR")


@pytest.mark.asyncio
async def test_create_job_existing_non_terminal_job_throws_conflict(
    scratch_session: AsyncSession,
) -> None:
    db = scratch_session
    seed = await seed_project(db)
    vendor = await _seed_vendor(db)
    await _seed_agreement(db, seed.project.id, vendor.id, "de-DE")
    job_service = jobs(db)

    await job_service.create_job_async(seed.project.slug, "de-DE")

    with pytest.raises(InvalidJobStateException):
        await job_service.create_job_async(seed.project.slug, "de-DE")
    assert len((await db.execute(select(TranslationJob))).scalars().all()) == 1


@pytest.mark.asyncio
async def test_create_job_machine_translated_locale_creates_job_over_all_strings(
    scratch_session: AsyncSession,
) -> None:
    db = scratch_session
    seed = await seed_project(db)
    vendor = await _seed_vendor(db)
    await _seed_agreement(db, seed.project.id, vendor.id, "de-DE")
    now = datetime.now(UTC)
    for item in seed.strings:
        db.add(
            LocalizationTranslation(
                string_id=item.id,
                locale_code="de-DE",
                target_text="maschinell",
                stage="Translated",
                translation_source="AI",
                needs_review=False,
                updated_at=now,
            )
        )
    await db.flush()
    job_service = jobs(db)

    row = await job_service.create_job_async(seed.project.slug, "de-DE")

    assert row.status == "Assigned"
    assert row.string_count == 2


@pytest.mark.asyncio
async def test_create_job_fully_approved_locale_throws_nothing_left(
    scratch_session: AsyncSession,
) -> None:
    db = scratch_session
    seed = await seed_project(db)
    vendor = await _seed_vendor(db)
    await _seed_agreement(db, seed.project.id, vendor.id, "de-DE")
    now = datetime.now(UTC)
    for item in seed.strings:
        db.add(
            LocalizationTranslation(
                string_id=item.id,
                locale_code="de-DE",
                target_text="genehmigt",
                stage="Approved",
                translation_source="Marketplace",
                needs_review=False,
                updated_at=now,
            )
        )
    await db.flush()
    job_service = jobs(db)

    with pytest.raises(InvalidJobStateException, match="nothing left to translate"):
        await job_service.create_job_async(seed.project.slug, "de-DE")


@pytest.mark.asyncio
async def test_job_lifecycle_assigned_to_approved(
    scratch_session: AsyncSession,
) -> None:
    db = scratch_session
    seed = await seed_project(db)
    vendor = await _seed_vendor(db)
    await _seed_agreement(db, seed.project.id, vendor.id, "de-DE")
    job_service = jobs(db)
    portal = vendor_portal(db)

    created = await job_service.create_job_async(seed.project.slug, "de-DE")
    assert created.status == "Assigned"
    assert created.id is not None
    job_id = created.id

    await portal.update_job_string_async(job_id, seed.strings[0].id, "Hallo Welt")
    await portal.update_job_string_async(job_id, seed.strings[1].id, "Gute Nacht")
    edited = (
        await db.execute(
            select(TranslationJob).where(TranslationJob.id == job_id)
        )
    ).scalar_one()
    assert edited.status == "InProgress"

    submitted = await portal.submit_job_for_review_async(job_id)
    assert submitted.status == "SubmittedForReview"

    approved = await job_service.approve_async(job_id)
    assert approved.status == "Approved"
    assert approved.approved_at is not None

    stages = (
        await db.execute(
            select(LocalizationTranslation.stage).where(
                LocalizationTranslation.locale_code == "de-DE"
            )
        )
    ).scalars().all()
    assert len(stages) == 2
    assert all(stage == "Approved" for stage in stages)


@pytest.mark.asyncio
async def test_approved_job_rejects_further_edits_and_submits(
    scratch_session: AsyncSession,
) -> None:
    db = scratch_session
    seed = await seed_project(db)
    vendor = await _seed_vendor(db)
    await _seed_agreement(db, seed.project.id, vendor.id, "de-DE")
    job_service = jobs(db)
    portal = vendor_portal(db)

    created = await job_service.create_job_async(seed.project.slug, "de-DE")
    assert created.id is not None
    job_id = created.id
    await portal.update_job_string_async(job_id, seed.strings[0].id, "Hallo Welt")
    await portal.update_job_string_async(job_id, seed.strings[1].id, "Gute Nacht")
    await portal.submit_job_for_review_async(job_id)
    await job_service.approve_async(job_id)

    with pytest.raises(InvalidJobStateException):
        await portal.update_job_string_async(job_id, seed.strings[0].id, "x")
    with pytest.raises(InvalidJobStateException):
        await portal.submit_job_for_review_async(job_id)


@pytest.mark.asyncio
async def test_send_back_returns_job_to_vendor_loop(
    scratch_session: AsyncSession,
) -> None:
    db = scratch_session
    seed = await seed_project(db)
    vendor = await _seed_vendor(db)
    await _seed_agreement(db, seed.project.id, vendor.id, "de-DE")
    job_service = jobs(db)
    portal = vendor_portal(db)

    created = await job_service.create_job_async(seed.project.slug, "de-DE")
    assert created.id is not None
    job_id = created.id
    await portal.update_job_string_async(job_id, seed.strings[0].id, "Hallo Welt")
    await portal.update_job_string_async(job_id, seed.strings[1].id, "Gute Nacht")
    await portal.submit_job_for_review_async(job_id)

    sent_back = await job_service.send_back_async(job_id)
    assert sent_back.status == "NeedsRevision"

    await portal.update_job_string_async(job_id, seed.strings[0].id, "Hallo Welt!")
    edited = (
        await db.execute(
            select(TranslationJob).where(TranslationJob.id == job_id)
        )
    ).scalar_one()
    assert edited.status == "InProgress"


@pytest.mark.asyncio
async def test_completed_percent_counts_vendor_reviewed_non_approved_over_job_total(
    scratch_session: AsyncSession,
) -> None:
    db = scratch_session
    project = LocalizationProject(
        slug="pct", name="Pct", source_locale="en-US", client_alias="Client Team Test"
    )
    db.add(project)
    await db.flush()
    db.add(
        LocalizationLocale(
            project_id=project.id, locale_code="de-DE", display_name="German"
        )
    )
    cases = [
        ("Translated", "Marketplace"),  # counts: vendor-reviewed and open
        ("InReview", "Marketplace"),  # counts: vendor-reviewed and open
        ("Approved", "Marketplace"),  # excluded: approved
        ("Translated", "AI"),  # excluded: machine output
    ]
    for index, (stage, source) in enumerate(cases):
        item = LocalizationString(
            project_id=project.id, key=f"k{index}", source_text=f"text {index}"
        )
        db.add(item)
        await db.flush()
        db.add(
            LocalizationTranslation(
                string_id=item.id,
                locale_code="de-DE",
                target_text="t",
                stage=stage,
                translation_source=source,
                updated_at=datetime.now(UTC),
            )
        )
    db.add(
        TranslationJob(
            project_id=project.id,
            locale_code="de-DE",
            status="InProgress",
            string_count=4,
            word_count=8,
            created_at=datetime.now(UTC),
        )
    )
    await db.flush()
    job_service = jobs(db)

    rows = await job_service.get_jobs_for_project_async("pct")

    assert len(rows) == 1
    assert rows[0].completed_percent == 50


@pytest.mark.asyncio
async def test_completed_percent_zero_strings_is_zero(
    scratch_session: AsyncSession,
) -> None:
    db = scratch_session
    project = LocalizationProject(
        slug="empty",
        name="Empty",
        source_locale="en-US",
        client_alias="Client Team Test",
    )
    db.add(project)
    await db.flush()
    db.add(
        LocalizationLocale(
            project_id=project.id, locale_code="de-DE", display_name="German"
        )
    )
    await db.flush()
    job_service = jobs(db)

    rows = await job_service.get_jobs_for_project_async("empty")

    assert len(rows) == 1
    assert rows[0].status == "NotCreated"
    assert rows[0].string_count == 0
    assert rows[0].completed_percent == 0


@pytest.mark.asyncio
async def test_not_created_row_counts_open_strings(
    scratch_session: AsyncSession,
) -> None:
    db = scratch_session
    seed = await seed_project(db)
    now = datetime.now(UTC)
    db.add_all(
        [
            LocalizationTranslation(
                string_id=seed.strings[0].id,
                locale_code="de-DE",
                target_text="genehmigt",
                stage="Approved",
                translation_source="Marketplace",
                needs_review=False,
                updated_at=now,
            ),
            LocalizationTranslation(
                string_id=seed.strings[1].id,
                locale_code="de-DE",
                target_text="maschinell",
                stage="Translated",
                translation_source="AI",
                needs_review=False,
                updated_at=now,
            ),
        ]
    )
    await db.flush()
    job_service = jobs(db)

    rows = await job_service.get_jobs_for_project_async(seed.project.slug)

    row = next(r for r in rows if r.locale_code == "de-DE")
    assert row.status == "NotCreated"
    assert row.string_count == 1
    assert row.completed_percent == 0


@pytest.mark.asyncio
async def test_completed_percent_one_accepted_of_four_is_25_approved_is_100(
    scratch_session: AsyncSession,
) -> None:
    db = scratch_session
    project = LocalizationProject(
        slug="pct-accept",
        name="PctAccept",
        source_locale="en-US",
        client_alias="Client Team Test",
    )
    db.add(project)
    await db.flush()
    db.add(
        LocalizationLocale(
            project_id=project.id, locale_code="de-DE", display_name="German"
        )
    )
    strings: list[LocalizationString] = []
    for index in range(4):
        item = LocalizationString(
            project_id=project.id, key=f"k{index}", source_text=f"text {index}"
        )
        db.add(item)
        strings.append(item)
    await db.flush()
    now = datetime.now(UTC)
    for item in strings:
        db.add(
            LocalizationTranslation(
                string_id=item.id,
                locale_code="de-DE",
                target_text="maschinell",
                stage="Translated",
                translation_source="AI",
                needs_review=False,
                updated_at=now,
            )
        )
    vendor = await _seed_vendor(db)
    await _seed_agreement(db, project.id, vendor.id, "de-DE")
    await db.flush()
    job_service = jobs(db)
    portal = vendor_portal(db)

    created = await job_service.create_job_async(project.slug, "de-DE")
    assert created.string_count == 4
    assert created.id is not None
    job_id = created.id

    await portal.update_job_string_async(job_id, strings[0].id, "maschinell")
    rows = await job_service.get_jobs_for_project_async(project.slug)
    assert len(rows) == 1
    assert rows[0].completed_percent == 25

    for item in strings[1:]:
        await portal.update_job_string_async(job_id, item.id, "maschinell")
    await portal.submit_job_for_review_async(job_id)
    approved = await job_service.approve_async(job_id)
    assert approved.completed_percent == 100


@pytest.mark.asyncio
async def test_save_agreement_unknown_tier_is_rejected(
    scratch_session: AsyncSession,
) -> None:
    db = scratch_session
    seed = await seed_project(db)
    job_service = jobs(db)

    with pytest.raises(ValueError):
        await job_service.save_agreement_async(
            seed.project.slug, SaveAgreementRequest(tier="Bronze", teams=[])
        )


@pytest.mark.asyncio
async def test_save_agreement_foreign_locale_is_rejected(
    scratch_session: AsyncSession,
) -> None:
    db = scratch_session
    seed = await seed_project(db)
    vendor = await _seed_vendor(db)
    job_service = jobs(db)

    with pytest.raises(ValueError):
        await job_service.save_agreement_async(
            seed.project.slug,
            SaveAgreementRequest(
                tier=ServiceTiers.GOLD,
                teams=[AgreementTeamRequest(locale_code="xx-XX", vendor_team_id=vendor.id)],
            ),
        )


@pytest.mark.asyncio
async def test_save_agreement_unknown_team_is_rejected(
    scratch_session: AsyncSession,
) -> None:
    db = scratch_session
    seed = await seed_project(db)
    job_service = jobs(db)

    with pytest.raises(ValueError):
        await job_service.save_agreement_async(
            seed.project.slug,
            SaveAgreementRequest(
                tier=ServiceTiers.GOLD,
                teams=[AgreementTeamRequest(locale_code="de-DE", vendor_team_id=999)],
            ),
        )


@pytest.mark.asyncio
async def test_save_agreement_duplicate_locale_is_rejected(
    scratch_session: AsyncSession,
) -> None:
    db = scratch_session
    seed = await seed_project(db)
    vendor = await _seed_vendor(db)
    job_service = jobs(db)

    with pytest.raises(ValueError):
        await job_service.save_agreement_async(
            seed.project.slug,
            SaveAgreementRequest(
                tier=ServiceTiers.GOLD,
                teams=[
                    AgreementTeamRequest(
                        locale_code="de-DE", vendor_team_id=vendor.id
                    ),
                    AgreementTeamRequest(
                        locale_code="de-DE", vendor_team_id=vendor.id
                    ),
                ],
            ),
        )


@pytest.mark.asyncio
async def test_save_agreement_tier_update_changes_member_counts(
    scratch_session: AsyncSession,
) -> None:
    db = scratch_session
    seed = await seed_project(db)
    vendor = await _seed_vendor(db)
    job_service = jobs(db)

    await job_service.save_agreement_async(
        seed.project.slug,
        SaveAgreementRequest(
            tier=ServiceTiers.SILVER,
            teams=[
                AgreementTeamRequest(locale_code="de-DE", vendor_team_id=vendor.id)
            ],
        ),
    )

    saved = await job_service.save_agreement_async(
        seed.project.slug,
        SaveAgreementRequest(
            tier=ServiceTiers.PLATINUM,
            teams=[
                AgreementTeamRequest(locale_code="de-DE", vendor_team_id=vendor.id)
            ],
        ),
    )

    assert saved.tier == ServiceTiers.PLATINUM
    assert saved.members_per_team == 10
    assert len(saved.teams) == 1
    assert saved.teams[0].member_count == 10

    stored = (await db.execute(select(TeamAssignment))).scalars().all()
    assert len(stored) == 1
    assert stored[0].member_count == 10


def test_audience_separation_serializes_only_allowed_fields() -> None:
    now = datetime.now(UTC)

    job_json = TranslationJobRowDto(
        id=1,
        project_id=2,
        locale_code="de-DE",
        status="Assigned",
        string_count=10,
        word_count=50,
        completed_percent=0,
        vendor_team_alias="Vendor Team Larch",
        member_count=3,
        created_at=now,
        submitted_at=None,
        approved_at=None,
    ).model_dump_json()
    assert "vendorTeamAlias" in job_json
    assert "realName" not in job_json
    assert "RealName" not in job_json
    assert "score" not in job_json

    vendor_json = VendorStringRowDto(
        string_id=1,
        key="k",
        source_text="source",
        locale_code="de-DE",
        target_text="target",
        stage="Translated",
        translation_source="Manual",
        updated_at=now,
        score=4,
        needs_review=False,
        raw_mt_text="raw",
        raw_mt_score=3,
        in_job=True,
        vendor_reviewed=False,
    ).model_dump_json()
    assert '"score"' in vendor_json
    assert '"inJob"' in vendor_json
    assert '"vendorReviewed"' in vendor_json
    assert "project" not in vendor_json
    assert "Project" not in vendor_json

    agreement_json = ServiceAgreementDto(
        tier=ServiceTiers.GOLD,
        members_per_team=6,
        valid_from=now,
        valid_to=None,
        teams=[AgreementTeamDto(locale_code="de-DE", vendor_team_alias="Vendor Team Larch", member_count=6)],
    ).model_dump_json()
    assert "vendorTeamAlias" in agreement_json
    assert "realName" not in agreement_json
    assert "vendorTeamId" not in agreement_json
    assert "clientAlias" not in agreement_json
