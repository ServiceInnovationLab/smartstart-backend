# -*- coding: utf-8 -*-
import requests
import logging

from django.conf import settings
from django.contrib.postgres import fields as pgfields
from django.db import models
from django.utils import timezone
from apps.base.models import TimeStampedModel
from apps.request_cache import ckan

log = logging.getLogger(__name__)


class RequestCache(TimeStampedModel):
    name = models.CharField(max_length=50, unique=True)
    """
    Query name as a slug, using the name parameter in urls.py, e.g. "lbs_parenting_support".
    """

    result = pgfields.JSONField(null=False, default={})
    """
    The most recently fetched result, as JSON.
    """

    def fetch_query(self):
        """
        Fetch the remote result, and store in the database on success.
        """
        if self.name == 'content_timeline':
            r = requests.get(settings.TIMELINE_URL, headers={'User-Agent': settings.TIMELINE_USER_AGENT})
        else:
            # Collapse SQL whitespace to reduce URL length as much as possible
            sql = ' '.join(ckan.SQL_QUERIES[self.name].format(**ckan.SQL_SUBST).split())
            r = requests.get(settings.CKAN_QUERY_URL, params={'sql': sql})

        try:
            response = r.json()
        except ValueError as e:
            log.warn('Did not get JSON response from remote query: {}'.format(self.name))
            log.debug('Got error "{}" from remote URL {}'.format(e, r.request.url))
            return False

        if r.status_code == 200:
            self.result = response
            self.save()
            return True

        # Update TTL if we get a cache not modified response.
        if r.status_code == 304:
            self.modified_at = timezone.now()
            self.save()
            return True

        status_class = r.status_code // 100
        if status_class in (4, 5) or ('success' in response and not response['success']):
            log.debug('Error from query "{}": {}'.format(self.name, response['error'] if 'error' in response else 'HTTP {}'.format(r.status_code)))
            return False

    def get_result(self):
        """
        This returns a result, fetching a new one if it is too old or empty.
        """
        if self.result == {} or self.modified_at < timezone.now() - settings.REQUEST_CACHE_TTL:
            self.fetch_query()
        return self.result
