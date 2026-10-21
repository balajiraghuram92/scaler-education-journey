from __future__ import annotations


class GatewayError(Exception):
    """Base class for every error this service raises on purpose."""

    retryable: bool = False


class UpstreamError(GatewayError):
    """An upstream failure. Must expose a ``status`` attribute (``int | None``).

    Constructor: ``UpstreamError(message, *, status=None)``.
    """

    def __init__(self, message: str, *, status: int | None = None) -> None:
        raise NotImplementedError("Implement UpstreamError.__init__")


class UpstreamTimeout(UpstreamError):
    """Retryable (set ``retryable = True``)."""


class UpstreamUnavailable(UpstreamError):
    """Retryable."""


class RateLimited(UpstreamError):
    """Retryable, status 429, with ``retry_after: float | None``.

    Constructor: ``RateLimited(message, *, retry_after=None)``.
    """

    def __init__(self, message: str, *, retry_after: float | None = None) -> None:
        raise NotImplementedError("Implement RateLimited.__init__")


class BadRequest(UpstreamError):
    """Not retryable."""


def from_status(
    status: int, *, retry_after: float | None = None, cause: BaseException | None = None
) -> UpstreamError:
    """Translate an HTTP status into a domain error.

    429 -> RateLimited; 408 and 504 -> UpstreamTimeout; other 5xx -> UpstreamUnavailable;
    other 4xx -> BadRequest; below 400 -> ``ValueError("not an error status: <n>")``.
    The returned error's ``__cause__`` must be ``cause``.
    """
    raise NotImplementedError("Implement from_status")
