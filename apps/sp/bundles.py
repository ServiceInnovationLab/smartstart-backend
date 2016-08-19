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


def dt_fmt(dt):
    return dt.strftime('%Y-%m-%dT%H:%M:%SZ')


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
        dir_name = self.name.split('-')[0]  # ITE-uat --> ITE

        self.bundles_root = path(bundles_root or settings.BUNDLES_ROOT)
        assert self.bundles_root.isdir(), self.bundles_root
        self.path = self.bundles_root / dir_name
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

    def send_token_issue_request(self):
        url = 'https://ws.ite.realme.govt.nz/iCMS/Issue_v1_1'
        headers = {'content-type': 'text/xml'}
        cert = (
            self.file_path('mutual_ssl_sp_cer'),
            self.file_path('mutual_ssl_sp_key'),
        )
        soap_xml = self.render_token_issue_request()
        return requests.post(url, data=soap_xml, headers=headers, cert=cert)

    def render_token_issue_request(self):
        NAMESPACES = {
            'soap': 'http://www.w3.org/2003/05/soap-envelope',
            'wsse': 'http://docs.oasis-open.org/wss/2004/01/oasis-200401-wss-wssecurity-secext-1.0.xsd',
            'wsu': 'http://docs.oasis-open.org/wss/2004/01/oasis-200401-wss-wssecurity-utility-1.0.xsd',
        }
        created = datetime.utcnow()  # must use utc time
        expires = created + timedelta(minutes=5)
        context = {
            'conf': self,
            'Created': dt_fmt(created),
            'Expires': dt_fmt(expires),
            'MessageID': str(uuid.uuid4()),
        }
        xml = render_to_string('sp/token_issue_tmpl.xml', context)
        # etree.parse will return ElementTree, then you need to call getroot on it
        # fromstring will return the root directly.
        root_element = etree.fromstring(xml.encode('utf-8'))
        header_element = root_element.find('soap:Header', namespaces=NAMESPACES)
        security_element = header_element.find('wsse:Security', namespaces=NAMESPACES)
        # Create a signature template for RSA-SHA1 enveloped signature.
        signature_node = xmlsec.template.create(
            security_element,  # Element
            xmlsec.Transform.EXCL_C14N,  # c14n_method
            xmlsec.Transform.RSA_SHA1,   # sign_method
            ns='ds'
        )

        # Add the <ds:Signature/> node to the document.
        security_element.append(signature_node)

        ref_ids = ("Id-Action", "Id-MessageID", "Id-To", "Id-ReplyTo", "Id-Body")

        for elem_id in ref_ids:
            # Add the <ds:Reference/> node to the signature template.
            ref = xmlsec.template.add_reference(signature_node, xmlsec.Transform.SHA256, uri='#' + elem_id)
            # Add the excl_c14n transform descriptor.
            xmlsec.template.add_transform(ref, xmlsec.Transform.EXCL_C14N)

        # Add the <ds:KeyInfo/> and <ds:KeyName/> nodes.
        key_info = xmlsec.template.ensure_key_info(signature_node)
        xmlsec.template.add_x509_data(key_info)

        # Load private key (assuming that there is no password).
        file_path = self.file_path('mutual_ssl_sp_key')
        assert file_path.isfile
        key = xmlsec.Key.from_file(file_path, xmlsec.KeyFormat.PEM)
        assert key is not None

        # Load the certificate and add it to the key.
        file_path = self.file_path('mutual_ssl_sp_cer')
        assert file_path.isfile
        key.load_cert_from_file(file_path, xmlsec.KeyFormat.PEM)
        key.name = file_path.basename().encode('utf-8')

        # Create a digital signature context (no key manager is needed).
        ctx = xmlsec.SignatureContext()
        ctx.key = key

        # Sign the template.
        # ctx.sign(signature_node)

        import ipdb
        ipdb.set_trace()

        text = etree.tostring(root_element, pretty_print=True)
        return text.decode('utf-8')

