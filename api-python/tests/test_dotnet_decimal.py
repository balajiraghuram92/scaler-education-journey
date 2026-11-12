"""DotNetDecimal serialises as a JSON number, like System.Text.Json (no database)."""

from __future__ import annotations

import json
from datetime import UTC, datetime
from decimal import Decimal
from uuid import uuid4

from app.schemas.chat_dtos import ChatMessageDto
from app.schemas.localization_dtos import MarketplaceJobDto


def test_localization_decimals_dump_as_json_numbers() -> None:
    dto = MarketplaceJobDto(
        id=1,
        project_id=2,
        locale_code="de-DE",
        status="Open",
        string_count=10,
        word_count=50,
        suggested_price_low=Decimal("140.00"),
        suggested_price_high=Decimal("210.50"),
        awarded_vendor_id=None,
        awarded_vendor_name=None,
        posted_at=None,
        awarded_at=None,
        submitted_at=None,
        approved_at=None,
        bids=[],
    )
    data = json.loads(dto.model_dump_json())
    assert isinstance(data["suggestedPriceLow"], float)
    assert isinstance(data["suggestedPriceHigh"], float)
    assert data["suggestedPriceLow"] == 140.0
    assert data["suggestedPriceHigh"] == 210.5


def test_chat_decimals_dump_as_json_numbers() -> None:
    dto = ChatMessageDto(
        id=uuid4(),
        conversation_id=uuid4(),
        role="assistant",
        content="hi",
        client_request_id=None,
        prompt_tokens=None,
        completion_tokens=None,
        usage_estimated=False,
        estimated_cost_usd=Decimal("0.000001"),
        latency_ms=None,
        created_at=datetime.now(UTC),
    )
    data = json.loads(dto.model_dump_json())
    assert isinstance(data["estimatedCostUsd"], float)
    assert data["estimatedCostUsd"] == 0.000001


def test_optional_decimal_none_dumps_as_null() -> None:
    dto = ChatMessageDto(
        id=uuid4(),
        conversation_id=uuid4(),
        role="assistant",
        content="hi",
        client_request_id=None,
        prompt_tokens=None,
        completion_tokens=None,
        usage_estimated=False,
        estimated_cost_usd=None,
        latency_ms=None,
        created_at=datetime.now(UTC),
    )
    data = json.loads(dto.model_dump_json())
    assert data["estimatedCostUsd"] is None
