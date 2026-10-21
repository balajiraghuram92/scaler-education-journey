import asyncio
import json

from fastapi.testclient import TestClient

from stream_gateway import create_app


class FakeUpstream:
    """Configurable async-generator factory that records whether it was closed."""

    def __init__(self, tokens=("Hello", " world"), first_delay=0.0, gap=0.0, fail_after=None, clock=None):
        self.tokens, self.first_delay, self.gap = tokens, first_delay, gap
        self.fail_after, self.clock = fail_after, clock
        self.closed = False

    def __call__(self, prompt: str):
        return self._gen()

    async def _gen(self):
        try:
            await asyncio.sleep(self.first_delay)
            for i, tok in enumerate(self.tokens):
                if self.fail_after is not None and i == self.fail_after:
                    raise RuntimeError("provider exploded: secret-detail")
                if self.clock is not None:
                    self.clock[0] += 0.25
                await asyncio.sleep(self.gap)
                yield tok
        finally:
            self.closed = True


def lines(client, up_app) -> list[str]:
    with client.stream("POST", "/chat/stream", json={"prompt": "hi"}) as resp:
        assert resp.status_code == 200
        assert resp.headers["content-type"].startswith("text/event-stream")
        assert resp.headers["x-accel-buffering"] == "no"
        assert resp.headers["cache-control"] == "no-cache"
        return [ln for ln in resp.iter_lines() if ln]


def test_happy_path_event_order_and_cleanup():
    up = FakeUpstream()
    app, metrics = create_app(up)
    out = lines(TestClient(app), app)
    assert out[0] == "event: meta" and json.loads(out[1][6:])["request_id"]
    assert out[2:6] == ['data: {"delta": "Hello"}', 'data: {"delta": " world"}', "event: done",
                        'data: {"tokens": 2}']
    assert up.closed and metrics.outcomes == {"ok": 1}


def test_mid_stream_failure_becomes_an_error_event_without_leaking_details():
    up = FakeUpstream(fail_after=1)
    app, metrics = create_app(up)
    out = lines(TestClient(app), app)
    assert "event: error" in out
    err = json.loads(out[out.index("event: error") + 1][6:])
    assert err["code"] == "upstream_failed" and "secret" not in json.dumps(out)
    assert err["request_id"] == json.loads(out[1][6:])["request_id"], "error carries the same request id as meta"
    assert up.closed and metrics.outcomes == {"error": 1}


def test_keepalive_pings_are_sent_while_waiting_for_the_first_token():
    up = FakeUpstream(first_delay=0.12)
    app, _ = create_app(up, ping_interval_s=0.02)
    with TestClient(app).stream("POST", "/chat/stream", json={"prompt": "hi"}) as resp:
        raw = resp.read().decode()
    assert raw.count(": ping") >= 2
    assert raw.index(": ping") < raw.index('"delta"')
    assert raw.count('"delta"') == 2, "pings must not lose or restart the pending read"


def test_deadline_ends_the_stream_and_closes_upstream():
    up = FakeUpstream(tokens=("a", "b", "c"), gap=0.2)
    app, metrics = create_app(up, deadline_s=0.05)
    out = lines(TestClient(app), app)
    assert json.loads(out[out.index("event: error") + 1][6:])["code"] == "deadline_exceeded"
    assert up.closed and metrics.outcomes == {"deadline": 1}


def test_time_to_first_token_is_recorded_with_the_injected_clock():
    now = [0.0]
    up = FakeUpstream(clock=now)
    app, metrics = create_app(up, clock=lambda: now[0])
    lines(TestClient(app), app)
    assert metrics.ttft_ms == [250.0]


def test_client_disconnect_cancels_and_closes_upstream():
    up = FakeUpstream(tokens=tuple("abcdefgh"), gap=0.01)
    app, metrics = create_app(up)

    async def drive():
        disconnect = asyncio.Event()
        body_chunks = 0
        first = True

        async def receive():
            nonlocal first
            if first:
                first = False
                return {"type": "http.request", "body": b'{"prompt": "hi"}', "more_body": False}
            await disconnect.wait()
            return {"type": "http.disconnect"}

        async def send(message):
            nonlocal body_chunks
            if message["type"] == "http.response.body":
                body_chunks += 1
                if body_chunks == 3:
                    disconnect.set()

        scope = {"type": "http", "asgi": {"version": "3.0", "spec_version": "2.3"}, "http_version": "1.1",
                 "method": "POST", "path": "/chat/stream", "raw_path": b"/chat/stream", "query_string": b"",
                 "headers": [(b"content-type", b"application/json")], "server": ("t", 80),
                 "client": ("c", 1), "scheme": "http", "root_path": ""}
        try:
            await asyncio.wait_for(app(scope, receive, send), timeout=2)
        except Exception:
            pass
        await asyncio.sleep(0.05)

    asyncio.run(drive())
    assert up.closed
    assert metrics.outcomes == {"disconnected": 1}


def test_empty_upstream_sends_done_without_a_ttft_sample():
    app, metrics = create_app(FakeUpstream(tokens=()))
    out = lines(TestClient(app), app)
    assert out[0] == "event: meta" and out[2:4] == ["event: done", 'data: {"tokens": 0}']
    assert metrics.ttft_ms == [] and metrics.outcomes == {"ok": 1}


def test_validation_error_for_empty_prompt():
    app, _ = create_app(FakeUpstream())
    assert TestClient(app).post("/chat/stream", json={"prompt": ""}).status_code == 422
