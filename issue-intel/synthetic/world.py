"""World builder: people, cases, threads, changes. Deterministic given a seed."""
from __future__ import annotations

import importlib.util
import random
from dataclasses import dataclass, field
from pathlib import Path

from synthetic import data as D

REPO_ROOT = Path(__file__).resolve().parent.parent


def load_history_plan() -> list[dict]:
    spec = importlib.util.spec_from_file_location(
        "setup_history", REPO_ROOT / "sample_repo" / "setup-history.py"
    )
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return [p for p in module.PLAN if p["kind"] == "bug"]


@dataclass
class Person:
    handle: str
    name: str
    team: str
    status: str  # ACTIVE | LEFT


@dataclass
class Case:
    key: str
    source: str  # LEGACY | TRACKER | SUPPORT
    module: str
    filed_module: str
    title: str
    body: str
    version: str
    status: str
    resolution: str
    outcome: str
    fixed_change: str
    customer_ref: str
    restriction: str
    departments: list[str] = field(default_factory=list)


@dataclass
class Message:
    author: str
    text: str


@dataclass
class Thread:
    key: str
    case_key: str
    messages: list[Message] = field(default_factory=list)


@dataclass
class Change:
    ref: str
    repo: str
    author: str
    reviewers: list[str] = field(default_factory=list)
    files: list[str] = field(default_factory=list)
    message: str = ""
    planned_seq: int | None = None


@dataclass
class World:
    people: list[Person]
    ownership: dict[str, str]
    legacy: list[Case]
    tracker: list[Case]
    support: list[Case]
    threads: list[Thread]
    changes: list[Change]
    ground_truth: dict[str, object]


def _people(rng: random.Random) -> list[Person]:
    handles = [f"{f[0].lower()}{last.lower()}" for f in D.FIRST_NAMES for last in D.LAST_NAMES]
    rng.shuffle(handles)
    people = []
    for i in range(40):
        people.append(
            Person(
                handle=handles[i],
                name=f"{D.FIRST_NAMES[i % 20]} {D.LAST_NAMES[(i * 7) % 20]}",
                team=D.TEAMS[i % len(D.TEAMS)],
                status="LEFT" if i % 3 == 2 else "ACTIVE",
            )
        )
    return people


def _person_cycle(people: list[Person]) -> list[str]:
    return [p.handle for p in people]


def _case_body(rng: random.Random, version: str) -> str:
    return rng.choice(D.BODY_TEMPLATES).format(
        repro=rng.choice(D.REPROS),
        expected="the documented result",
        observed="the panel shows stale data",
        version=version,
        blame="last week's refactor",
    )


def _restriction(rng: random.Random) -> tuple[str, list[str]]:
    roll = rng.random()
    if roll < 0.70:
        return "OPEN", ["SE", "Support", "Partner"]
    if roll < 0.90:
        return "SE", ["SE"]
    return "CUSTOMER_RESTRICTED", ["SE"]


