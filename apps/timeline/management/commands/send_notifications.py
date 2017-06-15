import sys
from django.core.management.base import BaseCommand
from django.utils import timezone
from apps.base.models import SiteLocker
from ...models import Notification, MailStatus

import logging
log = logging.getLogger(__name__)

class Command(BaseCommand):
    help = "Send notifications via email, every 5 mins between 9 and 22"

    def handle(self, *args, **options):
        # we have multiple instances in AWS
        # make sure only the live instance is sending emails.
        locker = SiteLocker()
        if not locker.is_live():
            log.info('Aborting, this instance is not live.')
            sys.exit(1)

        lock = 'begin_sending_notifications_at'

        if locker.is_locked(lock):
            log.info('Aborting, another sending task is running')
            sys.exit(1)

        notifications = Notification.objects.filter(status=MailStatus.todo.name)
        if not notifications.exists():
            log.info('No notifications to send')
            sys.exit(0)

        try:
            locker.lock(lock)
            for n in notifications:
                # send method has try/except in it, no need to catch again
                n.send()
        finally:
            # clear lock once done, even failed
            locker.unlock(lock)
