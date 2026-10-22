from datetime import datetime
from decimal import ROUND_HALF_UP, Decimal
from typing import Literal, Self
from uuid import UUID, uuid4

from pydantic import BaseModel, ConfigDict, Field, computed_field, field_validator, model_validator
from pydantic.alias_generators import to_camel

Currency = Literal["USD", "EUR", "INR", "JPY"]


class _Base(BaseModel):
    model_config = ConfigDict(
        alias_generator=to_camel,
        populate_by_name=True,
        extra="forbid",
        frozen=True,
    )


class InvoiceLine(_Base):
    sku: str = Field(pattern=r"^[A-Z]{3}-\d{4}$")
    qty: int = Field(gt=0, strict=True)
    unit_price: Decimal = Field(ge=0, max_digits=12, decimal_places=2)


class Invoice(_Base):
    id: UUID = Field(default_factory=uuid4)
    currency: Currency
    lines: list[InvoiceLine] = Field(min_length=1)
    discount_pct: Decimal = Field(default=Decimal("0"), ge=0, le=100)
    issued_at: datetime

    @field_validator("issued_at")
    @classmethod
    def must_be_timezone_aware(cls, v: datetime) -> datetime:
        if v.utcoffset() is None:
            raise ValueError("issued_at must be timezone-aware")
        return v

    @model_validator(mode="after")
    def jpy_has_no_minor_units(self) -> Self:
        if self.currency == "JPY" and any(
            line.unit_price != line.unit_price.to_integral_value() for line in self.lines
        ):
            raise ValueError("JPY prices must be whole numbers")
        return self

    @computed_field
    @property
    def subtotal(self) -> Decimal:
        return sum((line.qty * line.unit_price for line in self.lines), start=Decimal("0"))

    @computed_field
    @property
    def total(self) -> Decimal:
        net = self.subtotal * (Decimal(100) - self.discount_pct) / Decimal(100)
        return net.quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)
