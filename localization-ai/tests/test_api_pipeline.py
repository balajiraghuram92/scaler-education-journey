"""HTTP tests for the four Part F.2 pipeline endpoints (fake providers)."""

import contextlib
import json

from fastapi.testclient import TestClient

import app.main
from app import db as db_module
from app.providers.fake import FakeChatProvider, FakeEmbeddingProvider
from tests.conftest import auth_headers, make_settings


@contextlib.contextmanager
def _client_for(conninfo: str, chat: FakeChatProvider):
    # Unopened: entering the TestClient opens the pool on the client's own
    # loop via lifespan, and leaving it closes the pool.
    pool = db_module.create_pool(conninfo)
    application = app.main.build_app(
        make_settings(database_url=conninfo),
        pool=pool,
        chat_provider=chat,
        embedding_provider=FakeEmbeddingProvider(),
    )
    with TestClient(application) as client:
        yield client


def test_translate_and_optimize_success_and_cache_hit(seeded_project_id):
    conninfo, _ = seeded_project_id
    chat = FakeChatProvider(responses=[json.dumps({"optimized_translation": "Links abbiegen"})])
    with _client_for(conninfo, chat) as client:
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
        assert data["operation"] == "mt-optimize"
        assert data["model"] == "fake-chat"
        assert data["promptVersion"] == "mt-optimize-v1"
        assert data["tokensUsed"] == data["inputTokens"] + data["outputTokens"] + data["embeddingTokens"]
        assert data["embeddingTokens"] > 0

        # Same source: served from the semantic cache, chat untouched again.
        second = client.post("/translate-and-optimize", json=body, headers=auth_headers())
        assert second.status_code == 200
        assert second.json()["cacheHit"] is True
        assert second.json()["optimizedTranslation"] == "Links abbiegen"
        assert len(chat.calls) == 1


def test_translate_and_optimize_falls_back_on_malformed(seeded_project_id):
    conninfo, _ = seeded_project_id
    chat = FakeChatProvider(responses=["nope", "still nope"])
    with _client_for(conninfo, chat) as client:
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


def test_translate_and_optimize_unknown_project_is_404(seeded_project_id):
    conninfo, _ = seeded_project_id
    with _client_for(conninfo, FakeChatProvider()) as client:
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


def test_qps_score_success_returns_new_fields(seeded_project_id):
    conninfo, _ = seeded_project_id
    chat = FakeChatProvider(
        responses=[json.dumps({"score": 4, "reason": "scripted", "flagged_issues": []})]
    )
    with _client_for(conninfo, chat) as client:
        response = client.post(
            "/qps-score",
            json={"sourceText": "Turn left", "targetText": "Links abbiegen", "targetLocale": "de-DE"},
            headers=auth_headers(),
        )
        assert response.status_code == 200
        data = response.json()
        assert data["score"] == 4
        assert data["vetoed"] is False
        assert data["fallback"] is False
        assert data["operation"] == "qps-score"
        assert data["model"] == "fake-chat"
        assert data["promptVersion"] == "qps_judge_v2"
        assert data["tokensUsed"] == data["inputTokens"] + data["outputTokens"]


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
    assert data["vetoed"] is False
    assert data["operation"] == "qps-score"
    assert data["model"] == "fake-chat"
    assert data["promptVersion"] == "qps_judge_v2"
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
        json={"qpsScore": 3, "projectThreshold": 4, "checks": {"glossary_present": True}},
        headers=auth_headers(),
    )
    assert response.status_code == 200
    data = response.json()
    assert (data["needsReview"], data["reasons"]) == (True, ["qps_below_threshold"])
    assert (data["tokensUsed"], data["fallback"]) == (0, False)


def test_auto_route_at_threshold_passes_and_out_of_range_is_422(client):
    at_threshold = client.post(
        "/auto-route", json={"qpsScore": 4, "projectThreshold": 4}, headers=auth_headers()
    )
    assert at_threshold.status_code == 200
    assert (at_threshold.json()["needsReview"], at_threshold.json()["reasons"]) == (False, [])

    for body in ({"qpsScore": 87, "projectThreshold": 4}, {"qpsScore": 4, "projectThreshold": 87}):
        response = client.post("/auto-route", json=body, headers=auth_headers())
        assert response.status_code == 422


def test_pipeline_endpoints_require_api_key(client):
    assert client.post("/qps-score", json={}).status_code == 401
    assert client.post("/comet-score", json={}).status_code == 401
    assert client.post("/auto-route", json={}).status_code == 401
    assert client.post("/translate-and-optimize", json={}).status_code == 401
