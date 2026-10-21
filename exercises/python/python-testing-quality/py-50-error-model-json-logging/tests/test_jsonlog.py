import asyncio
import io
import json
import logging

import pytest

import jsonlog
from errors import UpstreamTimeout, from_status


@pytest.fixture
def stream():
    buf = io.StringIO()
    jsonlog.configure(buf)
    yield buf
    logging.getLogger("gateway").handlers.clear()


def lines(stream):
    return [json.loads(line) for line in stream.getvalue().splitlines()]


def test_json_line_has_context_and_extras(stream):
    log = logging.getLogger("gateway.billing")
    with jsonlog.bind_request_id("req-1"):
        log.info("charged %s", "acme", extra={"tokens": 1200})
    log.debug("below INFO: dropped")
    assert lines(stream) == [
        {"level": "INFO", "logger": "gateway.billing", "msg": "charged acme", "request_id": "req-1", "tokens": 1200}
    ]
    raw = stream.getvalue().strip()
    assert "\n" not in raw, "exactly one JSON object per line"
    keys = list(json.loads(raw))
    assert keys == sorted(keys), "keys must be sorted"


def test_request_id_defaults_and_resets_after_context(stream):
    log = logging.getLogger("gateway.x")
    assert jsonlog.request_id.get() == "-"
    with jsonlog.bind_request_id("outer"):
        with jsonlog.bind_request_id("inner"):
            assert jsonlog.request_id.get() == "inner"
        assert jsonlog.request_id.get() == "outer", "the token reset must restore the previous value"
    log.info("after")
    assert lines(stream)[0]["request_id"] == "-"
    with pytest.raises(RuntimeError):
        with jsonlog.bind_request_id("req-err"):
            raise RuntimeError("boom")
    assert jsonlog.request_id.get() == "-", "the id must be reset even when the block raises"


def test_exception_logging_includes_type_and_cause(stream):
    log = logging.getLogger("gateway.vendor")
    try:
        try:
            raise TimeoutError("read timed out")
        except TimeoutError as exc:
            raise from_status(504, cause=exc)
    except UpstreamTimeout:
        log.exception("vendor call failed")
    record = lines(stream)[0]
    assert record["level"] == "ERROR"
    assert record["exc_type"] == "UpstreamTimeout"
    assert record["cause"] == "TimeoutError: read timed out"
    assert "upstream timeout" in str(record["exc"])
    try:
        raise ValueError("plain")
    except ValueError:
        log.exception("failed")
    plain = lines(stream)[1]
    assert plain["exc_type"] == "ValueError"
    assert plain["exc"] == "plain"
    assert "cause" not in plain, "no cause field without a __cause__"


def test_configure_sets_level_and_isolates_the_logger(stream):
    other = logging.getLogger("unrelated.lib")
    other.info("stays out of the stream")
    gateway = logging.getLogger("gateway")
    assert gateway.propagate is False
    buf = io.StringIO()
    jsonlog.configure(buf, level="WARNING")
    log = logging.getLogger("gateway.level")
    log.info("dropped")
    log.warning("kept")
    assert [r["msg"] for r in [json.loads(x) for x in buf.getvalue().splitlines()]] == ["kept"]
    assert len(gateway.handlers) == 1, "reconfiguring must not stack handlers"
    assert other.disabled is False, "disable_existing_loggers must be False"


@pytest.mark.asyncio
async def test_concurrent_tasks_do_not_share_request_ids(stream):
    log = logging.getLogger("gateway.async")

    async def handle(n):
        with jsonlog.bind_request_id(f"req-{n}"):
            await asyncio.sleep(0)
            log.info("working", extra={"n": n})

    await asyncio.gather(*(handle(n) for n in range(5)))
    seen = {(rec["n"], rec["request_id"]) for rec in lines(stream)}
    assert seen == {(n, f"req-{n}") for n in range(5)}, "each task must log its own request id"
