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
        return MessageBuilder(clock)


class MessageBuilder:
    def __init__(self, clock: Callable[[], int] | None = None) -> None:
        self._clock = clock or (lambda: int(time.time()))
        self._message_type: MessageType | None = None
        self._content = ""
        self._sender = ""
        self._recipient = ""
        self._is_delivered = False
        self._timestamp: int | None = None

    def message_type(self, message_type: MessageType) -> Self:
        self._message_type = message_type
        return self

    def content(self, content: str) -> Self:
        self._content = content
        return self

    def sender(self, sender: str) -> Self:
        self._sender = sender
        return self

    def recipient(self, recipient: str) -> Self:
        self._recipient = recipient
        return self

    def is_delivered(self, is_delivered: bool) -> Self:
        self._is_delivered = is_delivered
        return self

    def timestamp(self, timestamp: int) -> Self:
        self._timestamp = timestamp
        return self

    def build(self) -> Message:
        if self._message_type is None:
            raise ValueError("message_type is required")
        if not self._sender or not self._recipient:
            raise ValueError("sender and recipient are required")
        if self._message_type is MessageType.TEXT:
            if not self._content.strip():
                raise ValueError("TEXT messages need non-empty content")
        elif not self._content.startswith("https://"):
            raise ValueError(f"{self._message_type.value} messages need an https:// content URL")
        if self._timestamp is not None and self._timestamp < 0:
            raise ValueError("timestamp must be >= 0")
        timestamp = self._timestamp if self._timestamp is not None else self._clock()
        return Message(
            self._message_type, self._content, self._sender,
            self._recipient, self._is_delivered, timestamp,
        )
