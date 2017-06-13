from datetime import datetime, date
from django.core.management.base import BaseCommand
from apps.accounts.models import Profile, Preference


class Command(BaseCommand):
    help = "Generate notifications, run every 5 mins"

    def add_arguments(self, parser):
        parser.add_argument(
            '--date',
            help='fake the date with format: 2017-06-13'
        )

    def handle(self, *args, **options):
        date_str = options.get('date')
        if date_str:
            ref_date = datetime.strptime(date_str, '%Y-%m-%d').date()
        else:
            ref_date = date.today()
        # users who have due date and email
        user_ids = Preference.objects.filter(
            key='dd',
            user__email__isnull=False,
        ).exclude(
            user__email='',
        ).values_list(
            'user_id',
            flat=True
        )
        profiles = Profile.objects.filter(
            subscribed=True,
            user__id__in=user_ids,
        )
        for p in profiles:
            p.generate_notifications(ref_date=ref_date)
