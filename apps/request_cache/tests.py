# -*- coding: utf-8 -*-
from apps.base.tests import BaseTestCase
from apps.request_cache import models


class RequestCacheTests(BaseTestCase):

    def setUp(self):
        BaseTestCase.setUp(self)

    def test_fetch_ckan_result(self):
        # Fetch 'parenting support' data from CKAN
        self.login('test')
        result = self.get_json('/api/request/service-locations/parenting-support', expected=200)
        if 'success' not in result or not result['success']:
            self.fail(result)
        self.assertEqual(result['success'], True)

        # Check it's cached in the database
        row = models.RequestCache.objects.get(name='lbs_parenting_support')
        self.assertEqual(row.result['success'], True)
