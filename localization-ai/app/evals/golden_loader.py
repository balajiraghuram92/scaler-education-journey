"""Golden-set loader: ``evals/golden/*.jsonl`` -> localization_eval_golden_cases.

The upsert is implemented in code (SELECT then INSERT/UPDATE) so it needs no
unique constraint on the table. This module never commits: the CLI and the
tests commit after a successful load.

The per-case ``verified`` flag currently lives only in the JSONL: the
golden-case table has no verified column (LA1 schema gap), so the loader
reports verified/unverified counts but cannot persist the flag. The JSONL
files are the source of truth the owner checks by hand.
"""

import argparse
import asyncio
import glob
import json
from dataclasses import dataclass
from pathlib import Path
from typing import Literal

import psycopg
from pydantic import BaseModel, Field

from app.db import fetch_project

Category = Literal["short-label", "warning-message", "idiomatic", "legal-disclaimer"]
CATEGORIES: tuple[str, ...] = ("short-label", "warning-message", "idiomatic", "legal-disclaimer")

GOLDEN_DIR = Path(__file__).resolve().parent.parent.parent / "evals" / "golden"


class GoldenFileCase(BaseModel):
    locale_code: str = Field(min_length=1)
    category: Category
    source_text: str = Field(min_length=1)
    gold_translation: str = Field(min_length=1)
    notes: str = ""
    verified: bool = False


@dataclass
class LoadResult:
    files: int = 0
    cases: int = 0
    inserted: int = 0
    updated: int = 0
    verified: int = 0
    unverified: int = 0


def iter_golden_files(directory: Path | str = GOLDEN_DIR) -> list[Path]:
    return sorted(Path(p) for p in glob.glob(str(Path(directory) / "*.jsonl")))


def read_golden_file(path: Path) -> list[GoldenFileCase]:
    """Parse one JSONL file; raises ValueError naming file and line on any problem."""
    cases = []
    with open(path, encoding="utf-8") as fh:
        for lineno, line in enumerate(fh, start=1):
            if not line.strip():
                continue
            try:
                raw = json.loads(line)
                cases.append(GoldenFileCase.model_validate(raw))
            except (json.JSONDecodeError, ValueError) as exc:
                raise ValueError(f"{path.name}:{lineno}: {exc}") from exc
    return cases


async def upsert_case(conn: psycopg.AsyncConnection, project_id: int, case: GoldenFileCase) -> bool:
    """Insert or update one case. Returns True when a row was inserted."""
    cur = await conn.execute(
        "SELECT id FROM localization_eval_golden_cases WHERE project_id = %s AND locale_code = %s AND source_text = %s",
        (project_id, case.locale_code, case.source_text),
    )
    row = await cur.fetchone()
    if row is None:
        await conn.execute(
            "INSERT INTO localization_eval_golden_cases"
            " (project_id, locale_code, source_text, gold_translation, category, notes)"
            " VALUES (%s, %s, %s, %s, %s, %s)",
            (project_id, case.locale_code, case.source_text, case.gold_translation, case.category, case.notes),
        )
        return True
    await conn.execute(
        "UPDATE localization_eval_golden_cases SET gold_translation = %s, category = %s, notes = %s WHERE id = %s",
        (case.gold_translation, case.category, case.notes, row[0]),
    )
    return False


async def load_directory(
    conn: psycopg.AsyncConnection, project_id: int, directory: Path | str = GOLDEN_DIR
) -> LoadResult:
    result = LoadResult()
    for path in iter_golden_files(directory):
        result.files += 1
        for case in read_golden_file(path):
            result.cases += 1
            if case.verified:
                result.verified += 1
            else:
                result.unverified += 1
            if await upsert_case(conn, project_id, case):
                result.inserted += 1
            else:
                result.updated += 1
    return result


async def _run(project_slug: str, directory: Path) -> LoadResult:
    from app.settings import Settings

    settings = Settings()
    async with await psycopg.AsyncConnection.connect(settings.database_conninfo()) as conn:
        project = await fetch_project(conn, project_slug)
        if project is None:
            raise SystemExit(f"unknown project slug {project_slug!r}")
        result = await load_directory(conn, project.id, directory)
        await conn.commit()
        return result


def main(argv: list[str] | None = None) -> None:
    parser = argparse.ArgumentParser(description="Upsert evals/golden/*.jsonl into the golden-case table.")
    parser.add_argument("--project", default="auroraline-hud-v3", help="Project slug (default: auroraline-hud-v3).")
    parser.add_argument("--dir", default=str(GOLDEN_DIR), help="Directory of *.jsonl files.")
    args = parser.parse_args(argv)
    result = asyncio.run(_run(args.project, Path(args.dir)))
    print(
        f"loaded {result.cases} cases from {result.files} files "
        f"({result.inserted} inserted, {result.updated} updated; "
        f"{result.verified} verified, {result.unverified} unverified)"
    )


if __name__ == "__main__":
    main()
