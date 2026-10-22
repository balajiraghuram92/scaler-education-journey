import re
from abc import ABC, abstractmethod
from collections.abc import Callable, Sequence


class CommandError(Exception):
    pass


class Command(ABC):
    @abstractmethod
    def matches(self, user_input: str) -> bool: ...

    @abstractmethod
    def execute(self, user_input: str) -> str: ...


class CommandExecutor:
    def __init__(self, commands: Sequence[Command]) -> None:
        self.commands = list(commands)

    def execute(self, user_input: str) -> str:
        for command in self.commands:
            if command.matches(user_input):
                try:
                    return command.execute(user_input)
                except CommandError as exc:
                    return f"Error: {exc}"
        return "Invalid command"


class RegisterUser(Command):
    _RE = re.compile(
        r"register\s+(?P<name>\w+)\s+(?P<phone>\d{10})\s+(?P<password>\S+)",
        re.IGNORECASE,
    )

    def __init__(self, directory: dict[str, str], hasher: Callable[[str], str]) -> None:
        self.directory = directory
        self.hasher = hasher

    def matches(self, user_input: str) -> bool:
        return self._RE.fullmatch(user_input.strip()) is not None

    def execute(self, user_input: str) -> str:
        m = self._RE.fullmatch(user_input.strip())
        if m is None:
            raise CommandError("malformed register command")
        phone = m["phone"]
        if phone in self.directory:
            raise CommandError("phone already registered")
        self.directory[phone] = self.hasher(m["password"])
        return f"Registered {m['name']}"


class SettleUpUser(Command):
    def __init__(self, settle: Callable[[int], list[str]]) -> None:
        self.settle = settle

    def matches(self, user_input: str) -> bool:
        words = user_input.split()
        return (
            len(words) == 2
            and words[1].lower() == "settleup"
            and words[0][:1].lower() == "u"
            and words[0][1:].isdigit()
        )

    def execute(self, user_input: str) -> str:
        user_id = int(user_input.split()[0][1:])
        lines = self.settle(user_id)
        return "\n".join(lines) if lines else "Nothing to settle"
