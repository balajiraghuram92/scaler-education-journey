import pytest
from collections import OrderedDict
from importlib.metadata import EntryPoint

from plugins import LoadReport, discover, load_plugins

G = "gateway.providers"


def ep(name: str, value: str) -> EntryPoint:
    return EntryPoint(name=name, value=value, group=G)


def test_loads_valid_plugins_in_name_order() -> None:
    report = load_plugins([ep("zeta", "collections:OrderedDict"), ep("alpha", "json:JSONDecoder")])
    assert list(report.loaded) == ["alpha", "zeta"]
    assert report.loaded["zeta"] is OrderedDict
    assert report.failures == {}


def test_missing_module_and_attribute_are_isolated() -> None:
    report = load_plugins(
        [
            ep("ok", "collections:OrderedDict"),
            ep("nomod", "no_such_module_xyz:Thing"),
            ep("noattr", "collections:DoesNotExist"),
        ]
    )
    assert list(report.loaded) == ["ok"]
    assert isinstance(report.failures["nomod"], ModuleNotFoundError)
    assert isinstance(report.failures["noattr"], AttributeError)


def test_validation_rejects_wrong_types() -> None:
    report = load_plugins(
        [ep("good", "collections:OrderedDict"), ep("bad", "json:dumps")],
        validate=lambda obj: isinstance(obj, type),
    )
    assert list(report.loaded) == ["good"]
    assert isinstance(report.failures["bad"], TypeError)
    assert "json:dumps" in str(report.failures["bad"]), "the TypeError should mention the entry-point value"


def test_duplicate_names_are_rejected_for_both_entries() -> None:
    report = load_plugins([ep("dup", "collections:OrderedDict"), ep("dup", "json:JSONDecoder")])
    assert "dup" not in report.loaded
    assert "duplicate" in str(report.failures["dup"])


def test_discover_uses_installed_metadata() -> None:
    report = discover("console_scripts", validate=callable)
    assert isinstance(report, LoadReport)
    assert all(isinstance(name, str) for name in {**report.loaded, **report.failures})


def test_empty_group_returns_empty_report() -> None:
    report = discover("gateway.no_such_group_xyz")
    assert report.loaded == {} and report.failures == {}


class StubEntryPoint:
    """Duck-typed entry point: lets a test simulate plugins that misbehave at import time."""

    def __init__(self, name: str, value: str, action) -> None:
        self.name, self.value, self.group = name, value, G
        self._action = action

    def load(self):
        return self._action()


def _exit_on_import():
    raise SystemExit(3)


def test_plugin_calling_sys_exit_at_import_is_recorded_not_fatal() -> None:
    report = load_plugins(
        [
            StubEntryPoint("exits", "cli:main", _exit_on_import),
            StubEntryPoint("fine", "collections:OrderedDict", lambda: OrderedDict),
        ]
    )
    assert isinstance(report.failures["exits"], SystemExit), "SystemExit from a plugin must be recorded"
    assert list(report.loaded) == ["fine"], "the other plugin must still load"


def test_keyboard_interrupt_is_never_swallowed() -> None:
    def interrupt():
        raise KeyboardInterrupt

    with pytest.raises(KeyboardInterrupt):
        load_plugins([StubEntryPoint("ctrl-c", "x:y", interrupt)])


def test_errors_raised_while_importing_a_plugin_are_recorded_and_triple_duplicates_fail() -> None:
    def boom():
        raise RuntimeError("plugin exploded on import")

    report = load_plugins(
        [
            StubEntryPoint("broken", "x:y", boom),
            ep("same", "collections:OrderedDict"),
            ep("same", "json:JSONDecoder"),
            ep("same", "collections:deque"),
        ]
    )
    assert isinstance(report.failures["broken"], RuntimeError)
    assert "same" not in report.loaded
    assert isinstance(report.failures["same"], ValueError) and "duplicate" in str(report.failures["same"])


def test_discover_reads_the_requested_group_and_applies_validation(monkeypatch) -> None:
    import importlib.metadata

    import plugins

    asked: list[str] = []

    def fake_entry_points(*, group: str):
        asked.append(group)
        return [ep("b", "json:dumps"), ep("a", "collections:OrderedDict")]

    monkeypatch.setattr(importlib.metadata, "entry_points", fake_entry_points)
    if hasattr(plugins, "entry_points"):
        monkeypatch.setattr(plugins, "entry_points", fake_entry_points)

    report = discover(G, validate=lambda obj: isinstance(obj, type))
    assert asked == [G], "discover must query entry_points(group=group)"
    assert list(report.loaded) == ["a"]
    assert isinstance(report.failures["b"], TypeError)
