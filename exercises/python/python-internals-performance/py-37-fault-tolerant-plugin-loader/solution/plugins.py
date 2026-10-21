from __future__ import annotations

from collections.abc import Callable, Iterable
from dataclasses import dataclass, field
from importlib.metadata import EntryPoint, entry_points
from typing import Any


@dataclass
class LoadReport:
    loaded: dict[str, Any] = field(default_factory=dict)
    failures: dict[str, BaseException] = field(default_factory=dict)


def load_plugins(
    eps: Iterable[EntryPoint],
    validate: Callable[[Any], bool] = lambda obj: True,
) -> LoadReport:
    """Load entry points in name order; isolate failures and report them per plugin."""
    report = LoadReport()
    for ep in sorted(eps, key=lambda e: e.name):
        if ep.name in report.loaded or ep.name in report.failures:
            report.failures[ep.name] = ValueError(f"duplicate plugin name {ep.name!r}")
            report.loaded.pop(ep.name, None)
            continue
        try:
            obj = ep.load()
        except (Exception, SystemExit) as exc:  # a broken plugin (even one calling sys.exit) must not stop start-up
            report.failures[ep.name] = exc
            continue
        if not validate(obj):
            report.failures[ep.name] = TypeError(f"{ep.value} failed validation")
            continue
        report.loaded[ep.name] = obj
    return report


def discover(group: str, validate: Callable[[Any], bool] = lambda obj: True) -> LoadReport:
    """Load every installed entry point in `group`."""
    return load_plugins(entry_points(group=group), validate)
