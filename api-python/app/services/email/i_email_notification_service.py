"""Ported from api/Services/Email/IEmailNotificationService.cs."""

from __future__ import annotations

from typing import TYPE_CHECKING, Protocol

if TYPE_CHECKING:
    from ...models.app_user import AppUser


class IEmailNotificationService(Protocol):
    async def send_admin_new_user_alert(self, new_user: AppUser) -> None: ...
    async def send_user_pending_confirmation(self, new_user: AppUser) -> None: ...
    async def send_user_approved_notice(self, user: AppUser) -> None: ...
    async def send_user_rejected_notice(
        self, user: AppUser, reason: str | None
    ) -> None: ...
