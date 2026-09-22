from django.db import models
from .address import Address
from .delivery_hub import DeliveryHub


class DeliveryHubAddress(Address):
    delivery_hub = models.OneToOneField(
        DeliveryHub,
        on_delete=models.CASCADE,
        related_name="address"
    )
