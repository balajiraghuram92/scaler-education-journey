# Authentication and Security for FastAPI Services

Authentication bugs are rarely cryptographic. They are an endpoint that forgot to check ownership, a CORS config that reflects every origin, a refresh token that never rotates, or a password hash that blocks the event loop. In an AI or FDE interview you will be asked to secure an LLM gateway or a tenant-facing API, and the strong answer names the threat, the mechanism that stops it, and the way it fails in production.

## Concepts Covered

### OAuth2 bearer tokens and scopes in FastAPI

`OAuth2PasswordBearer(tokenUrl=...)` does two jobs: at runtime it extracts the token from the `Authorization: Bearer` header (returning `401` with `WWW-Authenticate: Bearer` when it is absent), and in OpenAPI it advertises the flow so `/docs` gets an Authorize button. It does not validate anything. Validation lives in your own dependency, and `Security(...)` is `Depends(...)` plus a list of required scopes that the dependency receives as `SecurityScopes`. The login endpoint that issues tokens takes `OAuth2PasswordRequestForm`, which needs the `python-multipart` package installed.

```python
from dataclasses import dataclass
from typing import Annotated

from fastapi import Depends, FastAPI, HTTPException, Security, status
from fastapi.security import OAuth2PasswordBearer, SecurityScopes

oauth2_scheme = OAuth2PasswordBearer(
    tokenUrl="auth/token",
    scopes={"rides:read": "Read rides", "rides:write": "Create and cancel rides"},
)


@dataclass
class Principal:
    sub: str
    scopes: frozenset[str]


def decode_access_token(token: str) -> Principal | None:
    ...  # verify signature, exp, iss, aud (see the JWT section); return None if invalid


async def get_principal(
    security_scopes: SecurityScopes, token: Annotated[str, Depends(oauth2_scheme)]
) -> Principal:
    challenge = f'Bearer scope="{security_scopes.scope_str}"' if security_scopes.scopes else "Bearer"
    principal = decode_access_token(token)
    if principal is None:
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, "Invalid token", headers={"WWW-Authenticate": challenge})
    missing = set(security_scopes.scopes) - principal.scopes
    if missing:
        raise HTTPException(
            status.HTTP_403_FORBIDDEN, f"Missing scope: {' '.join(sorted(missing))}",
            headers={"WWW-Authenticate": challenge},
        )
    return principal


app = FastAPI()


@app.post("/rides")
async def create_ride(p: Annotated[Principal, Security(get_principal, scopes=["rides:write"])]):
    return {"created_by": p.sub}
```

Run against a stub decoder, a token holding only `rides:read` gets `403` with `WWW-Authenticate: Bearer scope="rides:write"`, a missing token gets `401`, and a token with both scopes succeeds. Keep the distinction straight: `401` means "I do not know who you are", `403` means "I know, and the answer is no".

### What a JWT actually is

A JWT is `base64url(header).base64url(claims).base64url(signature)`. The payload is encoded, not encrypted: anyone holding the token can read it. Security comes from verification: recompute the signature, compare in constant time, then check `exp`, `iss` and `aud`. This stdlib implementation of HS256 shows exactly what a library like PyJWT does, and the three classic attacks it must refuse.

