from django.conf import settings
from django.core.urlresolvers import reverse
from django.template.loader import render_to_string

import uuid
import xmlsec
import requests
from lxml import etree
from path import path
from datetime import datetime, timedelta
from onelogin.saml2.constants import OneLogin_Saml2_Constants as constants
from onelogin.saml2.utils import OneLogin_Saml2_Utils

from utils import log_me
import logging
log = logging.getLogger(__name__)

URL_TOKEN_ISSUE = 'https://ws.ite.realme.govt.nz/iCMS/Issue_v1_1'

NAMESPACES = {
    'ds': 'http://www.w3.org/2000/09/xmldsig#',
    'ec': "http://www.w3.org/2001/10/xml-exc-c14n#",
    'env': 'http://www.w3.org/2003/05/soap-envelope',
    'soap': 'http://www.w3.org/2003/05/soap-envelope',
    'wsa': "http://www.w3.org/2005/08/addressing",
    'wsp': 'http://schemas.xmlsoap.org/ws/2004/09/policy',
    'wsse': 'http://docs.oasis-open.org/wss/2004/01/oasis-200401-wss-wssecurity-secext-1.0.xsd',
    'wsse11': 'http://docs.oasis-open.org/wss/oasis-wss-saml-token-profile-1.1#SAMLV2.0',
    'wst': "http://docs.oasis-open.org/ws-sx/ws-trust/200512",
    'wst14': "http://docs.oasis-open.org/ws-sx/ws-trust/200802",
    'wsu': 'http://docs.oasis-open.org/wss/2004/01/oasis-200401-wss-wssecurity-utility-1.0.xsd',
    'saml2': 'urn:oasis:names:tc:SAML:2.0:assertion',
    'iCMS': "urn:nzl:govt:ict:stds:authn:deployment:igovt:gls:iCMS:1_0",
}

def dt_fmt(dt):
    return dt.strftime('%Y-%m-%dT%H:%M:%S.%f')[:-3] + 'Z'


def pretty_xml(xml):
    element = etree.fromstring(xml)
    return etree.tostring(element, pretty_print=True).decode('utf-8')


class AuthnContextClassRef(object):
    LowStrength = 'urn:nzl:govt:ict:stds:authn:deployment:GLS:SAML:2.0:ac:classes:LowStrength'
    ModStrength = 'urn:nzl:govt:ict:stds:authn:deployment:GLS:SAML:2.0:ac:classes:ModStrength'
    # SHOULD NOT be used by a integrating Client SP without first obtaining approval from the RealMe Logon Service.
    ModStrength__OTP_Token_SID = 'urn:nzl:govt:ict:stds:authn:deployment:GLS:SAML:2.0:ac:classes:ModStrength::OTP:Token:SID'
    ModStrength__OTP_Mobile_SMS = 'urn:nzl:govt:ict:stds:authn:deployment:GLS:SAML:2.0:ac:classes:ModStrength::OTP:Mobile:SMS'


