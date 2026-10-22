from collections.abc import Callable, Sequence


class CommandError(Exception):
    """A domain error that the executor turns into an ``Error: ...`` message."""


class Command:
    """Make this an abstract base class (``abc.ABC``) with two abstract methods:

    - ``matches(self, user_input: str) -> bool``  (must never raise on odd input)
    - ``execute(self, user_input: str) -> str``
    """


class CommandExecutor:
    """Runs the FIRST matching command.

    - returns the command's result
    - ``CommandError`` -> ``f"Error: {message}"``
    - nothing matches (including empty / whitespace-only input) -> ``"Invalid command"``
    - any other exception propagates
    """

    def __init__(self, commands: Sequence[Command]) -> None:
        raise NotImplementedError("Implement CommandExecutor.__init__")

    def execute(self, user_input: str) -> str:
        raise NotImplementedError("Implement CommandExecutor.execute")


class RegisterUser(Command):
    """``register <name> <phone> <password>`` (keyword case-insensitive, any run of whitespace as separator).

    ``name`` is ``\w+``, ``phone`` exactly 10 digits, ``password`` has no spaces. Matching must be exact
    (``fullmatch``), never a loose ``startswith``. Stores ``directory[phone] = hasher(password)`` (never the
    plain password) and returns ``"Registered <name>"``. An existing phone -> ``CommandError("phone already registered")``.
    """

    def __init__(self, directory: dict[str, str], hasher: Callable[[str], str]) -> None:
        raise NotImplementedError("Implement RegisterUser.__init__")

    def matches(self, user_input: str) -> bool:
        raise NotImplementedError("Implement RegisterUser.matches")

    def execute(self, user_input: str) -> str:
        raise NotImplementedError("Implement RegisterUser.execute")


class SettleUpUser(Command):
    """``u<digits> settleup`` - exactly two words, keyword and the leading ``u`` case-insensitive.

    Calls ``settle(user_id)`` and returns the lines joined by ``"\n"``, or ``"Nothing to settle"`` if empty.
    """

    def __init__(self, settle: Callable[[int], list[str]]) -> None:
        raise NotImplementedError("Implement SettleUpUser.__init__")

    def matches(self, user_input: str) -> bool:
        raise NotImplementedError("Implement SettleUpUser.matches")

    def execute(self, user_input: str) -> str:
        raise NotImplementedError("Implement SettleUpUser.execute")
