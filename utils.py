from django.conf import settings
from path import Path

def log_me(text, print_me=True, write_me=True, file_path='/tmp/lef.log', append=True):
    if settings.DEBUG:
        if print_me:
            print(text)
        if write_me:
            Path(file_path).touch().write_text(text, append=append)
