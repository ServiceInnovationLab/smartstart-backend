from django.core.management.base import BaseCommand
from ...bundles import Bundle


class Command(BaseCommand):
    help = "Render POST Binding xml"

    def add_arguments(self, parser):
        parser.add_argument(
            '--site-url',
            nargs='?',
            dest='site_url',
            help='Optional site url, e.g.: https://uat.bundle.services.govt.nz'
        )

    def handle(self, *args, **options):
        site_url = options.get('site_url')
        idp = Bundle(site_url=site_url)
        text = idp.render_xml()
        self.stdout.write(text)
