from django.conf import settings
from path import Path


def log_me(text, print_me=True, write_me=True, name='lef', append=False):
    """
    This log is used to debug big blob of text like xml.

    The default logging will truncate long text.
    """
    if settings.DEBUG:
        if print_me:
            print(text)
        if write_me:
            Path('/tmp/{}'.format(name)).touch().write_text(text, append=append)


def set_exchange_cookie(response, value, **kwargs):
    """
    Set value for exchange cookie.

    We use a cookie called `is_authenticated` to exchange infomation like
    authentication status and error code to frontend. This function is a shortcurt
    to set the cookie value.
    """
    response.set_cookie(
        settings.EXCHANGE_COOKIE_NAME,
        value=value,
        **kwargs
    )
    return response
