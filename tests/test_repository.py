# -*- coding: utf-8 -*-
import json
import os

from bs4 import BeautifulSoup

from dlkit.runtime.errors import NotFound
from dlkit.runtime.primordium import DataInputStream, Type, Id, DisplayText
from dlkit.records.registry import ASSESSMENT_RECORD_TYPES,\
    ASSET_CONTENT_RECORD_TYPES, ASSET_CONTENT_GENUS_TYPES

from paste.fixture import AppError

from testing_utilities import BaseTestCase, get_fixture_repository,\
    get_managers
from urllib import unquote, quote

import utilities

PROJECT_PATH = os.path.dirname(os.path.abspath(__file__))
ABS_PATH = os.path.abspath(os.path.join(PROJECT_PATH, os.pardir))

SIMPLE_SEQUENCE_RECORD = Type(**ASSESSMENT_RECORD_TYPES['simple-child-sequencing'])
MULTI_LANGUAGE_ASSET_CONTENTS = Type(**ASSET_CONTENT_RECORD_TYPES['multi-language'])
ALT_TEXT_ASSET_CONTENT_GENUS_TYPE = Type(**ASSET_CONTENT_GENUS_TYPES['alt-text'])
MEDIA_DESCRIPTION_ASSET_CONTENT_GENUS_TYPE = Type(**ASSET_CONTENT_GENUS_TYPES['media-description'])


class BaseRepositoryTestCase(BaseTestCase):
    def _create_asset(self):
        form = self._repo.get_asset_form_for_create([])
        form.display_name = 'Test asset'
        asset = self._repo.create_asset(form)

        asset_records = [MULTI_LANGUAGE_ASSET_CONTENTS]
        try:
            config = asset._runtime.get_configuration()
            parameter_id = utilities.clean_id('parameter:assetContentRecordTypeForFiles@mongo')
            asset_records.append(config.get_value_by_parameter(parameter_id).get_type_value())
        except (AttributeError, KeyError, NotFound):
            pass

        content_form = self._repo.get_asset_content_form_for_create(asset.ident, asset_records)
        content_form.add_display_name(DisplayText(text='test asset content',
                                                  language_type='639-2%3AENG%40ISO',
                                                  format_type='TextFormats%3APLAIN%40okapia.net',
                                                  script_type='15924%3ALATN%40ISO'))
        content_form.add_description(DisplayText(text='foo',
                                                 language_type='639-2%3AENG%40ISO',
                                                 format_type='TextFormats%3APLAIN%40okapia.net',
                                                 script_type='15924%3ALATN%40ISO'))
        content_form.set_data(DataInputStream(self.test_file))
        ac = self._repo.create_asset_content(content_form)

        # need to get the IDs to match, so update it like in the system
        self.test_file.seek(0)
        form = self._repo.get_asset_content_form_for_update(ac.ident)
        form.set_data(DataInputStream(self.test_file))
        self._repo.update_asset_content(form)

        return self._repo.get_asset(asset.ident)

    def num_assets(self, val):
        self.assertEqual(
            self._repo.get_assets().available(),
            int(val)
        )

    def setUp(self):
        super(BaseRepositoryTestCase, self).setUp()
        self.url = '/api/v1/repository'
        self._repo = get_fixture_repository()
        test_file = '{0}/tests/files/sample_movie.MOV'.format(ABS_PATH)

        self.test_file = open(test_file, 'r')

    def tearDown(self):
        super(BaseRepositoryTestCase, self).tearDown()
        self.test_file.close()


class RepositoryTests(BaseRepositoryTestCase):
    def setUp(self):
        super(RepositoryTests, self).setUp()
        self.url += '/repositories'

    def tearDown(self):
        """
        Remove the test user from all groups in Membership
        Start from the smallest groupId because need to
        remove "parental" roles like for DepartmentAdmin / DepartmentOfficer
        """
        super(RepositoryTests, self).tearDown()

    def test_can_set_repository_alias_on_create(self):
        payload = {
            "name": "New repository",
            "aliasId": "repository.Repository%3Apublished-012345678910111213141516%40ODL.MIT.EDU"
        }
        req = self.app.post(self.url,
                            params=json.dumps(payload),
                            headers={'content-type': 'application/json'})
        self.ok(req)
        new_repository = self.json(req)

        url = '{0}/{1}'.format(self.url,
                               payload['aliasId'])
        req = self.app.get(url)
        self.ok(req)
        fetched_repository = self.json(req)
        self.assertEqual(new_repository['id'], fetched_repository['id'])
        self.assertEqual(new_repository['displayName']['text'], payload['name'])

    def test_can_query_on_repository_genus_type(self):
        genus_type = "repository-type%3Aedit%40ODL.MIT.EDU"
        payload = {
            "name": "New repository",
            "genusTypeId": genus_type
        }
        req = self.app.post(self.url,
                            params=json.dumps(payload),
                            headers={'content-type': 'application/json'})
        self.ok(req)
        new_repository = self.json(req)

        url = '{0}?genusTypeId={1}'.format(self.url,
                                           genus_type)
        req = self.app.get(url)
        self.ok(req)
        data = self.json(req)
        self.assertEqual(len(data), 1)
        self.assertEqual(new_repository['id'], data[0]['id'])
        self.assertEqual(data[0]['genusTypeId'], genus_type)

        unescaped_genus_type = unquote(genus_type)
        url = '{0}?genusTypeId={1}'.format(self.url,
                                           unescaped_genus_type)
        req = self.app.get(url)
        self.ok(req)
        data = self.json(req)
        self.assertEqual(len(data), 1)
        self.assertEqual(new_repository['id'], data[0]['id'])
        self.assertEqual(data[0]['genusTypeId'], genus_type)

        url = '{0}?genusTypeId=foo'.format(self.url)
        req = self.app.get(url)
        self.ok(req)
        data = self.json(req)
        self.assertEqual(len(data), 0)

    def test_can_query_on_repository_display_name(self):
        display_name = "New repository%3A bar %40"
        payload = {
            "name": display_name
        }
        req = self.app.post(self.url,
                            params=json.dumps(payload),
                            headers={'content-type': 'application/json'})
        self.ok(req)
        new_repository = self.json(req)

        url = '{0}?displayName={1}'.format(self.url,
                                           quote(display_name))
        req = self.app.get(url)
        self.ok(req)
        data = self.json(req)
        self.assertEqual(len(data), 1)
        self.assertEqual(new_repository['id'], data[0]['id'])
        self.assertEqual(data[0]['displayName']['text'], display_name)

        unescaped_display_name = unquote(display_name)
        url = '{0}?displayName={1}'.format(self.url,
                                           unescaped_display_name)
        req = self.app.get(url)
        self.ok(req)
        data = self.json(req)
        self.assertEqual(len(data), 1)
        self.assertEqual(new_repository['id'], data[0]['id'])
        self.assertEqual(data[0]['displayName']['text'], display_name)

        url = '{0}?displayName=foo'.format(self.url)
        req = self.app.get(url)
        self.ok(req)
        data = self.json(req)
        self.assertEqual(len(data), 0)

    def test_can_update_repository_alias(self):
        alias_id = "repository.Repository%3Apublished-012345678910111213141516%40ODL.MIT.EDU"
        name = "New Repository"
        payload = {
            "name": name
        }
        req = self.app.post(self.url,
                            params=json.dumps(payload),
                            headers={'content-type': 'application/json'})
        self.ok(req)
        new_repository = self.json(req)

        url = '{0}/{1}'.format(self.url,
                               alias_id)
        self.assertRaises(AppError,
                          self.app.get,
                          url)

        payload = {
            "aliasId": alias_id
        }
        url = '{0}/{1}'.format(self.url,
                               new_repository['id'])

        req = self.app.put(url,
                           params=json.dumps(payload),
                           headers={'content-type': 'application/json'})
        self.ok(req)

        url = '{0}/{1}'.format(self.url,
                               alias_id)

        req = self.app.get(url)
        self.ok(req)
        fetched_repository = self.json(req)
        self.assertEqual(new_repository['id'], fetched_repository['id'])
        self.assertEqual(new_repository['displayName']['text'], name)


