from rest_framework import authentication


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
