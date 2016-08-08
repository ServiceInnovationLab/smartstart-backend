from django.conf import settings
from django.core.urlresolvers import reverse
from django.template.loader import render_to_string

from path import path
from onelogin.saml2.constants import OneLogin_Saml2_Constants as constants


BUNDLES = {
    'MTS': {
        'idp_entity_id': 'https://mts.realme.govt.nz/saml2',
        'saml_idp_cer': 'mts_login_saml_idp.cer',
        'mutual_ssl_idp_cer': 'mts_mutual_ssl_idp.cer',
        'single_sign_on_service': 'https://mts.realme.govt.nz/logon-mts/mtsEntryPoint',
        'saml_sp_cer': 'mts_saml_sp.cer',
        'saml_sp_key': 'mts_saml_sp.key',
        'mutual_ssl_sp_cer': 'mts_mutual_ssl_sp.cer',
        'mutual_ssl_sp_key': 'mts_mutual_ssl_sp.key',
    },
    'ITE-uat': {
        'idp_entity_id': 'https://www.ite.logon.realme.govt.nz/saml2',
        'saml_idp_cer': 'ite.signing.logon.realme.govt.nz.cer',
        'mutual_ssl_idp_cer': 'ws.ite.realme.govt.nz.cer',
        'single_sign_on_service': 'https://www.ite.logon.realme.govt.nz/sso/logon/metaAlias/logon/logonidp',
        'site_url': 'https://uat.bundle.services.govt.nz',
        'saml_sp_cer': 'ite.sa.saml.sig.uat.bundle.services.govt.nz.crt',
        'saml_sp_key': 'ite.sa.saml.sig.uat.bundle.services.govt.nz.private.key',
        'mutual_ssl_sp_cer': 'ite.sa.mutual.sig.uat.bundle.services.govt.nz.crt',
        'mutual_ssl_sp_key': 'ite.sa.mutual.sig.uat.bundle.services.govt.nz.private.key',
    },
    'ITE-testing': {
        'idp_entity_id': 'https://www.ite.logon.realme.govt.nz/saml2',
        'saml_idp_cer': 'ite.signing.logon.realme.govt.nz.cer',
        'mutual_ssl_idp_cer': 'ws.ite.realme.govt.nz.cer',
        'single_sign_on_service': 'https://www.ite.logon.realme.govt.nz/sso/logon/metaAlias/logon/logonidp',
        'site_url': 'https://testing.bundle.services.govt.nz',
        'saml_sp_cer': 'ite.sa.saml.sig.testing.bundle.services.govt.nz.crt',
        'saml_sp_key': 'ite.sa.saml.sig.testing.bundle.services.govt.nz.private.key',
        'mutual_ssl_sp_cer': 'ite.sa.mutual.sig.testing.bundle.services.govt.nz.crt',
        'mutual_ssl_sp_key': 'ite.sa.mutual.sig.testing.bundle.services.govt.nz.private.key',
    },
    'PRD': {
        'idp_entity_id': 'https://www.logon.realme.govt.nz/saml2',
        'saml_idp_cer': 'signing.logon.realme.govt.nz.cer',
        'mutual_ssl_idp_cer': 'ws.realme.govt.nz.cer',
        'single_sign_on_service': 'https://www.logon.realme.govt.nz/sso/logon/metaAlias/logon/logonidp',
        'site_url': 'https://bundle.services.govt.nz',
        'saml_sp_cer': 'sa.saml.sig.bundle.services.govt.nz.crt',
        'saml_sp_key': 'sa.saml.sig.bundle.services.govt.nz.private.key',
        'mutual_ssl_sp_cer': 'sa.mutual.sig.bundle.services.govt.nz.crt',
        'mutual_ssl_sp_key': 'sa.mutual.sig.bundle.services.govt.nz.private.key',
    },
}


class AuthnContextClassRef(object):
    LowStrength = 'urn:nzl:govt:ict:stds:authn:deployment:GLS:SAML:2.0:ac:classes:LowStrength'
    ModStrength = 'urn:nzl:govt:ict:stds:authn:deployment:GLS:SAML:2.0:ac:classes:ModStrength'
    # SHOULD NOT be used by a integrating Client SP without first obtaining approval from the RealMe Logon Service.
    ModStrength__OTP_Token_SID = 'urn:nzl:govt:ict:stds:authn:deployment:GLS:SAML:2.0:ac:classes:ModStrength::OTP:Token:SID'
    ModStrength__OTP_Mobile_SMS = 'urn:nzl:govt:ict:stds:authn:deployment:GLS:SAML:2.0:ac:classes:ModStrength::OTP:Mobile:SMS'


