from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from ...bundles import Bundle


class Command(BaseCommand):
    help = "Send Token Issue Request for user_id"

    def add_arguments(self, parser):
        parser.add_argument('user_id', type=int)

    def handle(self, *args, **options):
        user_id = options['user_id']
        user = User.objects.get(id=user_id)
        b = Bundle(site_url=options.get('site_url'))
        b.send_token_issue_request(user)

