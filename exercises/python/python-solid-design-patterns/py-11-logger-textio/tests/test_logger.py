import threading

import pytest

from logger.logger import LogLevel
from logger.logger_impl import LoggerImpl


def _reset():
    try:
        LoggerImpl.reset_instance()
    except NotImplementedError:
        pass


@pytest.fixture(autouse=True)
def fresh_singleton():
    _reset()
    yield
    _reset()


def test_get_instance_returns_the_same_logger():
    log = LoggerImpl.get_instance()
    assert isinstance(log, LoggerImpl)
    assert LoggerImpl.get_instance() is log


def test_same_instance_across_threads():
    n = 8
    barrier = threading.Barrier(n)
    seen = []

    def worker():
        barrier.wait(timeout=5)
        seen.append(LoggerImpl.get_instance())

    threads = [threading.Thread(target=worker) for _ in range(n)]
    for t in threads:
        t.start()
    for t in threads:
        t.join(timeout=5)
    assert len(seen) == n
    assert len({id(i) for i in seen}) == 1, "double-checked locking must yield exactly one logger"


def test_reset_instance_gives_a_fresh_logger():
    first = LoggerImpl.get_instance()
    LoggerImpl.reset_instance()
    second = LoggerImpl.get_instance()
    assert second is not first
    assert second.get_log_file() is None, "a new logger has no log file yet"


def test_log_without_a_file_raises_runtime_error():
    log = LoggerImpl.get_instance()
    with pytest.raises(RuntimeError):
        log.log(LogLevel.INFO, "nowhere to write")


def test_log_writes_a_line_with_level_and_message(tmp_path):
    path = tmp_path / "app.log"
    log = LoggerImpl.get_instance()
    log.set_log_file(str(path))
    assert log.get_log_file() == str(path)
    log.log(LogLevel.INFO, "service started")
    log.log(LogLevel.ERROR, "disk full")
    log.flush()
    lines = path.read_text().splitlines()
    assert len(lines) == 2, f"expected one line per log call, got {lines}"
    assert "service started" in lines[0] and "disk full" in lines[1]
    assert any(tag in lines[0] for tag in (str(LogLevel.INFO.value), LogLevel.INFO.name)), "the line must carry the level"
    assert lines[0].startswith("["), "the line starts with a bracketed timestamp"


def test_set_log_file_appends_and_switches_files(tmp_path):
    first, second = tmp_path / "a.log", tmp_path / "b.log"
    first.write_text("existing line\n")
    log = LoggerImpl.get_instance()
    log.set_log_file(str(first))
    log.log(LogLevel.INFO, "to first")
    log.set_log_file(str(second))  # must close the first handle, flushing it
    log.log(LogLevel.INFO, "to second")
    log.close()
    assert first.read_text().splitlines()[0] == "existing line", "append mode must keep existing content"
    assert "to first" in first.read_text() and "to second" not in first.read_text()
    assert "to second" in second.read_text()


def test_close_clears_the_handle_so_logging_fails_again(tmp_path):
    log = LoggerImpl.get_instance()
    log.set_log_file(str(tmp_path / "x.log"))
    log.close()
    log.close()  # closing twice is harmless
    log.flush()  # flushing with no handle is harmless
    with pytest.raises(RuntimeError):
        log.log(LogLevel.DEBUG, "after close")


def test_set_log_file_wraps_io_errors(tmp_path):
    log = LoggerImpl.get_instance()
    with pytest.raises(RuntimeError):
        log.set_log_file(str(tmp_path / "missing-dir" / "x.log"))
