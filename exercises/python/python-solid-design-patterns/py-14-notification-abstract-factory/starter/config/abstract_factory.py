from abc import ABC, abstractmethod

from .notification import EmailNotification, Notification, PushNotification
from .sender import EmailNotificationSender, NotificationSender, PushNotificationSender
from .template import EmailNotificationTemplate, NotificationTemplate, PushNotificationTemplate


class NotificationFactory(ABC):
    """Abstract Factory for one notification channel.

    Declare THREE abstract methods (so NotificationFactory cannot be instantiated):
      create_notification(recipient, template) -> Notification
      create_template(template_name) -> NotificationTemplate
      create_sender(notification) -> NotificationSender   (the sender is built FROM the notification)
    """


class EmailNotificationFactory(NotificationFactory):
    """Implement all three methods; create only email products."""


class PushNotificationFactory(NotificationFactory):
    """Implement all three methods; create only push products."""
