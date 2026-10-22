import dataclasses
import os
import threading
from collections.abc import Iterator, Mapping
from contextlib import contextmanager
from dataclasses import dataclass
from typing import Any


@dataclass(frozen=True)
class Settings:
    llm_model: str
    monthly_budget_usd: float


def load_settings(env: Mapping[str, str]) -> Settings:
    """Pure function: parse and validate ``env``, touching no globals.

    Defaults: ``LLM_MODEL="small"``, ``MONTHLY_BUDGET_USD="100"``.
    A non-numeric budget raises ValueError whose message names MONTHLY_BUDGET_USD;
    a negative budget raises ValueError.
    """
    raise NotImplementedError("Implement load_settings")


def get_settings() -> Settings:
    """Lazily load from ``os.environ`` once, thread-safely; same object until reset."""
    raise NotImplementedError("Implement get_settings")


def reset_settings() -> None:
    """Clear the cached settings."""
    raise NotImplementedError("Implement reset_settings")


@contextmanager
def override_settings(**changes: Any) -> Iterator[Settings]:
    """Temporarily swap in ``dataclasses.replace(current, **changes)``.

    Restore the exact previous state on exit, even if the body raises.
    Unknown field names raise TypeError.
    """
    raise NotImplementedError("Implement override_settings")
    yield  # pragma: no cover


class BudgetGuard:
    """Receives its settings by constructor injection and never touches the global.

    ``allow(cost_usd)`` records the spend and returns True, or returns False
    (recording nothing) if the call would push total spend over the budget.
    """

    def __init__(self, settings: Settings) -> None:
        raise NotImplementedError("Implement the constructor")

    def allow(self, cost_usd: float) -> bool:
        raise NotImplementedError("Implement allow")
