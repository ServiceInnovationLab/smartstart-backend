# -*- coding: utf-8 -*-
import uuid
from datetime import datetime
from django.conf import settings
from django.db import models
from django.urls import reverse
from django.contrib.auth.models import User, UserManager
from django.core.signing import TimestampSigner
from annoying.fields import AutoOneToOneField
from apps.base.models import TimeStampedModel
from apps.base.utils import get_full_url
from apps.base.mail import ses_send_templated_mail

import logging
log = logging.getLogger(__name__)


class UserProxyManager(UserManager):

    def subscribers(self):
        """
        Users who:
        - have email
        - have due_date
        - have no subscribed = 'false'
        """
        users_with_due_date = Preference.objects.filter(
            key='dd',
            val__regex=r'\d{4}-\d{1,2}-\d{1,2}'
        ).values_list('user_id', flat=True)

        users_subscribed_false = Preference.objects.filter(
            key='subscribed',
            val='false'
        ).values_list('user_id', flat=True)

        return self.get_queryset().filter(
            id__in=users_with_due_date,
        ).exclude(
            email='',
        ).exclude(
            email__isnull=True,
        ).exclude(
            id__in=users_subscribed_false,
        ).distinct()

    def generate_notifications(self, ref_date=None):
        """
        Generate notifications for all subscribers
        """
        for u in self.subscribers():
            try:
                u.generate_notifications(ref_date=ref_date)
            except Exception as e:
                log.error(str(e))
                continue


class BroFormManager(models.Manager):
    """
    Django Manager for the :class:`BroForm` model.
    """

    def expire_old_data(self):
        """
        Use the ``STALE_BROFORM_PERIOD`` setting to control how long BRO form
        data should stick around in the database.

        :returns: the number of records deleted.
        """
        (n, _) = self.get_queryset().filter(
            modified_at__lt=datetime.now() - settings.STALE_BROFORM_PERIOD).delete()
        return n


class BroForm(TimeStampedModel):
    """
    Holds arbitrary JSON blobs of form data in order to support the partial form
    save requirement for authenticated users.
    """
    objects = BroFormManager()

    user = AutoOneToOneField(User, unique=True)
    form_data = models.TextField(blank=True, default='')

    def __str__(self):
        return 'BRO form data for {}'.format(self.user)


class Profile(TimeStampedModel):
    """Not used any more"""
    user = AutoOneToOneField(User)
    dob = models.DateField(verbose_name="Date of Birth", blank=True, null=True)
    # this field is not used so far, we are using the preference with key `dd` for now.
    due_date = models.DateField(blank=True, null=True)
    subscribed = models.BooleanField(default=True)
    logon_attributes_token = models.TextField(blank=True)

    def __str__(self):
        return self.user.username


class UserProxy(User):
    objects = UserProxyManager()

    class Meta:
        proxy = True
        verbose_name = 'User'
        verbose_name_plural = 'Users'

    def set_preference(self, key, val):
        Preference.objects.update_or_create(user=self, key=key, defaults={'val': val})

    def get_preference(self, key, default=None):
        pref = Preference.objects.filter(user=self, key=key).first()
        return pref.val if pref else default

    def set_due_date(self, due_date):
        due_date_str = due_date.strftime('%Y-%m-%d')
        return self.set_preference('dd', due_date_str)

    @property
    def due_date(self):
        due_date_str = self.get_preference('dd')
        if due_date_str:
            try:
                return datetime.strptime(due_date_str, '%Y-%m-%d').date()
            except Exception:
                pass
        return None

    def subscribe(self):
        return self.set_preference('subscribed', 'true')

    def unsubscribe(self):
        return self.set_preference('subscribed', 'false')

    @property
    def subscribed(self):
        return self.get_preference('subscribed', default='true') == 'true'

    def get_pregnancy_helper(self, due_date=None):
        from apps.timeline.models import PregnancyHelper
        due_date = due_date or self.due_date
        return PregnancyHelper(due_date) if due_date else None

    def generate_notifications(self, weeks_before=1, ref_date=None, send=False):
        """
        Generate notificaiton for user.

        This method will be trigged by a daily cron job.
        """
        if not self.email:
            return
        if not self.subscribed:
            return
        due_date = self.due_date
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
        self.notification_set.filter(
            phase=phase
        ).exclude(
            due_date=due_date
        ).delete()

        if not phase.subject:
            return

        notification, created = self.notification_set.get_or_create(
            phase=phase,
            due_date=due_date,
            defaults={
                'email': self.email,
            }
        )
        if send:
            notification.send()
        return notification

    def dump_preferences(self):
        from collections import defaultdict
        preferences = defaultdict(dict)
        for pref in Preference.objects.filter(user_id=self.id):
            preferences[pref.group][pref.key] = pref.val
        return preferences

    @property
    def unsubscribe_url(self):
        token = TimestampSigner().sign(self.id)
        url = reverse(
            'accounts:unsubscribe',
            kwargs={'token': token}
        )
        # must return full url since it's in email.
        return get_full_url(url)


class Preference(models.Model):
    user = models.ForeignKey(UserProxy)
    group = models.CharField(max_length=50, default='settings')
    key = models.SlugField(max_length=50)
    val = models.CharField(max_length=200, blank=True)

    class Meta:
        unique_together = ('user', 'group', 'key')

    def __str__(self):
        return '[{}] {}={}'.format(self.group, self.key, self.val)


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
    user = models.ForeignKey(UserProxy)
    email = models.CharField(max_length=140)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']
        verbose_name_plural = 'Email addresses'

    def __str__(self):
        return '{}: {}'.format(self.user, self.email)

    @property
    def has_email_changed(self):
        return self.email != self.user.email

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
            user.subscribe()
        # delete all of them
        user.emailaddress_set.all().delete()
