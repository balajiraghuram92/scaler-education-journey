"""G4 scorecards: per-task quality, cost and latency for a named model.

Entry (from issue-intel/):
  python -m evals.run_g4 score --model <name> [--adapter fake|openai] [--limit N]
  python -m evals.run_g4 report --incumbent <name> --candidate <name>

`score` runs every task suite against the named model and stores one
model_scorecards row per task type: quality (pass share), cost per resolved
case and p95 latency. outcome_classify is real accuracy against the
ground-truth outcome labels; the other chat tasks are contract conformance
(the reply parses as JSON holding the task's required keys); embed is
dimension conformance. With --adapter fake the numbers are machinery-only.
`report` prints incumbent against candidate from the stored scorecards.
"""
from __future__ import annotations

import argparse
import asyncio
import json
from pathlib import Path

from sqlalchemy import select

from app.agents.final_check import FINAL_SYSTEM, QUALITY_SYSTEM
from app.db import create_session_factory
from app.gateway.adapters import FakeAdapter
from app.gateway.gateway import ModelGateway
from app.gateway.tasks import TaskType
from app.governance.rls import service_session
from app.ingest.extract import RawCase, read_legacy_csv
from app.ingest.outcomes import SYSTEM as OUTCOME_SYSTEM
from app.ingest.outcomes import parse_outcome
from app.models.g4 import ModelScorecard
from app.pipeline.stages import S1_SYSTEM, S2_SYSTEM, S5_SYSTEM, S7_SYSTEM
from app.settings import Settings, get_settings
from evals.metrics import p95

ROOT = Path(__file__).resolve().parent.parent

FIX_PLAN_SYSTEM = (
    "Plan the fix. Reply with JSON only: "
    '{"steps": [...], "files": [...]}.'
)
FIX_PATCH_SYSTEM = (
    "Write the patch. Reply with JSON only: "
    '{"patch": "...", "files": [...]}.'
)
CONFLICT_SYSTEM = (
    "Resolve the conflict. Reply with JSON only: "
    '{"resolved": "..."}.'
)

# Task -> (system prompt, required reply keys). outcome_classify and embed
# are scored separately (real accuracy, dimension conformance).
CONTRACTS: dict[TaskType, tuple[str, frozenset[str]]] = {
    TaskType.TICKET_PARSE: (S1_SYSTEM, frozenset({"module", "version", "error_strings"})),
    TaskType.MODULE_CHECK: (S2_SYSTEM, frozenset({"predicted_module", "confidence"})),
    TaskType.RELEVANCE: (S5_SYSTEM, frozenset({"relevant", "score"})),
    TaskType.SYNTHESIS: (S7_SYSTEM, frozenset({"claims", "confidence"})),
    TaskType.FIX_PLAN: (FIX_PLAN_SYSTEM, frozenset({"steps", "files"})),
    TaskType.FIX_PATCH: (FIX_PATCH_SYSTEM, frozenset({"patch"})),
    TaskType.CONFLICT_RESOLVE: (CONFLICT_SYSTEM, frozenset({"resolved"})),
    TaskType.QUALITY_VERIFY: (QUALITY_SYSTEM, frozenset({"pass"})),
    TaskType.FINAL_CHECK: (FINAL_SYSTEM, frozenset({"verdict"})),
}

# Canned contract-satisfying replies for machinery runs (FakeAdapter matches
# them by system-prompt prefix, as in evals.run_g2.MACHINERY_DEFAULTS).
MACHINERY_CONTRACTS = {
    "Parse the ticket.": (
        '{"module": "UiState", "version": "2024.1", "error_strings": [], '
        '"stack_frames": [], "legacy_ids": []}'
    ),
    "Decide whether": '{"predicted_module": "UiState", "confidence": 0.9}',
    "Judge whether the change": '{"relevant": true, "score": 0.8}',
    "Write the investigation": (
        '{"seen_before": false, "outcomes": [], "likely_cause": "", '
        '"fix_or_workaround": "", "who_to_ask": "", "confidence": 0.5, '
        '"claims": []}'
    ),
    "Plan the fix.": '{"steps": ["edit"], "files": ["src/UiState/X.cs"]}',
    "Write the patch.": '{"patch": "@@ -1 +1 @@", "files": ["src/UiState/X.cs"]}',
    "Resolve the conflict.": '{"resolved": "kept both"}',
    "Screen the fix package cheaply.": '{"pass": true, "reason": "machinery"}',
    "Review the fix package.": '{"verdict": "OK", "reason": "machinery"}',
}


