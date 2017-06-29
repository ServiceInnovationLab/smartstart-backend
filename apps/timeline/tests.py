from datetime import date, timedelta
from django.core.management import call_command
from apps.base.tests import BaseTestCase
from apps.accounts.models import Profile
from apps.timeline import models as m


class PhaseMetadataTestCase(BaseTestCase):

    def setUp(self):
        BaseTestCase.setUp(self)

    def test_permission(self):
        # this api should be public, but readonly to all users
        data = {'weeks_start': 42, 'weeks_finish': 45}

        # test annoymous user
        self.get_json(self.api_phasemetadata, expected=200)
        self.post_json(self.api_phasemetadata, data=data, expected=403)

        # test normal user
        self.login('test')
        self.get_json(self.api_phasemetadata, expected=200)
        self.post_json(self.api_phasemetadata, data=data, expected=403)

        # test admin user
        self.login('admin')
        self.get_json(self.api_phasemetadata, expected=200)
        self.post_json(self.api_phasemetadata, data=data, expected=403)

    def test_get_weeks(self):
        due_date = date(2016, 10, 28)
        helper = m.PregnancyHelper(due_date)

        self.assertEqual(helper.get_weekno(ref_date=due_date - timedelta(days=1)), m.PREGNANCY_TOTAL_WEEKS-1)
        self.assertEqual(helper.get_weekno(ref_date=due_date), m.PREGNANCY_TOTAL_WEEKS)
        self.assertEqual(helper.get_weekno(ref_date=due_date + timedelta(days=1)), m.PREGNANCY_TOTAL_WEEKS)
        self.assertEqual(helper.get_weekno(ref_date=due_date + timedelta(days=7)), m.PREGNANCY_TOTAL_WEEKS+1)

    def test_notifications(self):
        """
        Test most common case for notification.

        Today, user knows she is pregnant 30 days ago.
        """
        user = self.test
        profile = user.profile
        today = date.today()
        pregnancy_date = today - timedelta(days=30)
        due_date = pregnancy_date + timedelta(weeks=40)

        # call for today
        # no due date, should not create
        ref_date = today
        Profile.objects.generate_notifications(ref_date=ref_date)
        self.assertEqual(profile.get_due_date(), None)
        self.assertFalse(user.notification_set.exists())

        # set due date
        profile.set_due_date(due_date)
        self.assertEqual(profile.get_due_date(), due_date)

        Profile.objects.generate_notifications(ref_date=ref_date)
        n = user.notification_set.get(phase_id=1)
        self.assertEqual(user.notification_set.count(), 1)
        self.assertEqual(n.status, 'pending')

        call_command('send_notifications')
        n = user.notification_set.get(phase_id=1)
        self.assertEqual(n.status, 'delivered')

        # call again 1 week later, should not do anything
        ref_date = today + timedelta(weeks=1)
        Profile.objects.generate_notifications(ref_date=ref_date)
        self.assertEqual(user.notification_set.count(), 1)
        n = user.notification_set.get(phase_id=1)
        self.assertEqual(n.status, 'delivered')

        # call again 14 weeks later, which is 1 week before phase 2: 15~30 weeks
        ref_date = today + timedelta(weeks=14)
        Profile.objects.generate_notifications(ref_date=ref_date)
        # should get a new notification for phase 2
        self.assertEqual(user.notification_set.count(), 2)
        n = user.notification_set.get(phase_id=2)
        self.assertEqual(n.status, 'pending')

        # call again 31 weeks and 2 days later
        # for some reason cron job is 2 days late, should still work
        ref_date = today + timedelta(weeks=31, days=2)
        Profile.objects.generate_notifications(ref_date=ref_date)
        # should get a new notification for phase 3
        self.assertEqual(user.notification_set.count(), 3)
        n = user.notification_set.get(phase_id=3)
        self.assertEqual(n.status, 'pending')
