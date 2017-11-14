from pathlib import Path
from apps.base.tests import BaseTestCase

SAMPLES = Path(__file__).parent / 'samples'


class RealMeTestCase(BaseTestCase):

    def setUp(self):
        BaseTestCase.setUp(self)

    def test_html_escape(self):
        """
        Compare html escape between Python and Java.
        """
        opaque_token_raw = (SAMPLES / 'opaque_token_raw.xml').read_text()
        from .views import escape_opaque_token
        opaque_token_escaped_python = escape_opaque_token(opaque_token_raw)
        opaque_token_escaped_java = (SAMPLES / 'opaque_token_escaped_java.xml').read_text()
        self.assertEqual(opaque_token_escaped_python, opaque_token_escaped_java)
