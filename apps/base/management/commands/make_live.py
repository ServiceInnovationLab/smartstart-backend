from django.core.management.base import BaseCommand
from apps.base import models as m


class Command(BaseCommand):
    help = 'Make current instance live'

    def handle(self, *args, **options):
        locker = m.SiteLocker()
        if not locker.is_live():
            locker.make_live()
