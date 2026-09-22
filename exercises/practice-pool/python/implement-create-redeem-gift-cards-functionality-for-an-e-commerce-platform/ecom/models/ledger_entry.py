from django.db import models
from .base_model import BaseModel
from .gift_card import GiftCard
from .transaction_type import TransactionType


class LedgerEntry(BaseModel):
    transaction_type = models.CharField(
        max_length=255,
        choices=TransactionType.choices,
    )
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    gift_card = models.ForeignKey(
        GiftCard, on_delete=models.CASCADE,
        related_name="entries",
    )
    created_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.transaction_type} - {self.amount} - {self.gift_card}"
