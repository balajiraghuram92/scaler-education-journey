"""Fake tracker: records posted comments and webhook events in memory.

Durable history lives in the writebacks table; this adapter is the transport.
"""
from __future__ import annotations

from dataclasses import dataclass, field


@dataclass
class PostedComment:
    ref: str
    ticket_key: str
    author: str
    text: str


@dataclass
class WebhookEvent:
    event: str  # created | updated | commented
    key: str
    rerun: bool = False


class FakeTracker:
    def __init__(self) -> None:
        self.posted: list[PostedComment] = []
        self.webhooks: list[WebhookEvent] = []
        self._counter = 0

    def post_comment(self, ticket_key: str, author: str, text: str) -> str:
        self._counter += 1
        ref = f"FC-{self._counter:05d}"
        self.posted.append(PostedComment(ref, ticket_key, author, text))
        return ref

    def receive_webhook(self, event: WebhookEvent) -> None:
        self.webhooks.append(event)

    def reset(self) -> None:
        self.posted.clear()
        self.webhooks.clear()
        self._counter = 0


TRACKER = FakeTracker()
