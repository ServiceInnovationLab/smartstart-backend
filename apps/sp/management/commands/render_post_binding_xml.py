from django.core.management.base import BaseCommand, CommandError
from django.template.loader import render_to_string
from django.conf import settings
from ...idps import get_idp


class Command(BaseCommand):
    help = "Render POST Binding xml"

    def add_arguments(self, parser):
        parser.add_argument(
            '--noinput', '--no-input',
            action='store_false', dest='interactive', default=True,
            help="Do NOT prompt the user for input of any kind.",
        )

    def handle(self, *args, **options):
        site_url = getattr(settings, 'SITE_URL')
        if not site_url:
            raise CommandError('Please specify SITE_URL in settings')

        if options['interactive']:
            msg = "\nYou're going to use this SITE_URL: \n\n    {}\n\nIs it correct?\n\nType 'yes' to continue, or 'no' to cancel: ".format(site_url)
            if input(msg).lower() != 'yes':
                raise CommandError("Render cancelled.")

        idp = get_idp(settings.IDP)
        if not idp:
            raise CommandError('Invalid IDP in settings: {}'.format(settings.IDP))

        template = 'sp/SP_PostBinding.xml'
        ctx = {
            'entity_id': idp.entity_id,
            'full_acs_url': idp.acs_url,
            'sp_cer': idp.sp_cer,
        }
        text = render_to_string(template, ctx)
        self.stdout.write('\n{0}PostBinding XML{0}\n\n'.format('=' * 20))
        self.stdout.write(text)
