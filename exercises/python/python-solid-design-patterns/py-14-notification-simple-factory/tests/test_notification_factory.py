import pytest

from notification.factory import NotificationFactory
from notification.products import (
    EmailNotification,
    Notification,
    NotificationType,
    PushNotification,
    SmsNotification,
)

EXPECTED = {
    NotificationType.EMAIL: EmailNotification,
    NotificationType.PUSH: PushNotification,
    NotificationType.SMS: SmsNotification,
}


@pytest.mark.parametrize("kind", list(NotificationType))
def test_factory_returns_the_right_concrete_type(kind):
    notification = NotificationFactory.create_notification(kind, "bob", "alice", "hello")
    assert type(notification) is EXPECTED[kind], f"{kind} should produce {EXPECTED[kind].__name__}"
    assert isinstance(notification, Notification)
    assert notification.notification_type() is kind


def test_args_are_unpacked_into_recipient_sender_message():
    notification = NotificationFactory.create_notification(NotificationType.SMS, "bob", "alice", "hello")
    assert (notification.recipient, notification.sender, notification.message) == ("bob", "alice", "hello")


def test_invalid_type_raises_value_error_with_message():
    for bad in ("EMAIL", None, 42):
        with pytest.raises(ValueError, match="Invalid notification type"):
            NotificationFactory.create_notification(bad, "bob", "alice", "hello")


def test_wrong_argument_count_is_an_error():
    with pytest.raises(TypeError):
        NotificationFactory.create_notification(NotificationType.EMAIL, "bob")


def test_send_notification_prints_recipient_sender_and_message(capsys):
    NotificationFactory.create_notification(NotificationType.PUSH, "bob", "alice", "meeting at 5").send_notification()
    out = capsys.readouterr().out
    assert "bob" in out and "alice" in out and "meeting at 5" in out, f"unexpected output: {out!r}"


def test_notification_base_is_abstract():
    with pytest.raises(TypeError):
        Notification("bob", "alice", "hello")


def test_every_notification_type_is_supported_without_changing_the_caller(capsys):
    # A caller written only against the abstract interface works for every channel.
    def broadcast(kind):
        n = NotificationFactory.create_notification(kind, "r", "s", "m")
        n.send_notification()
        return n.notification_type()

    assert [broadcast(k) for k in NotificationType] == list(NotificationType)


def test_each_call_returns_a_new_object_and_equal_values_compare_equal():
    a = NotificationFactory.create_notification(NotificationType.EMAIL, "r", "s", "m")
    b = NotificationFactory.create_notification(NotificationType.EMAIL, "r", "s", "m")
    assert a is not b and a == b
    c = NotificationFactory.create_notification(NotificationType.SMS, "r", "s", "m")
    assert a != c, "different channels are different products"
