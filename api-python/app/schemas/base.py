"""Shared Pydantic base: camelCase JSON like ASP.NET's default serializer."""

from __future__ import annotations

from datetime import UTC, datetime
from typing import Annotated

from pydantic import BaseModel, ConfigDict, PlainSerializer


def _to_camel(name: str) -> str:
    parts = name.split("_")
    return parts[0] + "".join(p[:1].upper() + p[1:] for p in parts[1:])


def format_dotnet_datetime(value: datetime) -> str:
    """Format like System.Text.Json writes a UTC DateTime: `...Z`, 7-digit fraction when nonzero."""
    if value.tzinfo is None:
        value = value.replace(tzinfo=UTC)
    else:
        value = value.astimezone(UTC)
    # Manual formatting: strftime breaks for years < 1000 (DateTime.MinValue).
    base = (
        f"{value.year:04d}-{value.month:02d}-{value.day:02d}"
        f"T{value.hour:02d}:{value.minute:02d}:{value.second:02d}"
    )
    if value.microsecond:
        return f"{base}.{value.microsecond * 10:07d}Z"
    return f"{base}Z"


DotNetDateTime = Annotated[
    datetime, PlainSerializer(format_dotnet_datetime, return_type=str, when_used="json")
]


class CamelModel(BaseModel):
    model_config = ConfigDict(
        populate_by_name=True,
        alias_generator=_to_camel,
        serialize_by_alias=True,
    )
