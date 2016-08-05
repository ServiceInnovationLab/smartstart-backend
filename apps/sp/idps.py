from onelogin.saml2.constants import OneLogin_Saml2_Constants as constants
from utils import full_reverse, get_cer_body, get_private_key_body
from path import path
from django.conf import settings
from django.template.loader import render_to_string

IDPS = {
    'MTS': {
        'saml_idp_cer': 'mts_login_saml_idp.cer',
        'mutual_ssl_idp_cer': 'mts_mutual_ssl_idp.cer',
        'single_sign_on_service': 'https://mts.realme.govt.nz/logon-mts/mtsEntryPoint',
        'sp': {
            'saml_sp_cer': 'mts_saml_sp.cer',
            'saml_sp_key': 'mts_saml_sp.key',
            'mutual_ssl_sp_cer': 'mts_mutual_ssl_sp.cer',
            'mutual_ssl_sp_key': 'mts_mutual_ssl_sp.key',
        }
    },
    'ITE': {
        'saml_idp_cer': 'ite.signing.logon.realme.govt.nz.cer',
        'mutual_ssl_idp_cer': 'ws.ite.realme.govt.nz.cer',
        'single_sign_on_service': 'https://www.ite.logon.realme.govt.nz/sso/logon/metaAlias/logon/logonidp',
        'uat': {
            'site_url': 'https://uat.bundle.services.govt.nz',
            'saml_sp_cer': 'ite.sa.saml.sig.uat.bundle.services.govt.nz.crt',
            'saml_sp_key': 'ite.sa.saml.sig.uat.bundle.services.govt.nz.private.key',
            'mutual_ssl_sp_cer': 'ite.sa.mutual.sig.uat.bundle.services.govt.nz.crt',
            'mutual_ssl_sp_key': 'ite.sa.mutual.sig.uat.bundle.services.govt.nz.private.key',
        },
        'testing': {
            'site_url': 'https://testing.bundle.services.govt.nz',
            'saml_sp_cer': 'ite.sa.saml.sig.testing.bundle.services.govt.nz.crt',
            'saml_sp_key': 'ite.sa.saml.sig.testing.bundle.services.govt.nz.private.key',
            'mutual_ssl_sp_cer': 'ite.sa.mutual.sig.testing.bundle.services.govt.nz.crt',
            'mutual_ssl_sp_key': 'ite.sa.mutual.sig.testing.bundle.services.govt.nz.private.key',
        },
    },
    'PRD': {
        'saml_idp_cer': 'signing.logon.realme.govt.nz.cer',
        'mutual_ssl_idp_cer': 'ws.realme.govt.nz.cer',
        'single_sign_on_service': 'https://www.logon.realme.govt.nz/sso/logon/metaAlias/logon/logonidp',
        'sp': {
            'site_url': 'https://bundle.services.govt.nz',
            'saml_sp_cer': 'ite.sa.saml.sig.bundle.services.govt.nz.crt',
            'saml_sp_key': 'ite.sa.saml.sig.bundle.services.govt.nz.private.key',
            'mutual_ssl_sp_cer': 'ite.sa.mutual.sig.bundle.services.govt.nz.crt',
            'mutual_ssl_sp_key': 'ite.sa.mutual.sig.bundle.services.govt.nz.private.key',
        },
    },
}


class AuthnContextClassRef(object):
    LowStrength = 'urn:nzl:govt:ict:stds:authn:deployment:GLS:SAML:2.0:ac:classes:LowStrength'
    ModStrength = 'urn:nzl:govt:ict:stds:authn:deployment:GLS:SAML:2.0:ac:classes:ModStrength'
    # SHOULD NOT be used by a integrating Client SP without first obtaining approval from the RealMe Logon Service.
    ModStrength__OTP_Token_SID = 'urn:nzl:govt:ict:stds:authn:deployment:GLS:SAML:2.0:ac:classes:ModStrength::OTP:Token:SID'
    ModStrength__OTP_Mobile_SMS = 'urn:nzl:govt:ict:stds:authn:deployment:GLS:SAML:2.0:ac:classes:ModStrength::OTP:Mobile:SMS'


class IDP(object):

    def __init__(self, site_url=None, bundles_root=None, idp=None, sp=None):
        if site_url:
            self.site_url = site_url
        else:
            self.site_url = settings.SITE_URL

        if bundles_root:
            self.bundles_root = path(bundles_root)
        else:
            self.bundles_root = path(settings.BUNDLES_ROOT)
        assert self.bundles_root.isdir()

        if idp:
            self.idp = idp
        else:
            self.idp = settings.IDP

        if sp:
            self.sp = sp
        else:
            self.sp = getattr(settings, 'SP', 'sp')

        self.idp_conf = IDPS[self.idp]
        assert self.sp in self.idp_conf
        self.sp_conf = self.idp_conf[self.sp]

        self.bundle_path = self.bundles_root / self.idp
        assert self.bundle_path.isdir()

        # sp_site_url = self.sp_conf.get('site_url')
        # if sp_site_url:
        #     assert self.site_url == sp_site_url
        filenames = (
            self.idp_conf['saml_idp_cer'],
            self.idp_conf['mutual_ssl_idp_cer'],
            self.sp_conf['saml_sp_cer'],
            self.sp_conf['saml_sp_key'],
            self.sp_conf['mutual_ssl_sp_cer'],
            self.sp_conf['mutual_ssl_sp_key'],
        )
        for filename in filenames:
            assert self.bundle_file(filename).isfile(), filename

    def bundle_file(self, filename):
        """
        Get full path from base filename.

        e.g.: mts_saml_sp.cer --> /path/bundles/root/MTS/mts_saml_sp.cer
        """
        return self.bundle_path / filename

    def bundle_text(self, filename):
        """
        Get text content from filename

        e.g.: bundle('mts_saml_sp.cer') --> cert content as text
        """
        return self.bundle_file(filename).text().strip()

    @property
    def sp_entity_id(self):
        # Just use full login url as entity id.
        # realme does not allow entity id ends with slash
        return full_reverse('sp_login', site_url=self.site_url).strip('/')

    @property
    def sp_acs_url(self):
        return full_reverse('sp_acs', site_url=self.site_url)

    @property
    def idp_cer_body(self):
        return get_cer_body(self.bundle_text(self.idp_conf['saml_idp_cer']))

    @property
    def sp_cer_body(self):
        return get_cer_body(self.bundle_text(self.sp_conf['saml_sp_cer']))

    @property
    def sp_key_body(self):
        return get_private_key_body(self.bundle_text(self.sp_conf['saml_sp_key']))

    def render_xml(self, template='sp/SP_PostBinding.xml'):
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
                #     "url": full_reverse('sp_ls'),
                #     "binding": constants.BINDING_HTTP_REDIRECT,
                # },
                "NameIDFormat": constants.NAMEID_UNSPECIFIED,
                "x509cert": self.sp_cer_body,
                "privateKey": self.sp_key_body,
            },
            "idp": {
                "entityId": self.idp_conf['entity_id'],
                "singleSignOnService": {
                    "url": self.idp_conf['single_singn_on_service'],
                    "binding": constants.BINDING_HTTP_REDIRECT,
                },
                # "singleLogoutService": {
                #     "url": "",
                #     "binding": constants.BINDING_HTTP_REDIRECT,
                # },
                "x509cert": self.idp_cer_body,
            }
        }
