from config.message_data import Message, MessageType

SETTERS = {
    "message_type": MessageType.IMAGE,
    "content": "Hello World",
    "sender": "sender@example.com",
    "recipient": "recipient@example.com",
    "is_delivered": True,
    "timestamp": 1700000000,
}


def test_builder_returns_a_new_builder_each_time():
    assert Message.builder() is not Message.builder(), "builder() must create a fresh builder"


def test_every_setter_returns_the_same_builder_for_chaining():
    builder = Message.builder()
    for name, value in SETTERS.items():
        assert getattr(builder, name)(value) is builder, f"{name} must return the builder"


def test_every_setter_stores_its_value():
    for name, value in SETTERS.items():
        message = getattr(Message.builder(), name)(value).build()
        assert getattr(message, name) == value, f"{name} should set the {name} field"


def test_build_with_nothing_set_gives_all_none():
    message = Message.builder().build()
    assert isinstance(message, Message)
    assert message == Message(None, None, None, None, None, None)


def test_partial_message_leaves_other_fields_none():
    message = (
        Message.builder()
        .message_type(MessageType.TEXT)
        .content("Hello World")
        .sender("sender@example.com")
        .recipient("recipient@example.com")
        .build()
    )
    assert message.content == "Hello World" and message.message_type is MessageType.TEXT
    assert message.is_delivered is None and message.timestamp is None


def test_full_chain_builds_the_expected_message():
    message = (
        Message.builder()
        .message_type(MessageType.VIDEO)
        .content("clip.mp4")
        .sender("a")
        .recipient("b")
        .is_delivered(False)
        .timestamp(42)
        .build()
    )
    assert message == Message(MessageType.VIDEO, "clip.mp4", "a", "b", False, 42)


def test_two_builders_do_not_share_state():
    first = Message.builder().content("first")
    second = Message.builder().content("second")
    assert first.build().content == "first" and second.build().content == "second"


def test_built_object_is_independent_of_the_builder():
    builder = Message.builder().content("draft").sender("alice")
    first = builder.build()
    builder.content("final")
    second = builder.build()
    assert first.content == "draft", "a reused builder must not change an object that was already built"
    assert second.content == "final" and second.sender == "alice"
    assert first is not second, "each build() should return a new object"
