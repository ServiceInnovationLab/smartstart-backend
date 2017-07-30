import json
from django.test import TestCase, override_settings
from apps.accounts.models import UserProxy

class BaseTestCase(TestCase):
    fixtures = [
        'test_users',
        'phasemetadata',
    ]

    def setUp(self):
        self.admin = UserProxy.objects.get(username='admin')
        self.admin.email = 'lef-dev+admin@catalyst.net.nz'
        self.admin.save()
        self.test = UserProxy.objects.get(username='test')
        self.test.email = 'lef-dev+test@catalyst.net.nz'
        self.test.save()

        self.api_preferences = '/api/preferences/'
        self.api_users = '/api/users/'
        self.api_me = '/api/users/me/'
        self.api_phasemetadata = '/api/phase-metadata/'
        self.api_emailaddresses = '/api/emailaddresses/'

    def login(self, username):
        credentials = {'username': username, 'password': 'admin' if username == 'admin' else 'test'}
        return self.client.login(**credentials)  # True or False

    def post_json(self, api, data, expected=201):
        r = self.client.post(api, json.dumps(data), content_type='application/json')
        self.assertEqual(r.status_code, expected)
        return json.loads(r.content.decode('utf-8'))

    def get_json(self, api, expected=200):
        r = self.client.get(api)
        self.assertEqual(r.status_code, expected)
        return json.loads(r.content.decode('utf-8'))


class GenericTestCase(BaseTestCase):

    def test_make_live_invalid(self):
        url = '/make_live/INVALID_SITE_HASH'
        r = self.client.get(url)
        self.assertEqual(r.status_code, 404)

    @override_settings(SITE_HASH='1234')
    def test_make_live(self):
        url = '/make_live/1234/'
        r = self.client.get(url.format('invalid-site-hash'))
        self.assertEqual(r.status_code, 200)
