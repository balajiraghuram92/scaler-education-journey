from abc import ABC, abstractmethod
from dataclasses import dataclass

from .model import NotificationType
from .template import NotificationTemplate


@dataclass
class Notification(ABC):
    recipient: str
    template: NotificationTemplate

    @abstractmethod
    def notification_type(self) -> NotificationType:
        pass


@dataclass
class EmailNotification(Notification):
    def notification_type(self) -> NotificationType:
        return NotificationType.EMAIL


@dataclass
class PushNotification(Notification):
    def notification_type(self) -> NotificationType:
        return NotificationType.PUSH
