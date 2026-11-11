"""Translated from VendorPortalServiceTests.cs."""

from __future__ import annotations

from decimal import Decimal

import pytest
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.localization.localization_translation import LocalizationTranslation
from app.models.localization.marketplace_bid import MarketplaceBid
from app.models.localization.marketplace_job import MarketplaceJob
from app.models.localization.vendor import Vendor
from app.services.localization.localization_exceptions import (
    InvalidJobStateException,
    VendorLanguageMismatchException,
)

from .localization_fixture import marketplace, seed_project, vendor_portal


@pytest.mark.asyncio
async def test_submit_bid_on_non_open_job_throws(
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
    bid = await portal.submit_bid_async(job.id, seed.vendor.id, Decimal("120"), "note")
    await market.award_bid_async(job.id, bid.id)

    with pytest.raises(InvalidJobStateException, match="Awarded"):
        await portal.submit_bid_async(job.id, other.id, Decimal("100"), "late")


@pytest.mark.asyncio
async def test_submit_bid_vendor_without_language_throws_mismatch(
    scratch_session: AsyncSession,
) -> None:
    db = scratch_session
    seed = await seed_project(db)
    market = marketplace(db)
    portal = vendor_portal(db)

    japanese_only = Vendor(name="JP Vendor", languages="ja-JP", rating=Decimal("5.0"))
    db.add(japanese_only)
    await db.flush()

    job = await market.post_to_marketplace_async(seed.project.slug, "de-DE")

    with pytest.raises(VendorLanguageMismatchException):
        await portal.submit_bid_async(
            job.id, japanese_only.id, Decimal("100"), "note"
        )

    bids = (await db.execute(select(MarketplaceBid))).scalars().all()
    assert bids == []


@pytest.mark.asyncio
async def test_submit_bid_duplicate_pending_bid_throws(
    scratch_session: AsyncSession,
) -> None:
    db = scratch_session
    seed = await seed_project(db)
    market = marketplace(db)
    portal = vendor_portal(db)

    job = await market.post_to_marketplace_async(seed.project.slug, "de-DE")
    await portal.submit_bid_async(job.id, seed.vendor.id, Decimal("120"), "first")

    with pytest.raises(InvalidJobStateException):
        await portal.submit_bid_async(job.id, seed.vendor.id, Decimal("110"), "second")

    bids = (await db.execute(select(MarketplaceBid))).scalars().all()
    assert len(bids) == 1


@pytest.mark.asyncio
async def test_submit_bid_non_positive_price_throws_argument_exception(
    scratch_session: AsyncSession,
) -> None:
    db = scratch_session
    seed = await seed_project(db)
    market = marketplace(db)
    portal = vendor_portal(db)

    job = await market.post_to_marketplace_async(seed.project.slug, "de-DE")

    with pytest.raises(ValueError):
        await portal.submit_bid_async(job.id, seed.vendor.id, Decimal("0"), "free")

    bids = (await db.execute(select(MarketplaceBid))).scalars().all()
    assert bids == []


@pytest.mark.asyncio
async def test_update_job_string_on_approved_job_throws_and_leaves_text_unchanged(
    scratch_session: AsyncSession,
) -> None:
    db = scratch_session
    seed = await seed_project(db)
    market = marketplace(db)
    portal = vendor_portal(db)

    job = await market.post_to_marketplace_async(seed.project.slug, "de-DE")
    bid = await portal.submit_bid_async(job.id, seed.vendor.id, Decimal("120"), "note")
    await market.award_bid_async(job.id, bid.id)
    for item in seed.strings:
        await portal.update_job_string_async(job.id, item.id, f"target-{item.key}")
    await portal.submit_job_for_review_async(job.id)
    await market.approve_submission_async(job.id)

    with pytest.raises(InvalidJobStateException):
        await portal.update_job_string_async(
            job.id, seed.strings[0].id, "sneaky edit"
        )

    translation = (
        await db.execute(
            select(LocalizationTranslation).where(
                LocalizationTranslation.string_id == seed.strings[0].id,
                LocalizationTranslation.locale_code == "de-DE",
            )
        )
    ).scalar_one()
    assert translation.target_text == f"target-{seed.strings[0].key}"


@pytest.mark.asyncio
async def test_update_job_string_on_needs_revision_moves_job_to_in_progress(
    scratch_session: AsyncSession,
) -> None:
    db = scratch_session
    seed = await seed_project(db)
    market = marketplace(db)
    portal = vendor_portal(db)

    job = await market.post_to_marketplace_async(seed.project.slug, "de-DE")
    bid = await portal.submit_bid_async(job.id, seed.vendor.id, Decimal("120"), "note")
    await market.award_bid_async(job.id, bid.id)
    for item in seed.strings:
        await portal.update_job_string_async(job.id, item.id, f"target-{item.key}")
    await portal.submit_job_for_review_async(job.id)
    sent_back = await market.send_back_for_revision_async(job.id)
    assert sent_back.status == "NeedsRevision"

    updated = await portal.update_job_string_async(
        job.id, seed.strings[0].id, "revised text"
    )

    assert updated.target_text == "revised text"
    reloaded = (
        await db.execute(
            select(MarketplaceJob).where(MarketplaceJob.id == job.id)
        )
    ).scalar_one()
    assert reloaded.status == "InProgress"


@pytest.mark.asyncio
async def test_update_job_string_on_awarded_job_moves_job_to_in_progress(
    scratch_session: AsyncSession,
) -> None:
    db = scratch_session
    seed = await seed_project(db)
    market = marketplace(db)
    portal = vendor_portal(db)

    job = await market.post_to_marketplace_async(seed.project.slug, "de-DE")
    bid = await portal.submit_bid_async(job.id, seed.vendor.id, Decimal("120"), "note")
    await market.award_bid_async(job.id, bid.id)

    await portal.update_job_string_async(job.id, seed.strings[0].id, "first edit")

    reloaded = (
        await db.execute(
            select(MarketplaceJob).where(MarketplaceJob.id == job.id)
        )
    ).scalar_one()
    assert reloaded.status == "InProgress"


@pytest.mark.asyncio
async def test_submit_job_for_review_on_open_job_throws(
    scratch_session: AsyncSession,
) -> None:
    db = scratch_session
    seed = await seed_project(db)
    market = marketplace(db)
    portal = vendor_portal(db)

    job = await market.post_to_marketplace_async(seed.project.slug, "de-DE")

    with pytest.raises(InvalidJobStateException, match="Open"):
        await portal.submit_job_for_review_async(job.id)
