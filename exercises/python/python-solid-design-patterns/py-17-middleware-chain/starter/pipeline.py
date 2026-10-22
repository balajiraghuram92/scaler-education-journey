from __future__ import annotations

from collections.abc import Callable, Sequence
from dataclasses import dataclass, field
from functools import reduce


# TODO: dataclass with fields user: str | None, prompt: str,
#       trace: list[str] (defaults to a fresh empty list per instance)
class Request:
    ...


# TODO: frozen dataclass with slots=True and fields status: int, body: str
class Response:
    ...


Next = Callable[[Request], Response]
Middleware = Callable[[Request, Next], Response]


def build_chain(middlewares: Sequence[Middleware], endpoint: Next) -> Next:
    """Compose middlewares around the endpoint.

    The first middleware in the sequence is outermost (sees the request first). An empty
    sequence behaves like the endpoint. The built chain must be reusable and must not
    suffer from the late-binding closure bug (each layer keeps its own middleware and next).
    """
    raise NotImplementedError("Implement build_chain")


def tracing(name: str) -> Middleware:
    """Append f"{name}>" to req.trace before calling next and f"<{name}" after it returns.
    Return next's response unchanged."""
    raise NotImplementedError("Implement tracing")


def require_user(req: Request, nxt: Next) -> Response:
    """Return Response(401, "unauthenticated") when req.user is None, else call next."""
    raise NotImplementedError("Implement require_user")


def max_prompt_chars(limit: int) -> Middleware:
    """Return a middleware: Response(413, "prompt too long") when len(req.prompt) > limit,
    else call next."""
    raise NotImplementedError("Implement max_prompt_chars")
