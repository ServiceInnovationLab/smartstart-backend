from django.db import models
from apps.base.models import TimeStampedModel
from django.contrib.auth.models import User


class PhaseMetadata(TimeStampedModel):
    modified_by = models.ForeignKey(User)

    weeks_start = models.IntegerField()
    weeks_finish = models.IntegerField()

    def __str__(self):
        return 'Phase {}: week {} - {}'.format(self.id, self.weeks_start, self.weeks_finish)

    class Meta:
        ordering = ['id']
        verbose_name = 'Phase metadata'
        verbose_name_plural = 'Phase metadata'
