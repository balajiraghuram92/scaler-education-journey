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
    """Load entry points in NAME order; isolate failures and report them per plugin.

    - any ``Exception`` from ``ep.load()`` - and also ``SystemExit`` (plugins sometimes call ``sys.exit()`` at import
      time) - is recorded in ``failures`` under the plugin name and does not stop the others;
      never swallow ``KeyboardInterrupt``
    - after loading, ``validate(obj)`` must be true, otherwise record a ``TypeError`` mentioning ``ep.value``
    - if two entry points share a name, neither is accepted: the name goes to ``failures`` with a ``ValueError``
      whose message contains "duplicate" (remove any earlier successful load of that name)
    """
    raise NotImplementedError("Implement load_plugins")


def discover(group: str, validate: Callable[[Any], bool] = lambda obj: True) -> LoadReport:
    """Read ``importlib.metadata.entry_points(group=group)`` and delegate to ``load_plugins``."""
    raise NotImplementedError("Implement discover")
