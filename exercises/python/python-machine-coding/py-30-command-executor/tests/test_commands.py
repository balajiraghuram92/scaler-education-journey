import pytest

from commands import Command, CommandError, CommandExecutor, RegisterUser, SettleUpUser


def make():
    directory: dict[str, str] = {}
    calls: list[int] = []

    def settle(uid: int) -> list[str]:
        calls.append(uid)
        return [f"u{uid} pays u2 100", "u3 pays u1 50"] if uid == 1 else []

    executor = CommandExecutor(
        [RegisterUser(directory, hasher=lambda pw: "h:" + pw[::-1]), SettleUpUser(settle)]
    )
    return executor, directory, calls


def test_register_and_duplicate_phone():
    executor, directory, _ = make()
    assert executor.execute("Register asha 9876543210 s3cret") == "Registered asha"
    assert directory == {"9876543210": "h:terc3s"}          # hashed, never plain
    assert executor.execute("  REGISTER ravi   9876543210  pw ") == "Error: phone already registered"
    assert list(directory) == ["9876543210"]


def test_settle_up_user_output():
    executor, _, calls = make()
    assert executor.execute("u1 SettleUp") == "u1 pays u2 100\nu3 pays u1 50"
    assert executor.execute("U7 SETTLEUP") == "Nothing to settle"
    assert calls == [1, 7]


@pytest.mark.parametrize(
    "text",
    [
        "",
        "   ",
        "u1 SettleUp now",
        "g1 SettleUp",
        "u SettleUp",
        "u1x SettleUp",
        "register asha 123 pw",
        "registerx asha 9876543210 pw",
        "register asha 9876543210",
        "delete g1",
    ],
)
def test_strict_matching(text):
    executor, directory, calls = make()
    assert executor.execute(text) == "Invalid command"
    assert directory == {} and calls == []


def test_first_match_wins_and_new_commands_need_no_executor_change():
    class Help(Command):
        def matches(self, user_input: str) -> bool:
            return user_input.strip().lower() == "help"

        def execute(self, user_input: str) -> str:
            return "commands: register, settleup"

    class Greedy(Command):
        def matches(self, user_input: str) -> bool:
            return True

        def execute(self, user_input: str) -> str:
            return "greedy"

    assert CommandExecutor([Help(), Greedy()]).execute("HELP") == "commands: register, settleup"
    assert CommandExecutor([Greedy(), Help()]).execute("help") == "greedy"


def test_only_command_errors_are_converted():
    class Boom(Command):
        def matches(self, user_input: str) -> bool:
            return True

        def execute(self, user_input: str) -> str:
            raise ZeroDivisionError

    class Soft(Boom):
        def execute(self, user_input: str) -> str:
            raise CommandError("nope")

    assert CommandExecutor([Soft()]).execute("x") == "Error: nope"
    with pytest.raises(ZeroDivisionError):
        CommandExecutor([Boom()]).execute("x")


def test_command_is_abstract():
    with pytest.raises(TypeError):
        Command()


def test_register_rejects_extra_words_and_non_digit_phones():
    executor, directory, _ = make()
    for text in (
        "register asha 9876543210 pw extra",
        "register asha 98765x3210 pw",
        "register asha 98765432100 pw",
        "register as-ha 9876543210 pw",
    ):
        assert executor.execute(text) == "Invalid command", f"{text!r} must not match"
    assert directory == {}


def test_matches_never_raises_on_odd_input():
    for command in (RegisterUser({}, hasher=str), SettleUpUser(lambda uid: [])):
        for text in ("", " ", "\t\n", "u", "register", "\u00e9\u00e9", "u١ settleup"):
            assert command.matches(text) in (True, False), f"matches({text!r}) must return a bool"
