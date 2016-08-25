from django.core.management.base import BaseCommand
from ...bundles import Bundle


class Command(BaseCommand):
    help = "Send Token Issue Request"

    def handle(self, *args, **options):
        b = Bundle(site_url=options.get('site_url'))
        b.send_token_issue_request()

