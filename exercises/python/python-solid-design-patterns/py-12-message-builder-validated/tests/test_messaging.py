from dataclasses import FrozenInstanceError

import pytest

from messaging import Message, MessageType


def text_builder():
    return (
        Message.builder(clock=lambda: 1_700_000_000)
        .message_type(MessageType.TEXT)
        .content("Hello World")
        .sender("a@example.com")
        .recipient("b@example.com")
    )


def test_text_message_builds_with_clock_timestamp():
    message = text_builder().build()
    assert isinstance(message, Message)
    assert message.content == "Hello World" and message.sender == "a@example.com"
    assert message.timestamp == 1_700_000_000, "timestamp must come from the injected clock"
    assert message.is_delivered is False


def test_setters_return_the_builder_and_is_delivered_is_applied():
    builder = text_builder()
    assert builder.is_delivered(True) is builder
    assert builder.build().is_delivered is True


def test_default_clock_is_epoch_seconds():
    message = (
        Message.builder().message_type(MessageType.TEXT).content("x").sender("a").recipient("b").build()
    )
    assert isinstance(message.timestamp, int) and message.timestamp > 1_600_000_000


def test_explicit_timestamp_wins_over_the_clock_and_negative_is_rejected():
    assert text_builder().timestamp(42).build().timestamp == 42
    assert text_builder().timestamp(0).build().timestamp == 0, "0 is a valid explicit timestamp"
    with pytest.raises(ValueError):
        text_builder().timestamp(-1).build()


def test_message_type_is_required():
    with pytest.raises(ValueError, match="message_type"):
        Message.builder().sender("a").recipient("b").content("x").build()


def test_sender_and_recipient_are_required():
    with pytest.raises(ValueError, match="sender"):
        text_builder().sender("").build()
    with pytest.raises(ValueError):
        text_builder().recipient("").build()


@pytest.mark.parametrize("content", ["", "   "])
def test_text_needs_non_empty_content(content):
    with pytest.raises(ValueError, match="TEXT"):
        text_builder().content(content).build()


@pytest.mark.parametrize("kind", [MessageType.IMAGE, MessageType.AUDIO, MessageType.VIDEO])
def test_media_needs_https_url(kind):
    ok = text_builder().message_type(kind).content("https://cdn.example.com/a.bin").build()
    assert ok.message_type is kind
    with pytest.raises(ValueError, match="https://"):
        text_builder().message_type(kind).content("Hello").build()
    with pytest.raises(ValueError, match="https://"):
        text_builder().message_type(kind).content("http://insecure/a.bin").build()


def test_message_is_immutable_and_builds_are_independent():
    builder = text_builder()
    first = builder.build()
    builder.content("changed")
    assert first.content == "Hello World", "later builder changes must not affect an earlier message"
    with pytest.raises(FrozenInstanceError):
        first.content = "x"
    assert builder.build() is not builder.build(), "each build() returns a new object"
