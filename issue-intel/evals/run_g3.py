"""G3 fix benchmark: the agent on the ten in-scope planted bugs.

Prerequisites: sample_repo history built (`setup-history.py`), dotnet SDK with
restored packages, postgres with the corpus ingested, ground truth generated.
Entry: `python -m evals.run_g3 [--adapter fake|openai]`. Writes
`evals/reports/g3.json`.

With `--adapter fake` the loop is driven by scripted responses that apply the
reference patch, to prove the machinery; results are labelled machinery-only.
Against a real endpoint (`--adapter openai`) the model writes the patches and
candidates come from consider_run. Backports run through backport_pr onto the
release branches where each bug is present.
"""
from __future__ import annotations

import argparse
import asyncio
import json
import tempfile
from pathlib import Path

from sqlalchemy import select

from app.adapters.fake_tracker import WebhookEvent
from app.agents.backport import backport_pr
from app.agents.candidates import consider_run, ensure_opt_in
from app.agents.fix_loop import run_fix
from app.agents.sandbox import create_sandbox, remove_sandbox, run_cmd
from app.gateway.adapters import FakeAdapter
from app.gateway.gateway import ModelGateway
from app.governance.rls import service_session
from app.models.g1 import Ownership
from app.models.g3 import FixCandidate, FixPr
from app.pipeline.manager import execute_run, handle_event
from app.settings import Settings
from evals.run_g2 import MACHINERY_DEFAULTS

ROOT = Path(__file__).resolve().parent.parent
REPO = ROOT / "sample_repo"
FIX_CASES = ROOT / "evals" / "fix_cases"

HIDDEN_CSPROJ = """<Project Sdk="Microsoft.NET.Sdk">
  <PropertyGroup>
    <TargetFramework>net8.0</TargetFramework>
    <Nullable>enable</Nullable>
    <ImplicitUsings>enable</ImplicitUsings>
    <IsPackable>false</IsPackable>
  </PropertyGroup>
  <ItemGroup>
    <PackageReference Include="Microsoft.NET.Test.Sdk" Version="17.11.0" />
    <PackageReference Include="xunit" Version="2.9.2" />
    <PackageReference Include="xunit.runner.visualstudio" Version="2.8.2" />
  </ItemGroup>
  <ItemGroup>
{refs}    <Compile Include="{hidden}" />
  </ItemGroup>
</Project>
"""


def _load(name: str) -> object:
    return json.loads((ROOT / "evals" / "ground_truth" / f"{name}.json").read_text())


async def hidden_passing(worktree: Path, test_class: str, tmp: Path) -> bool:
    refs = "".join(
        f'    <ProjectReference Include="{worktree}/src/{m}/{m}.csproj" />\n'
        for m in ("VersionControl", "Localization", "UiState", "AssetImport")
    )
    proj_dir = tmp / "hidden"
    proj_dir.mkdir(exist_ok=True)
    proj = proj_dir / "Hidden.csproj"
    proj.write_text(
        HIDDEN_CSPROJ.format(refs=refs, hidden=f"{FIX_CASES}/HiddenTests.cs"),
        encoding="utf-8",
    )
    result = await run_cmd(
        ["dotnet", "test", "--nologo", "--filter",
         f"FullyQualifiedName~{test_class}"],
        cwd=proj_dir, timeout_s=600,
    )
    return result.returncode == 0


async def _ensure_run(gateway: ModelGateway, key: str) -> str:
    run_id, cached = await handle_event(WebhookEvent(event="created", key=key))
    if not cached:
        await execute_run(gateway, run_id)
    return run_id


async def _seed_candidate(run_id: str, ticket: str, module: str) -> FixCandidate:
    async with service_session() as session:
        existing = (
            await session.execute(
                select(FixCandidate).where(FixCandidate.run_id == run_id)
            )
        ).scalar_one_or_none()
        if existing is not None:
            return existing
        row = FixCandidate(run_id=run_id, ticket_key=ticket, module=module,
                           confidence=1.0, owner_opt_in=True, status="PENDING")
        session.add(row)
        await session.commit()
        return row


