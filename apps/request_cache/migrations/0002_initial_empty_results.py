# -*- coding: utf-8 -*-
from django.db import models, migrations
from django.core.management import call_command
from apps.request_cache.ckan import SQL_QUERIES


def commit_data(apps, schema_editor):
    RequestCache = apps.get_model('request_cache', 'RequestCache')

    # CKAN Location-Based Services SQL queries
    for name in SQL_QUERIES:
        (r, created) = RequestCache.objects.get_or_create(name=name)
        if created:
            r.result = {}
            r.save()

    # Separate timeline content query
    (r, created) = RequestCache.objects.get_or_create(name='content_timeline')
    if created:
        r.result = {}
        r.save()


def rollback_data(apps, schema_editor):
    RequestCache = apps.get_model('request_cache', 'RequestCache')
    RequestCache.objects.all().delete()
    return


class Migration(migrations.Migration):

    dependencies = [
        ('request_cache', '0001_initial'),
    ]

    operations = [
        migrations.RunPython(
            commit_data,
            reverse_code=rollback_data),
    ]
