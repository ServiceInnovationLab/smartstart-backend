from django.core.management.base import BaseCommand
from ...mail import ses_send_mail


class Command(BaseCommand):
    help = 'Send ses mail to address'

    def add_arguments(self, parser):
        parser.add_argument('--email', help='recipient email address')

    def handle(self, *args, **options):
        email = options.get('email', 'lef-dev@catalyst.net.nz')
        ses_send_mail(
            'this is a test mail from AWS SES',
            'Across the Great Wall we can reach every corner in the world.',
            [email],
        )
