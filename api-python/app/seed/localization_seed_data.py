"""Ported from api/Data/LocalizationSeedData.cs."""

from __future__ import annotations

from datetime import UTC, datetime, timedelta
from decimal import ROUND_HALF_UP, Decimal

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from ..models.localization.build_snapshot import BuildSnapshot
from ..models.localization.build_snapshot_locale_count import BuildSnapshotLocaleCount
from ..models.localization.glossary_term import GlossaryTerm
from ..models.localization.ledger_entry import LedgerEntry
from ..models.localization.localization_locale import LocalizationLocale
from ..models.localization.localization_project import LocalizationProject
from ..models.localization.localization_string import LocalizationString
from ..models.localization.localization_translation import LocalizationTranslation
from ..models.localization.marketplace_bid import MarketplaceBid
from ..models.localization.marketplace_job import MarketplaceJob
from ..models.localization.provider_health_snapshot import ProviderHealthSnapshot
from ..models.localization.vendor import Vendor
from ..models.localization.workflow_step import WorkflowStep
from .localization_seed_translations import BY_KEY


async def seed(session: AsyncSession) -> None:
    exists = (
        await session.execute(select(LocalizationProject.id).limit(1))
    ).first()
    if exists is None:
        now = datetime.now(UTC)

        # 1. Seed Project: auroraline-hud-v3
        project = LocalizationProject(
            slug="auroraline-hud-v3",
            name="Auroraline Automotive — HUD Strings",
            source_locale="en-US",
            created_at=now - timedelta(days=30),
        )
        session.add(project)
        await session.flush()

        # 2. Seed 5 Locales
        for code, display in [
            ("de-DE", "German (Germany)"),
            ("ja-JP", "Japanese (Japan)"),
            ("zh-CN", "Chinese Simplified (China)"),
            ("fr-FR", "French (France)"),
            ("es-ES", "Spanish (Spain)"),
        ]:
            session.add(
                LocalizationLocale(
                    project_id=project.id, locale_code=code, display_name=display
                )
            )
        await session.flush()

        # 3. Seed 6 Strings
        created = now - timedelta(days=25)
        str_speed = await _add_string(session, project.id, "hud.speed.label", "Current Speed", created)
        str_fuel = await _add_string(session, project.id, "hud.warning.lowfuel", "Low fuel warning", created)
        str_nav = await _add_string(session, project.id, "hud.nav.turnleft", "Turn left ahead", created)
        str_temp = await _add_string(session, project.id, "hud.climate.temp", "Cabin temperature", created)
        str_door = await _add_string(session, project.id, "hud.alert.doorajar", "Door ajar", created)
        str_gear = await _add_string(session, project.id, "hud.gear.reverse", "Reverse gear engaged", created)

        additional = [
            ("hud.gear.park", "Park gear selected"),
            ("hud.gear.neutral", "Neutral gear active"),
            ("hud.gear.drive", "Drive gear engaged"),
            ("hud.tire.frontleft", "Front left tire"),
            ("hud.tire.frontright", "Front right tire"),
            ("hud.tire.rearleft", "Rear left tire"),
            ("hud.tire.rearright", "Rear right tire"),
            ("hud.media.play", "Resume media playback"),
            ("hud.media.pause", "Pause audio playback"),
            ("hud.media.next", "Skip next track"),
            ("hud.media.volume", "Adjust volume level"),
            ("hud.climate.fanspeed", "Fan speed setting"),
            ("hud.climate.autoclimate", "Automatic climate control"),
            ("hud.settings.brightness", "Display screen brightness"),
            ("hud.settings.language", "Select system language"),
            ("hud.nav.recalculating", "Recalculating navigation route"),
            ("hud.nav.arrived", "Destination reached ahead"),
            ("hud.battery.low", "Low battery level"),
            ("hud.battery.fastcharge", "Fast charging active"),
            ("hud.warning.enginetemp", "Engine coolant temperature high. Reduce speed and stop vehicle safely when convenient."),
            ("hud.warning.tirepressure", "Low tire pressure detected in rear left tire. Please inspect and reinflate promptly."),
            ("hud.assist.lanedeparture", "Lane departure alert: Unintended drift detected. Please keep both hands firmly on steering wheel."),
            ("hud.assist.forwardcollision", "Forward collision warning: Obstacle detected directly ahead. Apply emergency braking immediately."),
            ("hud.assist.blindspot", "Blind spot alert: Vehicle detected in adjacent blind zone. Do not change travel lanes."),
            ("hud.sensor.parkingrear", "Rear ultrasonic parking sensors active. Obstacle detected within three feet of rear bumper."),
            ("hud.connect.bluetooth", "Driver smartphone paired successfully over wireless Bluetooth. Audio streaming and hands-free calls ready."),
            ("hud.nav.tollroad", "Approaching toll road plaza in two miles. Move into open electronic transponder lane."),
            ("hud.system.otaavailable", "New system software update is ready for installation. Park vehicle and connect to Wi-Fi."),
            ("hud.service.oilchange", "Engine oil and filter change recommended within the next five hundred driving miles."),
            ("hud.service.brakewear", "Front brake pad wear limit reached. Schedule maintenance inspection with authorized dealer promptly."),
            ("hud.assist.adaptivecruise", "Adaptive cruise control enabled. Following distance set to three vehicle lengths ahead."),
            ("hud.alert.tractioncontrol", "Electronic traction control engaged. Slippery road conditions detected on current roadway surface."),
            ("hud.alert.washerfluid", "Windshield washer fluid reservoir is low. Please refill with recommended washer fluid."),
            ("hud.legal.assistdisclaimer", "Driver assistance systems, including adaptive cruise control, lane centering, and forward collision mitigation, are supplemental conveniences designed to support safe vehicle operation. These automated features do not replace an attentive driver or sound operational judgment. You must keep both hands on the steering wheel, monitor surrounding traffic conditions continuously, and remain prepared to resume manual vehicle control at any moment. Adverse weather, severe road glare, degraded pavement markings, and sensor contamination can impair system reliability. The vehicle operator remains fully responsible for safe driving and compliance with all motor vehicle traffic safety laws."),
            ("hud.legal.dataprivacy", "Connected vehicle services collect and transmit real-time telemetry data, including precise geographic location, operational diagnostics, trip durations, and driving performance indicators, to secure cloud servers. This information is utilized solely to enhance navigation accuracy, deliver remote diagnostic troubleshooting, facilitate emergency roadside response, and improve safety systems. You may manage data transmission preferences, request data export, or revoke cloud analytics permissions at any time through the privacy settings menu. Anonymous technical diagnostics may continue to be collected to fulfill statutory compliance, warranty administration, and mandatory automotive recall obligations."),
            ("hud.legal.appstoreterms", "Access to and use of third-party downloadable applications through the Auroraline In-Vehicle Digital Marketplace is governed by these Terms of Use and individual application developer licensing agreements. Certain applications may require active subscription services, supplementary cellular data connectivity, or paired mobile device integration to function properly. Applications must never be operated while driving if doing so causes driver distraction or creates safety hazards. Auroraline assumes no liability for external software errors, unauthorized in-app payment transactions, third-party content availability, or intermittent service disruptions caused by telecommunications network outages."),
            ("hud.legal.otaconsent", "Over-the-air software updates provide essential vehicle enhancements, operating system upgrades, security patches, and regulatory compliance adjustments. During installation, the vehicle must be safely parked in a secure location with the transmission in Park and the engine completely turned off. Select safety-critical electronic systems and drive functionality may be temporarily disabled while updates are applied. Do not attempt to operate the vehicle until the installation progress bar finishes and the infotainment display indicates successful completion. Failure to install mandatory firmware updates in a timely manner may impact warranty coverage and vehicle operations."),
            ("hud.legal.sosfeature", "The Automated Emergency Assistance SOS feature automatically initiates a hands-free voice call to emergency dispatch personnel whenever vehicle crash sensors register severe collision impact or airbag deployment. If occupants cannot respond verbally, vehicle location coordinates, travel direction, and impact severity telemetry are automatically transmitted to first responders. You may also initiate an emergency voice call manually by pressing and holding the overhead SOS button for three consecutive seconds. Emergency dispatch services depend on active mobile cellular network coverage and global positioning satellite reception in your operational territory."),
            ("hud.legal.teendriver", "The Teen Driver and Valet Monitoring configuration enables primary account holders to establish customized driving constraints, including maximum vehicle speed governors, audio volume limits, and mandatory seatbelt audio mutes. When activated, the system records comprehensive driving telemetry, including severe braking instances, forward collision alerts, high-speed travel events, and stability control interventions. A detailed driving report card is generated and accessible through the connected mobile application following each completed trip. These monitoring capabilities encourage safe, disciplined driving behaviors and reinforce responsible operational habits for newly licensed secondary operators."),
            ("hud.legal.roadsideassist", "Auroraline 24/7 Roadside Assistance provides prompt, professional emergency support for flat tires, unexpected mechanical breakdowns, high-voltage battery depletion, lockouts, and emergency towing services. When requested via the in-vehicle head-up display or connected smartphone application, your exact GPS coordinates, vehicle identification number, and current system diagnostics are automatically dispatched to the nearest authorized roadside assistance provider. Service availability, tow mileage allowances, and reimbursement coverage vary based on vehicle warranty terms and active membership tier. Emergency roadside services are subject to local traffic safety regulations, hazardous weather restrictions, and regional service provider availability."),
            ("hud.legal.telemetrydisclosure", "This vehicle continuously records diagnostic trouble codes, component temperatures, braking pressure histories, battery charge cycles, and powertrain efficiency metrics. Telemetry records are stored in non-volatile onboard electronic control modules and intermittently synchronized with engineering monitoring databases during service visits and secure wireless sessions. Collected diagnostic telemetry is utilized by automotive service technicians and development engineers to investigate unexpected component failures, design resilient hardware revisions, and refine onboard energy management algorithms. No biometric voice recordings or passenger visual imagery are ever captured or preserved as part of standard engineering telemetry datasets."),
        ]
        additional_strings = [
            await _add_string(session, project.id, key, text, created) for key, text in additional
        ]

        # 4. Seed de-DE Translations
        for string_id, target, stage, score, updated in [
            (str_speed.id, "Aktuelle Geschwindigkeit", "Approved", 95, now - timedelta(days=2)),
            (str_fuel.id, "Kraftstoff niedrig", "Reviewed", 88, now - timedelta(days=3)),
            (str_nav.id, "Links abbiegen", "Translated", 82, now - timedelta(hours=12)),
            # hud.climate.temp has no translation row seeded -> New
            (str_door.id, "Tür offen", "Approved", 92, now - timedelta(days=5)),
            (str_gear.id, "Rückwärtsgang eingelegt", "Reviewed", 89, now - timedelta(days=1)),
        ]:
            session.add(
                LocalizationTranslation(
                    string_id=string_id,
                    locale_code="de-DE",
                    target_text=target,
                    stage=stage,
                    translation_source="Manual",
                    qps_score=score,
                    needs_review=False,
                    updated_at=updated,
                )
            )

        # fr-FR and es-ES translations delivered through the marketplace. A job can only be
        # "Submitted for Review" or "Approved" once every string has target text, so these two
        # locales are fully translated: fr-FR awaiting owner review, es-ES already approved.
        seeded_strings = [str_speed, str_fuel, str_nav, str_temp, str_door, str_gear]
        seeded_strings.extend(additional_strings)
        for loc_string in seeded_strings:
            french, spanish = BY_KEY[loc_string.key]
            session.add(
                LocalizationTranslation(
                    string_id=loc_string.id,
                    locale_code="fr-FR",
                    target_text=french,
                    stage="Translated",
                    translation_source="Marketplace",
                    needs_review=False,
                    updated_at=now - timedelta(days=1),
                )
            )
            session.add(
                LocalizationTranslation(
                    string_id=loc_string.id,
                    locale_code="es-ES",
                    target_text=spanish,
                    stage="Approved",
                    translation_source="Marketplace",
                    needs_review=False,
                    updated_at=now - timedelta(days=1),
                )
            )

        # 5. Seed 3 Workflow Steps
        for order, action, last_run_at, last_run_outcome in [
            (1, "Mark Translated", now - timedelta(hours=2), "12 strings affected"),
            (2, "Send to Review", now - timedelta(days=1), "8 strings affected"),
            (3, "Approve", None, None),
        ]:
            session.add(
                WorkflowStep(
                    project_id=project.id,
                    order=order,
                    trigger="On Manual Click",
                    action=action,
                    last_run_at=last_run_at,
                    last_run_outcome=last_run_outcome,
                )
            )

        # 6. Seed 3 Build Snapshots
        snap1 = BuildSnapshot(
            project_id=project.id,
            snapshot_identifier="snap-2026-09-01-a",
            source_revision="r18234",
            localization_revision="l09981",
            config="Production-Default",
            created_at=datetime(2026, 9, 1, 14, 0, 0, tzinfo=UTC),
        )
        snap2 = BuildSnapshot(
            project_id=project.id,
            snapshot_identifier="snap-2026-08-22-c",
            source_revision="r17910",
            localization_revision="l09750",
            config="Production-Default",
            created_at=datetime(2026, 8, 22, 11, 30, 0, tzinfo=UTC),
        )
        snap3 = BuildSnapshot(
            project_id=project.id,
            snapshot_identifier="snap-2026-08-10-b",
            source_revision="r17402",
            localization_revision="l09520",
            config="Production-Default",
            created_at=datetime(2026, 8, 10, 16, 45, 0, tzinfo=UTC),
        )
        session.add_all([snap1, snap2, snap3])
        await session.flush()

        # Seed Snapshot Locale Counts
        for snap_id, counts in [
            (snap1.id, [("de-DE", 128), ("ja-JP", 94), ("zh-CN", 156), ("fr-FR", 140), ("es-ES", 94)]),
            (snap2.id, [("de-DE", 120), ("ja-JP", 90), ("zh-CN", 150), ("fr-FR", 138), ("es-ES", 90)]),
            (snap3.id, [("de-DE", 110), ("ja-JP", 85), ("zh-CN", 146), ("fr-FR", 130)]),
        ]:
            for locale_code, approved_count in counts:
                session.add(
                    BuildSnapshotLocaleCount(
                        build_snapshot_id=snap_id,
                        locale_code=locale_code,
                        approved_count=approved_count,
                    )
                )

        # 7. Seed 5 Vendors
        vendor_maria = Vendor(name="Maria Fischer", languages="de-DE,fr-FR", rating=Decimal("4.9"))
        vendor_kenji = Vendor(name="Kenji Sato", languages="ja-JP,ko-KR", rating=Decimal("5.0"))
        vendor_aiko = Vendor(name="Aiko Tanaka", languages="ja-JP", rating=Decimal("4.7"))
        vendor_marcus = Vendor(name="Marcus Webb", languages="ja-JP,zh-CN,ko-KR", rating=Decimal("4.2"))
        vendor_elena = Vendor(name="Elena Rostova", languages="de-DE,es-ES", rating=Decimal("4.8"))
        session.add_all([vendor_maria, vendor_kenji, vendor_aiko, vendor_marcus, vendor_elena])
        await session.flush()

        # 8. Seed Marketplace Jobs & Bids
        # Keep formula in sync with CreditLedgerService.EstimatePriceBandAsync
        all_strings = (
            await session.execute(
                select(LocalizationString).where(LocalizationString.project_id == project.id)
            )
        ).scalars().all()
        total_string_count = len(all_strings)
        total_word_count = sum(
            sum(1 for word in s.source_text.split(" ") if word) for s in all_strings
        )
        seed_price_low = _round_band(Decimal(total_word_count) * Decimal("0.145") / Decimal(5))
        seed_price_high = _round_band(Decimal(total_word_count) * Decimal("0.19") / Decimal(5))
        if seed_price_low < Decimal(5):
            seed_price_low = Decimal(5)
        if seed_price_high < seed_price_low + Decimal(15):
            seed_price_high = seed_price_low + Decimal(15)

        # de-DE: Awarded to Maria Fischer
        job_de = MarketplaceJob(
            project_id=project.id,
            locale_code="de-DE",
            status="Awarded",
            string_count=total_string_count,
            word_count=total_word_count,
            suggested_price_low=seed_price_low,
            suggested_price_high=seed_price_high,
            awarded_vendor_id=vendor_maria.id,
            posted_at=now - timedelta(days=5),
            awarded_at=now - timedelta(days=2),
        )
        session.add(job_de)
        await session.flush()
        session.add(
            MarketplaceBid(
                marketplace_job_id=job_de.id,
                vendor_id=vendor_maria.id,
                proposed_price=Decimal("210"),
                note="Experienced automotive HUD terminology specialist.",
                status="Awarded",
                submitted_at=now - timedelta(days=3),
            )
        )

        # ja-JP: Open with 3 bids
        job_ja = MarketplaceJob(
            project_id=project.id,
            locale_code="ja-JP",
            status="Open",
            string_count=total_string_count,
            word_count=total_word_count,
            suggested_price_low=seed_price_low,
            suggested_price_high=seed_price_high,
            posted_at=now - timedelta(days=3),
        )
        session.add(job_ja)
        await session.flush()
        for vendor_id, price, note, submitted_at in [
            (vendor_kenji.id, "345", "Native Japanese automotive localization expert.", now - timedelta(days=2)),
            (vendor_aiko.id, "298", "Automotive cluster & infotainment UI specialist.", now - timedelta(days=2) + timedelta(hours=4)),
            (vendor_marcus.id, "420", "Senior technical translator with HUD experience.", now - timedelta(days=1)),
        ]:
            session.add(
                MarketplaceBid(
                    marketplace_job_id=job_ja.id,
                    vendor_id=vendor_id,
                    proposed_price=Decimal(price),
                    note=note,
                    status="Pending",
                    submitted_at=submitted_at,
                )
            )

        # fr-FR: Submitted for Review
        job_fr = MarketplaceJob(
            project_id=project.id,
            locale_code="fr-FR",
            status="SubmittedForReview",
            string_count=total_string_count,
            word_count=total_word_count,
            suggested_price_low=seed_price_low,
            suggested_price_high=seed_price_high,
            awarded_vendor_id=vendor_maria.id,
            posted_at=now - timedelta(days=7),
            awarded_at=now - timedelta(days=4),
            submitted_at=now - timedelta(days=1),
        )
        session.add(job_fr)
        await session.flush()
        session.add(
            MarketplaceBid(
                marketplace_job_id=job_fr.id,
                vendor_id=vendor_maria.id,
                proposed_price=Decimal("215"),
                note="Automotive translation completed per DIN standards.",
                status="Awarded",
                submitted_at=now - timedelta(days=5),
            )
        )

        # es-ES: Approved
        job_es = MarketplaceJob(
            project_id=project.id,
            locale_code="es-ES",
            status="Approved",
            string_count=total_string_count,
            word_count=total_word_count,
            suggested_price_low=seed_price_low,
            suggested_price_high=seed_price_high,
            awarded_vendor_id=vendor_elena.id,
            posted_at=now - timedelta(days=10),
            awarded_at=now - timedelta(days=6),
            submitted_at=now - timedelta(days=3),
            approved_at=now - timedelta(days=1),
        )
        session.add(job_es)
        await session.flush()
        session.add(
            MarketplaceBid(
                marketplace_job_id=job_es.id,
                vendor_id=vendor_elena.id,
                proposed_price=Decimal("195"),
                note="Certified Spanish automotive translator.",
                status="Awarded",
                submitted_at=now - timedelta(days=7),
            )
        )

        # Ledger entry for approved job
        session.add(
            LedgerEntry(
                project_id=project.id,
                source="Marketplace",
                amount=Decimal("195"),
                related_marketplace_job_id=job_es.id,
                created_at=now - timedelta(days=1),
            )
        )

        # 9. Seed 2 Provider Health Rows
        session.add(
            ProviderHealthSnapshot(
                provider="GoogleMT",
                p50_latency_ms=210,
                p99_latency_ms=640,
                error_rate_percent=Decimal("0.4"),
                circuit_state="Closed",
                updated_at=now,
            )
        )
        session.add(
            ProviderHealthSnapshot(
                provider="LlmAzureGpt",
                p50_latency_ms=480,
                p99_latency_ms=1450,
                error_rate_percent=Decimal("1.1"),
                circuit_state="Closed",
                updated_at=now,
            )
        )
        await session.flush()

    await _seed_glossary_terms(session)
    await session.flush()


