from datetime import UTC, datetime, timedelta

import jwt
import pytest

from conftest import TEST_KEY, bearer, make_token


def test_valid_bearer_token_returns_claims(client):
    response = client.get("/me", headers=bearer(make_token()))
    assert response.status_code == 200
    assert response.json()["nameid"] == "42"


def test_valid_cookie_token(client):
    client.cookies.set("na_auth", make_token())
    assert client.get("/me").status_code == 200


def test_missing_token(client):
    response = client.get("/me")
    assert response.status_code == 401
    assert response.headers["www-authenticate"] == "Bearer"


@pytest.mark.parametrize(
    "token",
    [
        pytest.param(make_token(exp=datetime.now(UTC) - timedelta(minutes=1)), id="expired"),
        pytest.param(make_token(iss="someone-else"), id="wrong-issuer"),
        pytest.param(make_token(aud="other-app"), id="wrong-audience"),
        pytest.param(make_token(exp=None), id="missing-exp"),
        pytest.param(make_token(iss=None), id="missing-iss"),
        pytest.param(make_token(aud=None), id="missing-aud"),
        pytest.param(make_token(key="x" * 40), id="wrong-key"),
        pytest.param(
            jwt.encode(
                {"iss": "neuralascent", "aud": "neuralascent-app", "exp": datetime.now(UTC) + timedelta(minutes=5)},
                None,
                algorithm="none",
            ),
            id="alg-none",
        ),
        pytest.param(make_token(key=TEST_KEY) + "tampered", id="bad-signature"),
        pytest.param("not-a-jwt", id="garbage"),
    ],
)
def test_rejected_tokens(client, token):
    response = client.get("/me", headers=bearer(token))
    assert response.status_code == 401
    assert response.json() == {"detail": "Invalid or expired token"}
