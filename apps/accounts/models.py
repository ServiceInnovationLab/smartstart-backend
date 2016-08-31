from django.db import models
from django.contrib.auth.models import User
from annoying.fields import AutoOneToOneField, JSONField
from apps.base.models import TimeStampedModel


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

    def __str__(self):
        return self.user.get_full_name()

    @property
    def saml2_assertion(self):
        return self.attrs.get('logon_attributes_token', [''])[0] if self.attrs else ''
