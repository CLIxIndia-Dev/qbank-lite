import os

from dlkit_edx.configs import FILESYSTEM_ASSET_CONTENT_TYPE
from dlkit_edx.primordium import DataInputStream

from nose.tools import *

from testing_utilities import BaseTestCase, create_test_repository
from urllib import unquote, quote

PROJECT_PATH = os.path.dirname(os.path.abspath(__file__))
ABS_PATH = os.path.abspath(os.path.join(PROJECT_PATH, os.pardir))


class BaseRepositoryTestCase(BaseTestCase):
    def _create_asset(self):
        form = self._repo.get_asset_form_for_create([])
        form.display_name = 'Test asset'
        asset = self._repo.create_asset(form)

        content_form = self._repo.get_asset_content_form_for_create(asset.ident, [FILESYSTEM_ASSET_CONTENT_TYPE])
        content_form.display_name = 'test asset content'
        content_form.set_data(DataInputStream(self.test_file))
        self._repo.create_asset_content(content_form)

        return self._repo.get_asset(asset.ident)

    def setUp(self):
        super(BaseRepositoryTestCase, self).setUp()
        self.url = '/api/v1/repository'
        self._repo = create_test_repository()
        test_file = '{0}/tests/files/sample_movie.MOV'.format(ABS_PATH)

        self.test_file = open(test_file, 'r')

    def tearDown(self):
        super(BaseRepositoryTestCase, self).tearDown()
        self.test_file.close()


class AssetContentTests(BaseRepositoryTestCase):
    def setUp(self):
        super(AssetContentTests, self).setUp()
        self.asset = self._create_asset()
        asset_content = self.asset.get_asset_contents().next()
        self.url = '{0}/repositories/{1}/assets/{2}/contents/{3}'.format(self.url,
                                                                         unquote(str(self._repo.ident)),
                                                                         unquote(str(self.asset.ident)),
                                                                         unquote(str(asset_content.ident)))

    def tearDown(self):
        """
        Remove the test user from all groups in Membership
        Start from the smallest groupId because need to
        remove "parental" roles like for DepartmentAdmin / DepartmentOfficer
        """
        set_trace()
        super(AssetContentTests, self).tearDown()

    def test_can_get_asset_content_file(self):
        req = self.app.get(self.url)
        self.ok(req)
        self.test_file.seek(0)
        self.assertEqual(
            req.body,
            self.test_file.read()
        )
