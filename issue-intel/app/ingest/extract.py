"""Extract the three raw corpus formats into plain records. Pure, no DB."""
from __future__ import annotations

import csv
import json
from dataclasses import dataclass, field
from pathlib import Path
from xml.etree.ElementTree import parse


@dataclass
class RawCase:
    source: str
    key: str
    filed_module: str
    true_module: str
    title: str
    body: str
    version: str
    status: str
    resolution: str
    fixed_change: str
    customer_ref: str
    restriction: str
    departments: list[str] = field(default_factory=list)


@dataclass
class RawMessage:
    seq: int
    author: str
    text: str


@dataclass
class RawThread:
    key: str
    case_key: str
    messages: list[RawMessage] = field(default_factory=list)


@dataclass
class RawChange:
    ref: str
    repo: str
    author: str
    reviewers: list[str] = field(default_factory=list)
    files: list[str] = field(default_factory=list)
    message: str = ""
    planned_seq: int | None = None


@dataclass
class RawPerson:
    handle: str
    name: str
    team: str
    status: str


@dataclass
class TrackerExport:
    cases: list[RawCase]
    changes: list[RawChange]
    people: list[RawPerson]
    ownership: dict[str, str]


def _row_to_case(row: dict[str, str], source: str) -> RawCase:
    departments = [d for d in row.get("departments", "").split(",") if d]
    return RawCase(
        source=source,
        key=row["key"],
        filed_module=row["module"],
        true_module=row.get("true_module", "") or row["module"],
        title=row["title"],
        body=row["body"],
        version=row["version"],
        status=row["status"],
        resolution=row.get("resolution", ""),
        fixed_change=row.get("fixed_change", ""),
        customer_ref=row.get("customer_ref", ""),
        restriction=row.get("restriction", "OPEN"),
        departments=departments,
    )


def read_legacy_csv(path: Path) -> list[RawCase]:
    with path.open(newline="", encoding="utf-8") as fh:
        return [_row_to_case(row, "LEGACY") for row in csv.DictReader(fh)]


def read_tracker_json(path: Path) -> TrackerExport:
    payload = json.loads(path.read_text(encoding="utf-8"))
    cases = [_row_to_case(r, "TRACKER") for r in payload["tracker_cases"]]
    cases += [_row_to_case(r, "SUPPORT") for r in payload["support_cases"]]
    changes = [
        RawChange(
            ref=pr["ref"], repo=pr["repo"], author=pr["author"],
            reviewers=list(pr["reviewers"]), files=list(pr["files"]),
            message=pr["message"], planned_seq=pr.get("planned_seq"),
        )
        for pr in payload["pull_requests"]
    ]
    people = [RawPerson(**p) for p in payload["people"]]
    return TrackerExport(cases=cases, changes=changes, people=people,
                         ownership=dict(payload["ownership"]))


def read_chat_xml(path: Path) -> list[RawThread]:
    root = parse(path).getroot()
    threads = []
    for node in root.findall("thread"):
        messages = [
            RawMessage(seq=n, author=item.get("author", ""), text=item.text or "")
            for n, item in enumerate(node.findall("message"))
        ]
        key = node.get("key", "")
        threads.append(RawThread(key=key, case_key=node.get("case", ""), messages=messages))
    return threads
