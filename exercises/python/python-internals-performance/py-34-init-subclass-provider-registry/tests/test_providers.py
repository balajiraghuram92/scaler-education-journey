import pytest

from providers import Provider, UnknownProvider


@pytest.fixture(autouse=True)
def clean_registry():
    saved = dict(Provider.registry)
    yield
    Provider.registry.clear()
    Provider.registry.update(saved)


def test_subclass_registers_itself_with_default_and_explicit_names() -> None:
    class OpenAI(Provider):
        def complete(self, prompt: str) -> str:
            return "openai:" + prompt

    class Local(Provider, name="llama"):
        def complete(self, prompt: str) -> str:
            return "llama:" + prompt

    assert Provider.registry["openai"] is OpenAI
    assert Provider.registry["llama"] is Local
    assert OpenAI.name == "openai" and Local.name == "llama"


def test_duplicate_names_fail_at_class_creation() -> None:
    class A(Provider, name="dup"):
        def complete(self, prompt: str) -> str:
            return prompt

    with pytest.raises(TypeError, match="duplicate"):
        class B(Provider, name="dup"):
            def complete(self, prompt: str) -> str:
                return prompt


def test_missing_complete_fails_at_class_creation() -> None:
    with pytest.raises(TypeError, match="complete"):
        class Broken(Provider):
            pass

    assert "broken" not in Provider.registry


def test_create_passes_config_and_unknown_raises() -> None:
    class Echo(Provider):
        def __init__(self, prefix: str = "") -> None:
            self.prefix = prefix

        def complete(self, prompt: str) -> str:
            return self.prefix + prompt

    p = Provider.create("echo", prefix=">> ")
    assert p.complete("hi") == ">> hi"
    with pytest.raises(UnknownProvider, match="known: .*echo"):
        Provider.create("nope")


def test_subclass_of_subclass_inherits_complete_and_registers() -> None:
    class Base(Provider, name="base"):
        def complete(self, prompt: str) -> str:
            return "base"

    class Child(Base, name="child"):
        pass

    assert Provider.create("child").complete("x") == "base"


def test_failed_duplicate_leaves_the_original_registered() -> None:
    class First(Provider, name="same"):
        def complete(self, prompt: str) -> str:
            return "first"

    with pytest.raises(TypeError, match="duplicate"):
        class Second(Provider, name="same"):
            def complete(self, prompt: str) -> str:
                return "second"

    assert Provider.registry["same"] is First
    assert Provider.create("same").complete("x") == "first"


def test_extra_class_keywords_are_forwarded_to_the_next_init_subclass() -> None:
    seen: list[object] = []

    class Tracked:
        def __init_subclass__(cls, tag: object = None, **kwargs: object) -> None:
            super().__init_subclass__(**kwargs)
            seen.append(tag)

    class Tagged(Provider, Tracked, name="tagged", tag="blue"):
        def complete(self, prompt: str) -> str:
            return prompt

    assert seen == ["blue"], "unknown class keywords must be forwarded to super().__init_subclass__"
    assert Provider.registry["tagged"] is Tagged
