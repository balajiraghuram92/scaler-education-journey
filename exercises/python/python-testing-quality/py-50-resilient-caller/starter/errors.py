from __future__ import annotations


class GatewayError(Exception):
    """Base class for every error this service raises on purpose."""

    retryable: bool = False


class UpstreamError(GatewayError):
    def __init__(self, message: str, *, status: int | None = None) -> None:
        super().__init__(message)
        self.status = status


class UpstreamTimeout(UpstreamError):
    retryable = True


class UpstreamUnavailable(UpstreamError):
    retryable = True


class RateLimited(UpstreamError):
    retryable = True

    def __init__(self, message: str, *, retry_after: float | None = None) -> None:
        super().__init__(message, status=429)
        self.retry_after = retry_after


class BadRequest(UpstreamError):
    retryable = False


def from_status(
    status: int, *, retry_after: float | None = None, cause: BaseException | None = None
) -> UpstreamError:
    """Translate an HTTP status into a domain error (optionally chaining a cause)."""
    err: UpstreamError
    if status == 429:
        err = RateLimited("rate limited", retry_after=retry_after)
    elif status in (408, 504):
        err = UpstreamTimeout(f"upstream timeout ({status})", status=status)
    elif status >= 500:
        err = UpstreamUnavailable(f"upstream unavailable ({status})", status=status)
    elif status >= 400:
        err = BadRequest(f"bad request ({status})", status=status)
    else:
        raise ValueError(f"not an error status: {status}")
    err.__cause__ = cause
    return err
