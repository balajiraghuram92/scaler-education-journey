import pytest

from chat import Completion, FallbackChat, ProviderError, contract_violations


class EchoModel:
    def __init__(self) -> None:
        self.calls = 0
        self.last_max_tokens = None

    def complete(self, prompt: str, *, max_tokens: int = 512) -> Completion:
        self.calls += 1
        self.last_max_tokens = max_tokens
        return Completion(prompt[:max_tokens])


class DownModel:
    def __init__(self) -> None:
        self.calls = 0

    def complete(self, prompt: str, *, max_tokens: int = 512) -> Completion:
        self.calls += 1
        raise ProviderError("503")


class BuggyModel:
    def complete(self, prompt: str, *, max_tokens: int = 512) -> Completion:
        raise ValueError("bug in adapter")


class CappedModel:
    def complete(self, prompt: str, *, max_tokens: int = 512) -> Completion:
        if max_tokens > 256:
            raise ValueError("max_tokens must be <= 256")
        return Completion(prompt[:max_tokens])


class WrongTypeModel:
    def complete(self, prompt: str, *, max_tokens: int = 512):
        return "just a string"


def test_first_success_wins_and_later_models_are_not_called():
    first, second = EchoModel(), EchoModel()
    assert FallbackChat([first, second]).complete("hello").text == "hello"
    assert (first.calls, second.calls) == (1, 0), "the second model must not be called after a success"


def test_falls_back_on_provider_error_and_forwards_max_tokens():
    down, echo = DownModel(), EchoModel()
    result = FallbackChat([down, echo]).complete("hello", max_tokens=3)
    assert result.text == "hel", "max_tokens must be forwarded to the model that answers"
    assert (down.calls, echo.calls) == (1, 1)


def test_all_failing_raises_exception_group_with_every_cause():
    with pytest.raises(ExceptionGroup) as info:
        FallbackChat([DownModel(), DownModel(), DownModel()]).complete("hi")
    assert len(info.value.exceptions) == 3, "the group must carry every ProviderError"
    assert all(isinstance(e, ProviderError) for e in info.value.exceptions)
    assert info.value.message == "all providers failed"


def test_programming_errors_are_not_swallowed():
    echo = EchoModel()
    with pytest.raises(ValueError):
        FallbackChat([BuggyModel(), echo]).complete("hi")
    assert echo.calls == 0, "a bug must not silently route traffic to the next model"


def test_empty_model_list_is_rejected():
    with pytest.raises(ValueError):
        FallbackChat([])


def test_contract_accepts_compliant_model():
    assert contract_violations(EchoModel()) == []
    assert contract_violations(DownModel()) == [], "ProviderError is allowed by the contract"


def test_contract_flags_strengthened_precondition():
    problems = contract_violations(CappedModel())
    assert any(p.startswith("default") for p in problems), "default (512) exceeds the cap, so it must be flagged"
    assert any(p.startswith("max_tokens=4096") for p in problems)
    assert not any(p.startswith("max_tokens=1:") for p in problems), "max_tokens=1 is fine for this model"


def test_contract_flags_wrong_return_type():
    problems = contract_violations(WrongTypeModel())
    assert len(problems) == 3, f"expected one message per call, got {problems}"


def test_composite_is_itself_substitutable():
    assert contract_violations(FallbackChat([DownModel(), EchoModel()])) == []
    assert contract_violations(FallbackChat([CappedModel()])) != [], "the composite inherits its members' violations"
