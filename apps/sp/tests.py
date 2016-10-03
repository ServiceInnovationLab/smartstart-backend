from os.path import abspath, dirname
from path import Path
from apps.base.tests import BaseTestCase

HERE = Path(dirname(abspath(__file__)))
SAMPLES = HERE/'samples'

class RealMeTestCase(BaseTestCase):

    def setUp(self):
        BaseTestCase.setUp(self)

    def test_html_escape(self):
        """
        Compare html escape between Python and Java.
        """
        opaque_token_raw = (SAMPLES/'opaque_token_raw.xml').text()
        from .views import escape_opaque_token
        opaque_token_escaped_python = escape_opaque_token(opaque_token_raw)
        opaque_token_escaped_java = (SAMPLES/'opaque_token_escaped_java.xml').text()
        self.assertEqual(opaque_token_escaped_python, opaque_token_escaped_java)

