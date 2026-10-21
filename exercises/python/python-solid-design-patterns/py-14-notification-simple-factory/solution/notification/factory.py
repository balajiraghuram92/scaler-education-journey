from .products import *

class NotificationFactory:
    @staticmethod
    def create_notification(notification_type: NotificationType, *args) -> Notification:
        if notification_type == NotificationType.EMAIL:
            return EmailNotification(*args)
        elif notification_type == NotificationType.PUSH:
            return PushNotification(*args)
        elif notification_type == NotificationType.SMS:
            return SmsNotification(*args)
        else:
            raise ValueError("Invalid notification type")
