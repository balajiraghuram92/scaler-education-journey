from django.db import models


class TransactionType(models.Choices):
    DEBIT = "DEBIT"
    CREDIT = "CREDIT"
