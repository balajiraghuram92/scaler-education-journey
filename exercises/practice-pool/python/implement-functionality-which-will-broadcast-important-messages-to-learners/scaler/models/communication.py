from django.db import models

from .batch import Batch
from .base_model import BaseModel
from .user import User


class Communication(BaseModel):
    batch = models.ForeignKey(Batch, on_delete=models.CASCADE)
    sender = models.ForeignKey(User, on_delete=models.CASCADE)
    message = models.CharField(max_length=255)
    created_at = models.DateTimeField(
        auto_now_add=True
    )