```python
import base64
import hashlib
import hmac
import json


def b64u(data: bytes) -> str:
    return base64.urlsafe_b64encode(data).rstrip(b"=").decode()


def b64u_decode(text: str) -> bytes:
    return base64.urlsafe_b64decode(text + "=" * (-len(text) % 4))


def compact(obj: dict) -> bytes:
    return json.dumps(obj, separators=(",", ":"), sort_keys=True).encode()


class InvalidToken(Exception):
    pass


def sign(claims: dict, key: bytes, *, now: int, ttl: int = 900) -> str:
    header = {"alg": "HS256", "typ": "JWT"}
    body = {**claims, "iat": now, "exp": now + ttl}
    signing_input = f"{b64u(compact(header))}.{b64u(compact(body))}"
    sig = hmac.new(key, signing_input.encode(), hashlib.sha256).digest()
    return f"{signing_input}.{b64u(sig)}"


def verify(token: str, key: bytes, *, now: int) -> dict:
    try:
        head_b64, body_b64, sig_b64 = token.split(".")
        header = json.loads(b64u_decode(head_b64))
        claims = json.loads(b64u_decode(body_b64))
    except ValueError as exc:
        raise InvalidToken("malformed") from exc
    if header.get("alg") != "HS256":  # pin the algorithm; never trust the header
        raise InvalidToken("unexpected alg")
    expected = hmac.new(key, f"{head_b64}.{body_b64}".encode(), hashlib.sha256).digest()
    if not hmac.compare_digest(expected, b64u_decode(sig_b64)):
        raise InvalidToken("bad signature")
    if claims["exp"] <= now:
        raise InvalidToken("expired")
    return claims


KEY = b"dev-only-secret-change-me-32-bytes!"
token = sign({"sub": "user-42", "scope": "rides:read"}, KEY, now=1_000)
print(len(token.split(".")))
print(json.loads(b64u_decode(token.split(".")[1])))
print(verify(token, KEY, now=1_100)["sub"])

head, body, sig = token.split(".")
forged_body = b64u(compact({"sub": "user-42", "scope": "admin", "iat": 1000, "exp": 1900}))
for label, candidate in {
    "tampered": f"{head}.{forged_body}.{sig}",
    "alg none": f"{b64u(compact({'alg': 'none', 'typ': 'JWT'}))}.{body}.",
    "expired": token,
}.items():
    try:
        verify(candidate, KEY, now=5_000 if label == "expired" else 1_100)
    except InvalidToken as exc:
        print(label, "->", exc)
```

Output:

```text
3
{'exp': 1900, 'iat': 1000, 'scope': 'rides:read', 'sub': 'user-42'}
user-42
tampered -> bad signature
alg none -> unexpected alg
expired -> expired
```

With PyJWT the equivalent is `jwt.decode(token, key, algorithms=["HS256"], audience="rides-api", issuer="https://auth.example.com", options={"require": ["exp", "iat", "sub", "iss", "aud"]})`. The `algorithms` list is mandatory for a reason: accepting whatever the header says enables `alg: none` and, with asymmetric keys, HS256/RS256 key-confusion attacks. Catch `jwt.InvalidTokenError`, the base class for expiry, signature and claim failures. Use HS256 only when one service both issues and verifies; use RS256 or EdDSA with a JWKS endpoint when many services verify, and put a `kid` header on tokens so keys can rotate with an overlap window.

### Access and refresh tokens with rotation

Short-lived access tokens (5 to 15 minutes) limit the damage of a leak, because JWTs cannot be revoked individually without server-side state. A longer-lived refresh token obtains new access tokens. Store refresh tokens server-side (hashed), and **rotate** them: each use invalidates the presented token and issues a new one in the same family. If an already-used token appears again, someone is replaying a stolen copy, so revoke the entire family and force re-login.

```python
class ReuseDetected(Exception):
    pass


class RefreshStore:
    def __init__(self) -> None:
        self._tokens: dict[str, str] = {}      # token id -> family id
        self._used: set[str] = set()
        self._revoked_families: set[str] = set()
        self._n = 0

    def _new(self, family: str) -> str:
        self._n += 1
        tid = f"r{self._n}"
        self._tokens[tid] = family
        return tid

    def login(self, user: str) -> str:
        return self._new(f"fam:{user}")

    def rotate(self, tid: str) -> str:
        family = self._tokens.get(tid)
        if family is None or family in self._revoked_families:
            raise PermissionError("invalid refresh token")
        if tid in self._used:
            self._revoked_families.add(family)
            raise ReuseDetected(f"{tid} replayed; family {family} revoked")
        self._used.add(tid)
        return self._new(family)


s = RefreshStore()
r1 = s.login("alice")
r2 = s.rotate(r1)
r3 = s.rotate(r2)
print(r1, r2, r3)
try:
    s.rotate(r1)
except ReuseDetected as exc:
    print("ReuseDetected:", exc)
try:
    s.rotate(r3)
except PermissionError as exc:
    print("PermissionError:", exc)
```