class Bundle(object):

    def __init__(self, site_url=None, bundles_root=None, name=None):
        self.name = name or settings.BUNDLE_NAME
        assert self.name in settings.BUNDLES, 'invalid bundle name: {}'.format(self.name)
        self.config = settings.BUNDLES[self.name]

        self.bundles_root = path(bundles_root or settings.BUNDLES_ROOT)
        assert self.bundles_root.isdir(), self.bundles_root
        self.path = self.bundles_root / self.name
        assert self.path.isdir(), self.path

        self.site_url = site_url or settings.SITE_URL

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

    @property
    def idp_cer_body(self):
        return self.file_text('saml_idp_cer')

    @property
    def sp_cer_body(self):
        return self.file_text('saml_sp_cer')

    @property
    def sp_key_body(self):
        return self.file_text('saml_sp_key')

    def full_url(self, url):
        return self.site_url.strip('/') + url

    @property
    def idp_entity_id(self):
        return self.config['idp_entity_id']

    @property
    def sp_entity_id(self):
        return self.config['sp_entity_id'].strip()

    @property
    def sp_acs_url(self):
        return self.full_url(reverse('sp_acs'))

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

    def render(self, template='sp/SP_PostBinding.xml'):
        return render_to_string(template, {'conf': self})

    @property
    def key_identifier(self):
        fp_ascii = OneLogin_Saml2_Utils.calculate_x509_fingerprint(self.sp_cer_body)
        # --> unicode str in ascii: 'b5a10daa4250aea3b036b4a2a6e66829f852363f'
        from binascii import a2b_hex, b2a_base64
        fp_hex = a2b_hex(fp_ascii)
        # --> unicode str in hex: '\xb5\xa1\r\xaaBP\xae\xa3\xb06\xb4\xa2\xa6\xe6h)\xf8R6?'
        # TODO: why \n at end?
        return b2a_base64(fp_hex).strip()  # 'taENqkJQrqOwNrSipuZoKfhSNj8=\n'

    def render_token_issue_request(self, logon_attributes_token=''):
        REF_IDS = ("Id-Action", "Id-MessageID", "Id-To", "Id-ReplyTo", "Id-Body", "Id-Timestamp")
        created = datetime.utcnow()  # must use utc time
        expires = created + timedelta(minutes=5)
        context = {
            'conf': self,
            'created': dt_fmt(created),
            'expires': dt_fmt(expires),
            'message_id': str(uuid.uuid4()),
            'to': URL_TOKEN_ISSUE,
            'REF_IDS': REF_IDS,
            'NAMESPACES': NAMESPACES,
            'key_identifier': self.key_identifier,
            'logon_attributes_token': logon_attributes_token,
        }
        return render_to_string('sp/token_issue_tmpl.xml', context)

    def sign_token_issue_request(self, rendered_xml):
        # etree.parse will return ElementTree, then you need to call getroot on it
        # fromstring will return the root directly.
        root_element = etree.fromstring(rendered_xml.encode('utf-8'))
        xmlsec.tree.add_ids(root_element, ["Id"])  # important!
        header_element = root_element.find('soap:Header', namespaces=NAMESPACES)
        security_element = header_element.find('wsse:Security', namespaces=NAMESPACES)
        signature_node = security_element.find('ds:Signature', namespaces=NAMESPACES)

        key_path = self.file_path('saml_sp_key')
        assert key_path.isfile
        cer_path = self.file_path('saml_sp_cer')
        assert cer_path.isfile

        # Load private key (assuming that there is no password).
        key = xmlsec.Key.from_file(key_path, xmlsec.KeyFormat.PEM)
        assert key is not None

        # Load the certificate and add it to the key.
        key.load_cert_from_file(cer_path, xmlsec.KeyFormat.PEM)

        # Create a digital signature context (no key manager is needed).
        ctx = xmlsec.SignatureContext()
        ctx.key = key
        # Sign the template.
        ctx.sign(signature_node)
        # return a utf-8 encoded byte str
        return etree.tostring(root_element, pretty_print=True).decode('utf-8')

    def send_token_issue_request(self, user):
        logon_attributes_token = user.profile.logon_attributes_token
        rendered_xml = self.render_token_issue_request(logon_attributes_token=logon_attributes_token)
        log_me(rendered_xml, name='token_issue_request_rendered.xml', print_me=False)
        signed_xml = self.sign_token_issue_request(rendered_xml)
        log_me(signed_xml, name='token_issue_request_signed.xml', print_me=False)

        headers = {'content-type': 'text/xml'}
        cert = (
            self.file_path('mutual_ssl_sp_cer'),
            self.file_path('mutual_ssl_sp_key'),
        )
        r = requests.post(URL_TOKEN_ISSUE, data=signed_xml, headers=headers, cert=cert)
        response_xml = pretty_xml(r.content.decode('utf-8'))
        log_me(response_xml, name='token_issue_response.xml')
        return r

