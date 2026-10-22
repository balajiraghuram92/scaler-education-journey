import pytest

from config.abstract_factory import EmailNotificationFactory, NotificationFactory, PushNotificationFactory
from config.model import NotificationType
from config.notification import EmailNotification, Notification, PushNotification
from config.sender import EmailNotificationSender, NotificationSender, PushNotificationSender
from config.template import EmailNotificationTemplate, NotificationTemplate, PushNotificationTemplate

FAMILIES = [
    (EmailNotificationFactory, NotificationType.EMAIL, EmailNotificationTemplate, EmailNotification, EmailNotificationSender),
    (PushNotificationFactory, NotificationType.PUSH, PushNotificationTemplate, PushNotification, PushNotificationSender),
]
IDS = ["email", "push"]


def test_notification_factory_is_abstract_with_three_abstract_methods():
    with pytest.raises(TypeError):
        NotificationFactory()
    assert NotificationFactory.__abstractmethods__ == {
        "create_notification",
        "create_template",
        "create_sender",
    }, f"abstract methods found: {sorted(NotificationFactory.__abstractmethods__)}"


@pytest.mark.parametrize("factory_cls, kind, template, notification, sender", FAMILIES, ids=IDS)
def test_concrete_factories_extend_the_abstract_factory(factory_cls, kind, template, notification, sender):
    assert issubclass(factory_cls, NotificationFactory)
    assert isinstance(factory_cls(), NotificationFactory)


@pytest.mark.parametrize("factory_cls, kind, template, notification, sender", FAMILIES, ids=IDS)
def test_factory_creates_the_concrete_products_of_its_channel(factory_cls, kind, template, notification, sender):
    factory = factory_cls()
    made_template = factory.create_template("welcome")
    made_notification = factory.create_notification("bob", made_template)
    assert type(made_template) is template
    assert type(made_notification) is notification
    assert type(factory.create_sender(made_notification)) is sender


@pytest.mark.parametrize("factory_cls, kind, template, notification, sender", FAMILIES, ids=IDS)
def test_products_share_the_common_abstract_parents(factory_cls, kind, template, notification, sender):
    factory = factory_cls()
    made_template = factory.create_template("welcome")
    made_notification = factory.create_notification("bob", made_template)
    assert isinstance(made_template, NotificationTemplate)
    assert isinstance(made_notification, Notification)
    assert isinstance(factory.create_sender(made_notification), NotificationSender)


@pytest.mark.parametrize("factory_cls, kind, template, notification, sender", FAMILIES, ids=IDS)
def test_every_product_reports_the_matching_notification_type(factory_cls, kind, template, notification, sender):
    factory = factory_cls()
    made_template = factory.create_template("welcome")
    made_notification = factory.create_notification("bob", made_template)
    products = [made_template, made_notification, factory.create_sender(made_notification)]
    assert [p.notification_type() for p in products] == [kind] * 3, "all three products must belong to one channel"


def test_arguments_reach_the_products_and_the_sender_wraps_the_notification():
    factory = PushNotificationFactory()
    made_template = factory.create_template("promo")
    made_notification = factory.create_notification("alice", made_template)
    made_sender = factory.create_sender(made_notification)
    assert made_template.template_name == "promo"
    assert made_notification.recipient == "alice"
    assert made_notification.template is made_template, "the notification must keep the given template"
    assert made_sender.notification is made_notification, "the factory must pass the notification into the sender"


def test_each_call_creates_a_new_product():
    factory = EmailNotificationFactory()
    assert factory.create_template("t") is not factory.create_template("t")


def test_client_code_depends_only_on_the_abstract_factory():
    def notify(factory: NotificationFactory):
        template = factory.create_template("t")
        notification = factory.create_notification("someone", template)
        return {
            template.notification_type(),
            notification.notification_type(),
            factory.create_sender(notification).notification_type(),
        }

    for factory_cls, kind, *_ in FAMILIES:
        assert notify(factory_cls()) == {kind}, "one factory must never mix channels"
