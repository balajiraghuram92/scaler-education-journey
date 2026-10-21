from __future__ import annotations

from collections import Counter
from collections.abc import Iterable, Mapping
from dataclasses import dataclass, field


class LedgerError(Exception):
    """Base class for ledger errors."""


class InvalidEvent(LedgerError):
    def __init__(self, index: int, reason: str) -> None:
        super().__init__(f"event {index}: {reason}")
        self.index = index
        self.reason = reason


@dataclass(frozen=True, slots=True, kw_only=True)
class UsageEvent:
    tenant: str
    tokens: int
    model: str = "default"

    def __post_init__(self) -> None:
        if not self.tenant:
            raise ValueError("tenant must not be empty")
        if self.tokens < 0:
            raise ValueError("tokens must be >= 0")


@dataclass(frozen=True, slots=True)
class Summary:
    tokens_by_tenant: dict[str, int] = field(default_factory=dict)
    errors: tuple[InvalidEvent, ...] = ()


def parse_event(raw: Mapping[str, object], index: int = 0) -> UsageEvent:
    try:
        tenant, tokens = raw["tenant"], raw["tokens"]
    except KeyError as exc:
        raise InvalidEvent(index, f"missing field {exc.args[0]!r}") from exc
    model = raw.get("model", "default")
    if not isinstance(tenant, str) or not isinstance(model, str):
        raise InvalidEvent(index, "tenant and model must be strings")
    if type(tokens) is not int:
        raise InvalidEvent(index, "tokens must be an int")
    try:
        return UsageEvent(tenant=tenant, tokens=tokens, model=model)
    except ValueError as exc:
        raise InvalidEvent(index, str(exc)) from exc


def summarize(raw_events: Iterable[Mapping[str, object]], *, strict: bool = False) -> Summary:
    totals: Counter[str] = Counter()
    errors: list[InvalidEvent] = []
    for index, raw in enumerate(raw_events):
        try:
            event = parse_event(raw, index)
        except InvalidEvent as exc:
            errors.append(exc)
            continue
        totals[event.tenant] += event.tokens
    if strict and errors:
        raise ExceptionGroup(f"{len(errors)} invalid events", errors)
    return Summary(dict(totals), tuple(errors))
