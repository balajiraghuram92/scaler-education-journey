import pytest

from notification import EmailChannel, NotificationChannel, PushChannel, SMSChannel


@pytest.fixture
def clean_registry():
    """Restore the shared registry after tests that define extra channels."""
    before = dict(NotificationChannel.registry)
    yield NotificationChannel.registry
    NotificationChannel.registry.clear()
    NotificationChannel.registry.update(before)


def test_builtin_channels_register_themselves():
    registry = NotificationChannel.registry
    assert registry.get("sms") is SMSChannel, "SMSChannel must register as 'sms'"
    assert registry.get("email") is EmailChannel, "EmailChannel must register as 'email'"
    assert registry.get("push") is PushChannel, "PushChannel must register as 'push'"
    assert NotificationChannel not in registry.values(), "the abstract base must not register itself"


def test_sms_send_prints_the_documented_line(capsys):
    NotificationChannel.registry["sms"]().send("Alice", "Your cab has arrived.")
    assert capsys.readouterr().out == "Sending SMS to Alice: Your cab has arrived.\n"


@pytest.mark.parametrize("name, user, message", [("email", "Bob", "Trip receipt"), ("push", "Charlie", "Driver is nearby")])
def test_other_channels_name_channel_user_and_message(capsys, name, user, message):
    NotificationChannel.registry[name]().send(user, message)
    out = capsys.readouterr().out
    assert out.count("\n") == 1, "send must print exactly one line"
    assert name in out.lower() and user in out and message in out, f"line must name the {name} channel, user and message, got {out!r}"


def test_get_status_is_delivered_for_every_channel():
    for name in ("sms", "email", "push"):
        assert NotificationChannel.registry[name]().get_status("42") == "DELIVERED", name


def test_cannot_instantiate_abstract_channel_or_incomplete_subclass(clean_registry):
    with pytest.raises(TypeError):
        NotificationChannel()

    class OnlySend(NotificationChannel, channel_name="only-send"):
        def send(self, user, message):
            pass

    with pytest.raises(TypeError):
        OnlySend()


def test_new_subclass_with_name_registers_at_class_creation(clean_registry):
    class SlackChannel(NotificationChannel, channel_name="slack"):
        def send(self, user, message):
            print("slack")

        def get_status(self, message_id):
            return "QUEUED"

    assert clean_registry["slack"] is SlackChannel, "the hook must run when the subclass is defined"
    assert isinstance(clean_registry["slack"](), SlackChannel)


def test_subclass_without_name_is_created_but_not_registered(clean_registry):
    size = len(clean_registry)

    class Helper(NotificationChannel):
        def send(self, user, message):
            pass

        def get_status(self, message_id):
            return "X"

    assert len(clean_registry) == size, "unnamed subclasses must stay out of the registry"
    assert Helper().get_status("1") == "X"


def test_hook_forwards_other_class_keywords_to_super(clean_registry):
    class Tagged:
        def __init_subclass__(cls, tag=None, **kwargs):
            super().__init_subclass__(**kwargs)
            cls.tag = tag

    class Tagged_Channel(NotificationChannel, Tagged, channel_name="tagged", tag="blue"):
        def send(self, user, message):
            pass

        def get_status(self, message_id):
            return "OK"

    assert clean_registry["tagged"] is Tagged_Channel
    assert Tagged_Channel.tag == "blue", "unconsumed keywords must be forwarded with super().__init_subclass__(**kwargs)"


def test_unknown_class_keyword_is_still_rejected(clean_registry):
    with pytest.raises(TypeError):
        class Bad(NotificationChannel, colour="red"):
            pass
