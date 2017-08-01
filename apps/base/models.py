from enum import Enum, unique
from django.db import models
from django.conf import settings


@unique
class Choice(Enum):

    @classmethod
    def choices(cls):
        return ((e.name, e.value) for e in cls)


class TimeStampedModel(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    modified_at = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True
        ordering = ['-modified_at']


class ConfigManager(models.Manager):

    def set_value(self, key, value):
        return Config.objects.update_or_create(key=key, defaults={'value': value})

    def get_value(self, key, default=None):
        obj = Config.objects.filter(key=key).first()
        return obj.value if obj else default


class Config(models.Model):
    objects = ConfigManager()

    key = models.CharField(max_length=100, unique=True)
    value = models.TextField(blank=True, default='')

    def __str__(self):
        return '{}: {}'.format(self.key, self.value)


class SiteLocker:

    @property
    def site_hash(self):
        """Get SITE_HASH in django settings"""
        return getattr(settings, 'SITE_HASH', None)

    def is_live(self):
        """
        Return whether this Django instance is "live" by checking the
        ``SITE_HASH`` setting against the database value.

        For dev and test instances, both value are None, should still equal.
        """
        return Config.objects.get_value('site_hash') == self.site_hash

    def make_live(self):
        """
        The ``SITE_HASH`` setting is populated from the configuration management
        tool at the point of building the servers. This will put the hash in the
        database so that any instance of Django (in a cluster, or a blue/green
        scenario, etc.) can determine which instance is "live".
        """
        Config.objects.set_value('site_hash', self.site_hash)

    def lock(self, name):
        """
        Implement a simple and generic locker based on the Config model in database.

        Given a locker name, set the timestamp to mark it as locked.
        Use together with `unlock` and `is_locked`.
        """
        from django.utils import timezone
        return Config.objects.set_value(name, timezone.now().isoformat())

    def unlock(self, name):
        return Config.objects.set_value(name, '')

    def is_locked(self, name):
        return bool(Config.objects.get_value(name))
