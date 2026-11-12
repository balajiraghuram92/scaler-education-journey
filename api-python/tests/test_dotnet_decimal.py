"""DotNetDecimal serialises as a JSON number, like System.Text.Json (no database)."""

from __future__ import annotations

import json
from datetime import UTC, datetime
from decimal import Decimal
from uuid import uuid4

from app.schemas.chat_dtos import ChatMessageDto
from app.schemas.localization_dtos import ProviderRateDto, UsageMeterTotalDto


def test_localization_decimals_dump_as_json_numbers() -> None:
    rate = ProviderRateDto(
        id=1,
        meter="llm-score",
        unit_kind="input-token",
        usd_per_million=Decimal("2.00"),
        valid_from=datetime.now(UTC),
    )
    total = UsageMeterTotalDto(
        meter="llm-score",
        calls=3,
        failed_calls=0,
        cache_hits=0,
        units=100,
        units_out=8,
        cost_usd=Decimal("0.42"),
    )
    rate_data = json.loads(rate.model_dump_json())
    assert isinstance(rate_data["usdPerMillion"], float)
    assert rate_data["usdPerMillion"] == 2.0
    total_data = json.loads(total.model_dump_json())
    assert isinstance(total_data["costUsd"], float)
    assert total_data["costUsd"] == 0.42


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
