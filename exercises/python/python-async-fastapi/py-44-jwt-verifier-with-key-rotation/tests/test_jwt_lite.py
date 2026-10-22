import base64
import hashlib
import hmac
import json

import pytest

from jwt_lite import Forbidden, JwtCodec, Principal, Unauthorized, require_scopes

ISS = "https://auth.example"
AUD = "rides-api"
KEY1 = b"a" * 32
KEY2 = b"b" * 32


def b64u(data: bytes) -> str:
    return base64.urlsafe_b64encode(data).rstrip(b"=").decode()


def b64u_decode(text: str) -> bytes:
    return base64.urlsafe_b64decode(text + "=" * (-len(text) % 4))


def compact(obj) -> bytes:
    return json.dumps(obj, separators=(",", ":"), sort_keys=True).encode()


def sign(header: dict, claims, key: bytes = KEY1, alg_hash=hashlib.sha256) -> str:
    """Hand-build a token so tests can craft claims the codec itself would never issue."""
    signing_input = f"{b64u(compact(header))}.{b64u(compact(claims))}"
    mac = hmac.new(key, signing_input.encode(), alg_hash).digest()
    return f"{signing_input}.{b64u(mac)}"


def good_claims(**overrides):
    claims = {"sub": "u1", "iss": ISS, "aud": AUD, "iat": 1000, "exp": 2000, "scope": "rides:read"}
    claims.update(overrides)
    return {k: v for k, v in claims.items() if v is not None}


HEADER = {"alg": "HS256", "typ": "JWT", "kid": "k1"}


class Clock:
    def __init__(self, t: float = 1_000.0) -> None:
        self.t = t

    def __call__(self) -> float:
        return self.t


def codec(clock, keys=None, kid="k1", **kw):
    return JwtCodec(keys or {"k1": KEY1}, active_kid=kid, issuer=ISS, audience=AUD, clock=clock, **kw)


def test_round_trip_and_token_shape():
    c = codec(Clock())
    token = c.issue("u1", ["rides:read", "rides:write"], ttl_s=60)
    p = c.verify(token)
    assert p.sub == "u1" and p.scopes == {"rides:read", "rides:write"}
    assert isinstance(p.scopes, frozenset) and p.claims["exp"] == 1060
    head, body, sig = token.split(".")
    assert "=" not in token, "base64url segments are unpadded"
    assert json.loads(b64u_decode(head)) == {"alg": "HS256", "typ": "JWT", "kid": "k1"}
    claims = json.loads(b64u_decode(body))
    assert claims["iss"] == ISS and claims["aud"] == AUD and claims["iat"] == 1000
    assert claims["scope"] == "rides:read rides:write"
    assert c.verify(c.issue("u2", [])).scopes == frozenset(), "no scopes gives an empty frozenset"


def test_tampering_algorithm_confusion_and_garbage():
    c = codec(Clock())
    token = c.issue("u1", ["rides:read"])
    h, b, s = token.split(".")
    forged = b64u(compact(good_claims(scope="admin")))
    with pytest.raises(Unauthorized, match="signature"):
        c.verify(f"{h}.{forged}.{s}")
    none_head = b64u(compact({"alg": "none", "typ": "JWT", "kid": "k1"}))
    with pytest.raises(Unauthorized, match="alg"):
        c.verify(f"{none_head}.{b}.")
    hs512 = sign({**HEADER, "alg": "HS512"}, good_claims(), alg_hash=hashlib.sha512)
    with pytest.raises(Unauthorized, match="alg"):
        c.verify(hs512)  # a validly signed HS512 token must still be refused: never trust the header's alg
    for junk in ["", "a.b", "a.b.c.d", "!!.!!.!!"]:
        with pytest.raises(Unauthorized, match="malformed"):
            c.verify(junk)


def test_header_and_claims_must_be_json_objects():
    c = codec(Clock())
    list_claims = f"{b64u(compact(HEADER))}.{b64u(b'[]')}.{b64u(b'sig')}"
    list_header = f"{b64u(b'[]')}.{b64u(compact(good_claims()))}.{b64u(b'sig')}"
    not_json = f"{b64u(b'nope')}.{b64u(compact(good_claims()))}.{b64u(b'sig')}"
    for token in (list_claims, list_header, not_json):
        with pytest.raises(Unauthorized, match="malformed"):
            c.verify(token)