This prints `r1 r2 r3`, then `ReuseDetected: r1 replayed; family fam:alice revoked`, then `PermissionError: invalid refresh token`: the legitimate holder of `r3` is logged out too, which is the intended trade-off. In production the store is a database or Redis table, rotation must be atomic (a compare-and-set, otherwise two concurrent refreshes both succeed), and a short grace window is sometimes allowed so a flaky mobile network does not log users out.

### Cookies versus bearer headers, and CSRF

| | Cookie (HttpOnly) | Bearer in `Authorization` |
|---|---|---|
| XSS can read the token | No (HttpOnly) | Yes if kept in `localStorage` |
| CSRF exposure | Yes, the browser attaches it automatically | No, JavaScript must attach it |
| Best fit | Browser apps on your own domain | Mobile apps, service-to-service, third-party clients |
| Extra defence needed | SameSite, Origin check or CSRF token | Strict CSP, short TTL |

For a first-party browser app prefer an HttpOnly, Secure, SameSite cookie. With the `__Host-` prefix the browser additionally enforces `Secure`, `Path=/` and no `Domain`, which blocks sibling-subdomain cookie injection.

```python
from fastapi import Response


@app.post("/login")
async def login(response: Response):
    response.set_cookie(
        "__Host-session", "opaque-session-id",
        max_age=3600, httponly=True, secure=True, samesite="lax", path="/",
    )
    return {}
```

The header emitted is `__Host-session=...; HttpOnly; Max-Age=3600; Path=/; SameSite=lax; Secure`. `SameSite=Lax` stops cross-site POSTs from carrying the cookie, but it does not cover same-site attackers (a compromised sibling subdomain) or older clients. Add a defence for state-changing requests: verify the `Origin` header against an allowlist, or use a double-submit CSRF token. CORS is not CSRF protection: a cross-origin form POST is still sent, CORS only controls whether the response is readable.

### Password hashing

Use a memory-hard, salted, adaptive hash: argon2id (the `argon2-cffi` package) or bcrypt. Plain SHA-256 is far too fast to resist GPU cracking. Hashing is deliberately CPU-expensive, so run it in a thread, and spend the same time when the user does not exist so response timing does not reveal valid emails.

```python
from argon2 import PasswordHasher
from argon2.exceptions import InvalidHashError, VerifyMismatchError
from fastapi.concurrency import run_in_threadpool

ph = PasswordHasher()  # argon2id with library defaults
DUMMY_HASH = ph.hash("not-a-real-password")


async def check_password(stored_hash: str | None, password: str) -> bool:
    candidate = stored_hash or DUMMY_HASH  # equalise timing for unknown users
    try:
        await run_in_threadpool(ph.verify, candidate, password)
    except (VerifyMismatchError, InvalidHashError):
        return False
    return stored_hash is not None


def needs_upgrade(stored_hash: str) -> bool:
    return ph.check_needs_rehash(stored_hash)  # rehash on next successful login
```

bcrypt silently truncates input at 72 bytes, so pre-hash or cap long passphrases. Passlib is unmaintained and breaks with recent bcrypt releases, which is why current FastAPI documentation moved to `pwdlib`.

### CORS misconfiguration

CORS is a browser-enforced relaxation of the same-origin policy, set by `CORSMiddleware`. Typical mistakes: `allow_origins=["*"]` combined with `allow_credentials=True` (browsers reject `*` with credentials, and servers that "fix" it by reflecting the request's Origin become open to every site; Starlette does exactly that, answering a cookie-bearing request from `https://evil.example` with that origin and `access-control-allow-credentials: true`), regex origins that match `evil-example.com`, and adding the middleware before others, so a response returned directly by a later middleware (a rate limiter's `429`) never passes through it and lacks CORS headers. Also note that an unhandled exception produces a `500` from Starlette's outermost error layer, outside `CORSMiddleware`, so the browser reports a misleading CORS error for a crash. List exact origins per environment from settings.

```python
from fastapi.middleware.cors import CORSMiddleware

app.add_middleware(
    CORSMiddleware,
    allow_origins=["https://app.example.com"],
    allow_credentials=True,
    allow_methods=["GET", "POST"],
    allow_headers=["Authorization", "Content-Type"],
    max_age=600,
)
```

