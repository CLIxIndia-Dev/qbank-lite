import os

from dlkit_edx.configs import FILESYSTEM_ASSET_CONTENT_TYPE
from dlkit_edx.primordium import DataInputStream, Type, Id

from nose.tools import *

from testing_utilities import BaseTestCase, create_test_repository, get_managers
from urllib import unquote, quote

from records.registry import ASSESSMENT_RECORD_TYPES

import utilities

PROJECT_PATH = os.path.dirname(os.path.abspath(__file__))
ABS_PATH = os.path.abspath(os.path.join(PROJECT_PATH, os.pardir))

SIMPLE_SEQUENCE_RECORD = Type(**ASSESSMENT_RECORD_TYPES['simple-child-sequencing'])


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

    def num_assets(self, val):
        self.assertEqual(
            self._repo.get_assets().available(),
            int(val)
        )

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
    def create_assessment_offered_for_item(self, bank_id, item_id):
        if isinstance(bank_id, basestring):
            bank_id = utilities.clean_id(bank_id)
        if isinstance(item_id, basestring):
            item_id = utilities.clean_id(item_id)

        bank = get_managers()['am'].get_bank(bank_id)
        form = bank.get_assessment_form_for_create([SIMPLE_SEQUENCE_RECORD])
        form.display_name = 'a test assessment'
        form.description = 'for testing with'
        new_assessment = bank.create_assessment(form)

        bank.add_item(new_assessment.ident, item_id)

        form = bank.get_assessment_offered_form_for_create(new_assessment.ident, [])
        new_offered = bank.create_assessment_offered(form)

        return new_offered

    def create_upload_item(self):
        url = '{0}/items'.format(self.assessment_url)
        self._generic_upload_test_file.seek(0)
        req = self.app.post(url,
                            upload_files=[('qtiFile', 'testFile', self._generic_upload_test_file.read())])
        self.ok(req)
        return self.json(req)

    def create_taken_for_item(self, bank_id, item_id):
        if isinstance(bank_id, basestring):
            bank_id = utilities.clean_id(bank_id)
        if isinstance(item_id, basestring):
            item_id = utilities.clean_id(item_id)

        bank = get_managers()['am'].get_bank(bank_id)

        new_offered = self.create_assessment_offered_for_item(bank_id, item_id)

        form = bank.get_assessment_taken_form_for_create(new_offered.ident, [])
        taken = bank.create_assessment_taken(form)
        return taken, new_offered

    def setUp(self):
        super(AssetContentTests, self).setUp()
        self.asset = self._create_asset()
        asset_content = self.asset.get_asset_contents().next()
        self.assessment_url = '/api/v1/assessment/banks/{0}'.format(unquote(str(self._repo.ident)))
        self.url = '{0}/repositories/{1}/assets/{2}/contents/{3}'.format(self.url,
                                                                         unquote(str(self._repo.ident)),
                                                                         unquote(str(self.asset.ident)),
                                                                         unquote(str(asset_content.ident)))

        self._generic_upload_test_file = open('{0}/tests/files/generic_upload_test_file.zip'.format(ABS_PATH), 'r')
        self._logo_upload_test_file = open('{0}/tests/files/Epidemic2.sltng'.format(ABS_PATH), 'r')

    def tearDown(self):
        """
        Remove the test user from all groups in Membership
        Start from the smallest groupId because need to
        remove "parental" roles like for DepartmentAdmin / DepartmentOfficer
        """
        super(AssetContentTests, self).tearDown()

        self._generic_upload_test_file.close()
        self._logo_upload_test_file.close()

    def test_can_get_asset_content_file(self):
        req = self.app.get(self.url)
        self.ok(req)
        self.test_file.seek(0)
        self.assertEqual(
            req.body,
            self.test_file.read()
        )

    def test_unknown_asset_content_extensions_preserved(self):
        upload_item = self.create_upload_item()
        taken, offered = self.create_taken_for_item(self._repo.ident, Id(upload_item['id']))
        url = '{0}/assessmentstaken/{1}/questions/{2}/submit'.format(self.assessment_url,
                                                                     unquote(str(taken.ident)),
                                                                     unquote(upload_item['id']))

        self._logo_upload_test_file.seek(0)
        req = self.app.post(url,
                            upload_files=[('submission', 'Epidemic2.sltng', self._logo_upload_test_file.read())])
        self.ok(req)

        url = '/api/v1/repository/repositories/{0}/assets'.format(unquote(str(self._repo.ident)))
        req = self.app.get(url)
        self.ok(req)
        data = self.json(req)
        self.assertEqual(len(data), 2)
        for asset in data:
            if asset['id'] != str(self.asset.ident):
                self.assertTrue('.sltng' in asset['assetContents'][0]['url'])
                self.assertEqual('asset-content-genus-type%3Asltng%40ODL.MIT.EDU',
                                 asset['assetContents'][0]['genusTypeId'])


class AssetUploadTests(BaseRepositoryTestCase):
    def setUp(self):
        super(AssetUploadTests, self).setUp()
        self.url = '{0}/repositories/{1}/assets'.format(self.url,
                                                        unquote(str(self._repo.ident)))

        self._video_upload_test_file = open('{0}/tests/files/video-js-test.mp4'.format(ABS_PATH), 'r')
        self._caption_upload_test_file = open('{0}/tests/files/video-js-test-en.vtt'.format(ABS_PATH), 'r')

    def tearDown(self):
        """
        Remove the test user from all groups in Membership
        Start from the smallest groupId because need to
        remove "parental" roles like for DepartmentAdmin / DepartmentOfficer
        """
        super(AssetUploadTests, self).tearDown()

        self._video_upload_test_file.close()
        self._caption_upload_test_file.close()

    def test_can_upload_video_files_to_repository(self):
        self._video_upload_test_file.seek(0)
        req = self.app.post(self.url,
                            upload_files=[('inputFile', 'video-js-test.mp4', self._video_upload_test_file.read())])
        self.ok(req)
        data = self.json(req)
        self.assertEqual(
            len(data['assetContents']),
            1
        )
        self.assertEqual(
            data['assetContents'][0]['genusTypeId'],
            'asset-content-genus-type%3Amp4%40ODL.MIT.EDU'
        )
        self.assertIn(
            'CLIX/datastore/repository/AssetContents/',
            data['assetContents'][0]['url']
        )

    def test_can_upload_caption_vtt_files_to_repository(self):
        self.fail('finish writing the test')

    def test_caption_and_video_files_uploaded_as_asset_contents_on_same_asset(self):
        self.fail('finish writing the test')