from abc import ABC, abstractmethod

from .notification import EmailNotification, Notification, PushNotification
from .sender import EmailNotificationSender, NotificationSender, PushNotificationSender
from .template import EmailNotificationTemplate, NotificationTemplate, PushNotificationTemplate


class NotificationFactory(ABC):
    @abstractmethod
    def create_notification(self, recipient: str, template: NotificationTemplate) -> Notification:
        pass

    @abstractmethod
    def create_template(self, template_name: str) -> NotificationTemplate:
        pass

    @abstractmethod
    def create_sender(self, notification: Notification) -> NotificationSender:
        pass


class EmailNotificationFactory(NotificationFactory):
    def create_notification(self, recipient: str, template: NotificationTemplate) -> Notification:
        return EmailNotification(recipient, template)

    def create_template(self, template_name: str) -> NotificationTemplate:
        return EmailNotificationTemplate(template_name)

    def create_sender(self, notification: Notification) -> NotificationSender:
        return EmailNotificationSender(notification)


class PushNotificationFactory(NotificationFactory):
    def create_notification(self, recipient: str, template: NotificationTemplate) -> Notification:
        return PushNotification(recipient, template)

    def create_template(self, template_name: str) -> NotificationTemplate:
        return PushNotificationTemplate(template_name)

    def create_sender(self, notification: Notification) -> NotificationSender:
        return PushNotificationSender(notification)
