from apps.base.tests import BaseTestCase

class PhaseMetadataTestCase(BaseTestCase):

    def setUp(self):
        BaseTestCase.setUp(self)

    def test_permission(self):
        # this api should be public, but readonly to all users
        data = {'weeks_start': 42, 'weeks_finish': 45}

        # test annoymous user
        self.get_json(self.api_phasemetadata, expected=200)
        self.post_json(self.api_phasemetadata, data=data, expected=403)

        # test normal user
        self.login('test')
        self.get_json(self.api_phasemetadata, expected=200)
        self.post_json(self.api_phasemetadata, data=data, expected=403)

        # test admin user
        self.login('admin')
        self.get_json(self.api_phasemetadata, expected=200)
        self.post_json(self.api_phasemetadata, data=data, expected=403)
