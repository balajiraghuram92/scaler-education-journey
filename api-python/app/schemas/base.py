"""Shared Pydantic base: camelCase JSON like ASP.NET's default serializer."""

from __future__ import annotations

from datetime import UTC, datetime
from decimal import Decimal
from typing import Annotated

from pydantic import BaseModel, ConfigDict, PlainSerializer


def _to_camel(name: str) -> str:
    parts = name.split("_")
    return parts[0] + "".join(p[:1].upper() + p[1:] for p in parts[1:])


def format_dotnet_datetime(value: datetime) -> str:
    """Format like System.Text.Json writes a DateTime: aware values convert to UTC with `Z`; naive values (the port's `Kind = Unspecified`) are written as-is with no suffix. Fractions strip trailing zeros."""
    suffix = "Z"
    if value.tzinfo is None:
        suffix = ""
    else:
        value = value.astimezone(UTC)
    # Manual formatting: strftime breaks for years < 1000 (DateTime.MinValue).
    base = (
        f"{value.year:04d}-{value.month:02d}-{value.day:02d}"
        f"T{value.hour:02d}:{value.minute:02d}:{value.second:02d}"
    )
    if value.microsecond:
        fraction = f"{value.microsecond:06d}".rstrip("0")
        return f"{base}.{fraction}{suffix}"
    return f"{base}{suffix}"


DotNetDateTime = Annotated[
    datetime, PlainSerializer(format_dotnet_datetime, return_type=str, when_used="json")
]


def _decimal_to_json_number(value: Decimal) -> float:
    """System.Text.Json writes a C# decimal as a JSON number; Pydantic would use a string."""
    return float(value)


DotNetDecimal = Annotated[
    Decimal, PlainSerializer(_decimal_to_json_number, return_type=float, when_used="json")
]


class CamelModel(BaseModel):
    model_config = ConfigDict(
        populate_by_name=True,
        alias_generator=_to_camel,
        serialize_by_alias=True,
    )
