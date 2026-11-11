"""HTTP tests for the four Part F.2 pipeline endpoints (fake providers)."""

import asyncio
import json

from fastapi.testclient import TestClient

import app.main
from app import db as db_module
from app.providers.fake import FakeChatProvider, FakeEmbeddingProvider
from tests.conftest import auth_headers, make_settings


def _client_for(conninfo: str, chat: FakeChatProvider):
    pool = db_module.create_pool(conninfo)
    asyncio.run(pool.open())
    asyncio.run(pool.wait())
    application = app.main.build_app(
        make_settings(database_url=conninfo),
        pool=pool,
        chat_provider=chat,
        embedding_provider=FakeEmbeddingProvider(),
    )
    return TestClient(application), pool


def test_translate_and_optimize_success_and_cache_hit(seeded_project_id):
    conninfo, _ = seeded_project_id
    chat = FakeChatProvider(responses=[json.dumps({"optimized_translation": "Links abbiegen"})])
    client, pool = _client_for(conninfo, chat)
    try:
        body = {
            "rawMtText": "Drehe links",
            "sourceText": "Turn left",
            "targetLocale": "de-DE",
            "projectSlug": "test-proj",
            "glossaryTerms": [{"source": "Turn left", "target": "Links abbiegen"}],
        }
        first = client.post("/translate-and-optimize", json=body, headers=auth_headers())
        assert first.status_code == 200, first.text
        data = first.json()
        assert data["optimizedTranslation"] == "Links abbiegen"
        assert data["cacheHit"] is False
        assert data["checks"]["glossary_present"] is True
        assert data["fallback"] is False
        assert data["tokensUsed"] == data["inputTokens"] + data["outputTokens"] + data["embeddingTokens"]
        assert data["embeddingTokens"] > 0

        # Same source: served from the semantic cache, chat untouched again.
        second = client.post("/translate-and-optimize", json=body, headers=auth_headers())
        assert second.status_code == 200
        assert second.json()["cacheHit"] is True
        assert second.json()["optimizedTranslation"] == "Links abbiegen"
        assert len(chat.calls) == 1
    finally:
        asyncio.run(pool.close())


def test_translate_and_optimize_falls_back_on_malformed(seeded_project_id):
    conninfo, _ = seeded_project_id
    chat = FakeChatProvider(responses=["nope", "still nope"])
    client, pool = _client_for(conninfo, chat)
    try:
        response = client.post(
            "/translate-and-optimize",
            json={
                "rawMtText": "Rohe MT",
                "sourceText": "Turn left",
                "targetLocale": "de-DE",
                "projectSlug": "test-proj",
                "glossaryTerms": [],
            },
            headers=auth_headers(),
        )
        assert response.status_code == 200
        data = response.json()
        assert (data["optimizedTranslation"], data["fallback"]) == ("Rohe MT", True)
    finally:
        asyncio.run(pool.close())


def test_translate_and_optimize_unknown_project_is_404(seeded_project_id):
    conninfo, _ = seeded_project_id
    client, pool = _client_for(conninfo, FakeChatProvider())
    try:
        response = client.post(
            "/translate-and-optimize",
            json={
                "rawMtText": "x",
                "sourceText": "Turn left",
                "targetLocale": "de-DE",
                "projectSlug": "nope",
                "glossaryTerms": [],
            },
            headers=auth_headers(),
        )
        assert response.status_code == 404
    finally:
        asyncio.run(pool.close())


def test_qps_score_success_and_fallback(client):
    # The shared `client` fixture has an unscripted fake: "{}" is malformed
    # twice, so this exercises the fallback path through HTTP.
    response = client.post(
        "/qps-score",
        json={"sourceText": "Turn left", "targetText": "Links abbiegen", "targetLocale": "de-DE"},
        headers=auth_headers(),
    )
    assert response.status_code == 200
    data = response.json()
    assert (data["score"], data["fallback"]) == (None, True)
    assert data["flaggedIssues"] == []
    assert data["tokensUsed"] == data["inputTokens"] + data["outputTokens"]


def test_comet_score_unavailable_without_scorer(client):
    response = client.post(
        "/comet-score",
        json={"sourceText": "Turn left", "targetText": "Links abbiegen", "targetLocale": "de-DE"},
        headers=auth_headers(),
    )
    assert response.status_code == 200
    data = response.json()
    assert data["score"] is None
    assert data["available"] is False
    assert (data["tokensUsed"], data["fallback"]) == (0, False)
    assert data["latencyMs"] >= 0


def test_auto_route_through_http(client):
    response = client.post(
        "/auto-route",
        json={"qpsScore": 60, "projectThreshold": 70, "checks": {"glossary_present": True}},
        headers=auth_headers(),
    )
    assert response.status_code == 200
    data = response.json()
    assert (data["needsReview"], data["reasons"]) == (True, ["qps_below_threshold"])
    assert (data["tokensUsed"], data["fallback"]) == (0, False)


def test_pipeline_endpoints_require_api_key(client):
    assert client.post("/qps-score", json={}).status_code == 401
    assert client.post("/comet-score", json={}).status_code == 401
    assert client.post("/auto-route", json={}).status_code == 401
    assert client.post("/translate-and-optimize", json={}).status_code == 401
