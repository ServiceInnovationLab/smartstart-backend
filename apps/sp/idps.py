from onelogin.saml2.constants import OneLogin_Saml2_Constants as constants
from utils import full_reverse
from path import path
from django.conf import settings


class AuthnContextClassRef(object):
    LowStrength = 'urn:nzl:govt:ict:stds:authn:deployment:GLS:SAML:2.0:ac:classes:LowStrength'
    ModStrength = 'urn:nzl:govt:ict:stds:authn:deployment:GLS:SAML:2.0:ac:classes:ModStrength'
    # SHOULD NOT be used by a integrating Client SP without first obtaining approval from the RealMe Logon Service.
    ModStrength__OTP_Token_SID = 'urn:nzl:govt:ict:stds:authn:deployment:GLS:SAML:2.0:ac:classes:ModStrength::OTP:Token:SID'
    ModStrength__OTP_Mobile_SMS = 'urn:nzl:govt:ict:stds:authn:deployment:GLS:SAML:2.0:ac:classes:ModStrength::OTP:Mobile:SMS'


class IDP(object):
    # default to True, only PRD needs to be False
    debug = True

    # Override in subclasses, does not need to be a real url
    # example: https://mts.dev.boac.lef/sp/login
    sp_entity_id = ''

    def __init__(self, *args, **kwargs):
        """
        Bundle path for each idp.

        e.g.: result for MTS would be /path/to/bundles/root/MTS
        """
        self.bundle_path = path(settings.BUNDLES_ROOT) / self.__class__.__name__

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
        return self.bundle_file(filename).text()

    def get_settings(self):
        assert self.sp_entity_id, 'must specify sp entityId'
        return {
            "strict": True,
            "debug": self.debug,
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
                    "url": full_reverse('sp_acs'),
                    "binding": constants.BINDING_HTTP_POST,
                },
                # "singleLogoutService": {
                #     "url": full_reverse('sp_ls'),
                #     "binding": constants.BINDING_HTTP_REDIRECT,
                # },
                "NameIDFormat": constants.NAMEID_UNSPECIFIED,
                "x509cert": self.bundle_text(self.sp_cer_filename),
                "privateKey": self.bundle_text(self.sp_key_filename),
            },
            "idp": {
                "entityId": "https://mts.realme.govt.nz/saml2",
                "singleSignOnService": {
                    "url": "https://mts.realme.govt.nz/logon-mts/mtsEntryPoint",
                    "binding": constants.BINDING_HTTP_REDIRECT,
                },
                # "singleLogoutService": {
                #     "url": "",
                #     "binding": constants.BINDING_HTTP_REDIRECT,
                # },
                "x509cert": self.bundle_text(self.idp_cer_filename),
            }
        }


class MTS(IDP):
    sp_entity_id = 'https://mts.dev.boac.lef/sp/login'
    sp_cer_filename = 'mts_saml_sp.cer'
    sp_key_filename = 'mts_saml_sp.key'
    idp_cer_filename = 'mts_login_saml_idp.cer'


class ITS(IDP):
    # TODO
    sp_entity_id = 'https://its.dev.boac.lef/sp/login'
    sp_cer_filename = 'its_saml_sp.cer'
    sp_key_filename = 'its_saml_sp.key'
    idp_cer_filename = 'its_login_saml_idp.cer'


class PRD(IDP):
    # TODO
    debug = False
    sp_entity_id = 'https://boac.lef/sp/login'
    sp_cer_filename = 'prd_saml_sp.cer'
    sp_key_filename = 'prd_saml_sp.key'
    idp_cer_filename = 'prd_login_saml_idp.cer'


def get_idp(name):
    name = name.upper()
    if name == 'PRD':
        return PRD()
    elif name == 'ITS':
        return ITS()
    elif name == 'MTS':
        return MTS()
    else:
        return None
