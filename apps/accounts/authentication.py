from django.conf import settings
from django.utils import timezone
from django.contrib.auth import logout
from rest_framework import status, authentication, exceptions


class FixedSessionTimeout(exceptions.APIException):
    status_code = status.HTTP_401_UNAUTHORIZED
    default_code = 'local-timeout'
    default_detail = 'Local session timeout.'


class FixedSessionAuthentication(authentication.SessionAuthentication):
    """Stop API to write if user logged in more than 30 mins"""

    def authenticate(self, request):
        user_auth = super().authenticate(request)
        if user_auth:
            user = user_auth[0]
            if user and user.is_authenticated():
                delta = timezone.now() - user.last_login
                if delta.total_seconds() > settings.SESSION_COOKIE_AGE:
                    logout(request._request)
                    raise FixedSessionTimeout()
        return user_auth


class AnonymousSessionAuthentication(authentication.SessionAuthentication):
    """
    Enforces CSRF validation on anonymous sessions. This is done in an
    Authentication class for consistency with SessionAuthentication, where
    Django Rest Framework normally validates the CSRF token
    """

    def authenticate(self, request):

        # Get the session-based user from the underlying HttpRequest object.
        # If user hasn't authenticated, Django provides an AnonymousUser object
        user = getattr(request._request, 'user', None)

        self.enforce_csrf(request)

        return user, None