async def _run_bug(
    bug: dict, ticket: str, adapter: str, tmp: Path
) -> dict[str, object]:
    settings = Settings(model_adapter="fake") if adapter == "fake" else Settings(  # type: ignore[arg-type]
        model_adapter="openai"
    )
    pipe_gateway = ModelGateway(
        settings=settings,
        adapter=FakeAdapter(defaults=dict(MACHINERY_DEFAULTS)) if adapter == "fake" else None,
    )
    run_id = await _ensure_run(pipe_gateway, ticket)
    if adapter == "fake":
        candidate = await _seed_candidate(run_id, ticket, bug["module"])
        patch_text = (FIX_CASES / bug["patch"]).read_text(encoding="utf-8")
        script = {
            "tessera-large": [
                json.dumps({"reads": bug["files"], "approach": "reference fix"}),
                json.dumps({"patch": patch_text, "files": bug["files"],
                            "explanation": "scripted reference fix"}),
            ]
        }
        gateway = ModelGateway(settings=settings, adapter=FakeAdapter(script=script))
    else:
        gateway = ModelGateway(settings=settings)
        candidate = await consider_run(settings, run_id)
        if candidate.status != "PENDING":
            return {"bug": bug["id"], "candidate_status": candidate.status,
                    "skipped": True}
    hidden_dir = tmp / bug["id"]
    hidden_dir.mkdir(exist_ok=True)

    async def hidden_check(worktree: Path) -> bool:
        return await hidden_passing(worktree, bug["test_class"], hidden_dir)

    async with service_session() as session:
        attempt = await run_fix(session, gateway, settings, candidate.id, REPO,
                                hidden_check)
    tag = f"{run_id}:fix"
    cost = sum(c.cost_usd for c in gateway.logged_calls if c.run_id == tag)
    tokens = sum(c.tokens_in + c.tokens_out for c in gateway.logged_calls
                 if c.run_id == tag)
    trace = attempt.trace if isinstance(attempt.trace, list) else []
    tested_steps = [s for s in trace if s.get("step") == "tested"]
    last = tested_steps[-1] if tested_steps else {}
    hidden_before = next(
        (s.get("hidden_passing") for s in trace if s.get("step") == "baseline"),
        None,
    )
    # Independent verification on the committed branch.
    branch_ok: bool | None = None
    ship_ok: bool | None = None
    if attempt.status == "OFFERED":
        sandbox = await create_sandbox(REPO, tmp / "verify", f"verify-{bug['id']}",
                                       base=attempt.branch)
        try:
            branch_ok = await hidden_passing(sandbox.path, bug["test_class"],
                                             hidden_dir / "verify")
            ship = await run_cmd(["dotnet", "test", "--nologo"],
                                 cwd=sandbox.path, timeout_s=600)
            ship_ok = ship.returncode == 0
        finally:
            await remove_sandbox(REPO, sandbox)
    return {
        "bug": bug["id"], "ticket": ticket, "status": attempt.status,
        "hidden_before": hidden_before,
        "hidden_flipped": bool(last.get("hidden_flipped", False)),
        "hidden_on_branch": branch_ok, "ship_green": ship_ok,
        "attempt_no": attempt.attempt_no,
        "tokens": tokens, "cost_usd": round(cost, 6),
    }


