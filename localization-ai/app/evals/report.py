"""Baseline-to-delta comparison table across stored eval runs (Part F.6).

One row per pipeline config (the latest run wins when a config ran more than
once), one column per metric. CLI: ``python -m app.evals.report --project
<slug>`` from ``localization-ai/``.
"""

import argparse
import asyncio
from dataclasses import dataclass

import psycopg


@dataclass(frozen=True)
class RunRow:
    run_id: int
    pipeline_config: str
    run_at: str
    case_count: int
    avg_comet_kiwi: float | None
    avg_qps_score: float | None
    glossary_adherence_rate: float | None
    placeholder_preservation_rate: float | None
    cache_hit_rate: float | None
    avg_latency_ms: int | None
    total_cost_usd: float | None


async def fetch_runs(conn: psycopg.AsyncConnection, project_slug: str) -> list[RunRow]:
    """Latest stored run per pipeline config, oldest config run first."""
    cur = await conn.execute(
        "SELECT r.id, r.pipeline_config, r.run_at::text, COUNT(c.id),"
        " r.avg_comet_kiwi, r.avg_qps_score, r.glossary_adherence_rate,"
        " r.placeholder_preservation_rate, r.cache_hit_rate, r.avg_latency_ms, r.total_cost_usd"
        " FROM localization_eval_runs r"
        " JOIN localization_projects p ON p.id = r.project_id"
        " LEFT JOIN localization_eval_case_results c ON c.eval_run_id = r.id"
        " WHERE p.slug = %s"
        " GROUP BY r.id ORDER BY r.run_at",
        (project_slug,),
    )
    latest: dict[str, RunRow] = {}
    for r in await cur.fetchall():
        latest[r[1]] = RunRow(
            run_id=r[0],
            pipeline_config=r[1],
            run_at=r[2],
            case_count=r[3],
            avg_comet_kiwi=_f(r[4]),
            avg_qps_score=_f(r[5]),
            glossary_adherence_rate=_f(r[6]),
            placeholder_preservation_rate=_f(r[7]),
            cache_hit_rate=_f(r[8]),
            avg_latency_ms=r[9],
            total_cost_usd=_f(r[10]),
        )
    return list(latest.values())


def _f(value: object) -> float | None:
    return None if value is None else float(str(value))


def _pct(value: float | None) -> str:
    return "n/a" if value is None else f"{value * 100:.1f}%"


def _num(value: float | None, digits: int) -> str:
    return "n/a" if value is None else f"{value:.{digits}f}"


def format_table(rows: list[RunRow]) -> str:
    """Render the comparison table. Pure function (tested without a DB)."""
    header = (
        f'{"config":<32} {"cases":>5} {"COMET":>7} {"QPS":>6}'
        f' {"gloss%":>7} {"place%":>7} {"cache%":>7} {"lat_ms":>7} {"cost_usd":>10}'
    )
    lines = [header]
    for r in rows:
        lines.append(
            f"{r.pipeline_config:<32} {r.case_count:>5} {_num(r.avg_comet_kiwi, 4):>7} {_num(r.avg_qps_score, 1):>6}"
            f" {_pct(r.glossary_adherence_rate):>7} {_pct(r.placeholder_preservation_rate):>7}"
            f" {_pct(r.cache_hit_rate):>7}"
            f" {(str(r.avg_latency_ms) if r.avg_latency_ms is not None else 'n/a'):>7}"
            f" {('$' + _num(r.total_cost_usd, 6)) if r.total_cost_usd is not None else 'n/a':>10}"
        )
    return "\n".join(lines)


async def _run(project_slug: str) -> list[RunRow]:
    from app.settings import Settings

    settings = Settings()
    async with await psycopg.AsyncConnection.connect(settings.database_conninfo()) as conn:
        return await fetch_runs(conn, project_slug)


def main(argv: list[str] | None = None) -> None:
    parser = argparse.ArgumentParser(description="Print the eval comparison table for a project.")
    parser.add_argument("--project", default="auroraline-hud-v3", help="Project slug.")
    args = parser.parse_args(argv)
    rows = asyncio.run(_run(args.project))
    if not rows:
        print(f"no eval runs stored for project {args.project!r}")
        return
    print(format_table(rows))


if __name__ == "__main__":
    main()
