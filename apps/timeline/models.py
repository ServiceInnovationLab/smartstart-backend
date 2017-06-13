from datetime import date, timedelta
from django.conf import settings
from django.db import models
from django.contrib.auth.models import User
from django.template.loader import render_to_string
from apps.base.models import TimeStampedModel, Choice
from apps.base.mail import ses_send_mail
import logging
log = logging.getLogger(__name__)

PREGNANCY_TOTAL_WEEKS = 40


class PregnancyHelper:

    def __init__(self, due_date):
        self.due_date = due_date

    def get_weekno(self, ref_date=None):
        """Get weekno at ref_date or today as integer"""
        today = ref_date or date.today()
        return int((today - self.due_date).days/7 + PREGNANCY_TOTAL_WEEKS)

    def get_week_start_date(self, weekno):
        return self.due_date + timedelta(weeks=weekno-PREGNANCY_TOTAL_WEEKS)

    def get_week_finish_date(self, weekno):
        """week finish date is last day of that week"""
        return self.get_week_start_date(weekno) + timedelta(days=6)

    def get_pregnany_start_date(self):
        return self.get_week_start_date(0)

    def get_due_phase(self, ref_date=None, weeks_before=1):
        """Find phase which will be due in next week."""
        weekno = self.get_weekno(ref_date=ref_date)
        # we send notifications 1 week before
        weekno_next_week = weekno + weeks_before
        return PhaseMetadata.objects.get_phase_by_weekno(weekno_next_week)

    def get_phase_date(self, phase):
        """For current due date, get the date for phase"""
        start = self.get_week_start_date(phase.weeks_start)
        return {
            'start': start,
            'finish': self.get_week_start_date(phase.weeks_finish),
            'notify': start - timedelta(weeks=1)
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
    modified_by = models.ForeignKey(User)

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


class MailStatus(Choice):
    todo = 'Waiting'
    sending = 'Sending'
    delivered = 'Delivered'
    failed = 'Failed'
    unsubscribed = 'Unsubscribed'
    noemail = 'No Email'


class Notification(TimeStampedModel):
    phase = models.ForeignKey(PhaseMetadata)
    user = models.ForeignKey(User)
    due_date = models.DateField(help_text="User's due date while this notification is created")

    email = models.EmailField(help_text="User's email while this notification is created")
    status = models.CharField(
        max_length=20,
        choices=MailStatus.choices(),
        default=MailStatus.todo.name
    )

    class Meta:
        unique_together = ['user', 'phase', 'due_date']

    def __str__(self):
        return '{} -> {}'.format(self.phase, self.email)

    def render_email_template(self):
        return render_to_string(
            'timeline/notification.html',
            {
                'obj': self,
                'SITE_URL': settings.SITE_URL,
                # 'logo_img_data': get_logo_img_data(),
            }
        )

    def send(self):
        if self.status != MailStatus.todo.name:
            log.info('Try to send mail with status {}, skipped'.format(self.status))
            return
        if not self.user.email:
            log.info('Try to send mail to user {} with no email, skipped'.format(self.user.id))
            self.status = MailStatus.noemail.name
            self.save()
            return
        profile = self.user.profile
        if not profile.subscribed:
            log.info('Try to send mail to unsubscribed user {}, skipped'.format(self.user))
            self.status = MailStatus.unsubscribed.name
            self.save()
            return
        text_message = html_message = self.render_email_template()
        try:
            ses_send_mail(
                self.phase.subject,
                text_message,
                [self.user.email],
                html_message=html_message
            )
            # set it to devlivered directly
            self.status = MailStatus.delivered.name
            self.save()
            log.debug('Send notification {} for phase "{}" and user email "{}"'.format(
                self.id, self.phase, self.user.email))
        except Exception as e:
            log.error('Sending notification {} failed: {}'.format(self.id, e))
            self.status = MailStatus.failed.name
            self.save()
