"""Translated from MarketplaceServiceTests.cs."""

from __future__ import annotations

from datetime import datetime, timezone
from decimal import Decimal

import pytest
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.localization.localization_string import LocalizationString
from app.models.localization.localization_translation import LocalizationTranslation
from app.models.localization.marketplace_bid import MarketplaceBid
from app.models.localization.marketplace_job import MarketplaceJob
from app.models.localization.vendor import Vendor
from app.services.localization.localization_exceptions import (
    InvalidJobStateException,
    LocalizationLocaleNotFoundException,
)

from .localization_fixture import marketplace, seed_project, vendor_portal


@pytest.mark.asyncio
async def test_post_to_marketplace_unknown_locale_throws_locale_not_found(
    scratch_session: AsyncSession,
) -> None:
    db = scratch_session
    seed = await seed_project(db)
    market = marketplace(db)

    with pytest.raises(LocalizationLocaleNotFoundException):
        await market.post_to_marketplace_async(seed.project.slug, "xx-XX")

    jobs = (await db.execute(select(MarketplaceJob))).scalars().all()
    assert jobs == []


@pytest.mark.asyncio
async def test_post_to_marketplace_when_job_already_open_throws_and_leaves_row_untouched(
    scratch_session: AsyncSession,
) -> None:
    db = scratch_session
    seed = await seed_project(db)
    market = marketplace(db)

    first = await market.post_to_marketplace_async(seed.project.slug, "de-DE")
    assert first.status == "Open"

    with pytest.raises(InvalidJobStateException, match="Open"):
        await market.post_to_marketplace_async(seed.project.slug, "de-DE")

    jobs = (await db.execute(select(MarketplaceJob))).scalars().all()
    assert len(jobs) == 1
    only = jobs[0]
    assert only.id == first.id
    assert only.status == "Open"
    assert only.string_count == first.string_count
    assert only.word_count == first.word_count
    assert only.suggested_price_low == first.suggested_price_low
    assert only.suggested_price_high == first.suggested_price_high
    assert only.posted_at == first.posted_at


@pytest.mark.asyncio
async def test_post_to_marketplace_when_nothing_left_to_translate_throws(
    scratch_session: AsyncSession,
) -> None:
    db = scratch_session
    seed = await seed_project(db)
    market = marketplace(db)

    for item in seed.strings:
        db.add(
            LocalizationTranslation(
                string_id=item.id,
                locale_code="de-DE",
                target_text="übersetzt",
                stage="Translated",
                translation_source="Manual",
                needs_review=False,
                updated_at=datetime.now(timezone.utc),
            )
        )
    await db.flush()

    with pytest.raises(InvalidJobStateException, match="nothing left to translate"):
        await market.post_to_marketplace_async(seed.project.slug, "de-DE")

    jobs = (await db.execute(select(MarketplaceJob))).scalars().all()
    assert jobs == []


@pytest.mark.asyncio
async def test_post_to_marketplace_after_approved_creates_second_row_and_leaves_first_untouched(
    scratch_session: AsyncSession,
) -> None:
    db = scratch_session
    seed = await seed_project(db)
    market = marketplace(db)
    portal = vendor_portal(db)

    first = await market.post_to_marketplace_async(seed.project.slug, "de-DE")
    bid = await portal.submit_bid_async(first.id, seed.vendor.id, Decimal("120"), "note")
    await market.award_bid_async(first.id, bid.id)
    for item in seed.strings:
        await portal.update_job_string_async(first.id, item.id, f"target-{item.key}")
    await portal.submit_job_for_review_async(first.id)
    await market.approve_submission_async(first.id)

    # New source string arrives after approval, so there is work for a second job.
    s3 = LocalizationString(
        project_id=seed.project.id,
        key="k.three",
        source_text="Brand new string",
        created_at=datetime.now(timezone.utc),
    )
    db.add(s3)
    await db.flush()

    second = await market.post_to_marketplace_async(seed.project.slug, "de-DE")

    assert second.id != first.id
    assert second.status == "Open"
    assert second.string_count == 1

    jobs = (
        await db.execute(
            select(MarketplaceJob)
            .where(MarketplaceJob.locale_code == "de-DE")
            .order_by(MarketplaceJob.id)
        )
    ).scalars().all()
    assert len(jobs) == 2
    assert jobs[0].id == first.id
    assert jobs[0].status == "Approved"
    assert jobs[0].string_count == first.string_count
    assert jobs[0].word_count == first.word_count
    assert jobs[0].posted_at == first.posted_at


