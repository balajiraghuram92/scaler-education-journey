from django.db import models
from .address import Address
from .user import User


class UserAddress(Address):
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="addresses"
    )
