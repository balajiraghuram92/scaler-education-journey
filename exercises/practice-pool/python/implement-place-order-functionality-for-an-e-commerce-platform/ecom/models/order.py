from django.db import models

from . import User
from .base_model import BaseModel
from .order_status import OrderStatus


class Order(BaseModel):
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE
    )
    order_status = models.CharField(
        max_length=100,
        choices=OrderStatus.choices,
        default=OrderStatus.PLACED
    )

