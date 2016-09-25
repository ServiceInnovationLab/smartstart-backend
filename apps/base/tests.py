import json
from django.test import TestCase
from django.contrib.auth.models import User

class BaseTestCase(TestCase):
    fixtures = [
        'test_users',
        'phasemetadata',
    ]

    def setUp(self):
        self.admin = User.objects.get(username='admin')
        self.test = User.objects.get(username='test')

        self.api_preferences = '/api/preferences/'
        self.api_users = '/api/users/'
        self.api_me = '/api/users/me/'
        self.api_phasemetadata = '/api/phase-metadata/'

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
