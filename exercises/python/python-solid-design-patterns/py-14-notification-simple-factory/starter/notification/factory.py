from .products import *


class NotificationFactory:
    """Simple Factory: callers pass a NotificationType and never name a concrete class."""

    @staticmethod
    def create_notification(notification_type: NotificationType, *args) -> Notification:
        """Unpack ``*args`` (recipient, sender, message) into the chosen class.

        Anything that is not a supported NotificationType raises
        ``ValueError("Invalid notification type")``.
        """
        raise NotImplementedError("Implement create_notification")
