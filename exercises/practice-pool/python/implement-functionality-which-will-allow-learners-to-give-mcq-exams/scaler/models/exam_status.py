from django.db import models


class ExamStatus(models.Choices):
    STARTED = 'STARTED'
    ENDED = 'ENDED'
