from datetime import date, timedelta
from django.core.management.base import BaseCommand, CommandError
from django.contrib.auth.models import User
from apps.timeline import models as m


class Command(BaseCommand):
    help = 'Generate fake users in all phases'

    def handle(self, *args, **options):
        today = date.today()
        for weekno in range(-2, 73):
            due_date = today + timedelta(weeks=m.PREGNANCY_TOTAL_WEEKS-weekno)
            username = 'week{}'.format(weekno)
            email = 'lef-dev+{}@catalyst.net.nz'.format(username)
            user, created = User.objects.update_or_create(username=username, email=email)
            profile = user.profile
            profile.set_due_date(due_date)
            self.stdout.write('{} user {}'.format('create' if created else 'update', username))