class AssetContentTests(BaseRepositoryTestCase):
    @staticmethod
    def _english_headers():
        return {'content-type': 'application/json',
                'x-api-locale': 'en'}

    @staticmethod
    def _hindi_headers():
        return {'content-type': 'application/json',
                'x-api-locale': 'hi'}

    @staticmethod
    def _telugu_headers():
        return {'content-type': 'application/json',
                'x-api-locale': 'te'}

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

    def create_item_with_image(self):
        url = '{0}/items'.format(self.assessment_url)
        self._image_in_question.seek(0)
        req = self.app.post(url,
                            upload_files=[('qtiFile',
                                           self._filename(self._image_in_question),
                                           self._image_in_question.read())])
        self.ok(req)
        return self.json(req)

    def create_item_with_image_in_choices(self):
        url = '{0}/items'.format(self.assessment_url)
        self._images_in_choices.seek(0)
        req = self.app.post(url,
                            upload_files=[('qtiFile',
                                           self._filename(self._images_in_choices),
                                           self._images_in_choices.read())])
        self.ok(req)
        return self.json(req)

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

        self.contents_url = '/api/v1/repository/repositories/{0}/assets/{1}/contents'.format(unquote(str(self._repo.ident)),
                                                                                             unquote(str(self.asset.ident)))

        self._generic_upload_test_file = open('{0}/tests/files/generic_upload_test_file.zip'.format(ABS_PATH), 'r')
        self._logo_upload_test_file = open('{0}/tests/files/Epidemic2.sltng'.format(ABS_PATH), 'r')
        self._replacement_image_file = open('{0}/tests/files/replacement_image.png'.format(ABS_PATH), 'r')
        self._images_in_choices = open('{0}/tests/files/qti_file_with_images.zip'.format(ABS_PATH), 'r')
        self._image_in_question = open('{0}/tests/files/mw_sentence_with_audio_file.zip'.format(ABS_PATH), 'r')

        self._english_text = 'english'
        self._hindi_text = u'हिंदी'
        self._telugu_text = u'తెలుగు'

        self._english_language_type = '639-2%3AENG%40ISO'
        self._english_script_type = '15924%3ALATN%40ISO'

        self._hindi_language_type = '639-2%3AHIN%40ISO'
        self._hindi_script_type = '15924%3ADEVA%40ISO'

        self._telugu_language_type = '639-2%3ATEL%40ISO'
        self._telugu_script_type = '15924%3ATELU%40ISO'

    def tearDown(self):
        """
        Remove the test user from all groups in Membership
        Start from the smallest groupId because need to
        remove "parental" roles like for DepartmentAdmin / DepartmentOfficer
        """
        super(AssetContentTests, self).tearDown()

        self._generic_upload_test_file.close()
        self._logo_upload_test_file.close()
        self._replacement_image_file.close()
        self._images_in_choices.close()
        self._image_in_question.close()

    def test_can_get_asset_content_file(self):
        req = self.app.get(self.url + '/stream')
        # self.ok(req)
        self.code(req, 206)
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
                            upload_files=[('submission',
                                           'Epidemic2.sltng',
                                           self._logo_upload_test_file.read())])
        self.ok(req)

        url = '/api/v1/repository/repositories/{0}/assets'.format(unquote(str(self._repo.ident)))
        req = self.app.get(url)
        self.ok(req)
        data = self.json(req)
        self.assertEqual(len(data), 2)
        for asset in data:
            if asset['id'] != str(self.asset.ident):
                asset_obj = self._repo.get_asset(Id(asset['id']))

                contents = asset_obj.get_asset_contents()
                content = contents.next()
                self.assertEqual(content.get_url(),
                                 asset['assetContents'][0]['url'])
                self.assertNotEqual('', asset['assetContents'][0]['url'])
                self.assertEqual('asset-content-genus-type%3Asltng%40ODL.MIT.EDU',
                                 asset['assetContents'][0]['genusTypeId'])

    def test_can_update_asset_content_with_new_file(self):
        req = self.app.get(self.url)
        self.ok(req)
        asset_content = self.asset.get_asset_contents().next()
        original_genus_type = str(asset_content.genus_type)
        original_file_name = asset_content.display_name.text
        original_on_disk_name = asset_content.get_url()
        original_id = str(asset_content.ident)

        self._replacement_image_file.seek(0)
        req = self.app.put(self.url,
                           upload_files=[('inputFile',
                                          self._filename(self._replacement_image_file),
                                          self._replacement_image_file.read())])
        self.ok(req)
        data = self.json(req)
        asset_content = data['assetContents'][0]
        self.assertNotEqual(
            original_genus_type,
            asset_content['genusTypeId']
        )
        self.assertIn('png', asset_content['genusTypeId'])
        self.assertNotEqual(
            original_file_name,
            asset_content['displayName']['text']
        )
        self.assertEqual(
            original_on_disk_name.split('.')[0],
            asset_content['url'].split('.')[0]
        )
        self.assertEqual(
            original_id,
            asset_content['id']
        )
        self.assertIn(
            self._replacement_image_file.name.split('/')[-1],
            asset_content['displayName']['text']
        )

    def test_can_update_asset_content_with_new_file_and_set_genus_type(self):
        req = self.app.get(self.url)
        self.ok(req)
        asset_content = self.asset.get_asset_contents().next()
        original_genus_type = str(asset_content.genus_type)
        original_file_name = asset_content.display_name.text
        original_on_disk_name = asset_content.get_url()
        original_id = str(asset_content.ident)

        self._replacement_image_file.seek(0)
        thumbnail_genus = "asset-content-genus%3Athumbnail%40ODL.MIT.EDU"
        req = self.app.put(self.url,
                           params={"genusTypeId": thumbnail_genus},
                           upload_files=[('inputFile',
                                          self._filename(self._replacement_image_file),
                                          self._replacement_image_file.read())])
        self.ok(req)
        data = self.json(req)
        asset_content = data['assetContents'][0]
        self.assertNotEqual(
            original_genus_type,
            asset_content['genusTypeId']
        )
        self.assertNotEqual(
            original_file_name,
            asset_content['displayName']['text']
        )
        self.assertEqual(
            original_on_disk_name.split('.')[0],
            asset_content['url'].split('.')[0]
        )
        self.assertEqual(
            original_id,
            asset_content['id']
        )
        self.assertIn(
            self._replacement_image_file.name.split('/')[-1],
            asset_content['displayName']['text']
        )
        self.assertEqual(asset_content['genusTypeId'], thumbnail_genus)

    def test_can_update_asset_content_name_and_description(self):
        req = self.app.get(self.url)
        self.ok(req)
        asset_content = self.asset.get_asset_contents().next()
        original_genus_type = str(asset_content.genus_type)
        original_file_name = asset_content.display_name.text
        original_on_disk_name = asset_content.get_url()
        original_id = str(asset_content.ident)

        thumbnail_genus = "asset-content-genus%3Athumbnail%40ODL.MIT.EDU"
        new_name = "foobar"
        new_description = "a small image"
        req = self.app.put(self.url,
                           params=json.dumps({
                               "genusTypeId": thumbnail_genus,
                               "displayName": new_name,
                               "description": new_description
                           }),
                           headers={"content-type": "application/json"})
        self.ok(req)
        data = self.json(req)
        asset_content = data['assetContents'][0]
        self.assertNotEqual(
            original_genus_type,
            asset_content['genusTypeId']
        )
        self.assertNotEqual(
            original_file_name,
            asset_content['displayName']['text']
        )
        self.assertEqual(
            original_on_disk_name.split('.')[0],
            asset_content['url'].split('.')[0]
        )
        self.assertEqual(
            original_id,
            asset_content['id']
        )
        self.assertEqual(
            new_name,
            asset_content['displayName']['text']
        )
        self.assertEqual(
            new_description,
            asset_content['description']['text']
        )
        self.assertEqual(asset_content['genusTypeId'], thumbnail_genus)

    def test_updated_asset_content_in_question_shows_up_properly_in_item_qti(self):
        item = self.create_item_with_image()
        taken, offered = self.create_taken_for_item(self._repo.ident, Id(item['id']))
        url = '{0}/assessmentstaken/{1}/questions?qti'.format(self.assessment_url,
                                                              unquote(str(taken.ident)))

        req = self.app.get(url)
        self.ok(req)
        data = self.json(req)['data']
        soup = BeautifulSoup(data[0]['qti'], 'xml')
        image = soup.find('img')

        req = self.app.get(image['src'])
        # self.ok(req)
        self.code(req, 206)
        headers = req.header_dict
        self.assertIn('image/png', headers['content-type'])
        self.assertEqual(headers['accept-ranges'], 'bytes')
        # self.assertIn('.png', headers['content-disposition'])
        # original_content_length = headers['content-length']
        self.assertIn('content-range', headers)
        self.assertEqual('bytes 0-8191/152318', headers['content-range'][0])
        self.assertEqual('bytes 147456-152317/152318', headers['content-range'][-1])

        # need to get rid of the /stream part of the path to just get the content details URL
        content_url = image['src'].replace('/stream', '')
        self._logo_upload_test_file.seek(0)
        req = self.app.put(content_url,
                           upload_files=[('inputFile',
                                          self._filename(self._logo_upload_test_file),
                                          self._logo_upload_test_file.read())])
        self.ok(req)

        req = self.app.get(url)
        self.ok(req)
        data = self.json(req)['data']
        soup = BeautifulSoup(data[0]['qti'], 'xml')
        image = soup.find('img')

        req = self.app.get(image['src'])
        # self.ok(req)
        self.code(req, 206)
        headers = req.header_dict
        self.assertNotIn('image/png', headers['content-type'])
        self.assertEqual(headers['accept-ranges'], 'bytes')
        self.assertEqual('None', headers['content-type'])  # what would sltng be??
        # self.assertIn('.sltng', headers['content-disposition'])
        # self.assertNotEqual(original_content_length, headers['content-length'])
        self.assertIn('content-range', headers)
        expected_range = 'bytes 0-8191/{0}'.format(str(os.path.getsize(self._logo_upload_test_file.name)))
        self.assertIn(expected_range,
                      headers['content-range'])

    def test_updated_asset_content_in_choices_shows_up_properly_in_item_qti(self):
        item = self.create_item_with_image_in_choices()
        taken, offered = self.create_taken_for_item(self._repo.ident, Id(item['id']))
        url = '{0}/assessmentstaken/{1}/questions?qti'.format(self.assessment_url,
                                                              unquote(str(taken.ident)))

        req = self.app.get(url)
        self.ok(req)
        data = self.json(req)['data']
        soup = BeautifulSoup(data[0]['qti'], 'xml')
        image = soup.find('img')

        req = self.app.get(image['src'])
        # self.ok(req)
        self.code(req, 206)
        headers = req.header_dict
        self.assertIn('image/png', headers['content-type'])
        self.assertEqual(headers['accept-ranges'], 'bytes')
        # self.assertIn('.png', headers['content-disposition'].lower())
        # original_content_length = headers['content-length']
        self.assertIn('content-range', headers)
        self.assertIn('bytes 0-', headers['content-range'])
        # small file that depends on the choice image, either 512 or 641 bytes...

        # need to get rid of the /stream part of the path to just get the content details URL
        content_url = image['src'].replace('/stream', '')
        self._logo_upload_test_file.seek(0)
        req = self.app.put(content_url,
                           upload_files=[('inputFile',
                                          self._filename(self._logo_upload_test_file),
                                          self._logo_upload_test_file.read())])
        self.ok(req)

        req = self.app.get(url)
        self.ok(req)
        data = self.json(req)['data']
        soup = BeautifulSoup(data[0]['qti'], 'xml')
        image = soup.find('img')

        req = self.app.get(image['src'])
        # self.ok(req)
        self.code(req, 206)
        headers = req.header_dict
        self.assertNotIn('image/png', headers['content-type'])
        self.assertEqual('None', headers['content-type'])  # what would sltng be??
        self.assertEqual(headers['accept-ranges'], 'bytes')
        # self.assertIn('.sltng', headers['content-disposition'])
        # self.assertNotEqual(original_content_length, headers['content-length'])
        self.assertIn('content-range', headers)
        expected_range = 'bytes 0-8191/{0}'.format(str(os.path.getsize(self._logo_upload_test_file.name)))
        self.assertIn(expected_range,
                      headers['content-range'])

    def test_can_set_asset_content_display_name_and_description_to_foreign_language(self):
        req = self.app.get(self.url)
        self.ok(req)
        asset_content = self.asset.get_asset_contents().next()
        original_genus_type = str(asset_content.genus_type)
        original_file_name = asset_content.display_name.text
        expected_url = asset_content.get_url()
        original_id = str(asset_content.ident)

        description_genus = "asset-content-genus%3Adescription%40ODL.MIT.EDU"
        new_name = self._hindi_text
        new_description = self._hindi_text
        req = self.app.put(self.url,
                           params=json.dumps({
                               "genusTypeId": description_genus,
                               "displayName": new_name,
                               "description": new_description
                           }),
                           headers=self._hindi_headers())
        self.ok(req)
        data = self.json(req)
        asset_content = data['assetContents'][0]
        self.assertNotEqual(
            original_genus_type,
            asset_content['genusTypeId']
        )
        self.assertNotEqual(
            original_file_name,
            asset_content['displayName']['text']
        )
        self.assertEqual(
            expected_url,
            asset_content['url']
        )
        self.assertEqual(
            original_id,
            asset_content['id']
        )
        self.assertEqual(
            new_name,
            asset_content['displayName']['text']
        )
        self.assertEqual(
            self._hindi_language_type,
            asset_content['displayName']['languageTypeId']
        )
        self.assertEqual(
            self._hindi_script_type,
            asset_content['displayName']['scriptTypeId']
        )
        self.assertEqual(
            new_description,
            asset_content['description']['text']
        )
        self.assertEqual(
            self._hindi_language_type,
            asset_content['description']['languageTypeId']
        )
        self.assertEqual(
            self._hindi_script_type,
            asset_content['description']['scriptTypeId']
        )
        self.assertEqual(asset_content['genusTypeId'], description_genus)

    def test_can_get_asset_content_display_name_and_description_in_foreign_language(self):
        req = self.app.get(self.url)
        self.ok(req)
        asset_content = self.asset.get_asset_contents().next()
        original_file_name = asset_content.display_name.text
        original_description = asset_content.description.text

        description_genus = "asset-content-genus%3Adescription%40ODL.MIT.EDU"
        new_name = self._hindi_text
        new_description = self._hindi_text
        req = self.app.put(self.url,
                           params=json.dumps({
                               "genusTypeId": description_genus,
                               "displayName": new_name,
                               "description": new_description
                           }),
                           headers=self._hindi_headers())
        self.ok(req)

        asset_url = '/api/v1/repository/repositories/{0}/assets/{1}'.format(unquote(str(self._repo.ident)),
                                                                            unquote(str(self.asset.ident)))

        req = self.app.get(asset_url,
                           headers=self._english_headers())
        self.ok(req)
        data = self.json(req)
        asset_content = data['assetContents'][0]

        self.assertEqual(
            asset_content['displayName']['text'],
            original_file_name
        )
        self.assertEqual(
            asset_content['displayName']['languageTypeId'],
            self._english_language_type
        )
        self.assertEqual(
            asset_content['displayName']['scriptTypeId'],
            self._english_script_type
        )
        self.assertEqual(
            asset_content['description']['text'],
            original_description
        )
        self.assertEqual(
            asset_content['description']['languageTypeId'],
            self._english_language_type
        )
        self.assertEqual(
            asset_content['description']['scriptTypeId'],
            self._english_script_type
        )

        req = self.app.get(asset_url,
                           headers=self._hindi_headers())
        self.ok(req)
        data = self.json(req)
        asset_content = data['assetContents'][0]
        self.assertEqual(
            asset_content['displayName']['text'],
            new_name
        )
        self.assertEqual(
            asset_content['displayName']['languageTypeId'],
            self._hindi_language_type
        )
        self.assertEqual(
            asset_content['displayName']['scriptTypeId'],
            self._hindi_script_type
        )
        self.assertEqual(
            asset_content['description']['text'],
            new_description
        )
        self.assertEqual(
            asset_content['description']['languageTypeId'],
            self._hindi_language_type
        )
        self.assertEqual(
            asset_content['description']['scriptTypeId'],
            self._hindi_script_type
        )

    def test_can_get_asset_contents_list(self):
        asset_content = self.asset.get_asset_contents().next()
        req = self.app.get(self.contents_url)
        self.ok(req)
        data = self.json(req)
        self.assertEqual(len(data), 1)
        self.assertEqual(data[0]['id'], str(asset_content.ident))
        self.assertEqual(asset_content.get_url(), data[0]['url'])
        self.assertNotEqual('', data[0]['url'])

    def test_can_get_asset_contents_list_with_full_urls(self):
        asset_content = self.asset.get_asset_contents().next()
        req = self.app.get(self.contents_url + '?fullUrls')
        self.ok(req)
        data = self.json(req)
        self.assertEqual(len(data), 1)
        self.assertEqual(data[0]['id'], str(asset_content.ident))
        self.assertEqual(asset_content.get_url(), data[0]['url'])
        self.assertNotEqual('', data[0]['url'])

    def test_can_add_new_asset_content_with_file(self):
        self._replacement_image_file.seek(0)
        payload = {
            "displayName": 'foo'
        }
        # Paste complains if you use unicode in the payload here,
        # so we'll test unicode language in a different test
        req = self.app.post(self.contents_url,
                            params=payload,
                            upload_files=[('inputFile',
                                           self._filename(self._replacement_image_file),
                                           self._replacement_image_file.read())],
                            headers={'x-api-locale': 'hi'})
        self.ok(req)
        data = self.json(req)
        self.assertEqual(data['assetId'], str(self.asset.ident))
        asset = self._repo.get_asset(self.asset.ident)

        self.assertEqual(asset.get_asset_contents().available(), 2)
        contents = asset.get_asset_contents()
        contents.next()
        content = contents.next()
        self.assertEqual(str(content.ident),
                         data['id'])
        self.assertEqual(data['displayName']['text'],
                         'foo')
        self.assertEqual(data['displayName']['languageTypeId'],
                         self._hindi_language_type)
        self.assertNotEqual('', data['url'])
        self.assertEqual(content.get_url(), data['url'])

    def test_can_add_new_asset_content_in_non_english_language(self):
        payload = {
            "displayName": self._hindi_text
        }
        req = self.app.post(self.contents_url,
                            params=json.dumps(payload),
                            headers=self._hindi_headers())
        self.ok(req)
        data = self.json(req)
        self.assertEqual(data['assetId'], str(self.asset.ident))
        asset = self._repo.get_asset(self.asset.ident)

        self.assertEqual(asset.get_asset_contents().available(), 2)
        contents = asset.get_asset_contents()
        contents.next()
        content = contents.next()
        self.assertEqual(str(content.ident),
                         data['id'])
        self.assertEqual(data['displayName']['text'],
                         self._hindi_text)
        self.assertEqual(data['displayName']['languageTypeId'],
                         self._hindi_language_type)
        self.assertEqual('', data['url'])
        self.assertIn('displayNames', data)

    def test_can_add_new_asset_content_with_json_only(self):
        payload = {
            "displayName": 'foo'
        }
        req = self.app.post(self.contents_url,
                            params=json.dumps(payload),
                            headers={"content-type": "application/json"})
        self.ok(req)
        data = self.json(req)
        self.assertEqual(data['assetId'], str(self.asset.ident))
        asset = self._repo.get_asset(self.asset.ident)

        self.assertEqual(asset.get_asset_contents().available(), 2)
        contents = asset.get_asset_contents()
        contents.next()
        second_content = contents.next()
        self.assertEqual(str(second_content.ident),
                         data['id'])
        self.assertEqual(data['displayName']['text'],
                         'foo')
        self.assertEqual('', data['url'])

    def test_can_add_new_asset_with_file_with_full_url(self):
        self._replacement_image_file.seek(0)
        payload = {
            "displayName": 'foo',
            "fullUrl": True
        }
        # Paste complains if you use unicode in the payload here,
        # so we'll test unicode language in a different test
        req = self.app.post(self.contents_url,
                            params=payload,
                            upload_files=[('inputFile',
                                           self._filename(self._replacement_image_file),
                                           self._replacement_image_file.read())],
                            headers={'x-api-locale': 'hi'})
        self.ok(req)
        data = self.json(req)
        self.assertEqual(data['assetId'], str(self.asset.ident))
        asset = self._repo.get_asset(self.asset.ident)

        self.assertEqual(asset.get_asset_contents().available(), 2)
        contents = asset.get_asset_contents()
        contents.next()
        content = contents.next()
        self.assertEqual(str(content.ident),
                         data['id'])
        self.assertEqual(data['displayName']['text'],
                         'foo')
        self.assertEqual(data['displayName']['languageTypeId'],
                         self._hindi_language_type)

        # this assumes usage of the filesystem adapter...
        # self.assertIn('/repository/repositories', data['url'])
        self.assertEqual(content.get_url(), data['url'])
        self.assertNotEqual('', data['url'])


