from django.db import models


class UserType(models.Choices):
    ADMIN = "ADMIN"
    CUSTOMER = "CUSTOMER"
