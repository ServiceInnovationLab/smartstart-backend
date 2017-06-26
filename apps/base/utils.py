import base64
from urllib.parse import urljoin
from django.conf import settings
from django.template import Template, Context
from path import Path


def get_full_url(url):
    return urljoin(settings.SITE_URL, url)


def get_logo_img_path():
    return Path(settings.BASE_DIR) / 'static/img/smartstart-logo.png'


def get_logo_img_data():
    logo_path = get_logo_img_path()
    return base64.encodebytes(logo_path.bytes())


def render_string(string='', context={}):
    """Render a template string with context"""
    return Template(string).render(Context(context))