@pytest.mark.asyncio
async def test_award_bid_on_non_open_job_throws(
    scratch_session: AsyncSession,
) -> None:
    db = scratch_session
    seed = await seed_project(db)
    market = marketplace(db)
    portal = vendor_portal(db)

    job = await market.post_to_marketplace_async(seed.project.slug, "de-DE")
    bid = await portal.submit_bid_async(job.id, seed.vendor.id, Decimal("120"), "note")
    awarded = await market.award_bid_async(job.id, bid.id)
    assert awarded.status == "Awarded"

    with pytest.raises(InvalidJobStateException, match="Awarded"):
        await market.award_bid_async(job.id, bid.id)


@pytest.mark.asyncio
async def test_award_bid_declines_sibling_bids(
    scratch_session: AsyncSession,
) -> None:
    db = scratch_session
    seed = await seed_project(db)
    market = marketplace(db)
    portal = vendor_portal(db)

    other = Vendor(name="Other Vendor", languages="de-DE", rating=Decimal("4.0"))
    db.add(other)
    await db.flush()

    job = await market.post_to_marketplace_async(seed.project.slug, "de-DE")
    chosen = await portal.submit_bid_async(
        job.id, seed.vendor.id, Decimal("120"), "first"
    )
    sibling = await portal.submit_bid_async(
        job.id, other.id, Decimal("100"), "second"
    )

    await market.award_bid_async(job.id, chosen.id)

    bids = (
        await db.execute(
            select(MarketplaceBid).where(MarketplaceBid.marketplace_job_id == job.id)
        )
    ).scalars().all()
    by_id = {bid.id: bid for bid in bids}
    assert by_id[chosen.id].status == "Awarded"
    assert by_id[sibling.id].status == "Declined"


@pytest.mark.asyncio
async def test_approve_submission_when_not_submitted_for_review_throws(
    scratch_session: AsyncSession,
) -> None:
    from app.models.localization.ledger_entry import LedgerEntry

    db = scratch_session
    seed = await seed_project(db)
    market = marketplace(db)
    portal = vendor_portal(db)

    job = await market.post_to_marketplace_async(seed.project.slug, "de-DE")
    with pytest.raises(InvalidJobStateException):
        await market.approve_submission_async(job.id)

    bid = await portal.submit_bid_async(job.id, seed.vendor.id, Decimal("120"), "note")
    await market.award_bid_async(job.id, bid.id)
    with pytest.raises(InvalidJobStateException):
        await market.approve_submission_async(job.id)

    entries = (await db.execute(select(LedgerEntry))).scalars().all()
    assert entries == []


@pytest.mark.asyncio
async def test_send_back_for_revision_when_not_submitted_for_review_throws(
    scratch_session: AsyncSession,
) -> None:
    db = scratch_session
    seed = await seed_project(db)
    market = marketplace(db)

    job = await market.post_to_marketplace_async(seed.project.slug, "de-DE")
    with pytest.raises(InvalidJobStateException, match="Open"):
        await market.send_back_for_revision_async(job.id)

    reloaded = (
        await db.execute(
            select(MarketplaceJob).where(MarketplaceJob.id == job.id)
        )
    ).scalar_one()
    assert reloaded.status == "Open"


@pytest.mark.asyncio
async def test_approve_submission_advances_only_translated_strings_and_writes_single_ledger_entry(
    scratch_session: AsyncSession,
) -> None:
    from app.models.localization.ledger_entry import LedgerEntry

    db = scratch_session
    seed = await seed_project(db)
    market = marketplace(db)
    portal = vendor_portal(db)

    job = await market.post_to_marketplace_async(seed.project.slug, "de-DE")
    bid = await portal.submit_bid_async(
        job.id, seed.vendor.id, Decimal("123.45"), "note"
    )
    await market.award_bid_async(job.id, bid.id)
    for item in seed.strings:
        await portal.update_job_string_async(job.id, item.id, f"target-{item.key}")
    await portal.submit_job_for_review_async(job.id)

    # One translation loses its target text before approval; it must stay behind.
    blanked = (
        await db.execute(
            select(LocalizationTranslation).where(
                LocalizationTranslation.string_id == seed.strings[0].id,
                LocalizationTranslation.locale_code == "de-DE",
            )
        )
    ).scalar_one()
    blanked.target_text = ""
    blanked.stage = "New"
    await db.flush()

    approved = await market.approve_submission_async(job.id)
    assert approved.status == "Approved"

    translations = (
        await db.execute(
            select(LocalizationTranslation).where(
                LocalizationTranslation.locale_code == "de-DE"
            )
        )
    ).scalars().all()
    by_string = {trans.string_id: trans for trans in translations}
    assert by_string[seed.strings[0].id].stage == "New"
    assert by_string[seed.strings[1].id].stage == "Approved"

    entries = (
        await db.execute(
            select(LedgerEntry).where(LedgerEntry.related_marketplace_job_id == job.id)
        )
    ).scalars().all()
    assert len(entries) == 1
    assert entries[0].amount == Decimal("123.45")
    assert entries[0].source == "Marketplace"
