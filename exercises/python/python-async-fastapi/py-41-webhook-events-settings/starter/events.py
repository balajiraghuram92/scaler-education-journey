import json
from dataclasses import dataclass
from datetime import datetime
from typing import Annotated, Literal

from pydantic import (
    BaseModel,
    ConfigDict,
    Field,
    SecretStr,
    TypeAdapter,
    ValidationError,
    field_validator,
)
from pydantic_settings import BaseSettings, SettingsConfigDict


class _EventBase(BaseModel):
    """Frozen base model. Fields: id (non-empty str), created (datetime)."""


class PaymentSucceeded(_EventBase):
    """type: Literal["payment.succeeded"]; amount_cents: int > 0; currency: Literal["USD", "EUR", "INR"]."""


class PaymentFailed(_EventBase):
    """type: Literal["payment.failed"]; reason: str."""


class RefundIssued(_EventBase):
    """type: Literal["refund.issued"]; amount_cents: int > 0; original_event_id: str."""


AnyEvent = PaymentSucceeded | PaymentFailed | RefundIssued
# TODO: Event = Annotated[AnyEvent, Field(discriminator="type")]
# TODO: build the TypeAdapters once, at module level (one for a single event, one for list[Event])


@dataclass(frozen=True)
class ItemError:
    index: int
    type: str  # the Pydantic error type code, e.g. "union_tag_invalid"
    loc: tuple[str | int, ...]
    msg: str


def parse_events(raw: bytes) -> list[AnyEvent]:
    """Strict: validate the whole JSON array with ``validate_json``.

    Any bad item raises ``ValidationError`` whose first error location starts with the item's index.
    """
    raise NotImplementedError("Implement parse_events")


def parse_events_lenient(raw: bytes) -> tuple[list[AnyEvent], list[ItemError]]:
    """Lenient: validate item by item. Return the valid events plus one ItemError per Pydantic
    error (with the item's index). A payload that is not a JSON array raises ``ValueError``.
    """
    raise NotImplementedError("Implement parse_events_lenient")


class WebhookSettings(BaseSettings):
    """Settings read from the environment (prefix ``WEBHOOK_``) and an optional ``.env`` file.

    - unknown keys in the env file are ignored (``extra="ignore"``)
    - secret: SecretStr, validated to be at least 8 characters with a field validator
    - tolerance_s: int, default 300, > 0 and <= 3600
    """
