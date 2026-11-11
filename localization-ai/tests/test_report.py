import psycopg

from app.evals.report import RunRow, fetch_runs, format_table


def _row(config: str, **overrides) -> RunRow:
    values = dict(
        run_id=1,
        pipeline_config=config,
        run_at="2026-01-01",
        case_count=40,
        avg_comet_kiwi=0.6123,
        avg_qps_score=58.5,
        glossary_adherence_rate=0.5,
        placeholder_preservation_rate=None,
        cache_hit_rate=0.0,
        avg_latency_ms=120,
        total_cost_usd=0.001234,
    )
    values.update(overrides)
    return RunRow(**values)


def test_format_table_renders_rows_and_n_a():
    table = format_table([_row("legacy-only"), _row("legacy+optimize", avg_qps_score=89.0)])
    lines = table.splitlines()
    assert len(lines) == 3
    assert lines[0].startswith("config")
    assert "legacy-only" in lines[1] and "58.5" in lines[1]
    assert "0.6123" in lines[1] and "50.0%" in lines[1] and "n/a" in lines[1]
    assert "legacy+optimize" in lines[2] and "89.0" in lines[2]


def test_fetch_runs_keeps_latest_per_config(fresh_db):
    with psycopg.connect(fresh_db) as conn:
        cur = conn.execute("INSERT INTO localization_projects (slug, name) VALUES ('r', 'R') RETURNING id")
        row = cur.fetchone()
        assert row is not None
        pid = row[0]
        conn.execute(
            "INSERT INTO localization_eval_runs (project_id, pipeline_config, avg_qps_score)"
            " VALUES (%s, 'legacy-only', 10), (%s, 'legacy+optimize', 50), (%s, 'legacy-only', 20)",
            (pid, pid, pid),
        )
        conn.commit()

    import asyncio

    async def go():
        conn = await psycopg.AsyncConnection.connect(fresh_db)
        try:
            return await fetch_runs(conn, "r")
        finally:
            await conn.close()

    rows = asyncio.run(go())
    assert [(r.pipeline_config, r.avg_qps_score, r.case_count) for r in rows] == [
        ("legacy-only", 20.0, 0),  # latest of the two legacy-only runs
        ("legacy+optimize", 50.0, 0),
    ]


def test_fetch_runs_unknown_project_is_empty(fresh_db):
    import asyncio

    async def go():
        conn = await psycopg.AsyncConnection.connect(fresh_db)
        try:
            return await fetch_runs(conn, "nope")
        finally:
            await conn.close()

    assert asyncio.run(go()) == []
