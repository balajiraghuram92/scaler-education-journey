from django.db import models

from . import User
from .base_model import BaseModel
from .product import Product
from .notification_status import NotificationStatus


class Notification(BaseModel):
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE
    )
    product = models.ForeignKey(
        Product,
        on_delete=models.CASCADE
    )
    status = models.CharField(
        choices=NotificationStatus.choices,
        max_length=20,
        default=NotificationStatus.PENDING
    )
