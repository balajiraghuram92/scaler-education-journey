import logging
import threading

import pytest

from provfac import ProviderFactory, ProviderLoadError, UnknownProviderError


class FakeEntryPoint:
    def __init__(self, name, target=None, error=None):
        self.name = name
        self._target = target
        self._error = error
        self.load_calls = 0

    def load(self):
        self.load_calls += 1
        if self._error:
            raise self._error
        return self._target


def make_factory():
    factory = ProviderFactory()

    @factory.register("openai")
    def build_openai(model="small"):
        return ("openai", model)

    return factory


def test_create_passes_keyword_arguments_and_register_returns_the_builder():
    factory = ProviderFactory()

    def build(x=1):
        return x * 2

    assert factory.register("dbl")(build) is build, "register must return the builder unchanged"
    assert factory.create("dbl", x=21) == 42
    assert make_factory().create("openai", model="big") == ("openai", "big")


def test_unknown_name_lists_known_names():
    with pytest.raises(UnknownProviderError, match="openai") as info:
        make_factory().create("mistral")
    assert isinstance(info.value, ValueError), "UnknownProviderError is a ValueError"


def test_duplicate_registration_is_rejected():
    factory = make_factory()
    with pytest.raises(ValueError, match="already registered"):
        factory.register("openai")(lambda: None)
    factory.load_entry_points([FakeEntryPoint("plug")])
    with pytest.raises(ValueError, match="already registered"):
        factory.register("plug")(lambda: None)


def test_plugins_are_loaded_lazily_and_only_once():
    factory = make_factory()
    ep = FakeEntryPoint("local", target=lambda: "local-client")
    assert factory.load_entry_points([ep]) == ["local"]
    assert ep.load_calls == 0, "recording an entry point must not import it"
    assert "local" in factory.names()
    assert factory.create("local") == "local-client"
    assert factory.create("local") == "local-client"
    assert ep.load_calls == 1, "load() must run exactly once; the result is cached"


def test_names_are_sorted_and_include_builtins_and_pending_plugins():
    factory = make_factory()

    @factory.register("anthropic")
    def build():
        return "a"

    factory.load_entry_points([FakeEntryPoint("zeta"), FakeEntryPoint("local")])
    assert factory.names() == ["anthropic", "local", "openai", "zeta"]


def test_a_broken_plugin_only_affects_itself():
    factory = make_factory()
    original = ImportError("no module")
    factory.load_entry_points([FakeEntryPoint("bad", error=original)])
    with pytest.raises(ProviderLoadError, match="bad") as info:
        factory.create("bad")
    assert info.value.__cause__ is original, "chain the original exception with 'raise ... from exc'"
    assert factory.create("openai") == ("openai", "small"), "other providers must stay usable"


def test_plugin_cannot_replace_a_builtin_and_a_warning_is_logged(caplog):
    factory = make_factory()
    evil = FakeEntryPoint("openai", target=lambda **kw: "hijacked")
    with caplog.at_level(logging.WARNING):
        added = factory.load_entry_points([evil])
    assert added == [], "a name that already exists is not added"
    assert factory.create("openai") == ("openai", "small"), "the built-in must win"
    assert evil.load_calls == 0
    assert any("openai" in r.getMessage() and r.levelno == logging.WARNING for r in caplog.records), (
        "log a warning that names the ignored plugin"
    )


def test_earlier_plugin_wins_over_a_later_plugin_with_the_same_name():
    factory = ProviderFactory()
    first = FakeEntryPoint("dup", target=lambda: "first")
    second = FakeEntryPoint("dup", target=lambda: "second")
    assert factory.load_entry_points([first, second]) == ["dup"]
    assert factory.create("dup") == "first"
    assert second.load_calls == 0


def test_concurrent_first_use_loads_the_plugin_once():
    factory = ProviderFactory()
    ep = FakeEntryPoint("local", target=lambda: object())
    factory.load_entry_points([ep])
    barrier = threading.Barrier(8)
    results = []
    out_lock = threading.Lock()

    def worker():
        barrier.wait(timeout=5)
        built = factory.create("local")
        with out_lock:
            results.append(built)

    threads = [threading.Thread(target=worker) for _ in range(8)]
    for t in threads:
        t.start()
    for t in threads:
        t.join(timeout=5)
    assert len(results) == 8, "all threads should get a provider"
    assert ep.load_calls == 1, f"load() must be called exactly once, was {ep.load_calls}"