async def _backport_benchmark(bug: dict, ticket: str, tmp: Path) -> list[dict]:
    branches = [b for b in bug["branches"] if b.startswith("release/")]
    if not branches:
        return []
    settings = Settings(model_adapter="fake")
    gateway = ModelGateway(settings=settings, adapter=FakeAdapter())
    async with service_session() as session:
        pr = (
            await session.execute(
                select(FixPr).where(FixPr.kind == "FIX").order_by(FixPr.id.desc())
            )
        ).scalars().all()
        mine = next((p for p in pr if ticket in p.title), None)
        if mine is None:
            return [{"bug": bug["id"], "error": "no fix PR to backport"}]
        pr_id = mine.id
    async with service_session() as session:
        made = await backport_pr(session, gateway, settings, pr_id, branches, REPO)
    rows = []
    for row in made:
        ok: bool | None = None
        if row.status == "OPEN":
            sandbox = await create_sandbox(REPO, tmp / "bpverify",
                                           f"bpverify-{row.id}", base=row.branch)
            try:
                ok = await hidden_passing(sandbox.path, bug["test_class"],
                                          tmp / f"bp-{row.id}")
            finally:
                await remove_sandbox(REPO, sandbox)
        rows.append({"bug": bug["id"], "branch": row.base, "status": row.status,
                     "hidden_passing": ok})
    return rows


async def _main(adapter: str) -> None:
    manifest = json.loads((FIX_CASES / "bugs.json").read_text(encoding="utf-8"))
    regressions = _load("regressions")
    assert isinstance(regressions, list)
    by_symptom = {r["symptom"]: r["case"] for r in regressions if r.get("symptom")}
    in_scope = [b for b in manifest["bugs"] if b["scope"] == "in"]
    async with service_session() as session:
        owners = {
            o.target: o.owner_handle
            for o in (await session.execute(select(Ownership))).scalars().all()
        }
    for module, owner in owners.items():
        await ensure_opt_in(owner, module, True)
    results = []
    with tempfile.TemporaryDirectory(prefix="g3bench-") as raw_tmp:
        tmp = Path(raw_tmp)
        for bug in in_scope:
            ticket = by_symptom.get(bug["symptom"], "")
            if not ticket:
                results.append({"bug": bug["id"], "error": "no regression case"})
                continue
            results.append(await _run_bug(bug, ticket, adapter, tmp))
        backports = []
        for bug in in_scope:
            ticket = by_symptom.get(bug["symptom"], "")
            if ticket:
                backports.extend(await _backport_benchmark(bug, ticket, tmp))
    offered = sum(1 for r in results if r.get("status") == "OFFERED")
    flipped = sum(1 for r in results if r.get("hidden_flipped"))
    total_cost = round(sum(float(r.get("cost_usd", 0.0)) for r in results), 6)
    report = {"adapter": adapter, "bugs": results, "backports": backports,
              "totals": {"offered": offered, "hidden_flipped": flipped,
                         "cost_usd": total_cost, "n": len(results)}}
    out = ROOT / "evals" / "reports" / "g3.json"
    out.write_text(json.dumps(report, indent=2, sort_keys=True), encoding="utf-8")
    print(f"adapter: {adapter}" + (" (machinery-only)" if adapter == "fake" else ""))
    for r in results:
        print(
            f"[{r.get('bug')}] status={r.get('status')} "
            f"hidden_before={r.get('hidden_before')} flipped={r.get('hidden_flipped')} "
            f"branch={r.get('hidden_on_branch')} ship={r.get('ship_green')} "
            f"attempts={r.get('attempt_no')} tokens={r.get('tokens')} "
            f"cost={r.get('cost_usd')}"
        )
    for b in backports:
        print(f"[backport {b.get('bug')} -> {b.get('branch')}] "
              f"{b.get('status')} hidden={b.get('hidden_passing')}")
    print(f"offered={offered}/{len(results)} flipped={flipped} cost={total_cost}")
    print(f"report: {out}")


def main() -> None:
    parser = argparse.ArgumentParser(description="Run the G3 fix benchmark.")
    parser.add_argument("--adapter", default="fake", choices=["fake", "openai"])
    args = parser.parse_args()
    asyncio.run(_main(args.adapter))


if __name__ == "__main__":
    main()