def build_world(seed: int) -> World:
    rng = random.Random(seed)
    people = _people(rng)
    handles = _person_cycle(people)
    ownership = {m: handles[i] for i, m in enumerate(D.MODULES)}
    plan = load_history_plan()

    changes: list[Change] = []
    for entry in plan:
        changes.append(
            Change(
                ref=f"SAMPLE-{entry['seq']:02d}",
                repo="sample_repo",
                author=handles[entry["seq"] % len(handles)],
                reviewers=[handles[(entry["seq"] + 3) % len(handles)]],
                files=list(entry["files"]),
                message=f"Introduce defect ({entry['symptom']})",
                planned_seq=entry["seq"],
            )
        )
    for i in range(8):
        changes.append(
            Change(
                ref=f"r{12000 + i}",
                repo="legacy-svn",
                author=handles[i % len(handles)],
                reviewers=[],
                files=[f"src/legacy/module{i}.cpp"],
                message=f"legacy refactor part {i}",
            )
        )

    legacy: list[Case] = []
    outcome_labels: dict[str, str] = {}
    for i in range(600):
        module = D.MODULES[i % 4]
        outcome = D.OUTCOMES[i % 7] if i % 11 else "FIXED"
        version = D.LEGACY_VERSIONS[i % len(D.LEGACY_VERSIONS)]
        change = changes[i % len(changes)].ref if outcome in ("FIXED", "REGRESSION") else ""
        other = f"LGC-{(i + 37) % 600 + 1:04d}"
        resolution = D.RESOLUTIONS[outcome].format(other=other, change=change)
        restriction, departments = _restriction(rng)
        key = f"LGC-{i + 1:04d}"
        legacy.append(
            Case(
                key=key, source="LEGACY", module=module, filed_module=module,
                title=rng.choice(D.TITLE_TEMPLATES[module]).format(thing=rng.choice(D.THINGS)),
                body=_case_body(rng, version), version=version, status="Closed",
                resolution=resolution, outcome=outcome, fixed_change=change,
                customer_ref=f"CUST-{1000 + i}" if restriction != "OPEN" else "",
                restriction=restriction, departments=departments,
            )
        )
        outcome_labels[key] = outcome

    tracker: list[Case] = []
    duplicates: list[dict[str, str]] = []
    regressions: list[dict[str, str]] = []
    wrong_module: dict[str, str] = {}
    for i in range(300):
        module = D.MODULES[(i + 1) % 4]
        version = D.TRACKER_VERSIONS[i % len(D.TRACKER_VERSIONS)]
        key = f"TES-{i + 1:04d}"
        title = rng.choice(D.TITLE_TEMPLATES[module]).format(thing=rng.choice(D.THINGS))
        body = _case_body(rng, version)
        filed = module
        if i < 60:  # re-reports of legacy cases under different wording
            target = legacy[(i * 9) % 600]
            title = f"Again: {target.title.lower()} [{version}]"
            duplicates.append({"case": key, "duplicate_of": target.key, "kind": "rereport"})
        if i < 30:  # filed under the wrong module
            filed = D.MODULES[(D.MODULES.index(module) + 1) % 4]
            wrong_module[key] = module
        restriction, departments = _restriction(rng)
        tracker.append(
            Case(
                key=key, source="TRACKER", module=module, filed_module=filed, title=title,
                body=body, version=version, status="Open", resolution="", outcome="UNKNOWN",
                fixed_change="", customer_ref="", restriction=restriction,
                departments=departments,
            )
        )
    # Planted-bug regression cases: one tracker case per planned defect.
    for j, entry in enumerate(plan):
        case = tracker[(j * 23) % 300]
        case.title = f"Regression from SAMPLE-{entry['seq']:02d}: {entry['symptom']}"
        regressions.append(
            {"case": case.key, "change": f"SAMPLE-{entry['seq']:02d}",
             "symptom": entry["symptom"], "kind": "planted"}
        )
    for k in range(8):  # legacy-era regressions
        case = tracker[(200 + k) % 300]
        regressions.append({"case": case.key, "change": f"r{12000 + k}",
                            "symptom": "legacy", "kind": "legacy"})

    support: list[Case] = []
    for i in range(150):
        module = D.MODULES[(i + 2) % 4]
        version = D.TRACKER_VERSIONS[i % len(D.TRACKER_VERSIONS)]
        key = f"SUP-{i + 1:04d}"
        restriction, departments = _restriction(rng)
        support.append(
            Case(
                key=key, source="SUPPORT", module=module, filed_module=module,
                title=rng.choice(D.TITLE_TEMPLATES[module]).format(thing=rng.choice(D.THINGS)),
                body=_case_body(rng, version), version=version, status="Open",
                resolution="", outcome="UNKNOWN", fixed_change="",
                customer_ref=f"CUST-{5000 + i}", restriction=restriction,
                departments=departments,
            )
        )
        if i < 25:
            duplicates.append(
                {"case": key, "duplicate_of": legacy[(i * 13) % 600].key, "kind": "support"}
            )

    threads: list[Thread] = []
    chat_root_cause: dict[str, str] = {}
    for i in range(250):
        case = tracker[i % 300] if i % 2 == 0 else legacy[i % 600]
        thread = Thread(key=f"THREAD-{i + 1:04d}", case_key=case.key)
        thread.messages.append(
            Message(handles[i % len(handles)],
                    rng.choice(D.CHAT_OPENERS).format(
                        symptom=case.title[:40], version=case.version))
        )
        if i < 40:  # the real root cause, spread over several messages
            thread.messages.append(Message(handles[(i + 1) % len(handles)], "looking now"))
            thread.messages.append(
                Message(handles[(i + 2) % len(handles)],
                        rng.choice(D.CHAT_CAUSE).format(
                            cause=rng.choice(D.CAUSES), change=changes[i % 12].ref))
            )
            chat_root_cause[thread.key] = case.key
        else:
            for k in range(rng.randint(1, 4)):
                thread.messages.append(
                    Message(handles[(i + k) % len(handles)], rng.choice(D.CHAT_NOISE))
                )
        threads.append(thread)

    # 15 prompt-injection samples planted in ticket bodies and chat messages.
    injections: list[dict[str, str]] = []
    for n, payload in enumerate(D.INJECTIONS):
        if n % 2 == 0:
            case = tracker[(n * 17) % 300]
            case.body = f"{case.body}\n\n--- customer note ---\n{payload}"
            injections.append({"location": f"ticket:{case.key}", "payload": payload})
        else:
            thread = threads[(n * 19) % 250]
            thread.messages.append(Message(handles[n % len(handles)], payload))
            injections.append({"location": f"chat:{thread.key}", "payload": payload})

    ground_truth: dict[str, object] = {
        "duplicates": duplicates,
        "regressions": regressions,
        "outcome_labels": outcome_labels,
        "chat_root_cause": chat_root_cause,
        "injections": injections,
        "wrong_module": wrong_module,
    }
    return World(
        people=people, ownership=ownership, legacy=legacy, tracker=tracker,
        support=support, threads=threads, changes=changes, ground_truth=ground_truth,
    )
