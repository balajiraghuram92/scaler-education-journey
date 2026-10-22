from __future__ import annotations

from collections.abc import Callable, Sequence
from dataclasses import dataclass, field
from functools import reduce


@dataclass
class Request:
    user: str | None
    prompt: str
    trace: list[str] = field(default_factory=list)


@dataclass(frozen=True, slots=True)
class Response:
    status: int
    body: str


Next = Callable[[Request], Response]
Middleware = Callable[[Request, Next], Response]


def build_chain(middlewares: Sequence[Middleware], endpoint: Next) -> Next:
    """First middleware in the sequence is outermost (sees the request first)."""
    def wrap(nxt: Next, mw: Middleware) -> Next:
        return lambda req: mw(req, nxt)
    return reduce(wrap, reversed(middlewares), endpoint)


def tracing(name: str) -> Middleware:
    def mw(req: Request, nxt: Next) -> Response:
        req.trace.append(f"{name}>")
        resp = nxt(req)
        req.trace.append(f"<{name}")
        return resp
    return mw


def require_user(req: Request, nxt: Next) -> Response:
    if req.user is None:
        return Response(401, "unauthenticated")
    return nxt(req)


def max_prompt_chars(limit: int) -> Middleware:
    def mw(req: Request, nxt: Next) -> Response:
        if len(req.prompt) > limit:
            return Response(413, "prompt too long")
        return nxt(req)
    return mw
