import json
import re

import pytest

from asgi_mw import AccessLogMiddleware, RequestContextMiddleware, request_id_var


async def drive(app, headers=None, path="/", scope_type="http", method="GET"):
    sent: list = []

    async def receive():
        return {"type": "http.request", "body": b"", "more_body": False}

    async def send(message):
        sent.append(message)

    scope = {"type": scope_type, "method": method, "path": path, "headers": headers or []}
    await app(scope, receive, send)
    return sent


def ok_app(seen, status=200, extra_headers=()):
    async def app(scope, receive, send):
        seen.append(request_id_var.get())
        await send({"type": "http.response.start", "status": status, "headers": list(extra_headers)})
        await send({"type": "http.response.body", "body": b"ok"})

    return app


def header(sent, name):
    return dict(sent[0]["headers"]).get(name)


@pytest.mark.asyncio
async def test_echoes_valid_incoming_id_and_resets():
    seen = []
    app = RequestContextMiddleware(ok_app(seen))
    sent = await drive(app, [(b"x-request-id", b"abc-123")])
    assert seen == ["abc-123"], "the inner app must see the inbound id in request_id_var"
    assert header(sent, b"x-request-id") == b"abc-123", "the id must be echoed in the response headers"
    assert request_id_var.get() == "-", "the variable must be reset after the request"


@pytest.mark.asyncio
async def test_generates_when_missing_or_unsafe():
    seen = []
    app = RequestContextMiddleware(ok_app(seen))
    for hdrs in ([], [(b"x-request-id", b"bad id\nINJECT")], [(b"x-request-id", b"x" * 65)], [(b"x-request-id", b"")]):
        sent = await drive(app, hdrs)
        generated = header(sent, b"x-request-id").decode()
        assert re.fullmatch(r"[0-9a-f]{32}", generated), f"expected a uuid4 hex for headers {hdrs}, got {generated!r}"
    assert len(set(seen)) == 4, "each generated id must be unique"
    sent = await drive(app, [(b"x-request-id", b"A.b_c-" + b"9" * 58)])
    assert header(sent, b"x-request-id") == b"A.b_c-" + b"9" * 58, "64 safe characters are accepted"


@pytest.mark.asyncio
async def test_response_headers_are_appended_not_replaced():
    app = RequestContextMiddleware(ok_app([], extra_headers=[(b"content-type", b"text/plain")]), header=b"x-trace")
    sent = await drive(app, [(b"x-trace", b"t-1")])
    assert dict(sent[0]["headers"]) == {b"content-type": b"text/plain", b"x-trace": b"t-1"}
    assert sent[1] == {"type": "http.response.body", "body": b"ok"}, "other messages pass through unchanged"


@pytest.mark.asyncio
async def test_reset_even_when_inner_app_raises():
    async def boom(scope, receive, send):
        raise RuntimeError("x")

    app = RequestContextMiddleware(boom)
    with pytest.raises(RuntimeError, match="x"):
        await drive(app, [(b"x-request-id", b"r1")])
    assert request_id_var.get() == "-", "the context variable must be reset even on failure"


@pytest.mark.asyncio
async def test_non_http_scopes_pass_through():
    calls = []

    async def inner(scope, receive, send):
        calls.append(scope["type"])

    await drive(RequestContextMiddleware(inner), scope_type="lifespan")
    await drive(AccessLogMiddleware(inner, lambda line: calls.append("LOG")), scope_type="websocket")
    assert calls == ["lifespan", "websocket"], "non-http scopes must not be logged or modified"


@pytest.mark.asyncio
async def test_access_log_has_request_id_status_and_duration():
    lines = []
    ticks = iter([10.0, 10.25])
    app = RequestContextMiddleware(AccessLogMiddleware(ok_app([]), lines.append, clock=lambda: next(ticks)))
    await drive(app, [(b"x-request-id", b"r9")], path="/chat", method="POST")
    assert len(lines) == 1, "exactly one line per request"
    expected = {"request_id": "r9", "method": "POST", "path": "/chat", "status": 200, "duration_ms": 250.0}
    assert json.loads(lines[0]) == expected
    assert ", " not in lines[0] and ": " not in lines[0], 'use separators=(",", ":")'


@pytest.mark.asyncio
async def test_duration_is_rounded_to_one_decimal_and_status_is_captured():
    lines = []
    ticks = iter([100.0, 100.0123])
    app = AccessLogMiddleware(ok_app([], status=404), lines.append, clock=lambda: next(ticks))
    await drive(app)
    logged = json.loads(lines[0])
    assert logged["duration_ms"] == 12.3 and logged["status"] == 404
    assert logged["request_id"] == "-", "without RequestContextMiddleware the id is the default '-'"


@pytest.mark.asyncio
async def test_access_log_records_500_when_inner_raises_and_reraises():
    lines = []

    async def boom(scope, receive, send):
        raise RuntimeError("x")

    app = RequestContextMiddleware(AccessLogMiddleware(boom, lines.append))
    with pytest.raises(RuntimeError, match="x"):
        await drive(app, [(b"x-request-id", b"r5")])
    assert len(lines) == 1, "a crash must still produce one log line"
    logged = json.loads(lines[0])
    assert logged["status"] == 500 and logged["request_id"] == "r5"


@pytest.mark.asyncio
async def test_one_line_per_request_and_status_kept_if_crash_after_response_start():
    lines = []

    async def half(scope, receive, send):
        await send({"type": "http.response.start", "status": 202, "headers": []})
        raise RuntimeError("late")

    app = AccessLogMiddleware(half, lines.append)
    with pytest.raises(RuntimeError):
        await drive(app)
    ok = AccessLogMiddleware(ok_app([]), lines.append)
    await drive(ok)
    await drive(ok)
    assert [json.loads(line)["status"] for line in lines] == [202, 200, 200], "one line per request, real status kept"
