import threading

import pytest

from config.config_manager_impl import FileBasedConfigurationManagerImpl as Config


@pytest.fixture(autouse=True)
def fresh_singleton():
    try:
        Config.reset_instance()
    except NotImplementedError:
        pass
    yield
    try:
        Config.reset_instance()
    except NotImplementedError:
        pass


def test_get_instance_returns_the_same_object():
    first = Config.get_instance()
    assert isinstance(first, Config)
    assert Config.get_instance() is first, "a second call must return the same instance"


def test_same_instance_across_threads():
    n = 8
    barrier = threading.Barrier(n)
    seen = []

    def worker():
        barrier.wait(timeout=5)  # release all threads together to provoke the race
        seen.append(Config.get_instance())

    threads = [threading.Thread(target=worker) for _ in range(n)]
    for t in threads:
        t.start()
    for t in threads:
        t.join(timeout=5)
    assert len(seen) == n, "all threads should finish"
    assert len({id(i) for i in seen}) == 1, "double-checked locking must yield exactly one instance"


def test_reset_instance_creates_a_new_object_and_state():
    first = Config.get_instance()
    first.set_configuration("k", "v")
    Config.reset_instance()
    second = Config.get_instance()
    assert second is not first, "after reset_instance a brand-new object is expected"
    assert second.get_configuration("k") is None, "the new instance starts empty"


def test_get_and_set_configuration():
    cfg = Config.get_instance()
    assert cfg.get_configuration("missing") is None
    cfg.set_configuration("name", "neuralascent")
    assert cfg.get_configuration("name") == "neuralascent"
    cfg.set_configuration("name", "other")
    assert cfg.get_configuration("name") == "other", "set overwrites an existing key"


def test_typed_access_and_set_with_value():
    cfg = Config.get_instance()
    cfg.set_configuration_with_value("port", 8080)
    assert cfg.get_configuration("port") == "8080", "values are stored as str(value)"
    assert cfg.get_configuration_with_type("port", int) == 8080
    assert cfg.get_configuration_with_type("nope", int) is None


def test_typed_access_with_bad_value_raises_value_error():
    cfg = Config.get_instance()
    cfg.set_configuration("port", "abc")
    with pytest.raises(ValueError):
        cfg.get_configuration_with_type("port", int)


def test_remove_and_clear():
    cfg = Config.get_instance()
    cfg.set_configuration("a", "1")
    cfg.set_configuration("b", "2")
    cfg.remove_configuration("a")
    cfg.remove_configuration("not-there")  # must not raise
    assert cfg.get_configuration("a") is None and cfg.get_configuration("b") == "2"
    cfg.clear()
    assert cfg.get_properties() == {}, "clear removes every setting"


def test_load_reads_key_value_lines_into_the_shared_instance(tmp_path):
    path = tmp_path / "config.properties"
    path.write_text("stringKey=stringValue\nintKey=42\n")
    cfg = Config.get_instance()
    cfg.load(path)
    assert cfg.get_configuration("stringKey") == "stringValue"
    assert cfg.get_configuration_with_type("intKey", int) == 42
    assert Config.get_instance().get_configuration("intKey") == "42", "the shared instance sees the loaded data"
