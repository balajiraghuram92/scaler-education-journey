"""Ingestion runner: extract -> normalise -> crosswalk -> outcomes -> embed.

Entry: `python -m app.ingest.run` (from issue-intel/). Idempotent: a second run
inserts nothing.
"""
from __future__ import annotations

import argparse
import asyncio
from pathlib import Path

from sqlalchemy.ext.asyncio import AsyncSession

from app.gateway.gateway import ModelGateway
from app.governance.rls import service_session
from app.ingest import chunk_embed, crosswalk, normalise, outcomes, ownership
from app.ingest.extract import read_chat_xml, read_legacy_csv, read_tracker_json

ROOT = Path(__file__).resolve().parent.parent.parent


async def run_ingest(
    session: AsyncSession, gateway: ModelGateway, corpus_dir: Path,
    run_id: str | None = None,
) -> dict[str, int]:
    legacy = read_legacy_csv(corpus_dir / "legacy_cases.csv")
    export = read_tracker_json(corpus_dir / "tracker_export.json")
    threads = read_chat_xml(corpus_dir / "chat_export.xml")

    counts = {"cases": 0, "threads": 0, "changes": 0, "people": 0}
    for raw_case in legacy + export.cases:
        await normalise.upsert_case(session, raw_case)
        counts["cases"] += 1
    for raw_person in export.people:
        await normalise.upsert_person(session, raw_person)
        counts["people"] += 1
    se_acl = await normalise.get_or_create_acl(
        session, "VersionControl,Localization,UiState,AssetImport", "SE", "SE"
    )
    for raw_change in export.changes:
        await normalise.upsert_change(session, raw_change, se_acl.id)
        counts["changes"] += 1
    for raw_thread in threads:
        await normalise.upsert_thread(session, raw_thread, se_acl.id)
        counts["threads"] += 1
    await session.commit()

    counts["links"] = await crosswalk.crosswalk(session)
    await session.commit()
    counts["outcomes"] = await outcomes.classify_legacy_outcomes(session, gateway, run_id)
    await session.commit()
    counts["chunks"] = await chunk_embed.chunk_and_embed(session, gateway, run_id)
    await session.commit()
    await ownership.build_ownership(session, export.ownership)
    await session.commit()
    return counts


async def _main(args: argparse.Namespace) -> None:
    gateway = ModelGateway()
    async with service_session() as session:
        counts = await run_ingest(session, gateway, Path(args.corpus))
    print(counts)


def main() -> None:
    parser = argparse.ArgumentParser(description="Ingest the Tessera corpus.")
    parser.add_argument("--corpus", default=str(ROOT / "synthetic" / "corpus"))
    _args = parser.parse_args()
    asyncio.run(_main(_args))


if __name__ == "__main__":
    main()
