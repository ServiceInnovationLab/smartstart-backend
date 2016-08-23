from __future__ import unicode_literals

from django.db import models
from django.contrib.auth.models import User
from annoying.fields import AutoOneToOneField, JSONField


class TimeStampedModel(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    modified_at = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True
        ordering = ['-modified_at']


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
    attrs = JSONField(blank=True, null=True)

    def __unicode__(self):
        return self.user.get_full_name()

    @property
    def saml2_assertion(self):
        return self.attrs['logon_attributes_token'][0]
