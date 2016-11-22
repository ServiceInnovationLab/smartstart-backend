from django.conf import settings
from django.utils import timezone
from django.contrib.auth import logout
from rest_framework import status, authentication, exceptions, permissions


class FixedSessionTimeout(exceptions.APIException):
    status_code = status.HTTP_401_UNAUTHORIZED
    default_code = 'local-timeout'
    default_detail = 'Local session timeout.'


class FixedSessionAuthentication(authentication.SessionAuthentication):
    """Stop API to write if user logged in more than 30 mins"""

    def authenticate(self, request):
        user_auth = super().authenticate(request)
        if request.method not in permissions.SAFE_METHODS:
            if user_auth:
                user = user_auth[0]
                if user and user.is_authenticated():
                    delta = timezone.now() - user.last_login
                    if delta.total_seconds() > settings.SESSION_COOKIE_AGE_SAVE:
                        logout(request._request)
                        raise FixedSessionTimeout()
        return user_auth
