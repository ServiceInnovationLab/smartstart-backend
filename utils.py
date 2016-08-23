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
            Path('/tmp/{}.log'.format(name)).touch().write_text(text, append=append)
