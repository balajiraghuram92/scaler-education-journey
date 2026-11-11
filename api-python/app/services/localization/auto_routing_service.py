"""Ported from api/Services/Localization/AutoRoutingService.cs.

Thin client over the localization-ai /auto-route endpoint.
Contains no threshold or routing logic; that stays in the Python service.
"""

from __future__ import annotations

from .localization_ai_client import NOT_CONFIGURED_MESSAGE, LocalizationAiClient


class AutoRoutingService:
    def __init__(self, client: LocalizationAiClient | None = None) -> None:
        self._client = client

    async def should_route_to_review_async(
        self, qps_score: int, project_threshold: int
    ) -> bool:
        if self._client is None:
            raise NotImplementedError(NOT_CONFIGURED_MESSAGE)
        response = await self._client.auto_route_async(
            qps_score, project_threshold, None
        )
        return response.needs_review
