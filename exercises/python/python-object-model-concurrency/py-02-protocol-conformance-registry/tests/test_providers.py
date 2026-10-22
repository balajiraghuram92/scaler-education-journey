from typing import Protocol

import pytest

from providers import ETAProvider, ProviderRegistry, conformance_errors


class Good:
    def estimate_minutes(self, origin, destination):
        return 12.0


class WrongArity:
    def estimate_minutes(self):
        return 1.0


class WrongNames:
    def estimate_minutes(self, a, b):
        return 1.0


class Missing:
    pass


class NotCallable:
    estimate_minutes = 5


def test_good_candidate_has_no_errors_as_class_and_instance():
    assert conformance_errors(Good, ETAProvider) == [], "a conforming class must give no errors"
    assert conformance_errors(Good(), ETAProvider) == [], "a conforming instance must give no errors"


def test_isinstance_is_fooled_but_conformance_is_not():
    assert isinstance(WrongArity(), ETAProvider), "isinstance only checks names"
    assert conformance_errors(WrongArity(), ETAProvider), "the signature must be checked as well"
    assert conformance_errors(WrongArity, ETAProvider), "classes are checked too"


def test_wrong_parameter_names_are_reported():
    (err,) = conformance_errors(WrongNames, ETAProvider)
    assert err.startswith("signature mismatch: estimate_minutes"), err
    assert "'origin'" in err and "'a'" in err, "the message should show expected and actual names"


def test_missing_and_not_callable():
    assert conformance_errors(Missing, ETAProvider) == ["missing method: estimate_minutes"]
    assert conformance_errors(NotCallable, ETAProvider) == ["not callable: estimate_minutes"]
    assert conformance_errors(object(), ETAProvider) == ["missing method: estimate_minutes"]


def test_properties_are_not_executed_and_dunders_are_skipped():
    class Exploding:
        @property
        def estimate_minutes(self):
            raise RuntimeError("property was executed")

    assert conformance_errors(Exploding, ETAProvider) == ["not callable: estimate_minutes"]

    class Sized(Protocol):
        def __len__(self) -> int: ...

        def size_hint(self, kind: str) -> int: ...

    class OnlyHint:
        def size_hint(self, kind):
            return 1

    assert conformance_errors(OnlyHint, Sized) == [], "dunder members of the protocol must be skipped"


def test_registry_registers_returns_class_and_creates_with_arguments():
    reg = ProviderRegistry(ETAProvider)

    class Configured:
        def __init__(self, key, *, region="eu"):
            self.key, self.region = key, region

        def estimate_minutes(self, origin, destination):
            return 1.0

    assert reg.register("configured")(Configured) is Configured, "the decorator must return the class unchanged"
    reg.register("good")(Good)
    made = reg.create("configured", "k1", region="us")
    assert isinstance(made, Configured) and (made.key, made.region) == ("k1", "us"), "create forwards *args and **kwargs"
    assert reg.names() == ["configured", "good"]


def test_registry_rejects_bad_provider_with_actionable_reasons():
    reg = ProviderRegistry(ETAProvider)

    class Bad:
        def estimate_minutes(self):
            return 1.0

    with pytest.raises(TypeError) as info:
        reg.register("bad")(Bad)
    assert str(info.value) == (
        "Bad does not satisfy ETAProvider: signature mismatch: estimate_minutes('origin', 'destination') != ()"
    )
    assert reg.names() == [], "a rejected class must not be stored"


def test_registry_joins_multiple_reasons_with_semicolons():
    class Two(Protocol):
        def first(self, x: int) -> int: ...

        def second(self, y: int) -> int: ...

    assert conformance_errors(Missing, Two) == ["missing method: first", "missing method: second"], (
        "every failing member of the protocol must be reported, in declaration order"
    )
    reg = ProviderRegistry(Two)
    with pytest.raises(TypeError, match="missing method: first; missing method: second"):
        reg.register("none")(Missing)


def test_registry_rejects_duplicates_and_keeps_the_original():
    reg = ProviderRegistry(ETAProvider)
    reg.register("a")(Good)

    class Other:
        def estimate_minutes(self, origin, destination):
            return 2.0

    with pytest.raises(ValueError):
        reg.register("a")(Other)
    assert isinstance(reg.create("a"), Good), "the first registration must stay in place"


def test_unknown_provider_lists_known_names():
    reg = ProviderRegistry(ETAProvider)
    reg.register("alpha")(Good)
    with pytest.raises(KeyError) as info:
        reg.create("zzz")
    message = str(info.value)
    assert "zzz" in message and "alpha" in message, f"KeyError must name the unknown and the known providers, got {message}"
