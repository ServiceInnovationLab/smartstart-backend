import logging

from django.shortcuts import redirect
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth import login as auth_login
from django.contrib.auth import authenticate
from django import http

from decorators import render_to

from onelogin.saml2.auth import OneLogin_Saml2_Auth
from onelogin.saml2.response import OneLogin_Saml2_Response
from onelogin.saml2.settings import OneLogin_Saml2_Settings
from onelogin.saml2.utils import OneLogin_Saml2_Utils
from onelogin.saml2.constants import OneLogin_Saml2_Constants
from .bundles import Bundle

log = logging.getLogger(__name__)
_saml2_settings = None


def get_saml2_settings():
    global _saml2_settings
    if not _saml2_settings:
        bundle = Bundle()
        _saml2_settings = OneLogin_Saml2_Settings(
            settings=bundle.get_settings(),
            sp_validation_only=True,
        )
    return _saml2_settings


def prepare_django_request(request):
    # If server is behind proxys or balancers use the HTTP_X_FORWARDED fields
    return {
        'https': 'on' if request.is_secure() else 'off',
        'http_host': request.META['HTTP_HOST'],
        'script_name': request.META['PATH_INFO'],
        'server_port': request.META.get('HTTP_X_FORWARDED_PORT') or request.META.get('SERVER_PORT'),
        'get_data': request.GET.copy(),
        # Uncomment if using ADFS as IdP, https://github.com/onelogin/python-saml/pull/144
        # 'lowercase_urlencoding': True,
        'post_data': request.POST.copy()
    }


def init_saml2_auth(request):
    req = prepare_django_request(request)
    return OneLogin_Saml2_Auth(req, get_saml2_settings())


def login(request):
    auth = init_saml2_auth(request)
    url = auth.login()
    log.info('sp login url: {}'.format(url))
    return redirect(url)


def metadata(request):
    metadata = get_saml2_settings().get_sp_metadata()
    errors = get_saml2_settings().validate_metadata(metadata)

    if errors:
        return http.HttpResponseServerError(content=', '.join(errors))
    else:
        return http.HttpResponse(content=metadata, content_type='text/xml')


@csrf_exempt
@render_to('sp/error.html')
def assertion_consumer_service(request):
    if request.method != 'POST':
        return http.HttpResponseBadRequest()

    auth = init_saml2_auth(request)
    saml2_response = OneLogin_Saml2_Response(
        get_saml2_settings(),
        request.POST['SAMLResponse'],
    )
    status = OneLogin_Saml2_Utils.get_status(saml2_response.document)
    # status example: {code: FOO, msg: BAR}
    code = status.get('code')
    if code != OneLogin_Saml2_Constants.STATUS_SUCCESS:
        log.error('saml response status: {}'.format(status))
        return status

    auth.process_response()
    error_reason = auth.get_last_error_reason()
    if error_reason:
        return {'code': 'ERROR', 'msg': error_reason}

    if not auth.is_authenticated():
        return {'code': 'NOTAUTHENTICATED', 'msg': 'NOT AUTHENTICATED'}

    user = authenticate(saml2_auth=auth)
    if user is not None:
        if user.is_active:
            auth_login(request, user)
            return redirect('/')

    return {'code': 'ERROR', 'msg': 'ACS Failed'}
