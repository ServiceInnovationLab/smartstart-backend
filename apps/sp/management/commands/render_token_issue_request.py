from django.core.management.base import BaseCommand
from ...bundles import Bundle


class Command(BaseCommand):
    help = "Render Token Request xml"

    def handle(self, *args, **options):
        b = Bundle(site_url=options.get('site_url'))
        text = b.render_token_issue_request()
        self.stdout.write(text.decode('utf-8'))

