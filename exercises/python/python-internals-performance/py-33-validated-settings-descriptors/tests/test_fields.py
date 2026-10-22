import pytest

from fields import BoundedFloat, CompletionSettings, ValidationError


def test_valid_values_are_stored_per_instance() -> None:
    a = CompletionSettings(0.2, 100, "small")
    b = CompletionSettings(1.5, 4000, "large")
    assert (a.temperature, a.max_tokens, a.model) == (0.2, 100, "small")
    assert (b.temperature, b.max_tokens, b.model) == (1.5, 4000, "large")
    assert a.__dict__ == {"temperature": 0.2, "max_tokens": 100, "model": "small"}


def test_ints_are_coerced_to_float() -> None:
    s = CompletionSettings(1, 10, "small")
    assert s.temperature == 1.0 and isinstance(s.temperature, float)


@pytest.mark.parametrize(
    "kwargs, fragment",
    [
        ({"temperature": 3.0, "max_tokens": 10, "model": "small"}, "temperature"),
        ({"temperature": 0.5, "max_tokens": 0, "model": "small"}, "max_tokens"),
        ({"temperature": 0.5, "max_tokens": 10, "model": "huge"}, "model"),
        ({"temperature": True, "max_tokens": 10, "model": "small"}, "temperature"),
        ({"temperature": 0.5, "max_tokens": 10.5, "model": "small"}, "max_tokens"),
    ],
)
def test_invalid_values_raise_validation_error(kwargs: dict, fragment: str) -> None:
    with pytest.raises(ValidationError, match=fragment):
        CompletionSettings(**kwargs)


def test_data_descriptor_beats_instance_dict() -> None:
    s = CompletionSettings(0.5, 10, "small")
    s.__dict__["temperature"] = 99.0  # bypasses validation, but reads still go via __get__
    assert s.temperature == 99.0
    with pytest.raises(ValidationError):
        s.temperature = 99.0


def test_class_access_returns_descriptor_and_names_are_set() -> None:
    field = CompletionSettings.temperature
    assert isinstance(field, BoundedFloat)
    assert field.name == "temperature"


def test_unset_attribute_and_delete() -> None:
    s = CompletionSettings(0.5, 10, "small")
    del s.model
    with pytest.raises(AttributeError):
        s.model
    with pytest.raises(AttributeError):
        del s.model


def test_error_message_names_the_field_and_the_offending_value() -> None:
    with pytest.raises(ValidationError) as info:
        CompletionSettings(0.5, 10, "huge")
    message = str(info.value)
    assert "model" in message and "huge" in message, f"message should name the field and value: {message!r}"


def test_bounds_are_inclusive_and_non_numbers_are_rejected() -> None:
    low = CompletionSettings(0.0, 1, "small")
    high = CompletionSettings(2.0, 128_000, "large")
    assert (low.temperature, low.max_tokens) == (0.0, 1)
    assert (high.temperature, high.max_tokens) == (2.0, 128_000)
    for bad in ("0.5", None, [1]):
        with pytest.raises(ValidationError):
            CompletionSettings(bad, 10, "small")
    with pytest.raises(ValidationError):
        CompletionSettings(0.5, True, "small")
    with pytest.raises(ValidationError):
        CompletionSettings(2.0001, 10, "small")
