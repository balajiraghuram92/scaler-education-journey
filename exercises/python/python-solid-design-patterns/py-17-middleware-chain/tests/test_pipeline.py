import dataclasses

import pytest

from pipeline import (
    Request,
    Response,
    build_chain,
    max_prompt_chars,
    require_user,
    tracing,
)


def endpoint(req: Request) -> Response:
    req.trace.append("endpoint")
    return Response(200, req.prompt.upper())


def test_request_and_response_types():
    a, b = Request("u", "p"), Request("u", "p")
    assert a.trace == [] and a.trace is not b.trace, "trace must default to a fresh list per request"
    r = Response(200, "ok")
    assert r == Response(200, "ok")
    with pytest.raises(dataclasses.FrozenInstanceError):
        r.status = 500
    assert not hasattr(r, "__dict__"), "Response must use slots=True"


def test_first_middleware_is_outermost():
    req = Request("u", "hi")
    resp = build_chain([tracing("a"), tracing("b")], endpoint)(req)
    assert req.trace == ["a>", "b>", "endpoint", "<b", "<a"], f"wrong order: {req.trace}"
    assert resp == Response(200, "HI"), "the endpoint's response must come back through the chain"


def test_short_circuit_skips_inner_layers_and_the_endpoint():
    req = Request(None, "hi")
    resp = build_chain([tracing("a"), require_user, tracing("b")], endpoint)(req)
    assert resp == Response(401, "unauthenticated")
    assert req.trace == ["a>", "<a"], f"inner layers and endpoint must be skipped; trace was {req.trace}"


def test_many_layers_are_not_late_bound():
    req = Request("u", "x" * 5)
    chain = build_chain([tracing("a"), tracing("b"), max_prompt_chars(3), tracing("c"), tracing("d")], endpoint)
    resp = chain(req)
    assert resp == Response(413, "prompt too long")
    assert req.trace == ["a>", "b>", "<b", "<a"], (
        f"each layer must call its own next; a late-binding bug would loop or skip layers, got {req.trace}"
    )
    ok = Request("u", "abc")
    assert chain(ok).status == 200
    assert ok.trace == ["a>", "b>", "c>", "d>", "endpoint", "<d", "<c", "<b", "<a"]


def test_empty_chain_behaves_like_the_endpoint():
    req = Request("u", "ok")
    assert build_chain([], endpoint)(req) == Response(200, "OK")
    assert req.trace == ["endpoint"]


def test_chain_is_reusable_without_shared_state():
    chain = build_chain([tracing("t"), require_user], endpoint)
    first, second, third = Request("u", "a"), Request(None, "a"), Request("u", "b")
    assert chain(first).status == 200
    assert chain(second).status == 401
    assert chain(third) == Response(200, "B")
    assert first.trace == ["t>", "endpoint", "<t"] and third.trace == first.trace, "a second call must behave like the first"
    assert second.trace == ["t>", "<t"]


def test_middleware_can_act_on_the_response_on_the_way_out():
    def stamp(req, nxt):
        resp = nxt(req)
        return Response(resp.status, resp.body + "!")

    chain = build_chain([stamp, tracing("t")], endpoint)
    assert chain(Request("u", "hi")) == Response(200, "HI!")


def test_require_user_and_prompt_limit_boundaries():
    chain = build_chain([require_user, max_prompt_chars(5)], endpoint)
    assert chain(Request(None, "hi")).status == 401, "missing user is rejected first"
    assert chain(Request("u", "12345")).status == 200, "a prompt exactly at the limit is allowed"
    assert chain(Request("u", "123456")) == Response(413, "prompt too long")
    assert chain(Request("", "ok")).status == 200, "only None means unauthenticated"
    assert chain(Request(None, "123456")).status == 401, "outer require_user wins over the inner limit"


def test_build_chain_accepts_any_sequence_and_does_not_mutate_it():
    layers = (tracing("a"), tracing("b"))
    build_chain(layers, endpoint)(Request("u", "x"))
    assert [type(m).__name__ for m in layers] == ["function", "function"] and len(layers) == 2
    lst = [tracing("a"), tracing("b")]
    snapshot = list(lst)
    req = Request("u", "x")
    build_chain(lst, endpoint)(req)
    assert lst == snapshot, "build_chain must not reorder or consume the middleware list"
    assert req.trace[:2] == ["a>", "b>"]
