from django.db import models


class NotificationStatus(models.Choices):
    PENDING = 'PENDING'
    SENT = 'SENT'
