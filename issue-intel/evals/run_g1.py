"""G1 eval runner: retrieval, outcome classification, leakage.

Needs postgres with the corpus ingested (`python -m app.ingest.run`) and the
generated ground truth. Entry: `python -m evals.run_g1`. Writes
`evals/reports/g1.json`. Numbers produced with the fake adapter are labelled.
"""
from __future__ import annotations

import argparse
import asyncio
import json
from pathlib import Path

from sqlalchemy import select, text
from sqlalchemy.ext.asyncio import AsyncSession

from app.db import create_session_factory
from app.gateway.gateway import ModelGateway
from app.governance.entitlements import Entitlements
from app.governance.rls import rls_session, service_session
from app.models.g1 import Acl, Case, Change, Thread, User
from app.models.g1 import Entitlement as EntitlementRow
from app.search.hybrid import SearchMode, hybrid_search
from app.search.lineage import expand_lineage
from evals.metrics import accuracy, mean, per_class_f1, recall_at_k, reciprocal_rank

ROOT = Path(__file__).resolve().parent.parent
MODES: list[SearchMode] = ["fulltext", "vector", "fused"]


def _load(name: str) -> object:
    return json.loads((ROOT / "evals" / "ground_truth" / f"{name}.json").read_text())


async def _case_keys_for_hits(session: AsyncSession, keys: list[tuple[str, str]]) -> list[str]:
    threads = {
        t.key: t.case_key for t in (await session.execute(select(Thread))).scalars().all()
    }
    out = []
    for owner_type, owner_key in keys:
        if owner_type == "case":
            out.append(owner_key)
        elif owner_type == "thread" and owner_key in threads:
            out.append(threads[owner_key])
    return out


async def _ranked_cases(
    session: AsyncSession, gateway: ModelGateway, query: str, mode: SearchMode
) -> list[str]:
    vectors = await gateway.embed([query])
    hits = await hybrid_search(session, query, vectors[0], limit=10, mode=mode)
    return await _case_keys_for_hits(session, [(h.owner_type, h.owner_key) for h in hits])


async def retrieval_eval(
    session: AsyncSession, gateway: ModelGateway
) -> dict[str, dict[str, float]]:
    duplicates = _load("duplicates")
    assert isinstance(duplicates, list)
    regressions = _load("regressions")
    assert isinstance(regressions, list)
    labels = _load("outcome_labels")
    assert isinstance(labels, dict)
    cases = {
        c.source_key: c for c in (await session.execute(select(Case))).scalars().all()
    }
    wontfix = [k for k, v in labels.items() if v == "WONT_FIX"][:50]
    report: dict[str, dict[str, float]] = {}
    for mode in MODES:
        r5, r10, mrr = [], [], []
        for pair in duplicates:
            origin = cases.get(pair["case"])
            if origin is None:
                continue
            ranked = await _ranked_cases(
                session, gateway, f"{origin.title}\n{origin.body}", mode
            )
            relevant = {pair["duplicate_of"]}
            r5.append(recall_at_k(ranked, relevant, 5))
            r10.append(recall_at_k(ranked, relevant, 10))
            mrr.append(reciprocal_rank(ranked, relevant))
        for case_key in wontfix:
            origin = cases.get(case_key)
            if origin is None:
                continue
            ranked = await _ranked_cases(session, gateway, origin.title, mode)
            relevant = {
                k for k in wontfix
                if k != case_key and cases[k].module == origin.module
            }
            r5.append(recall_at_k(ranked, relevant, 5))
            r10.append(recall_at_k(ranked, relevant, 10))
            mrr.append(reciprocal_rank(ranked, relevant))
        reg_hits = 0
        for reg in regressions:
            origin = cases.get(reg["case"])
            if origin is None:
                continue
            ranked = await _ranked_cases(
                session, gateway, f"{origin.title}\n{origin.body}", mode
            )
            lineage = await expand_lineage(session, ranked[:5])
            found = [c for keys in lineage.values() for c in keys.fixed_by]
            reg_hits += 1 if reg["change"] in found else 0
        report[mode] = {
            "recall@5": mean(r5), "recall@10": mean(r10), "mrr": mean(mrr),
            "regression_change_hit@5": reg_hits / len(regressions) if regressions else 0.0,
        }
    return report


