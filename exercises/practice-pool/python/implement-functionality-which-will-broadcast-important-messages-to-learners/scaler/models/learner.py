from django.db import models
from .user import User


class Learner(User):
    phone_number = models.CharField(max_length=255)
    address = models.TextField()
