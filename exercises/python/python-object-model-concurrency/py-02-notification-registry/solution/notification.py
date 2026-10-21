from abc import ABC, abstractmethod


class NotificationChannel(ABC):
    registry = {}

    def __init_subclass__(cls, channel_name=None, **kwargs):
        super().__init_subclass__(**kwargs)
        if channel_name is not None:
            cls.registry[channel_name] = cls

    @abstractmethod
    def send(self, user, message):
        pass

    @abstractmethod
    def get_status(self, message_id):
        pass


class SMSChannel(NotificationChannel, channel_name="sms"):
    def send(self, user, message):
        print(f"Sending SMS to {user}: {message}")

    def get_status(self, message_id):
        return "DELIVERED"


class EmailChannel(NotificationChannel, channel_name="email"):
    def send(self, user, message):
        print(f"Sending Email to {user}: {message}")

    def get_status(self, message_id):
        return "DELIVERED"


class PushChannel(NotificationChannel, channel_name="push"):
    def send(self, user, message):
        print(f"Sending Push notification to {user}: {message}")

    def get_status(self, message_id):
        return "DELIVERED"
