from django.core.management.base import BaseCommand
from apps.accounts.models import BroForm


class Command(BaseCommand):
    help = 'Expire stale BRO partial save data.'

    def handle(self, *args, **options):
        n = BroForm.objects.expire_old_data()
        self.stdout.write("Stale BRO forms deleted: {}".format(n))
