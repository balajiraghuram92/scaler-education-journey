import threading

import pytest

from slog import Logger, SingletonMeta


@pytest.fixture(autouse=True)
def clean():
    try:
        Logger.reset_instance()
    except NotImplementedError:
        pass
    yield
    try:
        Logger.reset_instance()
    except NotImplementedError:
        pass


def test_same_instance_every_time():
    first = Logger()
    assert Logger() is first, "the metaclass must return the cached instance"


def test_reset_gives_a_new_instance():
    first = Logger()
    Logger.reset_instance()
    assert Logger() is not first


def test_many_threads_get_one_instance():
    for _ in range(10):
        Logger.reset_instance()
        barrier = threading.Barrier(10)
        seen = []

        def worker():
            barrier.wait(timeout=5)
            seen.append(Logger())

        threads = [threading.Thread(target=worker) for _ in range(10)]
        for t in threads:
            t.start()
        for t in threads:
            t.join(timeout=5)
        assert len(seen) == 10
        assert len({id(x) for x in seen}) == 1, "double-checked locking must yield exactly one instance"


def test_metaclass_is_reusable_one_instance_per_class_and_init_runs_once():
    class A(metaclass=SingletonMeta):
        inits = 0

        def __init__(self):
            A.inits += 1

    class B(metaclass=SingletonMeta):
        pass

    assert A() is A()
    assert A.inits == 1, "__init__ must run exactly once"
    assert A() is not B(), "each class gets its own instance"
    assert isinstance(B(), B)
    A.reset_instance()
    B.reset_instance()


def test_reset_closes_the_instance(tmp_path):
    logger = Logger()
    logger.set_log_file(str(tmp_path / "app.log"))
    Logger.reset_instance()
    with pytest.raises(RuntimeError):
        logger.log("INFO", "closed by reset")


def test_log_before_set_log_file_raises():
    with pytest.raises(RuntimeError):
        Logger().log("INFO", "too early")


def test_log_after_close_raises(tmp_path):
    logger = Logger()
    logger.set_log_file(str(tmp_path / "app.log"))
    logger.close()
    with pytest.raises(RuntimeError):
        logger.log("INFO", "too late")


def test_log_line_format(tmp_path):
    path = tmp_path / "app.log"
    logger = Logger()
    logger.set_log_file(str(path))
    logger.log("INFO", "order shipped")
    logger.flush()
    line = path.read_text(encoding="utf-8").splitlines()[0]
    assert line.startswith("[") and "] [INFO] order shipped" in line, f"unexpected line format: {line!r}"
    assert logger.get_log_file() == str(path)


def test_concurrent_writes_produce_whole_lines(tmp_path):
    path = tmp_path / "app.log"
    logger = Logger()
    logger.set_log_file(str(path))

    def worker(n):
        for i in range(50):
            Logger().log("INFO", f"worker={n} line={i}")

    threads = [threading.Thread(target=worker, args=(n,)) for n in range(8)]
    for t in threads:
        t.start()
    for t in threads:
        t.join(timeout=10)
    logger.flush()
    lines = path.read_text(encoding="utf-8").splitlines()
    assert len(lines) == 400, f"expected 400 lines, got {len(lines)}"
    assert all(line.startswith("[") and "] [INFO] worker=" in line for line in lines), "lines must not interleave"
