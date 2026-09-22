from django.db import models
from .address import Address
from .seller import Seller


class SellerAddress(Address):
    seller = models.OneToOneField(
        Seller,
        on_delete=models.CASCADE,
        related_name="address"
    )
