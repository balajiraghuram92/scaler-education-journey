from django.db import models


class Schedule(models.Choices):
    MWF_MORNING = 'MWF_MORNING'
    MWF_EVENING = 'MWF_EVENING'
    TTS_MORNING = 'TTS_MORNING'
    TTS_EVENING = 'TTS_EVENING'
