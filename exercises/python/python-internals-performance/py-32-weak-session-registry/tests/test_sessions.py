import gc
import weakref
from functools import lru_cache

import pytest

from sessions import Session, SessionRegistry


def test_session_is_slotted_and_weakrefable() -> None:
    s = Session("acme")
    assert not hasattr(s, "__dict__")
    assert weakref.ref(s)() is s
    with pytest.raises(AttributeError):
        s.extra = 1  # type: ignore[attr-defined]


def test_render_prompt_is_cached_per_instance() -> None:
    a, b = Session("acme"), Session("globex")
    first = a.render_prompt("greet")
    assert a.render_prompt("greet") is first
    assert b.render_prompt("greet") == "[globex] greet"


def test_registry_does_not_keep_sessions_alive() -> None:
    reg = SessionRegistry()
    s = Session("acme")
    sid = reg.register(s)
    assert reg.get(sid) is s and len(reg) == 1
    del s
    gc.collect()
    assert reg.get(sid) is None
    assert len(reg) == 0


def test_ids_are_unique() -> None:
    reg = SessionRegistry()
    keep = [Session(str(i)) for i in range(3)]
    ids = [reg.register(s) for s in keep]
    assert len(set(ids)) == 3


def test_lru_cache_on_method_leaks_by_contrast() -> None:
    class Leaky:
        @lru_cache(maxsize=None)
        def render(self, name: str) -> str:
            return name

    obj = Leaky()
    probe = weakref.ref(obj)
    obj.render("x")
    del obj
    gc.collect()
    assert probe() is not None  # pinned by the cache: this is the bug
    Leaky.render.cache_clear()
    gc.collect()
    assert probe() is None


def test_ids_start_at_one_and_increase_and_unknown_ids_return_none() -> None:
    reg = SessionRegistry()
    a, b = Session("a"), Session("b")
    assert reg.register(a) == 1
    assert reg.register(b) == 2
    assert reg.get(999) is None


def test_rendered_prompt_cache_does_not_pin_the_session() -> None:
    s = Session("acme")
    s.render_prompt("greet")
    probe = weakref.ref(s)
    del s
    gc.collect()
    assert probe() is None, "the prompt cache must live on the session, not in a global that keeps it alive"


def test_len_counts_only_live_sessions() -> None:
    reg = SessionRegistry()
    keep = Session("keep")
    drop = Session("drop")
    reg.register(keep)
    reg.register(drop)
    assert len(reg) == 2
    del drop
    gc.collect()
    assert len(reg) == 1
    assert keep.tenant == "keep"
