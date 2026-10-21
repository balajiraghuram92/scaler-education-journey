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
    """Pure function: parse and validate, no globals."""
    raw = env.get("MONTHLY_BUDGET_USD", "100")
    try:
        budget = float(raw)
    except ValueError:
        raise ValueError(f"MONTHLY_BUDGET_USD must be a number, got {raw!r}") from None
    if budget < 0:
        raise ValueError("MONTHLY_BUDGET_USD must be >= 0")
    return Settings(llm_model=env.get("LLM_MODEL", "small"), monthly_budget_usd=budget)


_settings: Settings | None = None
_lock = threading.RLock()


def get_settings() -> Settings:
    """Lazy, thread-safe process-wide settings (usable as a FastAPI dependency)."""
    global _settings
    if _settings is None:
        with _lock:
            if _settings is None:
                _settings = load_settings(os.environ)
    return _settings


def reset_settings() -> None:
    global _settings
    with _lock:
        _settings = None


@contextmanager
def override_settings(**changes: Any) -> Iterator[Settings]:
    """Temporarily replace the settings; restores the previous state on exit."""
    global _settings
    with _lock:
        previous = _settings
        _settings = dataclasses.replace(get_settings(), **changes)
        current = _settings
    try:
        yield current
    finally:
        with _lock:
            _settings = previous


class BudgetGuard:
    """Receives its settings explicitly, so it never touches the global."""

    def __init__(self, settings: Settings) -> None:
        self._settings = settings
        self._spent = 0.0

    def allow(self, cost_usd: float) -> bool:
        if self._spent + cost_usd > self._settings.monthly_budget_usd:
            return False
        self._spent += cost_usd
        return True
