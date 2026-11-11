"""Fake chat: records posted messages in memory."""
from __future__ import annotations

from dataclasses import dataclass


@dataclass
class PostedMessage:
    ref: str
    thread_key: str
    author: str
    text: str


class FakeChat:
    def __init__(self) -> None:
        self.posted: list[PostedMessage] = []
        self._counter = 0

    def post_message(self, thread_key: str, author: str, text: str) -> str:
        self._counter += 1
        ref = f"CH-{self._counter:05d}"
        self.posted.append(PostedMessage(ref, thread_key, author, text))
        return ref

    def reset(self) -> None:
        self.posted.clear()
        self._counter = 0


CHAT = FakeChat()
