import logging
log = logging.getLogger(__name__)


class UserCookieMiddleWare(object):
    """
    Middleware to set user cookie
    If user is authenticated and there is no cookie, set the cookie,
    If the user is not authenticated and the cookie remains, delete it
    """

    def process_response(self, request, response):
        # if user and no cookie, set cookie
        if hasattr(request, 'user'):
            cookie_name = 'is_authenticated'
            if request.user.is_authenticated() and request.COOKIES.get(cookie_name) != 'true':
                response.set_cookie(cookie_name, 'true')
            elif not request.user.is_authenticated() and request.COOKIES.get(cookie_name) == 'true':
                # else if if no user and cookie remove user cookie, logout
                response.delete_cookie(cookie_name)
                log.info('is_authenticated deleted')
        return response
