from abc import ABC, abstractmethod
from dataclasses import dataclass

from .model import NotificationType
from .notification import Notification


@dataclass
class NotificationSender(ABC):
    notification: Notification

    @abstractmethod
    def notification_type(self) -> NotificationType:
        pass


@dataclass
class EmailNotificationSender(NotificationSender):
    def notification_type(self) -> NotificationType:
        return NotificationType.EMAIL


@dataclass
class PushNotificationSender(NotificationSender):
    def notification_type(self) -> NotificationType:
        return NotificationType.PUSH
