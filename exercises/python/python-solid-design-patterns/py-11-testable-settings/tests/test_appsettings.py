import threading

import pytest

from appsettings import BudgetGuard, Settings, get_settings, load_settings, override_settings, reset_settings


@pytest.fixture(autouse=True)
def clean(monkeypatch):
    monkeypatch.delenv("LLM_MODEL", raising=False)
    monkeypatch.delenv("MONTHLY_BUDGET_USD", raising=False)
    try:
        reset_settings()
    except NotImplementedError:
        pass
    yield
    try:
        reset_settings()
    except NotImplementedError:
        pass


def test_load_settings_defaults_and_values():
    assert load_settings({}) == Settings("small", 100.0)
    assert load_settings({"LLM_MODEL": "big", "MONTHLY_BUDGET_USD": "250.5"}) == Settings("big", 250.5)


def test_load_settings_is_pure(monkeypatch):
    monkeypatch.setenv("LLM_MODEL", "from-os-environ")
    assert load_settings({}).llm_model == "small", "load_settings must read only the mapping it is given"


def test_invalid_budget_is_rejected_with_a_clear_message():
    with pytest.raises(ValueError, match="MONTHLY_BUDGET_USD"):
        load_settings({"MONTHLY_BUDGET_USD": "abc"})
    with pytest.raises(ValueError):
        load_settings({"MONTHLY_BUDGET_USD": "-1"})


def test_settings_are_frozen():
    s = load_settings({})
    with pytest.raises(Exception):
        s.llm_model = "other"


def test_get_settings_is_cached_until_reset(monkeypatch):
    monkeypatch.setenv("LLM_MODEL", "first")
    assert get_settings().llm_model == "first"
    monkeypatch.setenv("LLM_MODEL", "second")
    assert get_settings().llm_model == "first", "settings are loaded once and cached"
    reset_settings()
    assert get_settings().llm_model == "second", "reset_settings clears the cache"


def test_concurrent_first_calls_share_one_object():
    barrier = threading.Barrier(8)
    seen = []

    def worker():
        barrier.wait(timeout=5)
        seen.append(get_settings())

    threads = [threading.Thread(target=worker) for _ in range(8)]
    for t in threads:
        t.start()
    for t in threads:
        t.join(timeout=5)
    assert len(seen) == 8
    assert len({id(s) for s in seen}) == 1, "the lazy global must be created exactly once"


def test_override_applies_and_restores():
    before = get_settings()
    with override_settings(llm_model="fake", monthly_budget_usd=1.0) as inside:
        assert inside.llm_model == "fake"
        assert get_settings().llm_model == "fake"
        assert get_settings().monthly_budget_usd == 1.0
    assert get_settings() is before, "the exact previous object must be restored"


def test_override_restores_even_when_the_body_raises():
    before = get_settings()
    with pytest.raises(RuntimeError):
        with override_settings(llm_model="fake"):
            raise RuntimeError("boom")
    assert get_settings() is before


def test_override_rejects_unknown_fields():
    before = get_settings()
    with pytest.raises(TypeError):
        with override_settings(not_a_field=1):
            pass
    assert get_settings() is before, "a failed override must leave the settings untouched"


def test_budget_guard_works_with_injected_settings_only():
    guard = BudgetGuard(Settings("x", 10.0))
    assert guard.allow(6.0) is True
    assert guard.allow(5.0) is False, "6 + 5 exceeds the budget of 10"
    assert guard.allow(4.0) is True, "a refused call must not consume budget"
    assert guard.allow(0.01) is False
