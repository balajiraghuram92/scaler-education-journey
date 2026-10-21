from __future__ import annotations

import dataclasses
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
        return Message.MessageBuilder()

    class MessageBuilder(Builder["Message"]):

        def __init__(self):
            self._instance = Message(None, None, None, None, None, None)

        def message_type(self, message_type: MessageType) -> Message.MessageBuilder:
            self._instance.message_type = message_type
            return self

        def content(self, content: str) -> Message.MessageBuilder:
            self._instance.content = content
            return self

        def sender(self, sender: str) -> Message.MessageBuilder:
            self._instance.sender = sender
            return self

        def recipient(self, recipient: str) -> Message.MessageBuilder:
            self._instance.recipient = recipient
            return self

        def is_delivered(self, is_delivered: bool) -> Message.MessageBuilder:
            self._instance.is_delivered = is_delivered
            return self

        def timestamp(self, timestamp: int) -> Message.MessageBuilder:
            self._instance.timestamp = timestamp
            return self

        def build(self) -> Message:
            return dataclasses.replace(self._instance)
