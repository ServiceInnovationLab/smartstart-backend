import uuid
from datetime import datetime, date
from django.db import models
from django.urls import reverse
from django.contrib.auth.models import User
from django.core.signing import TimestampSigner, BadSignature, SignatureExpired
from annoying.fields import AutoOneToOneField
from apps.base.models import TimeStampedModel
from apps.base.utils import get_full_url
from apps.base.mail import ses_send_templated_mail
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
    # this field is not used so far, we are using the preference with key `dd` for now.
    due_date = models.DateField(blank=True, null=True)
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
        """Get due date"""
        # migrate to this new field other then use preference
        if self.due_date:
            return self.due_date
        due_date_str = self.get_preference('dd')
        if due_date_str:
            return datetime.strptime(due_date_str, '%Y-%m-%d').date()
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

        helper = self.get_pregnancy_helper(due_date=due_date)
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

    @property
    def unsubscribe_url(self):
        full_token = TimestampSigner().sign(self.user_id)
        user_id, token = full_token.split(":", 1)
        url = reverse(
            'accounts:unsubscribe',
            kwargs={'user_id': user_id, 'token': token}
        )
        # must return full url since it's in email.
        return get_full_url(url)


class EmailAddress(models.Model):
    """
    Handles a change to the email address of a user account.
    This involves a confirmation email, sent to the new address with a token
    and confirmation URL.
    """

    id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False)
    user = models.ForeignKey(User)
    email = models.CharField(max_length=140)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']
        verbose_name_plural = 'Email addresses'

    def __str__(self):
        return '{}: {}'.format(self.user, self.email)

    @property
    def confirm_url(self):
        url = reverse(
            'accounts:confirm',
            kwargs={'uuid': self.id}
        )
        # must return full url since it's in email.
        return get_full_url(url)

    def send_confirm_email(self):
        return ses_send_templated_mail(
            'emails/email_confirm.txt',
            [self.email],
            context={'confirm_url': self.confirm_url}
        )

    def confirm(self):
        user = self.user
        if self.email and user.email != self.email:
            user.email = self.email
            user.save(update_fields=['email'])
            # while confirm new email, subscribe
            profile = user.profile
            profile.subscribed = True
            profile.save(update_fields=['subscribed'])
        # delete all of them
        user.emailaddress_set.all().delete()