async def outcome_eval(session: AsyncSession) -> dict[str, object]:
    labels = _load("outcome_labels")
    assert isinstance(labels, dict)
    cases = (
        await session.execute(select(Case).where(Case.source == "LEGACY"))
    ).scalars().all()
    predicted = [c.outcome for c in cases if c.source_key in labels]
    actual = [labels[c.source_key] for c in cases if c.source_key in labels]
    label_set = sorted(set(actual))
    return {
        "accuracy": accuracy(predicted, actual),
        "per_class_f1": per_class_f1(predicted, actual, label_set),
        "n": len(actual),
    }


def _entitled(acl: Acl, ent: Entitlements) -> bool:
    if acl.restriction > ent.max_restriction:
        return False
    if not (set(acl.modules.split(",")) & ent.modules):
        return False
    return bool(set(acl.departments.split(",")) & ent.departments)


async def leakage_eval() -> dict[str, float]:
    specs = {
        "open_support": Entitlements({"UiState"}, {"Support"}, 0),
        "se_engineer": Entitlements.service(),
        "partner": Entitlements({"Localization"}, {"Partner"}, 0),
    }
    factory = create_session_factory()
    report: dict[str, float] = {}
    for name, ent in specs.items():
        async with rls_session(ent) as session:
            case_rows = (await session.execute(select(Case))).scalars().all()
            raw_rows = (await session.execute(text("SELECT id, acl_id FROM cases"))).all()
            chunk_rows = (
                await session.execute(text("SELECT id, acl_id FROM chunks"))
            ).all()
        async with factory() as service:
            acls = {
                a.id: a for a in (await service.execute(select(Acl))).scalars().all()
            }
        visible = [c.acl_id for c in case_rows]
        visible += [r[1] for r in raw_rows] + [r[1] for r in chunk_rows]
        bad = sum(1 for aid in visible if not _entitled(acls[aid], ent))
        report[name] = bad / len(visible) if visible else 0.0
    void = Entitlements()
    async with rls_session(void) as session:
        n_cases = len((await session.execute(select(Case))).scalars().all())
        n_changes = len((await session.execute(select(Change))).scalars().all())
        n_threads = len((await session.execute(select(Thread))).scalars().all())
    report["no_entitlement_rows"] = float(n_cases + n_changes + n_threads)
    _ = User, EntitlementRow
    return report


async def _main(adapter: str) -> None:
    from app.settings import Settings

    gateway = ModelGateway(settings=Settings(model_adapter=adapter))  # type: ignore[arg-type]
    async with service_session() as session:
        retrieval = await retrieval_eval(session, gateway)
        outcome = await outcome_eval(session)
    leakage = await leakage_eval()
    report = {
        "adapter": adapter, "retrieval": retrieval,
        "outcome": outcome, "leakage_rate": leakage,
    }
    out = ROOT / "evals" / "reports" / "g1.json"
    out.write_text(json.dumps(report, indent=2, sort_keys=True), encoding="utf-8")
    print(
        f"adapter: {adapter} (numbers labelled fake)"
        if adapter == "fake"
        else f"adapter: {adapter}"
    )
    for mode, scores in retrieval.items():
        print(f"[{mode}] " + " ".join(f"{k}={v:.3f}" for k, v in scores.items()))
    print(f"[outcome] accuracy={outcome['accuracy']:.3f} n={outcome['n']}")
    for label, f1 in outcome["per_class_f1"].items():
        print(f"  F1 {label}={f1:.3f}")
    print("[leakage] " + " ".join(f"{k}={v:.3f}" for k, v in leakage.items()))
    print(f"report: {out}")


def main() -> None:
    parser = argparse.ArgumentParser(description="Run the G1 evals.")
    parser.add_argument("--adapter", default="fake", choices=["fake", "openai"])
    args = parser.parse_args()
    asyncio.run(_main(args.adapter))


if __name__ == "__main__":
    main()
