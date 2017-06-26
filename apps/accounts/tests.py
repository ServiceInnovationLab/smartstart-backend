import time
from datetime import date
from django.test import override_settings
from apps.base.tests import BaseTestCase
from apps.accounts.models import Preference


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
        self.assertEqual(self.test.profile.get_due_date(), date(2016, 10, 28))

    def test_unsubscribe(self):
        profile = self.test.profile
        profile.subscribed = True
        profile.save()
        self.client.get(profile.unsubscribe_url)
        profile.refresh_from_db()
        self.assertFalse(profile.subscribed)