class AssetQueryTests(BaseRepositoryTestCase):
    def setUp(self):
        super(AssetQueryTests, self).setUp()
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
        super(AssetQueryTests, self).tearDown()

        self._video_upload_test_file.close()
        self._caption_upload_test_file.close()

    def test_can_get_assets_with_valid_content_urls(self):
        self._video_upload_test_file.seek(0)
        req = self.app.post(self.url,
                            upload_files=[('inputFile', 'video-js-test.mp4', self._video_upload_test_file.read())])
        self.ok(req)
        data = self.json(req)

        self._caption_upload_test_file.seek(0)
        req = self.app.post(self.url,
                            upload_files=[('inputFile', 'video-js-test-en.vtt', self._caption_upload_test_file.read())])
        self.ok(req)

        url = '{0}?fullUrls'.format(self.url)
        req = self.app.get(url)
        self.ok(req)
        data = self.json(req)

        self.assertEqual(len(data), 1)
        asset = data[0]
        self.assertEqual(
            len(asset['assetContents']),
            2
        )

        for index, asset_content in enumerate(asset['assetContents']):
            if index == 0:
                self.assertEqual(
                    asset_content['genusTypeId'],
                    'asset-content-genus-type%3Amp4%40ODL.MIT.EDU'
                )
            else:
                self.assertEqual(
                    asset_content['genusTypeId'],
                    'asset-content-genus-type%3Avtt%40ODL.MIT.EDU'
                )
            asset_content_obj = self._repo.get_asset_content(Id(asset_content['id']))
            self.assertEqual(
                asset_content_obj.get_url(),
                asset_content['url']
            )

    def test_can_get_assets_from_all_repositories(self):
        from testing_utilities import create_test_repository
        self._video_upload_test_file.seek(0)
        req = self.app.post(self.url,
                            upload_files=[('inputFile', 'video-js-test.mp4', self._video_upload_test_file.read())])
        self.ok(req)
        data = self.json(req)

        new_repo = create_test_repository()
        url = '/api/v1/repository/repositories/{0}/assets'.format(str(new_repo.ident))

        self._caption_upload_test_file.seek(0)
        req = self.app.post(url,
                            upload_files=[('inputFile', 'new_file.vtt', self._caption_upload_test_file.read())])
        self.ok(req)

        url = '{0}?fullUrls&allAssets'.format(self.url)
        req = self.app.get(url)
        self.ok(req)
        data = self.json(req)

        self.assertEqual(len(data), 2)
        asset_1 = data[0]
        self.assertEqual(
            len(asset_1['assetContents']),
            1
        )
        possible_ac_types = ['asset-content-genus-type%3Amp4%40ODL.MIT.EDU',
                             'asset-content-genus-type%3Avtt%40ODL.MIT.EDU']
        self.assertIn(
            asset_1['assetContents'][0]['genusTypeId'],
            possible_ac_types
        )
        asset_2 = data[1]
        self.assertEqual(
            len(asset_2['assetContents']),
            1
        )
        self.assertIn(
            asset_2['assetContents'][0]['genusTypeId'],
            possible_ac_types
        )
        self.assertNotEqual(
            asset_1['assignedRepositoryIds'][0],
            asset_2['assignedRepositoryIds'][0]
        )
        self.assertNotEqual(
            asset_1['assetContents'][0]['genusTypeId'],
            asset_2['assetContents'][0]['genusTypeId']
        )