async def _add_string(
    session: AsyncSession, project_id: int, key: str, source_text: str, created_at: datetime
) -> LocalizationString:
    row = LocalizationString(
        project_id=project_id, key=key, source_text=source_text, created_at=created_at
    )
    session.add(row)
    await session.flush()
    return row


def _round_band(value: Decimal) -> Decimal:
    # Math.Round(x, MidpointRounding.AwayFromZero) * 5m
    return value.quantize(Decimal("1"), rounding=ROUND_HALF_UP) * 5


async def _seed_glossary_terms(session: AsyncSession) -> None:
    exists = (
        await session.execute(select(GlossaryTerm.id).limit(1))
    ).first()
    if exists is not None:
        return
    project = (
        await session.execute(
            select(LocalizationProject).where(
                LocalizationProject.slug == "auroraline-hud-v3"
            )
        )
    ).scalar_one_or_none()
    if project is None:
        return
    terms = [
        # de-DE
        ("de-DE", "HUD", "HUD", "Keep untranslated; system acronym."),
        ("de-DE", "ABS", "ABS", "Keep untranslated; safety-system acronym."),
        ("de-DE", "Turn left", "Links abbiegen", "Navigation instruction; approved HUD rendering."),
        ("de-DE", "Low fuel warning", "Kraftstoffwarnung", "Warning label; prefer the single-noun form."),
        ("de-DE", "Door ajar", "Tür offen", "Alert label; short form for the HUD."),
        # ja-JP
        ("ja-JP", "HUD", "HUD", "Keep untranslated; system acronym."),
        ("ja-JP", "ABS", "ABS", "Keep untranslated; safety-system acronym."),
        ("ja-JP", "Turn left", "左折", "Navigation instruction; approved HUD rendering."),
        ("ja-JP", "Low fuel warning", "燃料残量警告", "Warning label; approved HUD rendering."),
        ("ja-JP", "Door ajar", "ドアが開いています", "Alert label; approved HUD rendering."),
        # zh-CN
        ("zh-CN", "HUD", "HUD", "Keep untranslated; system acronym."),
        ("zh-CN", "ABS", "ABS", "Keep untranslated; safety-system acronym."),
        ("zh-CN", "Turn left", "左转", "Navigation instruction; approved HUD rendering."),
        ("zh-CN", "Low fuel warning", "燃油不足警告", "Warning label; approved HUD rendering."),
        ("zh-CN", "Door ajar", "车门未关", "Alert label; approved HUD rendering."),
        # fr-FR
        ("fr-FR", "HUD", "HUD", "Keep untranslated; system acronym."),
        ("fr-FR", "ABS", "ABS", "Keep untranslated; safety-system acronym."),
        ("fr-FR", "Turn left", "Tournez à gauche", "Navigation instruction; approved HUD rendering."),
        ("fr-FR", "Low fuel warning", "Avertissement de carburant bas", "Warning label; approved HUD rendering."),
        ("fr-FR", "Door ajar", "Porte entrouverte", "Alert label; approved HUD rendering."),
        # es-ES
        ("es-ES", "HUD", "HUD", "Keep untranslated; system acronym."),
        ("es-ES", "ABS", "ABS", "Keep untranslated; safety-system acronym."),
        ("es-ES", "Turn left", "Gire a la izquierda", "Navigation instruction; approved HUD rendering."),
        ("es-ES", "Low fuel warning", "Advertencia de combustible bajo", "Warning label; approved HUD rendering."),
        ("es-ES", "Door ajar", "Puerta entreabierta", "Alert label; approved HUD rendering."),
    ]
    for locale_code, source_term, target_term, notes in terms:
        session.add(
            GlossaryTerm(
                project_id=project.id,
                locale_code=locale_code,
                source_term=source_term,
                target_term=target_term,
                notes=notes,
            )
        )