def test_issuer_and_audience_checks():
    clock = Clock()
    c = codec(clock)
    other_aud = JwtCodec({"k1": KEY1}, active_kid="k1", issuer=ISS, audience="billing-api", clock=clock)
    other_iss = JwtCodec({"k1": KEY1}, active_kid="k1", issuer="https://evil.example", audience=AUD, clock=clock)
    with pytest.raises(Unauthorized, match="audience"):
        c.verify(other_aud.issue("u1", []))
    with pytest.raises(Unauthorized, match="issuer"):
        c.verify(other_iss.issue("u1", []))
    assert c.verify(sign(HEADER, good_claims(aud=["other-api", AUD]))).sub == "u1", "aud may be a list"
    with pytest.raises(Unauthorized, match="audience"):
        c.verify(sign(HEADER, good_claims(aud=["other-api"])))


def test_missing_required_claims():
    c = codec(Clock())
    for name in ("sub", "iss", "aud", "exp", "iat"):
        token = sign(HEADER, good_claims(**{name: None}))
        with pytest.raises(Unauthorized, match=f"missing {name}"):
            c.verify(token)


def test_expiry_and_leeway():
    clock = Clock()
    c = codec(clock)
    lenient = codec(clock, leeway_s=30)
    t = c.issue("u1", [], ttl_s=60)
    clock.t += 30
    assert c.verify(t).sub == "u1", "still valid before exp"
    clock.t += 31
    with pytest.raises(Unauthorized, match="expired"):
        c.verify(t)
    assert lenient.verify(t).sub == "u1", "leeway keeps an expired token alive for a short time"
    clock.t += 30
    with pytest.raises(Unauthorized, match="expired"):
        lenient.verify(t)


def test_not_before_with_leeway():
    clock = Clock(1000)
    token = sign(HEADER, good_claims(nbf=1100, exp=5000))
    with pytest.raises(Unauthorized, match="not yet valid"):
        codec(clock).verify(token)
    assert codec(clock, leeway_s=120).verify(token).sub == "u1", "leeway tolerates clock skew on nbf"
    clock.t = 1100
    assert codec(clock).verify(token).sub == "u1", "valid once nbf has passed"


def test_key_rotation_overlap_and_unknown_kid():
    clock = Clock()
    old = codec(clock, {"k1": KEY1})
    token = old.issue("u1", ["rides:read"])
    rotated = codec(clock, {"k1": KEY1, "k2": KEY2}, kid="k2")
    assert rotated.verify(token).sub == "u1", "a retired-but-configured kid still verifies"
    new_token = rotated.issue("u2", [])
    assert json.loads(b64u_decode(new_token.split(".")[0]))["kid"] == "k2", "new tokens use the active kid"
    assert rotated.verify(new_token).sub == "u2"
    retired = codec(clock, {"k2": KEY2}, kid="k2")
    with pytest.raises(Unauthorized, match="kid"):
        retired.verify(token)
    with pytest.raises(Unauthorized, match="signature"):
        rotated.verify(sign({**HEADER, "kid": "k2"}, good_claims(), key=KEY1)), "kid k2 must be checked with key k2"


def test_require_scopes_is_403_not_401():
    p = Principal("u1", frozenset({"rides:read"}))
    require_scopes(p, "rides:read")
    require_scopes(p)
    with pytest.raises(Forbidden) as info:
        require_scopes(p, "rides:write", "rides:read", "admin")
    assert str(info.value) == "missing scope: admin rides:write", "list the missing scopes in sorted order"
    assert not issubclass(Forbidden, Unauthorized) and not issubclass(Unauthorized, Forbidden)


def test_constructor_validation_and_principal_equality():
    with pytest.raises(ValueError):
        JwtCodec({"k1": b"x"}, active_kid="nope", issuer="i", audience="a")
    a = Principal("u1", frozenset({"x"}), {"iat": 1})
    b = Principal("u1", frozenset({"x"}), {"iat": 2})
    assert a == b, "claims must be excluded from equality"
    with pytest.raises(Exception):
        a.sub = "u2"  # type: ignore[misc]
