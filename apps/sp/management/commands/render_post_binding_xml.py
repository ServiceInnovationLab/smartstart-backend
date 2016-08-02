from django.core.management.base import BaseCommand
from django.template.loader import render_to_string
from django.conf import settings
from ...idps import get_idp


class Command(BaseCommand):
    help = "Render POST Binding xml"

    def handle(self, *args, **options):
        template = 'sp/SP_PostBinding.xml'
        idp = get_idp(settings.IDP)
        if not idp:
            self.stderr.write('Invalid IDP in settings: {}'.format(settings.IDP))
            return
        ctx = {
            'entity_id': idp.entity_id,
            'full_acs_url': idp.acs_url,
            'sp_cer': idp.sp_cer,
        }
        text = render_to_string(template, ctx)
        self.stdout.write(text)
