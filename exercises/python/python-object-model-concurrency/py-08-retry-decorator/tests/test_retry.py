from unittest.mock import patch

import pytest

from main.retry import retry


def test_returns_result_on_first_success_without_sleeping():
    calls = []

    @retry(times=5)
    def greet(name):
        calls.append(name)
        return f"Hello, {name}"

    with patch("main.retry.time.sleep") as fake_sleep:
        result = greet("Maya")

    assert result == "Hello, Maya"
    assert calls == ["Maya"], "a successful call must not be repeated"
    fake_sleep.assert_not_called()


def test_retries_until_function_succeeds():
    calls = []

    @retry(times=3)
    def sometimes_fails():
        calls.append("called")
        if len(calls) < 3:
            raise ValueError("not yet")
        return "done"

    with patch("main.retry.time.sleep") as fake_sleep:
        result = sometimes_fails()

    assert result == "done"
    assert len(calls) == 3, "expected 3 attempts: two failures and one success"
    assert fake_sleep.call_count == 2, "sleep between failed attempts only"


def test_passes_args_and_kwargs_to_decorated_function():
    @retry(times=2)
    def add_numbers(first, second=0):
        return first + second

    assert add_numbers(5, second=7) == 12
    assert add_numbers(1, 2) == 3


def test_waits_delay_between_failed_attempts_but_not_after_the_last():
    @retry(times=3, delay=0.25)
    def always_fails():
        raise OSError("temporary problem")

    with patch("main.retry.time.sleep") as fake_sleep:
        with pytest.raises(RuntimeError):
            always_fails()

    assert fake_sleep.call_count == 2, "3 attempts means 2 waits, none after the final failure"
    fake_sleep.assert_called_with(0.25)


def test_single_attempt_never_sleeps():
    @retry(times=1, delay=5)
    def always_fails():
        raise KeyError("missing")

    with patch("main.retry.time.sleep") as fake_sleep:
        with pytest.raises(RuntimeError, match="Function failed after 1 attempts"):
            always_fails()

    fake_sleep.assert_not_called()


def test_raises_runtime_error_after_all_attempts_fail():
    calls = []

    @retry(times=4)
    def always_fails():
        calls.append("called")
        raise KeyError("missing")

    with patch("main.retry.time.sleep"):
        with pytest.raises(RuntimeError) as info:
            always_fails()

    assert str(info.value) == "Function failed after 4 attempts"
    assert len(calls) == 4, "the function must be called exactly `times` times"


def test_runtime_error_is_chained_to_the_last_exception():
    attempts = []

    @retry(times=3)
    def failing_differently():
        attempts.append(1)
        raise ValueError(f"failure {len(attempts)}")

    with patch("main.retry.time.sleep"):
        with pytest.raises(RuntimeError) as info:
            failing_differently()

    assert isinstance(info.value.__cause__, ValueError)
    assert str(info.value.__cause__) == "failure 3", "__cause__ must be the last exception, not the first"


def test_preserves_function_name_and_docstring():
    @retry(times=2)
    def sample_function():
        """This is the original docstring."""
        return "ok"

    assert sample_function.__name__ == "sample_function"
    assert sample_function.__doc__ == "This is the original docstring."


@pytest.mark.parametrize("value", [0, -1, 1.5, "3", None, True, False])
def test_times_must_be_a_positive_integer_and_is_checked_eagerly(value):
    with pytest.raises(ValueError) as info:
        retry(value)  # no function has been decorated or called yet
    assert str(info.value) == "times must be a positive integer"


@pytest.mark.parametrize("value", [-1, -0.1, "1", None, True, False])
def test_delay_must_be_non_negative_number_and_is_checked_eagerly(value):
    with pytest.raises(ValueError) as info:
        retry(3, delay=value)
    assert str(info.value) == "delay must be non-negative"


@pytest.mark.parametrize("value", [0, 0.0, 1, 0.5])
def test_valid_delay_values_are_accepted(value):
    decorator = retry(1, delay=value)
    assert callable(decorator), "retry(...) returns a decorator"
