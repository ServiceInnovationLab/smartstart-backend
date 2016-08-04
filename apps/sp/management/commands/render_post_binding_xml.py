from path import path
from django.core.management.base import BaseCommand, CommandError
from django.template.loader import render_to_string
from django.conf import settings
from ...idps import get_idp
from utils import get_cer_body, full_reverse


class Command(BaseCommand):
    help = "Render POST Binding xml"

    def add_arguments(self, parser):
        parser.add_argument(
            '--site-url',
            nargs='?',
            dest='site_url',
            help='Optional site url, e.g.: https://uat.bundle.services.govt.nz'
        )
        parser.add_argument(
            '--sp-cer',
            nargs='?',
            dest='sp_cer',
            help='Optional full path to sp certificate file, e.g.: /home/joeg/bundles/MTS/mts_saml_sp.cer'
        )

    def handle(self, *args, **options):
        site_url = options.get('site_url') or getattr(settings, 'SITE_URL')
        if not site_url:
            raise CommandError('Please specify SITE_URL in command line or settings')

        entity_id = full_reverse('sp_login', site_url=site_url).strip('/')
        acs_url = full_reverse('sp_acs', site_url=site_url)

        sp_cer = options.get('sp_cer')
        sp_cer_body = ''
        if sp_cer:
            sp_cer_path = path(sp_cer)
            if not sp_cer_path.isfile():
                raise CommandError('sp_cer path is not a valid file: {}'.format(sp_cer))
            else:
                sp_cer_text = sp_cer_path.text()
                sp_cer_body = get_cer_body(sp_cer_text)
                if not sp_cer_body:
                    raise CommandError('sp_cer body is empty: {}'.format(sp_cer_text))

        if not sp_cer_body:
            idp = get_idp(settings.IDP)
            if not idp:
                raise CommandError('Invalid IDP in settings: {}'.format(settings.IDP))
            else:
                sp_cer_body = idp.sp_cer

        template = 'sp/SP_PostBinding.xml'
        ctx = {
            'entity_id': entity_id,
            'full_acs_url': acs_url,
            'sp_cer': sp_cer_body,
        }
        text = render_to_string(template, ctx)
        self.stdout.write(text)
