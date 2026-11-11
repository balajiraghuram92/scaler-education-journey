"""Routing tests: switch/rollback (needs DB) and shadow isolation (pure)."""
from __future__ import annotations

import asyncio

import pytest
from sqlalchemy import select

from app.db import create_session_factory
from app.gateway.adapters import FakeAdapter
from app.gateway.gateway import ModelGateway
from app.gateway.routing import create_version, get_active, rollback, switch_version
from app.gateway.tasks import TaskType
from app.models.g4 import RoutingVersion
from app.settings import Settings
from tests.db_helper import ensure_test_db


def test_shadow_output_never_reaches_caller() -> None:
    adapter = FakeAdapter(
        script={"tessera-large": ['{"shadow": true}']}, default='{"ok": true}'
    )
    settings = Settings(shadow_model="tessera-large", shadow_share=1.0)
    gateway = ModelGateway(settings=settings, adapter=adapter)
    result = asyncio.run(
        gateway.complete(TaskType.TICKET_PARSE, system="s", user="u")
    )
    assert result.model == "tessera-small"
    assert result.text == '{"ok": true}'
    assert adapter.calls == [("tessera-small", "u"), ("tessera-large", "u")]
    main = [c for c in gateway.logged_calls if not c.is_shadow]
    shadow = [c for c in gateway.logged_calls if c.is_shadow]
    assert len(main) == 1 and main[0].model == "tessera-small"
    assert len(shadow) == 1 and shadow[0].model == "tessera-large"


def test_switch_and_rollback() -> None:
    url = ensure_test_db()
    if url is None:
        pytest.skip("no postgres test database reachable")

    async def _run() -> None:
        factory = create_session_factory(Settings(database_url=url))
        async with factory() as session:
            before = await get_active(session)
            assert before is not None, "migration 0005 seeds an active version"
            before_n = before.version
            number = await create_version(
                session, dict(before.routes), "correction test"
            )
            assert number == before_n + 1
            assert (await get_active(session)).version == before_n
            await switch_version(session, number, "correction test switch")
            assert (await get_active(session)).version == number
            await rollback(session, "correction test rollback")
            assert (await get_active(session)).version == before_n
            created = (
                await session.execute(
                    select(RoutingVersion).where(RoutingVersion.version == number)
                )
            ).scalar_one()
            await session.delete(created)
            await session.commit()

    asyncio.run(_run())
