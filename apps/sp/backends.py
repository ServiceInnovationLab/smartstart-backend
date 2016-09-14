from django.contrib.auth.models import User
from apps.accounts.models import Profile
from utils import log_me

import logging
log = logging.getLogger(__name__)


class SamlBackend(object):

    def authenticate(self, saml2_auth=None):
        username = saml2_auth.get_nameid()
        user, _ = User.objects.get_or_create(username=username)
        attrs = saml2_auth.get_attributes()
        if attrs:
            logon_attributes_token = attrs.get('logon_attributes_token', [''])[0]
            Profile.objects.update_or_create(user=user, defaults={'logon_attributes_token': logon_attributes_token})
            log_me(logon_attributes_token, name='logon_attributes_token.xml')
        else:
            log.error('no attrs for logon')
        return user

    def get_user(self, user_id):
        try:
            return User.objects.get(pk=user_id)
        except User.DoesNotExist:
            return None