def _gateway(model: str, adapter: str) -> ModelGateway:
    """Fresh gateway per task so logged calls isolate cost and latency."""
    if adapter == "fake":
        settings = Settings(model_adapter="fake", shadow_model=None, shadow_share=0.0)
        fake = FakeAdapter(
            defaults=dict(MACHINERY_CONTRACTS), default='{"outcome": "FIXED"}'
        )
        return ModelGateway(settings=settings, adapter=fake, model_override=model)
    settings = Settings(model_adapter="openai", shadow_model=None, shadow_share=0.0)
    return ModelGateway(settings=settings, model_override=model)


def _cases(limit: int) -> list[RawCase]:
    return read_legacy_csv(ROOT / "synthetic" / "corpus" / "legacy_cases.csv")[:limit]


def _labels() -> dict[str, str]:
    payload = json.loads(
        (ROOT / "evals" / "ground_truth" / "outcome_labels.json").read_text()
    )
    assert isinstance(payload, dict)
    return {str(k): str(v) for k, v in payload.items()}


def _users(task: TaskType, cases: list[RawCase]) -> list[str]:
    if task in (TaskType.TICKET_PARSE, TaskType.MODULE_CHECK, TaskType.SYNTHESIS):
        return [f"Ticket {c.key}: {c.title}\n{c.body}" for c in cases]
    if task == TaskType.RELEVANCE:
        return [f"Issue: {c.title}\nChange: SAMPLE-01" for c in cases]
    if task in (TaskType.FIX_PLAN, TaskType.FIX_PATCH):
        return [f"Fix {c.key}: {c.title}\n{c.body[:500]}" for c in cases]
    if task == TaskType.CONFLICT_RESOLVE:
        return ["<<<<<<< main\nreturn a;\n=======\nreturn b;\n>>>>>>> fix"] * len(cases)
    return [f"Package for {c.key}: {c.title}" for c in cases]


def _stats(gateway: ModelGateway, passed: int, n: int) -> dict[str, float]:
    cost = sum(c.cost_usd for c in gateway.logged_calls)
    lat = [float(c.latency_ms) for c in gateway.logged_calls]
    return {
        "quality": passed / n if n else 0.0,
        "cost_per_resolved": cost / max(1, passed),
        "p95_latency_ms": p95(lat),
        "n": float(n),
    }


async def _score_contract(
    model: str, adapter: str, task: TaskType, cases: list[RawCase]
) -> dict[str, float]:
    system, keys = CONTRACTS[task]
    gateway = _gateway(model, adapter)
    passed = 0
    users = _users(task, cases)
    for user in users:
        try:
            result = await gateway.complete(task, system=system, user=user)
            payload = json.loads(result.text)
            ok = isinstance(payload, dict) and keys <= set(payload)
        except Exception:
            ok = False
        passed += ok
    return _stats(gateway, passed, len(users))


async def _score_outcomes(
    model: str, adapter: str, cases: list[RawCase], labels: dict[str, str]
) -> dict[str, float]:
    gateway = _gateway(model, adapter)
    passed = n = 0
    for case in cases:
        expected = labels.get(case.key)
        if expected is None:
            continue
        n += 1
        try:
            result = await gateway.complete(
                TaskType.OUTCOME_CLASSIFY, system=OUTCOME_SYSTEM,
                user=f"Title: {case.title}", data={"resolution": case.resolution},
            )
            ok = parse_outcome(result.text) == expected
        except Exception:
            ok = False
        passed += ok
    return _stats(gateway, passed, n)


