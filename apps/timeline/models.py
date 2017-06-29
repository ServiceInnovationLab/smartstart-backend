from datetime import date, timedelta

from django.conf import settings
from django.db import models
from django.contrib.auth.models import User
from django.template.loader import render_to_string
from django.utils.safestring import mark_safe
from django.core.mail import EmailMultiAlternatives, get_connection

from mistune import markdown
from apps.base.models import TimeStampedModel, Choice
from apps.base.mail import build_email_message
import logging
log = logging.getLogger(__name__)

PREGNANCY_TOTAL_WEEKS = 40


class PregnancyHelper:

    def set_due_date(self, due_date):
        if due_date:
            self.due_date = due_date
            self.pregnancy_date = due_date - timedelta(weeks=PREGNANCY_TOTAL_WEEKS)

    def __init__(self, due_date=None):
        self.set_due_date(due_date)

    def get_weekno(self, ref_date=None):
        """Get weekno at ref_date or today as integer"""
        today = ref_date or date.today()
        return int((today - self.pregnancy_date).days/7)

    def get_week_start_date(self, weekno):
        return self.pregnancy_date + timedelta(weeks=weekno)

    def get_week_finish_date(self, weekno):
        """week finish date is last day of that week"""
        return self.get_week_start_date(weekno) + timedelta(days=6)

    def get_due_phase(self, ref_date=None, weeks_before=1):
        """
        Which phase should we send email at ref_date.

        Email should be sent 1 week before phase.
        """
        today = ref_date or date.today()
        target_date = today + timedelta(weeks=weeks_before)
        weekno = self.get_weekno(ref_date=target_date)
        return PhaseMetadata.objects.get_phase_by_weekno(weekno)

    def get_phase_date(self, phase):
        """For current due date, get the date for phase"""
        return {
            'start': self.get_week_start_date(phase.weeks_start),
            'finish': self.get_week_finish_date(phase.weeks_finish),
        }

    def get_phase_date_for_all(self):
        return {
            phase.id: self.get_phase_date(phase)
            for phase in PhaseMetadata.objects.all()
        }


class PhaseMetadataManager(models.Manager):

    def get_phase_by_weekno(self, weekno):
        return self.get_queryset().filter(weeks_start__lte=weekno, weeks_finish__gte=weekno).first()

    def get_phase(self, due_date, ref_date=None):
        helper = PregnancyHelper(due_date)
        weekno = helper.get_weekno(ref_date=ref_date)
        return self.get_phase_by_weekno(weekno)


class PhaseMetadata(TimeStampedModel):
    weeks_start = models.IntegerField()
    weeks_finish = models.IntegerField()

    subject = models.CharField(max_length=140, blank=True)
    content = models.TextField(blank=True)

    button_text = models.CharField(max_length=50, blank=True)
    button_link = models.URLField(max_length=500, blank=True)

    objects = PhaseMetadataManager()

    class Meta:
        ordering = ['id']
        verbose_name = 'Phase metadata'
        verbose_name_plural = 'Phase metadata'

    @property
    def name(self):
        return 'Phase {}: week {} - {}'.format(self.id, self.weeks_start, self.weeks_finish)

    def __str__(self):
        return self.name

    @property
    def markdown_content(self):
        return mark_safe(markdown(self.content))


class MailStatus(Choice):
    pending = 'pending'
    sending = 'sending'
    delivered = 'delivered'
    failed = 'failed'
    unsubscribed = 'unsubscribed'
    noemail = 'noemail'


class NotificationManager(models.Manager):

    def pending(self):
        return self.get_queryset().filter(status=MailStatus.pending.name)

    def send_all(self):
        """
        Send emails for all pending notifications in batch.

        Establishing and closing an SMTP connection is an expensive process.
        This function will send all emails with one connection.

        The send_messages method will open a connection on the backend,
        sends the list of messages, and then closes the connection again.
        """
        notifications = self.pending()  # cache here for later use
        messages = [n.build_email_message() for n in notifications]
        connection = get_connection()
        connection.send_messages(messages)
        notifications.update(status=MailStatus.delivered.name)


class Notification(TimeStampedModel):
    phase = models.ForeignKey(PhaseMetadata)
    user = models.ForeignKey(User)
    due_date = models.DateField(help_text="User's due date while this notification is created")

    email = models.EmailField(help_text="User's email while this notification is created")
    status = models.CharField(
        max_length=20,
        choices=MailStatus.choices(),
        default=MailStatus.pending.name
    )

    objects = NotificationManager()

    class Meta:
        unique_together = ['user', 'phase', 'due_date']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = PregnancyHelper(self.due_date)

    def __str__(self):
        return '{} -> {}'.format(self.phase, self.email)

    @property
    def pregnancy_date(self):
        return self.helper.pregnancy_date

    @property
    def weekno(self):
        return self.helper.get_weekno(ref_date=self.created_at.date())

    def render_email_template(self):
        return render_to_string(
            'timeline/notification.html',
            {
                'obj': self,
                'SITE_URL': settings.SITE_URL,
                # 'logo_img_data': get_logo_img_data(),
            }
        )

    def build_email_message(self):
        """
        Build a EmailMultiAlternatives object from notification.

        This is a html mail, so has to use EmailMultiAlternatives,
        which is a subclass of EmailMessage.

        We have no text email template, so use html as text version.
        """
        text_message = html_message = self.render_email_template()
        return build_email_message(
            self.phase.subject,
            text_message,
            [self.email],
            html_message=html_message
        )