class AssetCRUDTests(BaseRepositoryTestCase):
    def setUp(self):
        super(AssetCRUDTests, self).setUp()
        self.url = '{0}/repositories/{1}/assets'.format(self.url,
                                                        unquote(str(self._repo.ident)))

        self._video_upload_test_file = open('{0}/tests/files/video-js-test.mp4'.format(ABS_PATH), 'r')
        self._caption_upload_test_file = open('{0}/tests/files/video-js-test-en.vtt'.format(ABS_PATH), 'r')
        self._image_2_test_file = open('{0}/tests/files/Picture2.png'.format(ABS_PATH), 'r')

    def tearDown(self):
        """
        Remove the test user from all groups in Membership
        Start from the smallest groupId because need to
        remove "parental" roles like for DepartmentAdmin / DepartmentOfficer
        """
        super(AssetCRUDTests, self).tearDown()

        self._video_upload_test_file.close()
        self._caption_upload_test_file.close()
        self._image_2_test_file.close()

    def upload_asset_with_provider(self):
        self._video_upload_test_file.seek(0)
        self._provider = "Doe, John. Images from the sky. Nature Magazine, vol 1 iss 10. pp 1-10, 2016"
        req = self.app.post(self.url,
                            params={"provider": self._provider},
                            upload_files=[('inputFile', 'video-js-test.mp4', self._video_upload_test_file.read())])
        self.ok(req)
        return self.json(req)

    def upload_asset_with_source(self):
        self._video_upload_test_file.seek(0)
        self._source = "John Doe, (c) 2016"
        req = self.app.post(self.url,
                            params={"source": self._source},
                            upload_files=[('inputFile', 'video-js-test.mp4', self._video_upload_test_file.read())])
        self.ok(req)
        return self.json(req)

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

        # because this is hidden / stripped out
        self.assertNotIn(
            'asset_content_record_type%3Afilesystem%40odl.mit.edu',
            data['recordTypeIds']
        )
        asset_content = self._repo.get_asset_content(Id(data['assetContents'][0]['id']))
        self.assertEqual(
            asset_content.get_url(),
            data['assetContents'][0]['url']
        )
        self.assertEqual(
            'video-js-test.mp4',
            data['assetContents'][0]['displayName']['text']
        )

    def test_can_create_asset_with_flag_to_return_valid_url(self):
        self._video_upload_test_file.seek(0)
        req = self.app.post(self.url,
                            params={'returnUrl': True},
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

        # because this is hidden / stripped out
        self.assertNotIn(
            'asset_content_record_type%3Afilesystem%40odl.mit.edu',
            data['recordTypeIds']
        )
        asset_content = self._repo.get_asset_content(Id(data['assetContents'][0]['id']))
        self.assertEqual(
            asset_content.get_url(),
            data['assetContents'][0]['url']
        )
        self.assertEqual(
            'video-js-test.mp4',
            data['assetContents'][0]['displayName']['text']
        )

    def test_can_upload_caption_vtt_files_to_repository(self):
        self._caption_upload_test_file.seek(0)
        req = self.app.post(self.url,
                            upload_files=[('inputFile', 'video-js-test-en.vtt', self._caption_upload_test_file.read())])
        self.ok(req)
        data = self.json(req)
        self.assertEqual(
            len(data['assetContents']),
            1
        )
        self.assertEqual(
            data['assetContents'][0]['genusTypeId'],
            'asset-content-genus-type%3Avtt%40ODL.MIT.EDU'
        )

        # because this is hidden / stripped out
        self.assertNotIn(
            'asset_content_record_type%3Afilesystem%40odl.mit.edu',
            data['recordTypeIds']
        )

        asset_content = self._repo.get_asset_content(Id(data['assetContents'][0]['id']))
        self.assertEqual(
            asset_content.get_url(),
            data['assetContents'][0]['url']
        )
        self.assertEqual(
            'video-js-test-en.vtt',
            data['assetContents'][0]['displayName']['text']
        )

    def test_caption_and_video_files_uploaded_as_asset_contents_on_same_asset(self):
        self._video_upload_test_file.seek(0)
        req = self.app.post(self.url,
                            upload_files=[('inputFile', 'video-js-test.mp4', self._video_upload_test_file.read())])
        self.ok(req)
        data = self.json(req)
        self.assertEqual(
            len(data['assetContents']),
            1
        )
        asset_id = data['id']
        self.assertEqual(
            data['displayName']['text'],
            'video_js_test'
        )

        self._caption_upload_test_file.seek(0)
        req = self.app.post(self.url,
                            upload_files=[('inputFile', 'video-js-test-en.vtt', self._caption_upload_test_file.read())])
        self.ok(req)
        data = self.json(req)
        self.assertEqual(
            len(data['assetContents']),
            2
        )
        self.assertEqual(
            asset_id,
            data['id']
        )
        self.assertEqual(
            data['displayName']['text'],
            'video_js_test'
        )

        self.assertEqual(
            data['assetContents'][0]['genusTypeId'],
            'asset-content-genus-type%3Amp4%40ODL.MIT.EDU'
        )
        asset_content = self._repo.get_asset_content(Id(data['assetContents'][0]['id']))
        self.assertEqual(
            asset_content.get_url(),
            data['assetContents'][0]['url']
        )
        self.assertEqual(
            'video-js-test.mp4',
            data['assetContents'][0]['displayName']['text']
        )

        self.assertEqual(
            data['assetContents'][1]['genusTypeId'],
            'asset-content-genus-type%3Avtt%40ODL.MIT.EDU'
        )
        asset_content = self._repo.get_asset_content(Id(data['assetContents'][1]['id']))
        self.assertEqual(
            asset_content.get_url(),
            data['assetContents'][1]['url']
        )
        self.assertEqual(
            'video-js-test-en.vtt',
            data['assetContents'][1]['displayName']['text']
        )

    def test_can_provide_license_on_upload(self):
        self._video_upload_test_file.seek(0)
        license_ = "BSD"
        req = self.app.post(self.url,
                            params={"license": license_},
                            upload_files=[('inputFile', 'video-js-test.mp4', self._video_upload_test_file.read())])
        self.ok(req)
        data = self.json(req)
        self.assertEqual(
            data['license']['text'],
            license_
        )

    def test_can_provide_copyright_on_upload(self):
        self._video_upload_test_file.seek(0)
        copyright_ = "CC BY"
        req = self.app.post(self.url,
                            params={"copyright": copyright_},
                            upload_files=[('inputFile', 'video-js-test.mp4', self._video_upload_test_file.read())])
        self.ok(req)
        data = self.json(req)
        self.assertEqual(
            data['copyright']['text'],
            copyright_
        )

    def test_can_update_asset_with_license(self):
        self._video_upload_test_file.seek(0)
        license_ = "BSD"
        req = self.app.post(self.url,
                            upload_files=[('inputFile', 'video-js-test.mp4', self._video_upload_test_file.read())])
        self.ok(req)
        data = self.json(req)
        asset_id = data['id']
        self.assertEqual(
            data['license']['text'],
            ''
        )

        payload = {
            "license": license_
        }
        url = '{0}/{1}'.format(self.url,
                               asset_id)
        req = self.app.put(url,
                           params=json.dumps(payload),
                           headers={'content-type': 'application/json'})
        self.ok(req)
        data = self.json(req)
        self.assertEqual(
            data['license']['text'],
            license_
        )

    def test_can_update_asset_with_copyright(self):
        self._video_upload_test_file.seek(0)
        copyright_ = "CC BY"
        req = self.app.post(self.url,
                            upload_files=[('inputFile', 'video-js-test.mp4', self._video_upload_test_file.read())])
        self.ok(req)
        data = self.json(req)
        asset_id = data['id']
        self.assertEqual(
            data['copyright']['text'],
            ''
        )

        payload = {
            "copyright": copyright_
        }
        url = '{0}/{1}'.format(self.url,
                               asset_id)
        req = self.app.put(url,
                           params=json.dumps(payload),
                           headers={'content-type': 'application/json'})
        self.ok(req)
        data = self.json(req)
        self.assertEqual(
            data['copyright']['text'],
            copyright_
        )

    def test_can_update_asset_name(self):
        self._video_upload_test_file.seek(0)
        req = self.app.post(self.url,
                            upload_files=[('inputFile', 'video-js-test.mp4', self._video_upload_test_file.read())])
        self.ok(req)
        data = self.json(req)
        asset_id = data['id']
        original_name = data['displayName']['text']
        new_name = "foobar"
        self.assertNotEqual(original_name, new_name)

        payload = {
            "displayName": new_name
        }
        url = '{0}/{1}'.format(self.url,
                               asset_id)
        req = self.app.put(url,
                           params=json.dumps(payload),
                           headers={'content-type': 'application/json'})
        self.ok(req)
        data = self.json(req)
        self.assertEqual(
            data['displayName']['text'],
            new_name
        )

    def test_can_update_asset_description(self):
        self._video_upload_test_file.seek(0)
        req = self.app.post(self.url,
                            upload_files=[('inputFile', 'video-js-test.mp4', self._video_upload_test_file.read())])
        self.ok(req)
        data = self.json(req)
        asset_id = data['id']
        original_description = data['displayName']['text']
        new_description = "foobar"
        self.assertNotEqual(original_description, new_description)

        payload = {
            "description": new_description
        }
        url = '{0}/{1}'.format(self.url,
                               asset_id)
        req = self.app.put(url,
                           params=json.dumps(payload),
                           headers={'content-type': 'application/json'})
        self.ok(req)
        data = self.json(req)
        self.assertEqual(
            data['description']['text'],
            new_description
        )

    def test_can_get_asset_with_content_urls(self):
        self._video_upload_test_file.seek(0)
        req = self.app.post(self.url,
                            upload_files=[('inputFile', 'video-js-test.mp4', self._video_upload_test_file.read())])
        self.ok(req)
        data = self.json(req)
        asset_id = data['id']
        url = '{0}/{1}?fullUrls'.format(self.url,
                                        asset_id)
        req = self.app.get(url)
        self.ok(req)
        data = self.json(req)
        asset_content = self._repo.get_asset_content(Id(data['assetContents'][0]['id']))
        self.assertEqual(
            asset_content.get_url(),
            data['assetContents'][0]['url']
        )

    def test_can_replace_main_media_element_in_asset(self):
        # using the convenience method
        self._video_upload_test_file.seek(0)
        req = self.app.post(self.url,
                            upload_files=[('inputFile', 'video-js-test.mp4', self._video_upload_test_file.read())])
        self.ok(req)
        data = self.json(req)

        url = '{0}/{1}'.format(self.url, data['id'])
        self._image_2_test_file.seek(0)
        req = self.app.put(url,
                           upload_files=[('inputFile',
                                          self._filename(self._image_2_test_file),
                                          self._image_2_test_file.read())])
        self.ok(req)
        data = self.json(req)
        self.assertEqual(len(data['assetContents']), 1)
        image_url = data['assetContents'][0]['url']
        req = self.app.get(image_url)
        self.code(req, 206)
        self._image_2_test_file.seek(0)
        self.assertEqual(req.body,
                         self._image_2_test_file.read())

    def test_can_set_asset_source(self):
        data = self.upload_asset_with_source()
        self.assertIn('source', data)
        self.assertEqual(
            data['source']['text'],
            self._source
        )

    def test_can_update_asset_source(self):
        self._video_upload_test_file.seek(0)
        source = "John Doe, (c) 2016"
        req = self.app.post(self.url,
                            upload_files=[('inputFile', 'video-js-test.mp4', self._video_upload_test_file.read())])
        self.ok(req)
        data = self.json(req)
        self.assertNotIn('source', data)
        self.assertEqual(data['sourceId'], '')
        url = '{0}/{1}'.format(self.url,
                               data['id'])
        payload = {
            'source': source
        }
        req = self.app.put(url,
                           params=json.dumps(payload),
                           headers={'content-type': 'application/json'})
        self.ok(req)
        data = self.json(req)
        self.assertIn('source', data)
        self.assertEqual(
            data['source']['text'],
            source
        )

    def test_can_change_asset_source(self):
        data = self.upload_asset_with_source()
        self.assertIn('source', data)
        self.assertEqual(
            data['source']['text'],
            self._source
        )
        resource_id_1 = data['sourceId']

        source_2 = 'foobar, (c) 1900'
        url = '{0}/{1}'.format(self.url,
                               data['id'])
        payload = {
            'source': source_2
        }
        req = self.app.put(url,
                           params=json.dumps(payload),
                           headers={'content-type': 'application/json'})
        self.ok(req)
        data = self.json(req)
        self.assertIn('source', data)
        self.assertEqual(
            data['source']['text'],
            source_2
        )

        self.assertNotEqual(resource_id_1,
                            data['sourceId'])

    def test_asset_source_returns_as_resource_name_on_get_details(self):
        data = self.upload_asset_with_source()
        original_source_id = data['sourceId']
        url = '{0}/{1}'.format(self.url,
                               data['id'])
        req = self.app.get(url)
        self.ok(req)
        data = self.json(req)
        self.assertIn('source', data)
        self.assertEqual(data['sourceId'], original_source_id)
        self.assertEqual(data['source']['text'], self._source)

    def test_asset_source_returns_as_resource_name_on_get_list(self):
        data = self.upload_asset_with_source()
        original_source_id = data['sourceId']
        req = self.app.get(self.url)
        self.ok(req)
        data = self.json(req)
        self.assertEqual(len(data), 1)
        self.assertIn('source', data[0])
        self.assertEqual(data[0]['sourceId'], original_source_id)
        self.assertEqual(data[0]['source']['text'], self._source)

    def test_can_set_asset_provider(self):
        data = self.upload_asset_with_provider()
        self.assertIn('provider', data)
        self.assertEqual(
            data['provider']['text'],
            self._provider
        )

    def test_can_update_asset_provider(self):
        self._video_upload_test_file.seek(0)
        provider = "Doe, John. Images from the sky. Nature Magazine, vol 1 iss 10. pp 1-10, 2016"
        req = self.app.post(self.url,
                            upload_files=[('inputFile', 'video-js-test.mp4', self._video_upload_test_file.read())])
        self.ok(req)
        data = self.json(req)
        self.assertNotIn('provider', data)
        self.assertEqual(data['providerId'], '')
        url = '{0}/{1}'.format(self.url,
                               data['id'])
        payload = {
            'provider': provider
        }
        req = self.app.put(url,
                           params=json.dumps(payload),
                           headers={'content-type': 'application/json'})
        self.ok(req)
        data = self.json(req)
        self.assertIn('provider', data)
        self.assertEqual(
            data['provider']['text'],
            provider
        )

    def test_can_change_asset_provider(self):
        data = self.upload_asset_with_provider()
        self.assertIn('provider', data)
        self.assertEqual(
            data['provider']['text'],
            self._provider
        )
        resource_id_1 = data['providerId']

        provider_2 = 'foobar, (c) 1900'
        url = '{0}/{1}'.format(self.url,
                               data['id'])
        payload = {
            'provider': provider_2
        }
        req = self.app.put(url,
                           params=json.dumps(payload),
                           headers={'content-type': 'application/json'})
        self.ok(req)
        data = self.json(req)
        self.assertIn('provider', data)
        self.assertEqual(
            data['provider']['text'],
            provider_2
        )

        self.assertNotEqual(resource_id_1,
                            data['providerId'])

    def test_asset_provider_returns_as_resource_name_on_get_details(self):
        data = self.upload_asset_with_provider()
        original_provider_id = data['providerId']
        url = '{0}/{1}'.format(self.url,
                               data['id'])
        req = self.app.get(url)
        self.ok(req)
        data = self.json(req)
        self.assertIn('provider', data)
        self.assertEqual(data['providerId'], original_provider_id)
        self.assertEqual(data['provider']['text'], self._provider)

    def test_asset_provider_returns_as_resource_name_on_get_list(self):
        data = self.upload_asset_with_provider()
        original_provider_id = data['providerId']
        req = self.app.get(self.url)
        self.ok(req)
        data = self.json(req)
        self.assertEqual(len(data), 1)
        self.assertIn('provider', data[0])
        self.assertEqual(data[0]['providerId'], original_provider_id)
        self.assertEqual(data[0]['provider']['text'], self._provider)
