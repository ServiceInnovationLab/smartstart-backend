from datetime import datetime, date
from django.db import models
from django.contrib.auth.models import User
from annoying.fields import AutoOneToOneField
from apps.base.models import TimeStampedModel
from apps.timeline.models import PhaseMetadata, PregnancyHelper

import logging
log = logging.getLogger(__name__)


class Preference(models.Model):
    user = models.ForeignKey(User)
    group = models.CharField(max_length=50, default='settings')
    key = models.SlugField(max_length=50)
    val = models.CharField(max_length=200, blank=True)

    class Meta:
        unique_together = ('user', 'group', 'key')

    def __str__(self):
        return '[{}] {}={}'.format(self.group, self.key, self.val)


class Profile(TimeStampedModel):
    user = AutoOneToOneField(User)
    dob = models.DateField(verbose_name="Date of Birth", blank=True, null=True)
    GENDER_MALE = 'M'
    GENDER_FEMALE = 'F'
    GENDER_CHOICES = (
        (None, 'Unknown'),
        (GENDER_MALE, 'Male'),
        (GENDER_FEMALE, 'Female'),
    )
    gender = models.CharField(max_length=10, blank=True, choices=GENDER_CHOICES)
    subscribed = models.BooleanField(default=True)
    logon_attributes_token = models.TextField(blank=True)

    def __str__(self):
        return self.user.get_full_name()

    def set_preference(self, key, val):
        Preference.objects.update_or_create(user=self.user, key=key, defaults={'val': val})

    def get_preference(self, key):
        pref =  Preference.objects.filter(user=self.user, key=key).first()
        return pref.val if pref else None

    def set_due_date(self, due_date):
        due_date_str = due_date.strftime('%Y-%m-%d')
        return self.set_preference('dd', due_date_str)

    def get_due_date(self):
        """Get due date value from preference and convert to date"""
        due_date_str = self.get_preference('dd')
        if due_date_str:
            return datetime.strptime(due_date_str, '%Y-%m-%d').date()
        else:
            return None

    def get_pregnancy_helper(self, due_date=None):
        due_date = due_date or self.get_due_date()
        return PregnancyHelper(due_date) if due_date else None

    def generate_notifications(self, weeks_before=1, ref_date=None):
        """
        Generate notificaiton for user.

        This method will be trigged by a daily cron job.
        """
        if not self.subscribed:
            return
        if not self.user.email:
            return
        due_date = self.get_due_date()
        if not due_date:
            return

        helper = get_pregnancy_helper(due_date=due_date)
        phase = helper.get_due_phase(
            ref_date=ref_date,
            weeks_before=weeks_before,
        )
        if not phase:
            return

        # notifications generated for this phase but other due date should be deleted
        self.user.notification_set.filter(
            phase=phase
        ).exclude(
            due_date=due_date
        ).delete()

        if not phase.subject:
            return

        notification, created = self.user.notification_set.get_or_create(
            phase=phase,
            due_date=due_date,
            defaults={
                'email': self.user.email,
            }
        )
        return notification

    def dump_preferences(self):
        from collections import defaultdict
        preferences = defaultdict(dict)
        for pref in Preference.objects.filter(user=self.user):
            preferences[pref.group][pref.key] = pref.val
        return preferences
