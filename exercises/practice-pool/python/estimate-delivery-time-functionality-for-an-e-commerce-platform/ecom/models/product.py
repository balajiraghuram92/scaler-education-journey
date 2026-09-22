from django.db import models
from .base_model import BaseModel
from .seller import Seller


class Product(BaseModel):
    name = models.CharField(max_length=255)
    description = models.CharField(max_length=255)
    price = models.FloatField()
    seller = models.ForeignKey(
        Seller,
        on_delete=models.CASCADE
    )
