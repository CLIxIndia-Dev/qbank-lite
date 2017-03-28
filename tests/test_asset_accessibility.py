# -*- coding: utf-8 -*-
import json
import os

from bs4 import BeautifulSoup

from dlkit_runtime.configs import FILESYSTEM_ASSET_CONTENT_TYPE
from dlkit_runtime.errors import NotFound
from dlkit_runtime.primordium import DataInputStream, Type, Id, DisplayText

from testing_utilities import BaseTestCase, get_fixture_repository, get_managers
from urllib import unquote, quote

from records.registry import ASSESSMENT_RECORD_TYPES,\
    ASSET_CONTENT_RECORD_TYPES, ASSET_CONTENT_GENUS_TYPES

from .test_assessment import QTI_ITEM_CHOICE_INTERACTION_GENUS,\
    QTI_QUESTION_CHOICE_INTERACTION_GENUS

import utilities

PROJECT_PATH = os.path.dirname(os.path.abspath(__file__))
ABS_PATH = os.path.abspath(os.path.join(PROJECT_PATH, os.pardir))

SIMPLE_SEQUENCE_RECORD = Type(**ASSESSMENT_RECORD_TYPES['simple-child-sequencing'])
MULTI_LANGUAGE_ASSET_CONTENTS = Type(**ASSET_CONTENT_RECORD_TYPES['multi-language'])
ALT_TEXT_ASSET_CONTENT_GENUS_TYPE = Type(**ASSET_CONTENT_GENUS_TYPES['alt-text'])
MEDIA_DESCRIPTION_ASSET_CONTENT_GENUS_TYPE = Type(**ASSET_CONTENT_GENUS_TYPES['media-description'])
VTT_FILE_ASSET_CONTENT_GENUS_TYPE = Type(**ASSET_CONTENT_GENUS_TYPES['vtt'])


class BaseAccessibilityTestCase(BaseTestCase):
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
        super(BaseAccessibilityTestCase, self).setUp()
        self.url = '/api/v1/repository'
        self._repo = get_fixture_repository()
        test_file = '{0}/tests/files/sample_movie.MOV'.format(ABS_PATH)

        self.test_file = open(test_file, 'r')

    def tearDown(self):
        super(BaseAccessibilityTestCase, self).tearDown()
        self.test_file.close()


