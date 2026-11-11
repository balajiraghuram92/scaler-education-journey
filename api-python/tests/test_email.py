"""Email tests using a fake SMTP transport (no real network calls)."""

from __future__ import annotations

from datetime import UTC, datetime
from email.message import EmailMessage

import pytest

from app.models.app_user import AppUser
from app.services.email.smtp_email_notification_service import (
    SmtpEmailNotificationService,
)
from app.settings import EmailSettings, SmtpSettings


def _user() -> AppUser:
    return AppUser(
        id=1,
        email="learner@example.com",
        password_hash="h",
        password_salt="s",
        role="User",
        status="PendingApproval",
        display_name="Learner",
        created_at=datetime.now(UTC),
    )


def _configured_service() -> SmtpEmailNotificationService:
    return SmtpEmailNotificationService(
        EmailSettings(Email__SmtpHost="smtp.example.com"),
        SmtpSettings(),
    )


@pytest.mark.asyncio
async def test_send_user_pending_confirmation_uses_fake_transport(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    service = _configured_service()
    sent: list[EmailMessage] = []

    async def fake_send(message: EmailMessage) -> None:
        sent.append(message)

    monkeypatch.setattr(service, "_send", fake_send)
    await service.send_user_pending_confirmation(_user())

    assert len(sent) == 1
    assert sent[0]["To"] == "learner@example.com"
    assert "Pending Approval" in str(sent[0]["Subject"])


@pytest.mark.asyncio
async def test_unconfigured_service_sends_nothing(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    service = SmtpEmailNotificationService(EmailSettings(), SmtpSettings())
    called = False

    async def fake_send(message: EmailMessage) -> None:
        nonlocal called
        called = True

    monkeypatch.setattr(service, "_send", fake_send)
    await service.send_user_approved_notice(_user())
    await service.send_user_rejected_notice(_user(), "reason")
    await service.send_admin_new_user_alert(_user())

    assert called is False


@pytest.mark.asyncio
async def test_send_failures_are_swallowed(monkeypatch: pytest.MonkeyPatch) -> None:
    service = _configured_service()

    async def failing_send(message: EmailMessage) -> None:
        raise OSError("smtp down")

    monkeypatch.setattr(service, "_send", failing_send)
    await service.send_user_pending_confirmation(_user())
