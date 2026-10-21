import pytest

from config.api import Api, ECommerceApi
from config.decorator import BaseApiDecorator, LoggingDecorator, RateLimitDecorator
from config.utils import ApiUtils


class RecordingApi(Api):
    def __init__(self, events, result="core-result"):
        self.events, self.result = events, result

    def execute_request(self, request_data):
        self.events.append(("core", request_data))
        return self.result


@pytest.fixture
def events(monkeypatch):
    log = []
    monkeypatch.setattr(ApiUtils, "log_request", staticmethod(lambda *a, **k: log.append(("log",) + a)))
    monkeypatch.setattr(ApiUtils, "apply_rate_limit", staticmethod(lambda *a, **k: log.append(("limit",) + a)))
    return log


def test_base_decorator_is_an_api_that_delegates(events):
    core = RecordingApi(events)
    deco = BaseApiDecorator(core)
    assert issubclass(BaseApiDecorator, Api), "BaseApiDecorator must inherit from Api"
    assert deco.api is core, "store the wrapped API in an attribute named api"
    payload = {"id": 1}
    assert deco.execute_request(payload) == "core-result", "return the wrapped call's result"
    assert events == [("core", payload)], "the base decorator adds no behaviour of its own"


def test_logging_decorator_logs_before_delegating(events):
    payload = {"sku": "A1"}
    result = LoggingDecorator(RecordingApi(events)).execute_request(payload)
    assert events == [("log", payload), ("core", payload)], f"log first, then call the core; got {events}"
    assert result == "core-result", "the result must be returned unchanged"


def test_rate_limit_decorator_limits_before_delegating(events):
    payload = {"sku": "B2"}
    result = RateLimitDecorator(RecordingApi(events)).execute_request(payload)
    assert [e[0] for e in events] == ["limit", "core"], f"rate limit first, then call the core; got {events}"
    assert events[0][1:] == (payload,), "apply_rate_limit must receive the request data"
    assert result == "core-result"


def test_stacked_decorators_run_outermost_first(events):
    api = LoggingDecorator(RateLimitDecorator(RecordingApi(events)))
    api.execute_request("req")
    assert [e[0] for e in events] == ["log", "limit", "core"], f"wrong order for Logging(RateLimit(core)): {events}"

    events.clear()
    api = RateLimitDecorator(LoggingDecorator(RecordingApi(events)))
    api.execute_request("req")
    assert [e[0] for e in events] == ["limit", "log", "core"], f"wrong order for RateLimit(Logging(core)): {events}"


def test_subclasses_keep_the_wrapped_api_via_the_parent_constructor(events):
    core = RecordingApi(events)
    assert LoggingDecorator(core).api is core
    assert RateLimitDecorator(core).api is core
    assert isinstance(LoggingDecorator(core), BaseApiDecorator) and isinstance(RateLimitDecorator(core), BaseApiDecorator)


def test_decorated_api_keeps_the_api_interface(events):
    stacked = LoggingDecorator(RateLimitDecorator(RecordingApi(events)))
    assert isinstance(stacked, Api), "a decorated API must still be usable wherever an Api is expected"


def test_errors_from_the_wrapped_api_propagate(events):
    class Failing(Api):
        def execute_request(self, request_data):
            raise RuntimeError("upstream down")

    with pytest.raises(RuntimeError, match="upstream down"):
        LoggingDecorator(RateLimitDecorator(Failing())).execute_request({})
    assert [e[0] for e in events] == ["log", "limit"], "decorators must not swallow the error"


def test_works_with_the_real_helpers_and_core_api(capsys):
    api = LoggingDecorator(RateLimitDecorator(ECommerceApi()))
    assert api.execute_request({"q": 1}) == "Response data"
    out = capsys.readouterr().out
    assert "Request data" in out and "Rate limit applied" in out, "the real helpers must have been called with the request data"
