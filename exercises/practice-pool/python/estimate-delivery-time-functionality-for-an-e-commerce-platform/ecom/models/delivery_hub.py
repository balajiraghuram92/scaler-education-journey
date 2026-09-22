from django.db import models

from .address import Address
from .base_model import BaseModel
from .seller import Seller


class DeliveryHub(BaseModel):
    name = models.CharField(max_length=255)
