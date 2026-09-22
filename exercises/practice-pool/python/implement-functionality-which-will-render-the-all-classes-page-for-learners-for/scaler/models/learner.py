from django.db import models
from .user import User


class Learner(User):
    address = models.TextField(max_length=255, null=True, blank=True)
