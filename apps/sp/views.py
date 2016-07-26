import logging

from django.conf import settings
from django.shortcuts import redirect
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth import login as auth_login
from django.contrib.auth import authenticate
from django import http

from annoying.decorators import render_to

from onelogin.saml2.auth import OneLogin_Saml2_Auth
from onelogin.saml2.settings import OneLogin_Saml2_Settings
from onelogin.saml2.utils import OneLogin_Saml2_Utils

log = logging.getLogger(__name__)


def init_saml_auth(req):
    return OneLogin_Saml2_Auth(req, custom_base_path=settings.SAML_FOLDER)


def prepare_django_request(request):
    # If server is behind proxys or balancers use the HTTP_X_FORWARDED fields
    result = {
        'https': 'on' if request.is_secure() else 'off',
        'http_host': request.META['HTTP_HOST'],
        'script_name': request.META['PATH_INFO'],
        'server_port': request.META['SERVER_PORT'],
        'get_data': request.GET.copy(),
        # Uncomment if using ADFS as IdP, https://github.com/onelogin/python-saml/pull/144
        # 'lowercase_urlencoding': True,
        'post_data': request.POST.copy()
    }
    return result


def login(request):
    req = prepare_django_request(request)
    auth = init_saml_auth(req)
    url = auth.login()
    log.info('sp login url: {}'.format(url))
    return redirect(url)


def metadata(request):
    # req = prepare_django_request(request)
    # auth = init_saml_auth(req)
    # saml_settings = auth.get_settings()
    saml_settings = OneLogin_Saml2_Settings(settings=None, custom_base_path=settings.SAML_FOLDER, sp_validation_only=True)
    metadata = saml_settings.get_sp_metadata()
    errors = saml_settings.validate_metadata(metadata)

    if errors:
        return http.HttpResponseServerError(content=', '.join(errors))
    else:
        return http.HttpResponse(content=metadata, content_type='text/xml')


@csrf_exempt
@render_to('realme/acs.html')
def assertion_consumer_service(request):
    if request.method == 'POST':
        req = prepare_django_request(request)
        auth = init_saml_auth(req)
        auth.process_response()
        errors = auth.get_errors()
        if not errors:
            request.session['samlUserdata'] = auth.get_attributes()
            request.session['samlNameId'] = auth.get_nameid()
            request.session['samlSessionIndex'] = auth.get_session_index()
            if auth.is_authenticated():
                user = authenticate(saml_auth=auth)
                if user is not None:
                    if user.is_active:
                        auth_login(request, user)
                        return redirect('/')
                # TODO: redirect to RelayState?
                # if 'RelayState' in req['post_data'] and OneLogin_Saml2_Utils.get_self_url(req) != req['post_data']['RelayState']:
                #     return redirect(auth.redirect_to(req['post_data']['RelayState']))
    else:
        return http.HttpResponseBadRequest()

    return {
        'errors': errors,
    }
