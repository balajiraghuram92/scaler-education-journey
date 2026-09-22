from django.db import models
from .base_model import BaseModel
from .product import Product


class ProductGroup(BaseModel):
    products = models.ManyToManyField(Product, related_name='product_groups')
