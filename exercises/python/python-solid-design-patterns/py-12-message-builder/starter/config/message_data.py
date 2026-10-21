from __future__ import annotations

from dataclasses import dataclass
from enum import Enum

from .builder import Builder


class MessageType(Enum):
    TEXT = "TEXT"
    IMAGE = "IMAGE"
    AUDIO = "AUDIO"
    VIDEO = "VIDEO"


@dataclass
class Message:
    message_type: MessageType
    content: str
    sender: str
    recipient: str
    is_delivered: bool
    timestamp: int

    @staticmethod
    def builder() -> MessageBuilder:
        """Return a NEW MessageBuilder on every call."""
        raise NotImplementedError("Implement Message.builder")

    class MessageBuilder(Builder["Message"]):
        """Fluent builder: every setter stores its value and returns the builder.

        Keep the working state in ``self._instance`` (a Message with every field
        ``None``). ``build()`` returns a configured Message that is independent of
        the builder: later setter calls must not change an object already built.
        """

        def __init__(self):
            raise NotImplementedError("Implement the constructor")

        def message_type(self, message_type: MessageType) -> Message.MessageBuilder:
            raise NotImplementedError("Implement message_type")

        def content(self, content: str) -> Message.MessageBuilder:
            raise NotImplementedError("Implement content")

        def sender(self, sender: str) -> Message.MessageBuilder:
            raise NotImplementedError("Implement sender")

        def recipient(self, recipient: str) -> Message.MessageBuilder:
            raise NotImplementedError("Implement recipient")

        def is_delivered(self, is_delivered: bool) -> Message.MessageBuilder:
            raise NotImplementedError("Implement is_delivered")

        def timestamp(self, timestamp: int) -> Message.MessageBuilder:
            raise NotImplementedError("Implement timestamp")

        def build(self) -> Message:
            raise NotImplementedError("Implement build")
