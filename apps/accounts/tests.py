import time
from datetime import date
from django.core import mail
from django.test import override_settings
from apps.base.tests import BaseTestCase
from apps.accounts.models import UserProxy, Preference, EmailAddress


class SessionTestCase(BaseTestCase):
    def setUp(self):
        BaseTestCase.setUp(self)

    @override_settings(SESSION_COOKIE_AGE=1)
    def test_session_timeout(self):
        self.login('test')
        time.sleep(2)

        self.get_json(self.api_me, expected=403)

        # should timeout for post
        obj = {'group': 'settings', 'key': 'key0', 'val': 'val0'}
        self.post_json(self.api_preferences, obj, expected=403)


class PreferenceTestCase(BaseTestCase):

    def setUp(self):
        BaseTestCase.setUp(self)

    def test_single_create(self):
        self.login('test')
        obj = {'group': 'settings', 'key': 'key0', 'val': 'val0'}
        self.post_json(self.api_preferences, obj)
        self.assertEqual(Preference.objects.all().count(), 1)
        yes = Preference.objects.filter(user=self.test, **obj)
        self.assertTrue(yes)

        me_json = self.get_json(self.api_me)
        pref_json = me_json['preferences']
        self.assertEqual(pref_json['settings'], {'key0': 'val0'})

    def test_bulk_create(self):
        self.login('test')
        objs = [
            {'group': 'settings', 'key': 'key0', 'val': 'val0'},
            {'group': 'settings', 'key': 'key1', 'val': 'val1'},
        ]
        self.post_json(self.api_preferences, objs)
        self.assertEqual(Preference.objects.all().count(), len(objs))
        for obj in objs:
            yes = Preference.objects.filter(user=self.test, **obj)
            self.assertTrue(yes)

        me_json = self.get_json(self.api_me)
        pref_json = me_json['preferences']
        self.assertEqual(pref_json['settings'], {'key0': 'val0', 'key1': 'val1'})

    def test_wrong_field_name(self):
        self.login('test')
        obj = {'group': 'settings', 'key': 'key0', 'value': 'val0'}  # should be val
        r = self.post_json(self.api_preferences, obj, expected=400)
        self.assertEqual(r, {'val': ['This field is required.']})

    def test_val_allow_blank(self):
        """
        Although val is required, but it's allowed to be blank
        """
        self.login('test')
        obj = {'group': 'settings', 'key': 'key0', 'val': ''}
        self.post_json(self.api_preferences, obj, expected=201)

    def test_due_date(self):
        """
        Set due date via preference API, and retrieve it.
        """
        self.login('test')
        obj = {'group': 'settings', 'key': 'dd', 'val': '2016-10-28'}
        self.post_json(self.api_preferences, obj, expected=201)
        self.assertEqual(self.test.due_date, date(2016, 10, 28))

    def test_unsubscribe(self):
        user = self.test
        self.client.get(user.unsubscribe_url)
        user.refresh_from_db()
        self.assertFalse(user.subscribed)


class AccountTestCase(BaseTestCase):

    def setUp(self):
        BaseTestCase.setUp(self)

    def test_email_confirm(self):
        # a user has no email and not subscribed
        user = self.test
        user.email = ''
        user.save()
        user.subscribe()

        # change mail via API
        self.login('test')
        data = {'email': 'lef-dev+test@catalyst.net.nz'}
        self.post_json(self.api_emailaddresses, data, expected=201)

        # should create pending EmailAddress recored for user
        obj = EmailAddress.objects.first()
        self.assertEqual(obj.user, user)
        self.assertEqual(obj.email, data['email'])

        # should trigger a email contains confirm url
        self.assertEqual(len(mail.outbox), 1)
        self.assertIn(obj.confirm_url, mail.outbox[0].body)

        # click url
        self.client.get(obj.confirm_url)
        user.refresh_from_db()
        self.assertEqual(user.email, data['email'])
        self.assertTrue(user.subscribed)
        self.assertEqual(EmailAddress.objects.count(), 0)

        # now change again
        data = {'email': 'lef-dev+test2@catalyst.net.nz'}
        self.post_json(self.api_emailaddresses, data, expected=201)

        obj = EmailAddress.objects.first()
        self.client.get(obj.confirm_url)
        user.refresh_from_db()
        self.assertEqual(user.email, data['email'])

    def test_subscribers_filter(self):
        user = self.test
        self.assertGreater(len(user.email), 5)
        # by default, user has no due date and no subscribe pref

        # no due date, not a subscriber
        self.assertNotIn(user, UserProxy.objects.subscribers())

        user.set_due_date(date.today())
        # user has due date now, although he has no subscribed pref
        # but it should default to true
        self.assertIn(user, UserProxy.objects.subscribers())

        user.subscribe()
        # subscribe explicitly
        self.assertIn(user, UserProxy.objects.subscribers())

        user.unsubscribe()
        # ubsubscribe explicitly
        self.assertNotIn(user, UserProxy.objects.subscribers())

        # no email
        user.subscribe()
        user.email = ''
        user.save()
        self.assertNotIn(user, UserProxy.objects.subscribers())

    def test_invalid_due_date_str(self):
        user = self.test
        # defaults to true
        self.assertTrue(user.subscribed)

        # wrong format, not a date
        user.set_preference('dd', 'hello')
        self.assertNotIn(user, UserProxy.objects.subscribers())
        self.assertIsNone(user.due_date)

        # a date with unstandard format(YYYY-mm-dd)
        user.set_preference('dd', '2016-1-1')
        self.assertIn(user, UserProxy.objects.subscribers())
        self.assertIsNotNone(user.due_date)

        # correct format
        user.set_preference('dd', '2016-10-28')
        self.assertIn(user, UserProxy.objects.subscribers())