async def _score_embed(
    model: str, adapter: str, cases: list[RawCase]
) -> dict[str, float]:
    gateway = _gateway(model, adapter)
    texts = [f"{c.title}\n{c.body}" for c in cases]
    dim = get_settings().embedding_dim
    try:
        vectors = await gateway.embed(texts)
        passed = sum(1 for v in vectors if len(v) == dim)
    except Exception:
        passed = 0
    return _stats(gateway, passed, len(texts))


async def cmd_score(model: str, adapter: str, limit: int) -> None:
    cases = _cases(limit)
    labels = _labels()
    factory = create_session_factory()
    report: dict[str, dict[str, float]] = {}
    for task in TaskType:
        if task == TaskType.OUTCOME_CLASSIFY:
            row = await _score_outcomes(model, adapter, cases, labels)
        elif task == TaskType.EMBED:
            row = await _score_embed(model, adapter, cases)
        else:
            row = await _score_contract(model, adapter, task, cases)
        report[task.value] = row
        async with factory() as session:
            session.add(
                ModelScorecard(
                    model=model, task_type=task.value, quality=row["quality"],
                    cost_per_resolved=row["cost_per_resolved"],
                    p95_latency_ms=row["p95_latency_ms"], n=int(row["n"]),
                )
            )
            await session.commit()
    out = ROOT / "evals" / "reports" / f"g4-score-{model}.json"
    out.parent.mkdir(parents=True, exist_ok=True)
    payload = {"model": model, "adapter": adapter, "tasks": report}
    if adapter == "fake":
        payload["label"] = "machinery-only"
    out.write_text(json.dumps(payload, indent=2, sort_keys=True), encoding="utf-8")
    print(f"model: {model} (adapter {adapter})")
    for task_value, row in report.items():
        print(
            f"[{task_value}] quality={row['quality']:.3f} "
            f"cost/resolved=${row['cost_per_resolved']:.4f} "
            f"p95={row['p95_latency_ms']:.0f}ms n={row['n']:.0f}"
        )
    print(f"report: {out}")


async def cmd_report(incumbent: str, candidate: str) -> None:
    async with service_session() as session:
        rows = (
            await session.execute(
                select(ModelScorecard)
                .where(ModelScorecard.model.in_([incumbent, candidate]))
                .order_by(ModelScorecard.task_type, ModelScorecard.id)
            )
        ).scalars().all()
    latest: dict[tuple[str, str], ModelScorecard] = {}
    for row in rows:
        latest[(row.model, row.task_type)] = row
    tasks = sorted({task for _, task in latest})
    if not tasks:
        print("no scorecards stored for these models; run score first")
        return
    print(f"{'task':<16}{'incumbent ' + incumbent:<26}{'candidate ' + candidate:<26}")
    for task in tasks:
        cells = []
        for model in (incumbent, candidate):
            row = latest.get((model, task))
            if row is None:
                cells.append("-")
            else:
                cells.append(
                    f"q={row.quality:.2f} ${row.cost_per_resolved:.4f} "
                    f"p95={row.p95_latency_ms:.0f}ms"
                )
        print(f"{task:<16}{cells[0]:<26}{cells[1]:<26}")


def main() -> None:
    parser = argparse.ArgumentParser(description="G4 model scorecards.")
    sub = parser.add_subparsers(dest="command", required=True)
    score = sub.add_parser("score", help="score a model on every task suite")
    score.add_argument("--model", required=True)
    score.add_argument("--adapter", default="fake", choices=["fake", "openai"])
    score.add_argument("--limit", type=int, default=20)
    report = sub.add_parser("report", help="print incumbent against candidate")
    report.add_argument("--incumbent", required=True)
    report.add_argument("--candidate", required=True)
    args = parser.parse_args()
    if args.command == "score":
        asyncio.run(cmd_score(args.model, args.adapter, args.limit))
    elif args.command == "report":
        asyncio.run(cmd_report(args.incumbent, args.candidate))


if __name__ == "__main__":
    main()
