from django.db import models


class OrderStatus(models.Choices):
    PLACED = 'PLACED'
    CANCELLED = 'CANCELLED'
    SHIPPED = 'SHIPPED'
    DELIVERED = 'DELIVERED'
