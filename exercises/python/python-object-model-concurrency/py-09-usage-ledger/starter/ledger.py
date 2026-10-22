from __future__ import annotations

from collections.abc import Iterable, Mapping


class LedgerError(Exception):
    """Base class for ledger errors."""


class InvalidEvent(LedgerError):
    """A raw event that failed validation.

    ``InvalidEvent(index: int, reason: str)`` stores both as attributes ``index`` and ``reason``
    and has the message ``event <index>: <reason>``.
    """

    def __init__(self, index: int, reason: str) -> None:
        raise NotImplementedError("Implement InvalidEvent")


class UsageEvent:
    """An immutable usage event: a frozen, slotted, keyword-only dataclass.

    Fields: ``tenant: str``, ``tokens: int``, ``model: str = "default"``.
    ``__post_init__`` raises ``ValueError`` if ``tenant`` is empty or ``tokens < 0``.
    """

    def __init__(self, *args, **kwargs) -> None:
        raise NotImplementedError("Turn UsageEvent into a frozen, slotted, keyword-only dataclass")


class Summary:
    """Aggregate result: a frozen, slotted dataclass.

    Fields: ``tokens_by_tenant: dict[str, int]`` and ``errors: tuple[InvalidEvent, ...]``,
    both defaulting to empty (use ``default_factory`` where needed).
    """

    def __init__(self, *args, **kwargs) -> None:
        raise NotImplementedError("Turn Summary into a frozen, slotted dataclass")


def parse_event(raw: Mapping[str, object], index: int = 0) -> UsageEvent:
    """Validate ``raw`` into a ``UsageEvent``.

    ``tenant`` and ``tokens`` are required; ``model`` is optional. Raise ``InvalidEvent`` (never a
    bare ``KeyError``, ``TypeError`` or ``ValueError``) for a missing field, a non-string ``tenant``
    or ``model``, a ``tokens`` that is not an ``int`` (a ``bool`` is rejected), or a domain-rule
    violation. Chain causes with ``raise ... from``: a missing field has the original ``KeyError`` as
    ``__cause__`` and a rule violation has the ``ValueError``.
    """
    raise NotImplementedError("Implement parse_event")


def summarize(raw_events: Iterable[Mapping[str, object]], *, strict: bool = False) -> Summary:
    """Aggregate tokens per tenant and collect bad events.

    - accumulate with a ``Counter``, collect each ``InvalidEvent`` with its position in the input,
      and continue past bad events; it must accept a one-shot generator
    - with ``strict=True`` and at least one error, raise
      ``ExceptionGroup(f"{n} invalid events", errors)`` after processing everything
    - catch only ``InvalidEvent``; no bare ``except:``
    """
    raise NotImplementedError("Implement summarize")
