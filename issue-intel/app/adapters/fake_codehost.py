"""Fake code host: transport for PR records (durable rows live in fix_prs)."""
from __future__ import annotations

from dataclasses import dataclass


@dataclass
class MergedPr:
    pr_id: int
    branch: str
    base: str
    approver: str
    commit: str


class FakeCodeHost:
    def __init__(self) -> None:
        self.merged: list[MergedPr] = []

    def record_merge(self, pr_id: int, branch: str, base: str,
                     approver: str, commit: str) -> None:
        self.merged.append(MergedPr(pr_id, branch, base, approver, commit))

    def reset(self) -> None:
        self.merged.clear()


CODEHOST = FakeCodeHost()
