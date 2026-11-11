"""Writers: three deliberately different raw formats + ground truth JSON."""
from __future__ import annotations

import csv
import json
from pathlib import Path
from xml.etree.ElementTree import Element, SubElement, tostring

from synthetic.data import FIXED_STAMP
from synthetic.world import Case, World


def _case_row(case: Case) -> dict[str, str]:
    return {
        "key": case.key, "source": case.source, "module": case.filed_module,
        "true_module": case.module, "title": case.title, "body": case.body,
        "version": case.version, "status": case.status, "resolution": case.resolution,
        "fixed_change": case.fixed_change, "customer_ref": case.customer_ref,
        "restriction": case.restriction, "departments": ",".join(case.departments),
    }


def write_legacy_csv(world: World, path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="", encoding="utf-8") as fh:
        writer = csv.DictWriter(fh, fieldnames=list(_case_row(world.legacy[0]).keys()))
        writer.writeheader()
        for case in world.legacy:
            writer.writerow(_case_row(case))


def write_tracker_json(world: World, path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    payload = {
        "exported_at": FIXED_STAMP,
        "tracker_cases": [_case_row(c) for c in world.tracker],
        "support_cases": [_case_row(c) for c in world.support],
        "pull_requests": [
            {"ref": c.ref, "repo": c.repo, "author": c.author,
             "reviewers": c.reviewers, "files": c.files, "message": c.message,
             "planned_seq": c.planned_seq}
            for c in world.changes
        ],
        "people": [
            {"handle": p.handle, "name": p.name, "team": p.team, "status": p.status}
            for p in world.people
        ],
        "ownership": world.ownership,
    }
    path.write_text(json.dumps(payload, indent=2, sort_keys=True), encoding="utf-8")


def write_chat_xml(world: World, path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    root = Element("chat-export", {"exported_at": FIXED_STAMP})
    for thread in world.threads:
        node = SubElement(root, "thread", {"key": thread.key, "case": thread.case_key})
        for message in thread.messages:
            item = SubElement(node, "message", {"author": message.author})
            item.text = message.text
    path.write_bytes(tostring(root, encoding="utf-8", xml_declaration=True))


def write_ground_truth(world: World, directory: Path) -> None:
    directory.mkdir(parents=True, exist_ok=True)
    for name, payload in world.ground_truth.items():
        (directory / f"{name}.json").write_text(
            json.dumps(payload, indent=2, sort_keys=True), encoding="utf-8"
        )