class Bundle(object):

    def __init__(self, site_url=None, bundles_root=None, name=None):
        self.site_url = site_url or settings.SITE_URL
        self.bundles_root = path(bundles_root or settings.BUNDLES_ROOT)
        assert self.bundles_root.isdir(), self.bundles_root
        self.name = name or settings.BUNDLE_NAME
        self.config = BUNDLES[self.name]
        dir_name = self.name.split('-')[0]  # ITE-uat --> ITE
        self.path = self.bundles_root / dir_name
        assert self.path.isdir(), self.path

        fields = (
            'saml_idp_cer',
            'mutual_ssl_idp_cer',
            'saml_sp_cer',
            'saml_sp_key',
            'mutual_ssl_sp_cer',
            'mutual_ssl_sp_key',
        )

        for field in fields:
            assert self.file_path(field).isfile()

        for prefix in ('saml_sp', 'mutual_ssl_sp'):
            assert self.check_cer_and_key(prefix)

    def __str__(self):
        return self.name

    def check_cer_and_key(self, prefix):
        from subprocess import check_output
        cer_field = '{}_cer'.format(prefix)
        key_field = '{}_key'.format(prefix)
        cer_path = self.file_path(cer_field)
        key_path = self.file_path(key_field)
        cmd = 'openssl x509 -noout -modulus -in {}'.format(cer_path)
        s1 = check_output(cmd.split())
        cmd = 'openssl rsa -noout -modulus -in {}'.format(key_path)
        s2 = check_output(cmd.split())
        return s1 == s2

    def file_path(self, field):
        return self.path / self.config[field]

    def file_text(self, field):
        return self.file_path(field).text().strip()

    def file_body(self, field, begin='', end=''):
        return self.file_text(field).lstrip(begin).rstrip(end).strip()

    def cer_body(self, field):
        begin = '-----BEGIN CERTIFICATE-----'
        end = '-----END CERTIFICATE-----'
        return self.file_body(field, begin=begin, end=end)

    def key_body(self, field):
        begin = '-----BEGIN PRIVATE KEY-----'
        end = '-----END PRIVATE KEY-----'
        return self.file_body(field, begin=begin, end=end)

    @property
    def idp_cer_body(self):
        return self.cer_body('saml_idp_cer')

    @property
    def sp_cer_body(self):
        return self.cer_body('saml_sp_cer')

    @property
    def sp_key_body(self):
        return self.key_body('saml_sp_key')

    def full_url(self, url):
        return self.site_url.strip('/') + url

    @property
    def idp_entity_id(self):
        return self.config['idp_entity_id']

    @property
    def sp_entity_id(self):
        # Just use full login url as entity id.
        # realme does not allow entity id ends with slash
        return self.full_url(reverse('sp_login')).strip('/')

    @property
    def sp_acs_url(self):
        return self.full_url(reverse('sp_acs'))

    def render(self, template='sp/SP_PostBinding.xml'):
        return render_to_string(template, {'conf': self})

    def get_settings(self):
        return {
            "strict": True,
            "debug": settings.DEBUG,
            "security": {
                "nameIdEncrypted": False,
                "authnRequestsSigned": True,
                "requestedAuthnContext": [AuthnContextClassRef.LowStrength],
                "logoutRequestSigned": False,
                "logoutResponseSigned": False,
                "signMetadata": False,
                "wantMessagesSigned": False,
                "wantAssertionsSigned": True,
                "wantAttributeStatement": False,
                "wantNameId": True,
                "wantNameIdEncrypted": False,
                "wantAssertionsEncrypted": False,
                "signatureAlgorithm": constants.RSA_SHA1,
            },
            "sp": {
                "entityId": self.sp_entity_id,
                "assertionConsumerService": {
                    "url": self.sp_acs_url,
                    "binding": constants.BINDING_HTTP_POST,
                },
                # "singleLogoutService": {
                #     "url": "",
                #     "binding": constants.BINDING_HTTP_REDIRECT,
                # },
                "NameIDFormat": constants.NAMEID_UNSPECIFIED,
                "x509cert": self.sp_cer_body,
                "privateKey": self.sp_key_body,
            },
            "idp": {
                "entityId": self.idp_entity_id,
                "singleSignOnService": {
                    "url": self.config['single_sign_on_service'],
                    "binding": constants.BINDING_HTTP_REDIRECT,
                },
                # "singleLogoutService": {
                #     "url": "",
                #     "binding": constants.BINDING_HTTP_REDIRECT,
                # },
                "x509cert": self.idp_cer_body,
            }
        }