With this configuration a preflight from `https://app.example.com` returns `200` with the origin echoed, while one from `https://evil.example` returns `400 Disallowed CORS origin`. Remember that non-browser clients ignore CORS entirely, so it never replaces authentication.

### Rate limiting, secrets and OWASP API risks

Rate limiting protects both availability and your bill (every LLM call costs money). Key limits by authenticated principal or API key before IP, since NAT puts thousands of users behind one address and behind a proxy you must trust forwarded headers only from known proxies (uvicorn's `--forwarded-allow-ips`). A token bucket allows bursts and a steady rate:

```python
import math


class TokenBucket:
    def __init__(self, capacity: float, refill_per_s: float, now: float) -> None:
        self.capacity, self.rate = capacity, refill_per_s
        self.tokens, self.updated = capacity, now

    def allow(self, now: float, cost: float = 1.0) -> tuple[bool, float]:
        self.tokens = min(self.capacity, self.tokens + (now - self.updated) * self.rate)
        self.updated = now
        if self.tokens >= cost:
            self.tokens -= cost
            return True, 0.0
        return False, math.ceil((cost - self.tokens) / self.rate)


b = TokenBucket(capacity=3, refill_per_s=1, now=0.0)
for t in [0.0, 0.1, 0.2, 0.3, 1.3, 1.4, 5.0]:
    ok, retry = b.allow(t)
    print(f"t={t:<4} allowed={ok!s:5} retry_after={retry:.0f}")
```

The first three calls pass, the fourth at `t=0.3` is refused with `retry_after=1`, `t=1.3` passes after a refill, `t=1.4` is refused again, and by `t=5.0` the bucket has refilled. An in-process bucket is multiplied by your worker count; for a real limit keep the counters in Redis with an atomic script, answer with `429` and a `Retry-After` header, and for LLM gateways meter tokens rather than requests.

Secrets belong in a secret manager or injected environment variables, wrapped in `SecretStr`, never in the image (build arguments and layers leak), never in logs (redact `Authorization`), and rotatable without redeploy: support two active signing keys by `kid`. Map your review to the OWASP API Security Top 10 (2023):

| Risk | FastAPI mitigation |
|---|---|
| API1 Broken object level authorization | filter by owner in the query: `where Ride.rider_id == principal.sub` |
| API2 Broken authentication | rotation, short TTL, lockouts, argon2 |
| API3 Broken object property level authorization | `response_model` to whitelist output, input models with `extra="forbid"` |
| API4 Unrestricted resource consumption | rate limits, body size caps, pagination limits, token budgets |
| API5 Broken function level authorization | scopes and roles enforced per router |
| API6 Unrestricted access to sensitive business flows | per-flow limits, anomaly checks |
| API7 SSRF | allowlist outbound URLs, especially in LLM tools that fetch pages |
| API8 Security misconfiguration | exact CORS, docs off in prod, security headers |
| API9 Improper inventory management | retire old versions, track every route |
| API10 Unsafe consumption of APIs | validate third-party and LLM output with Pydantic |

## Practical Backend Scenario

You run a multi-tenant LLM gateway. Customers call `POST /v1/chat` with an API key exchanged for a 10-minute JWT carrying `sub`, `tenant_id` and scopes; the dashboard uses a cookie session. A penetration test finds three things: `GET /v1/conversations/{id}` returns another tenant's conversation when the id is guessed (BOLA, because the query filtered by id only), the CORS config reflects any origin with credentials, and one leaked refresh token was usable for weeks because it never rotated. The fix is an ownership predicate in the repository query, an explicit origin allowlist per environment, refresh rotation with family revocation, and per-tenant token-bucket limits that count LLM tokens so one tenant cannot burn the shared provider quota.

## Practice Loop

1. Build `get_principal` with `Security` scopes (use the stdlib `sign` and `verify` above as the decoder) and test the 401, 403 and 200 paths with `TestClient`.
2. Extend the JWT code with `iss` and `aud` checks, then add tests for the tampered, `alg: none` and expired cases.
3. Implement refresh rotation against a database table and write a test where two concurrent refreshes with the same token must produce exactly one success.
4. Set a `__Host-` session cookie and inspect the `Set-Cookie` header. Then write the Origin-check dependency and prove a request with a foreign Origin gets `403`.
5. Configure `CORSMiddleware` with an exact allowlist and send preflights from an allowed and a forbidden origin.
6. Add a rate-limit dependency using the token bucket, return `429` with `Retry-After`, and explain what happens with 4 uvicorn workers.
7. Take one endpoint per OWASP API risk and write the abuse test that should fail.

## Evidence of Understanding

- I can explain why `OAuth2PasswordBearer` does not authenticate anything by itself.
- I can decode a JWT by hand, state which parts are secret (none of the payload) and name three verification failures.
- I can design refresh-token rotation with reuse detection and state its race-condition requirement.
- I can choose between cookies and bearer tokens for a given client and name the matching attack and defence.
- I can explain why wildcard origins with credentials are dangerous and why CORS is not CSRF protection.
- I can map a vulnerable endpoint to its OWASP API category and write the fix.

## Interview Questions to Rehearse

### Q: Are JWTs encrypted? Where would you store one in a browser app?
No, they are signed, not encrypted, so never put secrets in claims. For a first-party browser app I would avoid exposing the token to JavaScript: keep a session or refresh token in an HttpOnly, Secure, SameSite cookie and protect state-changing requests with an Origin check or CSRF token. Bearer headers suit mobile and service clients.

### Q: How do you revoke a JWT?
You mostly do not: keep access tokens short-lived and revoke refresh tokens server-side. If instant revocation is required, add a deny list keyed by `jti` or a per-user token version checked on each request, which reintroduces a lookup and so trades away statelessness.

### Q: Explain refresh token rotation and what reuse detection buys you.
Each refresh invalidates the presented token and issues a new one in the same family. If a used token is presented again, either the client or an attacker holds a stale copy, so the whole family is revoked. It converts silent token theft into a detectable event, at the cost of occasionally logging out a legitimate user.

### Q: What is BOLA and how do you prevent it in FastAPI?
Broken object level authorization: the caller is authenticated but can access objects they do not own by changing an id. Authentication dependencies cannot fix it; the ownership predicate must be part of the data access (`WHERE id = :id AND tenant_id = :tenant`), covered by tests that use two tenants.

### Q: Why can wildcard CORS with credentials be catastrophic?
Browsers refuse `*` with credentials, so frameworks sometimes reflect the request origin to make it work. That lets any website make credentialed requests as the logged-in user and read the responses. Use an exact allowlist, and remember CORS does not stop non-browser attackers.

### Q: Where do you enforce rate limits and what key do you use?
At the edge (gateway or CDN) for coarse protection and in the app for per-principal and per-tenant limits, backed by Redis so all workers share counters. Key on the API key or user before IP, return `429` with `Retry-After`, and meter expensive resources such as LLM tokens.

## Common Pitfalls

- **Trusting the algorithm in the token header:** always pass an explicit `algorithms` list.
- **Skipping `aud` and `iss`:** tokens minted for another service verify successfully.
- **Authenticating but never authorizing the object:** passes every auth test and still leaks data.
- **Hashing passwords on the event loop:** argon2 or bcrypt blocks all requests for tens of milliseconds each. Use a thread.
- **Different responses for unknown email and wrong password:** enables user enumeration.
- **CORS added before other middleware:** responses those middleware return directly (such as a `429`) lack CORS headers, so the browser reports a misleading CORS error. Add `CORSMiddleware` last so it is outermost; unhandled `500` responses still bypass it, so handle exceptions explicitly.
- **Logging full request headers:** bearer tokens end up in log storage.
- **Per-process rate limit with several workers:** the effective limit is the limit times the number of workers.

## Suggested Extension

Implement asymmetric signing: issue RS256 or EdDSA tokens with a `kid`, expose a JWKS endpoint, and have a second service verify with `PyJWKClient`. Rotate the signing key with an overlap window and write a test proving old tokens still verify during the overlap and fail after it.
