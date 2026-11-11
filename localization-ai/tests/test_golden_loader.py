import asyncio
from pathlib import Path

import psycopg
import pytest
from pydantic import ValidationError

from app.evals import golden_loader
from app.evals.golden_loader import GoldenFileCase


def test_golden_file_case_validation():
    ok = GoldenFileCase.model_validate(
        {
            "locale_code": "de-DE",
            "category": "short-label",
            "source_text": "Hi",
            "gold_translation": "Hallo",
            "verified": False,
        }
    )
    assert ok.notes == ""
    with pytest.raises(ValidationError):
        GoldenFileCase.model_validate(
            {
                "locale_code": "de-DE",
                "category": "not-a-category",
                "source_text": "Hi",
                "gold_translation": "Hallo",
            }
        )
    with pytest.raises(ValidationError):
        GoldenFileCase.model_validate(
            {"locale_code": "de-DE", "category": "short-label", "source_text": "", "gold_translation": "Hallo"}
        )


def test_read_golden_file_names_file_and_line(tmp_path):
    bad = tmp_path / "xx.jsonl"
    good_line = '{"locale_code": "de-DE", "category": "short-label", "source_text": "A", "gold_translation": "B"}\n'
    bad.write_text(good_line + "not json\n", encoding="utf-8")
    with pytest.raises(ValueError, match=r"xx\.jsonl:2"):
        golden_loader.read_golden_file(bad)


def test_shipped_golden_set_shape():
    """The shipped set: 40 cases, 5 locales x 4 categories, >=8 placeholders, >=10 glossary uses."""
    files = golden_loader.iter_golden_files()
    assert len(files) == 5
    cases = [c for f in files for c in golden_loader.read_golden_file(f)]
    assert len(cases) == 40
    assert {c.locale_code for c in cases} == {"de-DE", "ja-JP", "zh-CN", "fr-FR", "es-ES"}
    assert {c.category for c in cases} == set(golden_loader.CATEGORIES)
    assert all(c.verified is False for c in cases)
    with_placeholders = [c for c in cases if "{" in c.source_text and "}" in c.source_text]
    assert len(with_placeholders) >= 8
    glossary_sources = ("HUD", "ABS", "Turn left", "Low fuel", "Door ajar")
    using_glossary = [c for c in cases if any(g in c.source_text for g in glossary_sources)]
    assert len(using_glossary) >= 10


def _project_id(conninfo: str) -> int:
    with psycopg.connect(conninfo) as conn:
        cur = conn.execute("INSERT INTO localization_projects (slug, name) VALUES ('p', 'P') RETURNING id")
        row = cur.fetchone()
        assert row is not None
        conn.commit()
        return row[0]


async def _load(conninfo: str, project_id: int, directory: Path):
    conn = await psycopg.AsyncConnection.connect(conninfo)
    try:
        result = await golden_loader.load_directory(conn, project_id, directory)
        await conn.commit()
        return result
    finally:
        await conn.close()


def test_loader_inserts_then_updates(fresh_db, tmp_path):
    project_id = _project_id(fresh_db)
    one = tmp_path / "de-DE.jsonl"
    one.write_text(
        '{"locale_code": "de-DE", "category": "short-label", "source_text": "Hi",'
        ' "gold_translation": "Hallo", "verified": false}\n',
        encoding="utf-8",
    )
    first = asyncio.run(_load(fresh_db, project_id, tmp_path))
    assert (first.files, first.cases, first.inserted, first.updated) == (1, 1, 1, 0)
    assert (first.verified, first.unverified) == (0, 1)

    one.write_text(
        '{"locale_code": "de-DE", "category": "warning-message", "source_text": "Hi",'
        ' "gold_translation": "Hallo!", "notes": "edited", "verified": true}\n',
        encoding="utf-8",
    )
    second = asyncio.run(_load(fresh_db, project_id, tmp_path))
    assert (second.inserted, second.updated) == (0, 1)
    assert (second.verified, second.unverified) == (1, 0)

    with psycopg.connect(fresh_db) as conn:
        rows = conn.execute("SELECT gold_translation, category, notes FROM localization_eval_golden_cases").fetchall()
    assert rows == [("Hallo!", "warning-message", "edited")]