class AssetAccessibilityCRUDTests(BaseAccessibilityTestCase):
    def create_mc_item_with_image(self, asset):
        url = '/api/v1/assessment/banks/{0}/items'.format(str(self._repo.ident))

        payload = {
            "genusTypeId": str(QTI_ITEM_CHOICE_INTERACTION_GENUS),
            "name": "Question 1",
            "description": "For testing",
            "question": {
                "questionString": """<itemBody >
<p>Which of the following is a circle?</p>
</itemBody>""",
                "choices": [{
                    "id": "idc561552b-ed48-46c3-b20d-873150dfd4a2",
                    "text": """<simpleChoice identifier="idc561552b-ed48-46c3-b20d-873150dfd4a2">
<p>
  <img src="AssetContent:green_dot_png" alt="AssetContent:green_dot_alt" width="20" height="20" />
</p>
</simpleChoice>"""
                }, {
                    "id": "ida86a26e0-a563-4e48-801a-ba9d171c24f7",
                    "text": """<simpleChoice identifier="ida86a26e0-a563-4e48-801a-ba9d171c24f7">
<p>|__|</p>
</simpleChoice>"""
                }],
                "genusTypeId": str(QTI_QUESTION_CHOICE_INTERACTION_GENUS),
                "shuffle": True,
                "fileIds": {
                    'green_dot_png': {
                        'assetId': asset['id'],
                        'assetContentId': asset['assetContents'][0]['id'],
                        'assetContentTypeId': asset['assetContents'][0]['genusTypeId']
                    },
                    'green_dot_alt': {
                        'assetId': asset['id'],
                        'assetContentId': asset['assetContents'][1]['id'],
                        'assetContentTypeId': asset['assetContents'][1]['genusTypeId']
                    }
                }
            },
            "answers": []
        }

        return self.json(self.app.post(url,
                                       params=json.dumps(payload),
                                       headers={'content-type': 'application/json'}))

    def setUp(self):
        super(AssetAccessibilityCRUDTests, self).setUp()
        self.url = '{0}/repositories/{1}/assets'.format(self.url,
                                                        unquote(str(self._repo.ident)))

        self._video_upload_test_file = open('{0}/tests/files/video-js-test.mp4'.format(ABS_PATH), 'r')
        self._caption_upload_test_file = open('{0}/tests/files/video-js-test-en.vtt'.format(ABS_PATH), 'r')
        self._image_upload_test_file = open('{0}/tests/files/green_dot.png'.format(ABS_PATH), 'r')
        self._transcript_test_file = open('{0}/tests/files/transcript.txt'.format(ABS_PATH), 'r')

        self._hindi_text = {
            'text': u'हिंदी',
            'languageTypeId': '639-2%3AHIN%40ISO',
            'scriptTypeId': '15924%3ADEVA%40ISO',
            'formatTypeId': 'TextFormats%3APLAIN%40okapia.net'
        }

        self._english_language_type = '639-2%3AENG%40ISO'
        self._english_script_type = '15924%3ALATN%40ISO'

    def tearDown(self):
        """
        Remove the test user from all groups in Membership
        Start from the smallest groupId because need to
        remove "parental" roles like for DepartmentAdmin / DepartmentOfficer
        """
        super(AssetAccessibilityCRUDTests, self).tearDown()

        self._video_upload_test_file.close()
        self._caption_upload_test_file.close()
        self._image_upload_test_file.close()
        self._transcript_test_file.close()

    def test_can_create_asset_with_alt_text(self):
        # should add the alt-text as an asset content
        self._image_upload_test_file.seek(0)
        alt_text = "a green dot!"
        req = self.app.post(self.url,
                            params={"altText": alt_text},
                            upload_files=[('inputFile', 'green_dot.png', self._image_upload_test_file.read())])
        self.ok(req)
        data = self.json(req)
        self.assertEqual(len(data['assetContents']), 2)
        self.assertEqual(len(data['assetContents'][1]['altTexts']), 1)
        self.assertEqual(
            data['assetContents'][1]['altTexts'][0]['text'],
            alt_text
        )
        self.assertEqual(
            data['assetContents'][1]['altText']['text'],
            alt_text
        )
        self.assertEqual(
            data['assetContents'][1]['genusTypeId'],
            str(ALT_TEXT_ASSET_CONTENT_GENUS_TYPE)
        )

    def test_can_create_asset_with_media_description(self):
        # should add the description as an asset content
        self._image_upload_test_file.seek(0)
        description = "this is an image of a green dot"
        req = self.app.post(self.url,
                            params={"mediaDescription": description},
                            upload_files=[('inputFile', 'green_dot.png', self._image_upload_test_file.read())])
        self.ok(req)
        data = self.json(req)
        self.assertEqual(len(data['assetContents']), 2)
        self.assertEqual(
            len(data['assetContents'][1]['mediaDescriptions']),
            1
        )
        self.assertEqual(
            data['assetContents'][1]['mediaDescriptions'][0]['text'],
            description
        )
        self.assertEqual(
            data['assetContents'][1]['mediaDescription']['text'],
            description
        )
        self.assertEqual(
            data['assetContents'][1]['genusTypeId'],
            str(MEDIA_DESCRIPTION_ASSET_CONTENT_GENUS_TYPE)
        )

    def test_can_update_alt_text_with_new_language(self):
        self._image_upload_test_file.seek(0)
        alt_text = "a green dot!"
        req = self.app.post(self.url,
                            params={"altText": alt_text},
                            upload_files=[('inputFile', 'green_dot.png', self._image_upload_test_file.read())])
        self.ok(req)
        data = self.json(req)

        url = '{0}/{1}'.format(self.url,
                               data['id'])

        payload = {
            'altText': self._hindi_text
        }
        req = self.app.put(url,
                           params=json.dumps(payload),
                           headers={'content-type': 'application/json'})
        self.ok(req)
        data = self.json(req)

        self.assertEqual(len(data['assetContents']), 2)
        self.assertEqual(len(data['assetContents'][1]['altTexts']), 2)
        self.assertEqual(data['assetContents'][1]['genusTypeId'],
                         str(ALT_TEXT_ASSET_CONTENT_GENUS_TYPE))
        self.assertEqual(
            data['assetContents'][1]['altTexts'][1]['text'],
            self._hindi_text['text']
        )
        self.assertEqual(
            data['assetContents'][1]['altTexts'][1]['languageTypeId'],
            self._hindi_text['languageTypeId']
        )
        self.assertEqual(
            data['assetContents'][1]['altTexts'][1]['scriptTypeId'],
            self._hindi_text['scriptTypeId']
        )
        self.assertEqual(
            data['assetContents'][1]['altText']['text'],
            alt_text
        )

    def test_can_update_existing_alt_text_language(self):
        self._image_upload_test_file.seek(0)
        alt_text = "a green dot!"
        req = self.app.post(self.url,
                            params={"altText": alt_text},
                            upload_files=[('inputFile', 'green_dot.png', self._image_upload_test_file.read())])
        self.ok(req)
        data = self.json(req)

        url = '{0}/{1}'.format(self.url,
                               data['id'])
        new_alt_text = 'a purple dot?'
        payload = {
            'altText': new_alt_text
        }
        req = self.app.put(url,
                           params=json.dumps(payload),
                           headers={'content-type': 'application/json'})
        self.ok(req)
        data = self.json(req)

        self.assertEqual(len(data['assetContents']), 2)
        self.assertEqual(len(data['assetContents'][1]['altTexts']), 1)
        self.assertEqual(data['assetContents'][1]['genusTypeId'],
                         str(ALT_TEXT_ASSET_CONTENT_GENUS_TYPE))
        self.assertEqual(
            data['assetContents'][1]['altTexts'][0]['text'],
            new_alt_text
        )
        self.assertEqual(
            data['assetContents'][1]['altText']['text'],
            new_alt_text
        )
        self.assertEqual(
            data['assetContents'][1]['altText']['languageTypeId'],
            self._english_language_type
        )
        self.assertEqual(
            data['assetContents'][1]['altText']['scriptTypeId'],
            self._english_script_type
        )

    def test_can_update_media_description_with_new_language(self):
        self._image_upload_test_file.seek(0)
        media_description = "a bright green dot"
        req = self.app.post(self.url,
                            params={"mediaDescription": media_description},
                            upload_files=[('inputFile', 'green_dot.png', self._image_upload_test_file.read())])
        self.ok(req)
        data = self.json(req)

        url = '{0}/{1}'.format(self.url,
                               data['id'])

        payload = {
            'mediaDescription': self._hindi_text
        }
        req = self.app.put(url,
                           params=json.dumps(payload),
                           headers={'content-type': 'application/json'})
        self.ok(req)
        data = self.json(req)

        self.assertEqual(len(data['assetContents']), 2)
        self.assertEqual(len(data['assetContents'][1]['mediaDescriptions']), 2)
        self.assertEqual(data['assetContents'][1]['genusTypeId'],
                         str(MEDIA_DESCRIPTION_ASSET_CONTENT_GENUS_TYPE))
        self.assertEqual(
            data['assetContents'][1]['mediaDescriptions'][1]['text'],
            self._hindi_text['text']
        )
        self.assertEqual(
            data['assetContents'][1]['mediaDescription']['text'],
            media_description
        )
        self.assertEqual(
            data['assetContents'][1]['mediaDescriptions'][1]['languageTypeId'],
            self._hindi_text['languageTypeId']
        )
        self.assertEqual(
            data['assetContents'][1]['mediaDescriptions'][1]['scriptTypeId'],
            self._hindi_text['scriptTypeId']
        )

    def test_can_update_existing_media_description_language(self):
        self._image_upload_test_file.seek(0)
        media_description = "a bright green dot"
        req = self.app.post(self.url,
                            params={"mediaDescription": media_description},
                            upload_files=[('inputFile', 'green_dot.png', self._image_upload_test_file.read())])
        self.ok(req)
        data = self.json(req)

        url = '{0}/{1}'.format(self.url,
                               data['id'])
        new_media_description = 'a blurry blue dot'
        payload = {
            'mediaDescription': new_media_description
        }
        req = self.app.put(url,
                           params=json.dumps(payload),
                           headers={'content-type': 'application/json'})
        self.ok(req)
        data = self.json(req)

        self.assertEqual(len(data['assetContents']), 2)
        self.assertEqual(len(data['assetContents'][1]['mediaDescriptions']), 1)
        self.assertEqual(data['assetContents'][1]['genusTypeId'],
                         str(MEDIA_DESCRIPTION_ASSET_CONTENT_GENUS_TYPE))
        self.assertEqual(
            data['assetContents'][1]['mediaDescriptions'][0]['text'],
            new_media_description
        )
        self.assertEqual(
            data['assetContents'][1]['mediaDescription']['text'],
            new_media_description
        )
        self.assertEqual(
            data['assetContents'][1]['mediaDescriptions'][0]['languageTypeId'],
            self._english_language_type
        )
        self.assertEqual(
            data['assetContents'][1]['mediaDescriptions'][0]['scriptTypeId'],
            self._english_script_type
        )

    def test_can_remove_alt_text_by_language_type(self):
        self._image_upload_test_file.seek(0)
        alt_text = "a green dot!"
        req = self.app.post(self.url,
                            params={"altText": alt_text},
                            upload_files=[('inputFile', 'green_dot.png', self._image_upload_test_file.read())])
        self.ok(req)
        data = self.json(req)

        url = '{0}/{1}'.format(self.url,
                               data['id'])

        payload = {
            'altText': self._hindi_text
        }
        req = self.app.put(url,
                           params=json.dumps(payload),
                           headers={'content-type': 'application/json'})
        self.ok(req)
        data = self.json(req)

        self.assertEqual(len(data['assetContents']), 2)
        self.assertEqual(len(data['assetContents'][1]['altTexts']), 2)

        payload = {
            'removeAltTextLanguage': self._english_language_type
        }
        req = self.app.put(url,
                           params=json.dumps(payload),
                           headers={'content-type': 'application/json'})
        self.ok(req)
        data = self.json(req)
        self.assertEqual(len(data['assetContents']), 2)
        self.assertEqual(len(data['assetContents'][1]['altTexts']), 1)
        self.assertEqual(data['assetContents'][1]['genusTypeId'],
                         str(ALT_TEXT_ASSET_CONTENT_GENUS_TYPE))
        self.assertEqual(
            data['assetContents'][1]['altTexts'][0]['text'],
            self._hindi_text['text']
        )
        self.assertEqual(
            data['assetContents'][1]['altTexts'][0]['languageTypeId'],
            self._hindi_text['languageTypeId']
        )
        self.assertEqual(
            data['assetContents'][1]['altTexts'][0]['scriptTypeId'],
            self._hindi_text['scriptTypeId']
        )
        self.assertEqual(
            data['assetContents'][1]['altText']['text'],
            self._hindi_text['text']
        )

    def test_can_remove_media_description_by_language_type(self):
        self._image_upload_test_file.seek(0)
        media_description = "a green dot!"
        req = self.app.post(self.url,
                            params={"mediaDescription": media_description},
                            upload_files=[('inputFile', 'green_dot.png', self._image_upload_test_file.read())])
        self.ok(req)
        data = self.json(req)

        url = '{0}/{1}'.format(self.url,
                               data['id'])

        payload = {
            'mediaDescription': self._hindi_text
        }
        req = self.app.put(url,
                           params=json.dumps(payload),
                           headers={'content-type': 'application/json'})
        self.ok(req)
        data = self.json(req)

        self.assertEqual(len(data['assetContents']), 2)
        self.assertEqual(len(data['assetContents'][1]['mediaDescriptions']), 2)

        payload = {
            'removeMediaDescriptionLanguage': self._english_language_type
        }
        req = self.app.put(url,
                           params=json.dumps(payload),
                           headers={'content-type': 'application/json'})
        self.ok(req)
        data = self.json(req)
        self.assertEqual(len(data['assetContents']), 2)
        self.assertEqual(len(data['assetContents'][1]['mediaDescriptions']), 1)
        self.assertEqual(data['assetContents'][1]['genusTypeId'],
                         str(MEDIA_DESCRIPTION_ASSET_CONTENT_GENUS_TYPE))
        self.assertEqual(
            data['assetContents'][1]['mediaDescriptions'][0]['text'],
            self._hindi_text['text']
        )
        self.assertEqual(
            data['assetContents'][1]['mediaDescriptions'][0]['languageTypeId'],
            self._hindi_text['languageTypeId']
        )
        self.assertEqual(
            data['assetContents'][1]['mediaDescriptions'][0]['scriptTypeId'],
            self._hindi_text['scriptTypeId']
        )
        self.assertEqual(
            data['assetContents'][1]['mediaDescription']['text'],
            self._hindi_text['text']
        )

    def test_can_clear_all_alt_texts(self):
        self._image_upload_test_file.seek(0)
        alt_text = "a green dot!"
        req = self.app.post(self.url,
                            params={"altText": alt_text},
                            upload_files=[('inputFile', 'green_dot.png', self._image_upload_test_file.read())])
        self.ok(req)
        data = self.json(req)
        self.assertEqual(len(data['assetContents']), 2)
        self.assertEqual(len(data['assetContents'][1]['altTexts']), 1)

        payload = {
            'clearAltTexts': False
        }
        url = '{0}/{1}'.format(self.url,
                               data['id'])
        req = self.app.put(url,
                           params=json.dumps(payload),
                           headers={'content-type': 'application/json'})
        self.ok(req)
        data = self.json(req)
        self.assertEqual(len(data['assetContents']), 2)
        self.assertEqual(len(data['assetContents'][1]['altTexts']), 1)

        payload = {
            'clearAltTexts': True
        }
        req = self.app.put(url,
                           params=json.dumps(payload),
                           headers={'content-type': 'application/json'})
        self.ok(req)
        data = self.json(req)
        self.assertEqual(len(data['assetContents']), 2)
        self.assertEqual(len(data['assetContents'][1]['altTexts']), 0)

    def test_can_clear_all_media_descriptions(self):
        self._image_upload_test_file.seek(0)
        media_description = "a green dot!"
        req = self.app.post(self.url,
                            params={"mediaDescription": media_description},
                            upload_files=[('inputFile', 'green_dot.png', self._image_upload_test_file.read())])
        self.ok(req)
        data = self.json(req)
        self.assertEqual(len(data['assetContents']), 2)
        self.assertEqual(len(data['assetContents'][1]['mediaDescriptions']), 1)

        payload = {
            'clearMediaDescriptions': False
        }
        url = '{0}/{1}'.format(self.url,
                               data['id'])
        req = self.app.put(url,
                           params=json.dumps(payload),
                           headers={'content-type': 'application/json'})
        self.ok(req)
        data = self.json(req)
        self.assertEqual(len(data['assetContents']), 2)
        self.assertEqual(len(data['assetContents'][1]['mediaDescriptions']), 1)

        payload = {
            'clearMediaDescriptions': True
        }
        req = self.app.put(url,
                           params=json.dumps(payload),
                           headers={'content-type': 'application/json'})
        self.ok(req)
        data = self.json(req)
        self.assertEqual(len(data['assetContents']), 2)
        self.assertEqual(len(data['assetContents'][1]['mediaDescriptions']), 0)

    def test_image_alt_tag_shows_up_in_requested_language(self):
        self._image_upload_test_file.seek(0)
        alt_text = "a green dot!"
        req = self.app.post(self.url,
                            params={"altText": alt_text},
                            upload_files=[('inputFile', 'green_dot.png', self._image_upload_test_file.read())])
        self.ok(req)
        data = self.json(req)

        url = '{0}/{1}'.format(self.url,
                               data['id'])

        payload = {
            'altText': self._hindi_text
        }
        req = self.app.put(url,
                           params=json.dumps(payload),
                           headers={'content-type': 'application/json'})
        self.ok(req)
        data = self.json(req)

        self.assertEqual(len(data['assetContents']), 2)
        self.assertEqual(len(data['assetContents'][1]['altTexts']), 2)

        # Now put this into an Item, so that we can see if the alt-text gets added
        item = self.create_mc_item_with_image(data)

        url = '/api/v1/assessment/banks/{0}/items/{1}'.format(str(self._repo.ident),
                                                              item['id'])
        req = self.app.get(url)
        self.ok(req)
        data = self.json(req)

        self.assertIn('a green dot!',
                      data['question']['multiLanguageChoices'][0]['texts'][0]['text'])
        self.assertNotIn(self._hindi_text['text'],
                         data['question']['multiLanguageChoices'][0]['texts'][0]['text'])

        req = self.app.get(url,
                           headers={'x-api-locale': 'hi'})
        self.ok(req)
        data = self.json(req)

        self.assertNotIn('a green dot!',
                         data['question']['multiLanguageChoices'][0]['texts'][0]['text'])
        self.assertIn(self._hindi_text['text'],
                      data['question']['multiLanguageChoices'][0]['texts'][0]['text'])

    def test_can_send_vtt_file_on_asset_create(self):
        self._video_upload_test_file.seek(0)
        self._caption_upload_test_file.seek(0)
        req = self.app.post(self.url,
                            upload_files=[('inputFile', 'video-js-test.mp4', self._video_upload_test_file.read()),
                                          ('vttFile', 'video-js-test-en.vtt', self._caption_upload_test_file.read())])
        self.ok(req)
        data = self.json(req)
        self.assertEqual(len(data['assetContents']), 2)
        self.assertEqual(len(data['assetContents'][1]['fileIds']), 1)
        self.assertEqual(
            data['assetContents'][1]['fileIds'].keys()[0],
            'ENG'
        )
        vtt_files = data['assetContents'][1]['fileIds']['ENG']
        self.assertIn('assetId', vtt_files)
        self.assertIn('assetContentId', vtt_files)
        self.assertIn('assetContentTypeId', vtt_files)
        self.assertEqual(
            data['assetContents'][1]['genusTypeId'],
            str(VTT_FILE_ASSET_CONTENT_GENUS_TYPE)
        )

    def test_can_send_transcript_file_on_asset_create(self):
        self.fail('finish writing the test')

    def test_can_set_vtt_file_locale_on_asset_create(self):
        self._video_upload_test_file.seek(0)
        self._caption_upload_test_file.seek(0)
        req = self.app.post(self.url,
                            params={'locale': 'hi'},
                            upload_files=[('inputFile', 'video-js-test.mp4', self._video_upload_test_file.read()),
                                          ('vttFile', 'video-js-test-en.vtt', self._caption_upload_test_file.read())])
        self.ok(req)
        data = self.json(req)
        self.assertEqual(len(data['assetContents']), 2)
        self.assertEqual(len(data['assetContents'][1]['fileIds']), 1)
        self.assertEqual(
            data['assetContents'][1]['fileIds'].keys()[0],
            'HIN'
        )
        vtt_files = data['assetContents'][1]['fileIds']['HIN']
        self.assertIn('assetId', vtt_files)
        self.assertIn('assetContentId', vtt_files)
        self.assertIn('assetContentTypeId', vtt_files)
        self.assertEqual(
            data['assetContents'][1]['genusTypeId'],
            str(VTT_FILE_ASSET_CONTENT_GENUS_TYPE)
        )

    def test_can_set_transcript_file_locale_on_asset_create(self):
        self.fail('finish writing the test')

    def test_can_update_vtt_file_with_new_language(self):
        self.fail('finsih writing the test')

    def test_can_update_transcript_file_with_new_language(self):
        self.fail("finish writing the test")

    def test_can_replace_existing_vtt_file_language(self):
        self.fail('finish writing the test')

    def test_can_replace_existing_transcript_file_language(self):
        self.fail("finish writing the test")

    def test_can_clear_all_transcript_files(self):
        self.fail('finish writign the test')

    def test_can_clear_all_vtt_files(self):
        self._video_upload_test_file.seek(0)
        self._caption_upload_test_file.seek(0)
        req = self.app.post(self.url,
                            params={'locale': 'hi'},
                            upload_files=[('inputFile', 'video-js-test.mp4', self._video_upload_test_file.read()),
                                          ('vttFile', 'video-js-test-en.vtt', self._caption_upload_test_file.read())])
        self.ok(req)
        data = self.json(req)
        self.assertEqual(len(data['assetContents']), 2)
        self.assertEqual(len(data['assetContents'][1]['fileIds']), 1)

        payload = {
            'clearVTTFiles': False
        }

        url = '{0}/{1}'.format(self.url,
                               data['id'])
        req = self.app.put(url,
                           params=json.dumps(payload),
                           headers={'content-type': 'application/json'})
        self.ok(req)
        data = self.json(req)
        self.assertEqual(len(data['assetContents']), 2)
        self.assertEqual(len(data['assetContents'][1]['fileIds']), 1)

        payload = {
            'clearVTTFiles': True
        }

        url = '{0}/{1}'.format(self.url,
                               data['id'])
        req = self.app.put(url,
                           params=json.dumps(payload),
                           headers={'content-type': 'application/json'})
        self.ok(req)
        data = self.json(req)
        self.assertEqual(len(data['assetContents']), 2)
        self.assertEqual(len(data['assetContents'][1]['fileIds']), 0)

    def test_can_remove_vtt_file_by_language(self):
        self.fail('finish writing the test')

    def test_can_remove_transcript_file_by_language(self):
        self.fail('finish writing the test')

    def test_video_caption_track_shows_up_in_requested_language(self):
        self.fail('finish writing the test')

    def test_audio_transcript_shows_up_in_requested_language(self):
        self.fail('finish writing the test')

    def test_video_transcript_shows_up_in_requested_language(self):
        self.fail('finish writing the test')
