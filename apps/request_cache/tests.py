# -*- coding: utf-8 -*-
from django.urls import reverse
from apps.base.tests import BaseTestCase
from apps.request_cache import models
from apps.request_cache.ckan import SQL_QUERIES


class RequestCacheTests(BaseTestCase):

    def setUp(self):
        BaseTestCase.setUp(self)

    def test_fetch_ckan_result(self):
        # Fetch 'parenting support' data from CKAN
        self.login('test')
        for name in SQL_QUERIES:
            print('Trying SQL: {}'.format(name))
            result = self.get_json(reverse('request_cache:{}'.format(name)), expected=200)
            if 'success' not in result or not result['success']:
                self.fail(result)
            self.assertEqual(result['success'], True)
            print('Success.'.format(name))

            # Check it's cached in the database
            row = models.RequestCache.objects.get(name=name)
            self.assertEqual(row.result['success'], True)
