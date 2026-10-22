from abc import ABC, abstractmethod
from dataclasses import dataclass
from enum import Enum


class NotificationType(Enum):
    EMAIL = "Email"
    PUSH = "Push"
    SMS = "SMS"


@dataclass
class Notification(ABC):
    recipient: str
    sender: str
    message: str

    def send_notification(self):
        print(f"Email sent to {self.recipient} from {self.sender}")
        print(f"Message: {self.message}")

    @abstractmethod
    def notification_type(self) -> NotificationType:
        pass


@dataclass
class EmailNotification(Notification):
    def notification_type(self):
        return NotificationType.EMAIL


@dataclass
class PushNotification(Notification):
    def notification_type(self):
        return NotificationType.PUSH


@dataclass
class SmsNotification(Notification):
    def notification_type(self):
        return NotificationType.SMS
