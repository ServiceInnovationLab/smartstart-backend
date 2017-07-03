from datetime import date, timedelta
from django.core.management.base import BaseCommand, CommandError
from apps.accounts.models import UserProxy
from apps.timeline import models as m


class Command(BaseCommand):
    help = 'Generate fake users in all phases'

    def add_arguments(self, parser):
        parser.add_argument(
            '--name',
            help='given "joeg", will generate email joeg+weekN@catalyst.net.nz'
        )

    def handle(self, *args, **options):
        name = options.get('name') or 'lef-dev'
        today = date.today()
        for weekno in range(-2, 73):
            due_date = today + timedelta(weeks=m.PREGNANCY_TOTAL_WEEKS-weekno)
            username = 'week{}'.format(weekno)
            email = '{}+{}@catalyst.net.nz'.format(name, username)
            user, created = UserProxy.objects.update_or_create(username=username, defaults={'email': email})
            user.set_due_date(due_date)
            self.stdout.write('{} user {}'.format('create' if created else 'update', email))
