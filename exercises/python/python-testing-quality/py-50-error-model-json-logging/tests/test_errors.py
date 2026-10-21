import pytest

from errors import (
    BadRequest, GatewayError, RateLimited, UpstreamError, UpstreamTimeout, UpstreamUnavailable, from_status,
)


@pytest.mark.parametrize(
    ("status", "cls", "retryable"),
    [
        pytest.param(429, RateLimited, True, id="429"),
        pytest.param(408, UpstreamTimeout, True, id="408"),
        pytest.param(504, UpstreamTimeout, True, id="504"),
        pytest.param(500, UpstreamUnavailable, True, id="500"),
        pytest.param(503, UpstreamUnavailable, True, id="503"),
        pytest.param(400, BadRequest, False, id="400"),
        pytest.param(404, BadRequest, False, id="404"),
    ],
)
def test_status_translation(status, cls, retryable):
    err = from_status(status)
    assert type(err) is cls, f"status {status} should map to {cls.__name__}"
    assert err.retryable is retryable
    assert isinstance(err, GatewayError)


def test_hierarchy_and_attributes():
    assert GatewayError.retryable is False
    for cls in (UpstreamTimeout, UpstreamUnavailable, RateLimited, BadRequest):
        assert issubclass(cls, UpstreamError)
    assert issubclass(UpstreamError, GatewayError)
    err = from_status(503)
    assert err.status == 503
    limited = from_status(429)
    assert isinstance(limited, RateLimited)
    assert limited.status == 429
    assert limited.retry_after is None, "retry_after defaults to None"
    assert UpstreamError("boom").status is None


def test_retry_after_and_cause_are_kept():
    original = TimeoutError("read timed out")
    err = from_status(429, retry_after=7.5, cause=original)
    assert isinstance(err, RateLimited)
    assert err.retry_after == 7.5
    assert err.__cause__ is original
    assert from_status(500).__cause__ is None


@pytest.mark.parametrize("status", [200, 302, 399], ids=["200", "302", "399"])
def test_non_error_status_rejected(status):
    with pytest.raises(ValueError, match=f"not an error status: {status}"):
        from_status(status)
