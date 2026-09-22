from django.db import models
from .base_model import BaseModel


class GiftCard(BaseModel):
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    created_at = models.DateTimeField(auto_now=True)
    expires_at = models.DateTimeField()
    gift_card_code = models.CharField(max_length=255, unique=True)
