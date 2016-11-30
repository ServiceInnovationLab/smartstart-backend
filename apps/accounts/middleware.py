from django.conf import settings
from django.shortcuts import redirect
from django.utils.deprecation import MiddlewareMixin
import logging
log = logging.getLogger(__name__)


class UserCookieMiddleWare(MiddlewareMixin):
    """
    Middleware to set user cookie
    If user is authenticated and there is no cookie, set the cookie,
    If the user is not authenticated and the cookie remains, delete it
    """

    def process_response(self, request, response):
        # if user and no cookie, set cookie
        if hasattr(request, 'user'):
            cookie_name = settings.EXCHANGE_COOKIE_NAME
            if request.user.is_authenticated() and request.COOKIES.get(cookie_name) != 'true':
                response.set_cookie(
                    cookie_name,
                    'true',
                    max_age=settings.SESSION_COOKIE_AGE,
                    secure=settings.SESSION_COOKIE_SECURE
                )
            elif not request.user.is_authenticated() and request.COOKIES.get(cookie_name) == 'true':
                # else if if no user and cookie remove user cookie, logout
                response.delete_cookie(cookie_name)
                log.info('is_authenticated deleted')
        return response


class Check2FAMiddleware(MiddlewareMixin):
    """
    Check 2FA status for Django Admin.
    """
    def process_request(self, request):
        user = request.user
        if user.id and user.is_staff and user.totpdevice_set.count() == 0:
            if request.path.startswith('/admin'):
                return redirect('two_factor:setup')
