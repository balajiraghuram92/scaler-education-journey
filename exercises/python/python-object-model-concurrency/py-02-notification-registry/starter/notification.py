from abc import ABC, abstractmethod


class NotificationChannel(ABC):
    """Abstract notification contract with self-registering subclasses.

    - class-level ``registry = {}`` maps a channel name to its class
    - ``__init_subclass__(cls, channel_name=None, **kwargs)`` must call
      ``super().__init_subclass__(**kwargs)`` and, when ``channel_name`` is given,
      store ``registry[channel_name] = cls``. Subclasses without a name are not registered.
    - abstract methods: ``send(user, message)`` and ``get_status(message_id)``
    """

    registry = {}

    def __init_subclass__(cls, channel_name=None, **kwargs):
        # TODO: forward **kwargs to super() and register the subclass under channel_name
        pass

    @abstractmethod
    def send(self, user, message):
        """Deliver ``message`` to ``user``."""

    @abstractmethod
    def get_status(self, message_id):
        """Return the delivery status of a message."""


class SMSChannel(NotificationChannel, channel_name="sms"):
    """``send`` prints ``Sending SMS to <user>: <message>``; ``get_status`` returns ``"DELIVERED"``."""

    def send(self, user, message):
        raise NotImplementedError("Implement SMSChannel.send")

    def get_status(self, message_id):
        raise NotImplementedError("Implement SMSChannel.get_status")


class EmailChannel(NotificationChannel, channel_name="email"):
    """``send`` prints a line naming the Email channel, the user and the message; ``get_status`` returns ``"DELIVERED"``."""

    def send(self, user, message):
        raise NotImplementedError("Implement EmailChannel.send")

    def get_status(self, message_id):
        raise NotImplementedError("Implement EmailChannel.get_status")


class PushChannel(NotificationChannel, channel_name="push"):
    """``send`` prints a line naming the Push channel, the user and the message; ``get_status`` returns ``"DELIVERED"``."""

    def send(self, user, message):
        raise NotImplementedError("Implement PushChannel.send")

    def get_status(self, message_id):
        raise NotImplementedError("Implement PushChannel.get_status")
