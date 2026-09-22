from django.db import models
from .base_model import BaseModel
from .product import Product


class Inventory(BaseModel):
    product = models.ForeignKey(
        Product,
        on_delete=models.CASCADE
    )
    quantity = models.IntegerField()
