from django.db import models
from .base_model import BaseModel
from .partner import Partner
from .task import Task


class PartnerTaskMapping(BaseModel):
    partner = models.ForeignKey(
        Partner,
        on_delete=models.CASCADE
    )

    task = models.ForeignKey(
        Task,
        on_delete=models.CASCADE
    )
