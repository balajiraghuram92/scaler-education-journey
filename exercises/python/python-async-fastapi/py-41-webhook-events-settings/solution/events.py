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
    model_config = ConfigDict(frozen=True)

    id: str = Field(min_length=1)
    created: datetime


class PaymentSucceeded(_EventBase):
    type: Literal["payment.succeeded"]
    amount_cents: int = Field(gt=0)
    currency: Literal["USD", "EUR", "INR"]


class PaymentFailed(_EventBase):
    type: Literal["payment.failed"]
    reason: str


class RefundIssued(_EventBase):
    type: Literal["refund.issued"]
    amount_cents: int = Field(gt=0)
    original_event_id: str


AnyEvent = PaymentSucceeded | PaymentFailed | RefundIssued
Event = Annotated[AnyEvent, Field(discriminator="type")]

_EVENT = TypeAdapter(Event)  # built once, at import time
_EVENTS = TypeAdapter(list[Event])


@dataclass(frozen=True)
class ItemError:
    index: int
    type: str
    loc: tuple[str | int, ...]
    msg: str


def parse_events(raw: bytes) -> list[AnyEvent]:
    """Strict: the whole batch is valid or ValidationError is raised."""
    return _EVENTS.validate_json(raw)


def parse_events_lenient(raw: bytes) -> tuple[list[AnyEvent], list[ItemError]]:
    """Lenient: valid events are returned, invalid items are reported by index."""
    data = json.loads(raw)
    if not isinstance(data, list):
        raise ValueError("payload must be a JSON array")
    good: list[AnyEvent] = []
    errors: list[ItemError] = []
    for index, item in enumerate(data):
        try:
            good.append(_EVENT.validate_python(item))
        except ValidationError as exc:
            for err in exc.errors(include_url=False):
                errors.append(
                    ItemError(index=index, type=err["type"], loc=tuple(err["loc"]), msg=err["msg"])
                )
    return good, errors


class WebhookSettings(BaseSettings):
    model_config = SettingsConfigDict(env_prefix="WEBHOOK_", env_file=".env", extra="ignore")

    secret: SecretStr
    tolerance_s: int = Field(default=300, gt=0, le=3600)

    @field_validator("secret")
    @classmethod
    def secret_is_long_enough(cls, v: SecretStr) -> SecretStr:
        if len(v.get_secret_value()) < 8:
            raise ValueError("secret must be at least 8 characters")
        return v
