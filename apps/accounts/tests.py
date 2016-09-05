from apps.base.tests import BaseTestCase
from apps.accounts.models import Preference

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
