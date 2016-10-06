from django.db import models
from django.contrib.auth.models import User
from annoying.fields import AutoOneToOneField
from apps.base.models import TimeStampedModel

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
    logon_attributes_token = models.TextField(blank=True)

    def __str__(self):
        return self.user.get_full_name()

    def set_preference(self, key, val):
        Preference.objects.create_or_update(user=self.user, key=key, defaults={'val': val})

    def get_preference(self, key):
        pref =  Preference.objects.filter(user=self.user, key=key).first()
        return pref.val if pref else None

    def dump_preferences(self):
        from collections import defaultdict
        preferences = defaultdict(dict)
        for pref in Preference.objects.filter(user=self.user):
            preferences[pref.group][pref.key] = pref.val
        return preferences
