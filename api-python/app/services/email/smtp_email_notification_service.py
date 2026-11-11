"""Ported from api/Services/Email/SmtpEmailNotificationService.cs."""

from __future__ import annotations

import html
import logging
from email.message import EmailMessage
from typing import TYPE_CHECKING

import aiosmtplib

from ...settings import EmailSettings, SmtpSettings

if TYPE_CHECKING:
    from ...models.app_user import AppUser

logger = logging.getLogger(__name__)


def _pick(first: str, second: str) -> str:
    """First non-blank value (C# IsNullOrWhiteSpace semantics), else ""."""
    if first and first.strip():
        return first
    if second and second.strip():
        return second
    return ""


class SmtpEmailNotificationService:
    def __init__(self, email: EmailSettings, smtp: SmtpSettings | None) -> None:
        smtp_host = smtp.host if smtp else ""
        smtp_username = smtp.username if smtp else ""
        smtp_password = smtp.password if smtp else ""
        smtp_from_email = smtp.from_email if smtp else ""
        smtp_from_name = smtp.from_name if smtp else ""
        self._host = _pick(email.smtp_host, smtp_host)
        self._port = email.smtp_port if email.smtp_port > 0 else (smtp.port if smtp else 587)
        self._username = _pick(email.smtp_username, smtp_username)
        self._password = _pick(email.smtp_password, smtp_password)
        self._enable_ssl = email.use_ssl
        self._from_email = (
            _pick(email.from_address, smtp_from_email) or "noreply@neuralascent.top"
        )
        self._from_name = (
            _pick(email.from_display_name, smtp_from_name) or "Neuralascent"
        )
        self._frontend_url = (
            smtp.frontend_url if smtp is not None else "https://neuralascent.top"
        )
        self._admin_notification_email = smtp.admin_notification_email if smtp else ""
        self._is_configured = bool(self._host.strip() and self._from_email.strip())

    async def send_admin_new_user_alert(self, new_user: AppUser) -> None:
        recipient = (
            self._admin_notification_email
            if self._admin_notification_email.strip()
            else self._from_email
        )
        subject = f"[Neuralascent] New User Registration Pending Approval: {new_user.email}"
        registered = new_user.created_at.strftime("%Y-%m-%d %H:%M:%S")
        body = f"""
            <h2>New User Registration Pending Approval</h2>
            <p>A new user has registered on Neuralascent and is awaiting your review:</p>
            <ul>
                <li><strong>Email:</strong> {html.escape(new_user.email)}</li>
                <li><strong>Name:</strong> {html.escape(new_user.display_name or "Not provided")}</li>
                <li><strong>Registered At:</strong> {registered} UTC</li>
            </ul>
            <p>Please log in to the <a href="{self._frontend_url}/admin/users">Admin Dashboard</a> to approve or reject this request.</p>"""
        await self._send_email_safe(recipient, subject, body)

    async def send_user_pending_confirmation(self, new_user: AppUser) -> None:
        subject = "[Neuralascent] Registration Received - Pending Approval"
        body = f"""
            <h2>Welcome to Neuralascent</h2>
            <p>Hello {html.escape(new_user.display_name or new_user.email)},</p>
            <p>Thank you for registering on Neuralascent. Your account request has been received and is currently under administrative review.</p>
            <p>You will receive another email notification as soon as an administrator reviews and approves your account.</p>
            <p>Warm regards,<br/>The Neuralascent Team</p>"""
        await self._send_email_safe(new_user.email, subject, body)

    async def send_user_approved_notice(self, user: AppUser) -> None:
        login_url = f"{self._frontend_url}/login"
        subject = "[Neuralascent] Your Account Has Been Approved!"
        body = f"""
            <h2>Welcome to Neuralascent — Access Approved</h2>
            <p>Hello {html.escape(user.display_name or user.email)},</p>
            <p>Great news! Your Neuralascent account registration has been approved by an administrator.</p>
            <p>You may now sign in to explore the curriculum, interactive reading rooms, and knowledge atlas:</p>
            <p><a href="{login_url}" style="display:inline-block;padding:10px 20px;background-color:#2C5E55;color:#ffffff;text-decoration:none;border-radius:6px;font-weight:600;">Sign In to Neuralascent</a></p>
            <p>Or visit: <a href="{login_url}">{login_url}</a></p>
            <p style="margin-top:20px;padding:12px;background:#f4efe6;border-left:4px solid #2C5E55;font-size:0.9em;color:#4A4843;">
                <strong>Sustainability note:</strong> Neuralascent runs on a single small host with a shared daily AI compute budget ($2.00/day hard cap). Please use the lesson assistant thoughtfully so everyone has access.
            </p>
            <p>Warm regards,<br/>The Neuralascent Team</p>"""
        await self._send_email_safe(user.email, subject, body)

    async def send_user_rejected_notice(self, user: AppUser, reason: str | None) -> None:
        subject = "[Neuralascent] Registration Status Update"
        reason_html = (
            f"<p><strong>Reason provided:</strong> {html.escape(reason)}</p>"
            if reason and reason.strip()
            else ""
        )
        body = f"""
            <h2>Registration Status Update</h2>
            <p>Hello {html.escape(user.display_name or user.email)},</p>
            <p>Thank you for your interest in Neuralascent. After review, your registration request could not be approved at this time.</p>
            {reason_html}
            <p>If you believe this decision was made in error, please contact support.</p>
            <p>Warm regards,<br/>The Neuralascent Team</p>"""
        await self._send_email_safe(user.email, subject, body)

    async def _send_email_safe(self, to_email: str, subject: str, html_body: str) -> None:
        if not to_email or not to_email.strip():
            logger.warning("Skipping email dispatch: recipient address is empty. Subject: %s", subject)
            return
        if not self._is_configured:
            logger.info(
                "[Dev Email Mock] SMTP not configured. Would send to '%s': Subject: '%s'",
                to_email,
                subject,
            )
            return
        try:
            message = EmailMessage()
            message["From"] = f"{self._from_name} <{self._from_email}>"
            message["To"] = to_email
            message["Subject"] = subject
            message.set_content(html_body, subtype="html")
            await self._send(message)
            logger.info(
                "Successfully sent email '%s' to '%s' via %s:%s",
                subject,
                to_email,
                self._host,
                self._port,
            )
        except Exception as exc:  # noqa: BLE001 - C# logs and swallows send failures
            logger.error(
                "Failed to send email '%s' to '%s' via SMTP host %s:%s: %s",
                subject,
                to_email,
                self._host,
                self._port,
                exc,
            )

    async def _send(self, message: EmailMessage) -> None:
        await aiosmtplib.send(
            message,
            hostname=self._host,
            port=self._port,
            username=self._username or None,
            password=self._password or None,
            use_tls=self._enable_ssl,
        )
