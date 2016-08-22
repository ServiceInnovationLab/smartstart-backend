from django.core.management.base import BaseCommand
from ...bundles import Bundle


class Command(BaseCommand):
    help = "Send Token Issue Request"

    def handle(self, *args, **options):
        b = Bundle(site_url=options.get('site_url'))
        r = b.send_token_issue_request()
        self.stdout.write(r.content.decode('utf-8'))

