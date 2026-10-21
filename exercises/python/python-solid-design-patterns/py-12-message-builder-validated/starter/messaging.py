import time
from collections.abc import Callable
from dataclasses import dataclass
from enum import Enum
from typing import Self


class MessageType(Enum):
    TEXT = "TEXT"
    IMAGE = "IMAGE"
    AUDIO = "AUDIO"
    VIDEO = "VIDEO"


@dataclass(frozen=True, slots=True)
class Message:
    message_type: MessageType
    content: str
    sender: str
    recipient: str
    is_delivered: bool
    timestamp: int

    @staticmethod
    def builder(clock: Callable[[], int] | None = None) -> "MessageBuilder":
        """Return a MessageBuilder. ``clock`` is a zero-argument callable returning
        an int (default: current epoch seconds)."""
        raise NotImplementedError("Implement Message.builder")


class MessageBuilder:
    """Fluent, validating builder for Message.

    Setters (each returns the builder): message_type, content, sender, recipient,
    is_delivered, timestamp.

    ``build()`` raises ValueError when:
      - message_type is missing (message mentions ``message_type``)
      - sender or recipient is missing (mentions ``sender``)
      - a TEXT message has empty/blank content (mentions ``TEXT``)
      - an IMAGE/AUDIO/VIDEO message's content does not start with ``https://``
        (mentions ``https://``)
      - an explicit timestamp is negative

    With no explicit timestamp, ``build()`` uses the clock; an explicit one wins.
    Each ``build()`` returns a NEW immutable Message; later builder changes do not
    affect earlier messages. ``is_delivered`` defaults to False.
    """

    def __init__(self, clock: Callable[[], int] | None = None) -> None:
        raise NotImplementedError("Implement the constructor")

    def message_type(self, message_type: MessageType) -> Self:
        raise NotImplementedError("Implement message_type")

    def content(self, content: str) -> Self:
        raise NotImplementedError("Implement content")

    def sender(self, sender: str) -> Self:
        raise NotImplementedError("Implement sender")

    def recipient(self, recipient: str) -> Self:
        raise NotImplementedError("Implement recipient")

    def is_delivered(self, is_delivered: bool) -> Self:
        raise NotImplementedError("Implement is_delivered")

    def timestamp(self, timestamp: int) -> Self:
        raise NotImplementedError("Implement timestamp")

    def build(self) -> Message:
        raise NotImplementedError("Implement build")
