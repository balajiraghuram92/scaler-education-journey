from abc import ABC, abstractmethod
from dataclasses import dataclass

from .model import NotificationType


@dataclass
class NotificationTemplate(ABC):
    template_name: str

    @abstractmethod
    def notification_type(self) -> NotificationType:
        pass


@dataclass
class EmailNotificationTemplate(NotificationTemplate):
    def notification_type(self) -> NotificationType:
        return NotificationType.EMAIL


@dataclass
class PushNotificationTemplate(NotificationTemplate):
    def notification_type(self) -> NotificationType:
        return NotificationType.PUSH
