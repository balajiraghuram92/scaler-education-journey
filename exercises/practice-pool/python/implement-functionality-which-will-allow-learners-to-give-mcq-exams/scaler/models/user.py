from django.db import models
from .base_model import BaseModel
from .user_type import UserType


class User(BaseModel):
    name = models.CharField(max_length=255)
    email = models.EmailField()
    phone = models.CharField(max_length=255)
    user_type = models.CharField(
        choices=UserType.choices,
        max_length=255,
        default=UserType.LEARNER
    )
