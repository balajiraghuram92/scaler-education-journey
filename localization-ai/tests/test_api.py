from tests.conftest import auth_headers


def test_health_is_open(client):
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


def test_run_eval_requires_api_key(client):
    response = client.post("/run-eval", json={"projectSlug": "x", "pipelineConfig": "legacy-only"})
    assert response.status_code == 401
    response = client.post(
        "/run-eval", json={"projectSlug": "x", "pipelineConfig": "legacy-only"}, headers={"x-api-key": "wrong"}
    )
    assert response.status_code == 401


def test_run_eval_legacy_only_shape(db_client):
    response = db_client.post(
        "/run-eval",
        json={"projectSlug": "test-proj", "pipelineConfig": "legacy-only"},
        headers=auth_headers(),
    )
    assert response.status_code == 200
    body = response.json()
    # The unscripted fake answers "{}" (malformed twice), so the judge falls
    # back on both cases: null QPS, fallbackCount 2.
    assert body == {
        "evalRunId": body["evalRunId"],
        "avgCometKiwi": None,
        "avgQpsScore": None,
        "glossaryAdherenceRate": 0.5,
        "placeholderPreservationRate": 1.0,
        "cacheHitRate": 0.0,
        "avgLatencyMs": 0,
        "totalCostUsd": 0.0,
        "tokensUsed": body["tokensUsed"],
        "fallbackCount": 2,
        "promptVersion": "none",
    }
    assert isinstance(body["evalRunId"], int)
    assert body["tokensUsed"] > 0


def test_run_eval_unknown_pipeline_is_400(db_client):
    response = db_client.post(
        "/run-eval", json={"projectSlug": "test-proj", "pipelineConfig": "nope"}, headers=auth_headers()
    )
    assert response.status_code == 400
    assert "legacy-only" in response.json()["detail"]


def test_run_eval_unknown_project_is_404(db_client):
    response = db_client.post(
        "/run-eval", json={"projectSlug": "nope", "pipelineConfig": "legacy-only"}, headers=auth_headers()
    )
    assert response.status_code == 404
