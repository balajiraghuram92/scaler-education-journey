from abc import ABC, abstractmethod
from dataclasses import dataclass
from enum import Enum


class NotificationType(Enum):
    EMAIL = "Email"
    PUSH = "Push"
    SMS = "SMS"


@dataclass
class Notification(ABC):
    """Abstract product with ``recipient``, ``sender`` and ``message``."""

    recipient: str
    sender: str
    message: str

    def send_notification(self):
        """Print the recipient, the sender and the message."""
        raise NotImplementedError("Implement send_notification")

    @abstractmethod
    def notification_type(self) -> NotificationType:
        pass


@dataclass
class EmailNotification(Notification):
    def notification_type(self):
        raise NotImplementedError("Implement EmailNotification.notification_type")


@dataclass
class PushNotification(Notification):
    def notification_type(self):
        raise NotImplementedError("Implement PushNotification.notification_type")


@dataclass
class SmsNotification(Notification):
    def notification_type(self):
        raise NotImplementedError("Implement SmsNotification.notification_type")
