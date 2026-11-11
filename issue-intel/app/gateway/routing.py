"""Versioned model routing: exactly one active version; audited switching.

CLI (from issue-intel/): `python -m app.gateway.routing list|show|create|switch|rollback`.
"""
from __future__ import annotations

import argparse
import asyncio
import datetime
import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.g4 import RoutingVersion


@dataclass
class Route:
    primary: str
    fallback: str
    token_limit: int
    mode: str  # SYNC | BATCH
    canary_module: str | None = None
    canary_model: str | None = None
    canary_share: float = 0.0


def route_from_dict(task: str, payload: dict[str, Any]) -> Route:
    entry = payload.get(task, {})
    return Route(
        primary=str(entry.get("primary", "tessera-small")),
        fallback=str(entry.get("fallback", "tessera-large")),
        token_limit=int(entry.get("token_limit", 8000)),
        mode=str(entry.get("mode", "SYNC")),
        canary_module=entry.get("canary_module"),
        canary_model=entry.get("canary_model"),
        canary_share=float(entry.get("canary_share", 0.0)),
    )


async def get_active(session: AsyncSession) -> RoutingVersion | None:
    row: RoutingVersion | None = (
        await session.execute(
            select(RoutingVersion).where(RoutingVersion.active.is_(True))
        )
    ).scalar_one_or_none()
    return row


async def create_version(
    session: AsyncSession, routes: dict[str, Any], note: str
) -> int:
    latest = (
        await session.execute(
            select(RoutingVersion).order_by(RoutingVersion.version.desc()).limit(1)
        )
    ).scalar_one_or_none()
    number = (latest.version + 1) if latest else 1
    session.add(RoutingVersion(version=number, routes=routes, active=False,
                               note=note))
    await session.commit()
    return number


async def switch_version(session: AsyncSession, version: int, note: str) -> int:
    """One audited operation: exactly one version stays active."""
    target: RoutingVersion | None = (
        await session.execute(
            select(RoutingVersion).where(RoutingVersion.version == version)
        )
    ).scalar_one_or_none()
    if target is None:
        raise ValueError(f"unknown routing version {version}")
    current = await get_active(session)
    for row in (
        await session.execute(select(RoutingVersion).where(RoutingVersion.active.is_(True)))
    ).scalars().all():
        row.active = False
    target.active = True
    target.activated_at = datetime.datetime.now(datetime.UTC)
    from_version = current.version if current else None
    target.activated_note = f"switch {from_version} -> {version}: {note}"
    await session.commit()
    return target.version


async def rollback(session: AsyncSession, note: str = "rollback") -> int:
    current = await get_active(session)
    if current is None:
        raise ValueError("no active routing version")
    previous = (
        await session.execute(
            select(RoutingVersion)
            .where(RoutingVersion.version < current.version)
            .order_by(RoutingVersion.version.desc()).limit(1)
        )
    ).scalar_one_or_none()
    if previous is None:
        raise ValueError("no previous version to roll back to")
    return await switch_version(session, previous.version, note)


async def _list_versions() -> list[dict[str, Any]]:
    from app.governance.rls import service_session

    async with service_session() as session:
        rows = (
            await session.execute(
                select(RoutingVersion).order_by(RoutingVersion.version)
            )
        ).scalars().all()
        return [
            {"version": r.version, "active": r.active, "note": r.note,
             "activated_note": r.activated_note}
            for r in rows
        ]


async def _show_version(version: int) -> dict[str, Any]:
    from app.governance.rls import service_session

    async with service_session() as session:
        row = (
            await session.execute(
                select(RoutingVersion).where(RoutingVersion.version == version)
            )
        ).scalar_one_or_none()
        if row is None:
            raise ValueError(f"unknown routing version {version}")
        return dict(row.routes)


async def _create_cli(routes_file: Path, note: str) -> int:
    from app.governance.rls import service_session

    routes = json.loads(routes_file.read_text(encoding="utf-8"))
    if not isinstance(routes, dict):
        raise ValueError("routes file must hold a JSON object")
    async with service_session() as session:
        return await create_version(session, routes, note)


async def _switch_cli(version: int, note: str) -> int:
    from app.governance.rls import service_session

    async with service_session() as session:
        return await switch_version(session, version, note)


async def _rollback_cli(note: str) -> int:
    from app.governance.rls import service_session

    async with service_session() as session:
        return await rollback(session, note)


def main() -> None:
    parser = argparse.ArgumentParser(description="Routing version operations.")
    sub = parser.add_subparsers(dest="command", required=True)
    sub.add_parser("list", help="list versions and the active one")
    show = sub.add_parser("show", help="print one version's routes as JSON")
    show.add_argument("--version", type=int, required=True)
    create = sub.add_parser("create", help="store a new inactive version")
    create.add_argument("--routes", type=Path, required=True)
    create.add_argument("--note", default="")
    switch = sub.add_parser("switch", help="activate one version (audited)")
    switch.add_argument("--version", type=int, required=True)
    switch.add_argument("--note", default="")
    back = sub.add_parser("rollback", help="reactivate the previous version")
    back.add_argument("--note", default="rollback")
    args = parser.parse_args()
    if args.command == "list":
        for row in asyncio.run(_list_versions()):
            flag = "active" if row["active"] else "      "
            print(f"{flag} v{row['version']}: {row['note']} [{row['activated_note']}]")
    elif args.command == "show":
        print(json.dumps(asyncio.run(_show_version(args.version)), indent=2,
                         sort_keys=True))
    elif args.command == "create":
        number = asyncio.run(_create_cli(args.routes, args.note))
        print(f"created routing version {number} (inactive)")
    elif args.command == "switch":
        number = asyncio.run(_switch_cli(args.version, args.note))
        print(f"active routing version is now {number}")
    elif args.command == "rollback":
        number = asyncio.run(_rollback_cli(args.note))
        print(f"rolled back to routing version {number}")


if __name__ == "__main__":
    main()
