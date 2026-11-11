"""Audience profiles applied to every outward view, including PR records."""
from __future__ import annotations

from typing import Any

from sqlalchemy import select

from app.governance.rls import service_session
from app.models.g3 import AudienceProfile

DEFAULTS: dict[str, tuple[str, int, list[str]]] = {
    "SE_ENGINEER": ("SE,Support,Partner", 2, []),
    "SUPPORT_PARTNER": ("Support,Partner", 0, ["customer_ref", "who_to_ask"]),
    "VENDOR": ("Partner", 0, ["customer_ref", "who_to_ask", "reviewer", "diff"]),
}


async def seed_audience_profiles() -> None:
    async with service_session() as session:
        for name, (departments, max_restriction, hide) in DEFAULTS.items():
            existing = (
                await session.execute(
                    select(AudienceProfile).where(AudienceProfile.name == name)
                )
            ).scalar_one_or_none()
            if existing is None:
                session.add(
                    AudienceProfile(name=name, departments=departments,
                                    max_restriction=max_restriction,
                                    hide_fields=hide)
                )
        await session.commit()


async def hide_fields_for(audience: str) -> list[str]:
    async with service_session() as session:
        row = (
            await session.execute(
                select(AudienceProfile).where(AudienceProfile.name == audience)
            )
        ).scalar_one_or_none()
        if row is not None:
            return list(row.hide_fields)
    fallback = DEFAULTS.get(audience)
    return list(fallback[2]) if fallback else []


def apply_profile(view: dict[str, Any], hide: list[str]) -> dict[str, Any]:
    """Drop hidden keys top-level and inside one level of nested dicts/lists."""
    hidden = set(hide)
    cleaned: dict[str, Any] = {}
    for key, value in view.items():
        if key in hidden:
            continue
        if isinstance(value, dict):
            value = {k: v for k, v in value.items() if k not in hidden}
        elif isinstance(value, list):
            value = [
                {k: v for k, v in item.items() if k not in hidden}
                if isinstance(item, dict) else item
                for item in value
            ]
        cleaned[key] = value
    return cleaned
