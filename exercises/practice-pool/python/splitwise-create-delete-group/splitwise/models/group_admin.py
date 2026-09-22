from django.db import models
from django.db.models import ForeignKey

from .group import Group
from .base_model import BaseModel
from .user import User


class GroupAdmin(BaseModel):
    user = ForeignKey(
        User, on_delete=models.CASCADE,
    )
    group = ForeignKey(
        Group, on_delete=models.CASCADE
    )
    added_by = models.ForeignKey(
        User, on_delete=models.SET_NULL, null=True
    )
    added_on = models.DateTimeField(auto_now_add=True)
