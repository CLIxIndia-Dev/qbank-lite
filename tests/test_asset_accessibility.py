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
TRANSCRIPT_FILE_ASSET_CONTENT_GENUS_TYPE = Type(**ASSET_CONTENT_GENUS_TYPES['transcript'])


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
    def clear_alt_texts(self, data, value):
        payload = {
            'clearAltTexts': value
        }

        url = '{0}/{1}'.format(self.url,
                               data['id'])
        req = self.app.put(url,
                           params=json.dumps(payload),
                           headers={'content-type': 'application/json'})
        self.ok(req)
        return self.json(req)

    def clear_media_descriptions(self, data, value):
        payload = {
            'clearMediaDescriptions': value
        }

        url = '{0}/{1}'.format(self.url,
                               data['id'])
        req = self.app.put(url,
                           params=json.dumps(payload),
                           headers={'content-type': 'application/json'})
        self.ok(req)
        return self.json(req)

    def clear_transcript_files(self, data, value):
        payload = {
            'clearTranscriptFiles': value
        }

        url = '{0}/{1}'.format(self.url,
                               data['id'])
        req = self.app.put(url,
                           params=json.dumps(payload),
                           headers={'content-type': 'application/json'})
        self.ok(req)
        return self.json(req)

    def clear_vtt_files(self, data, value):
        payload = {
            'clearVTTFiles': value
        }

        url = '{0}/{1}'.format(self.url,
                               data['id'])
        req = self.app.put(url,
                           params=json.dumps(payload),
                           headers={'content-type': 'application/json'})
        self.ok(req)
        return self.json(req)

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

    def create_mc_item_with_video(self, asset, vtt_blank=False):
        url = '/api/v1/assessment/banks/{0}/items'.format(str(self._repo.ident))

        choice_text = """<simpleChoice identifier="idc561552b-ed48-46c3-b20d-873150dfd4a2">
<p>
  <video width="640" height="480" controls>
    <source src="AssetContent:cat_mp4" />
    <track src="AssetContent:vtt_file_vtt" kind="subtitles" srclang="en" label="English" />
  </video>
</p>
</simpleChoice>"""

        if vtt_blank:
            choice_text = """<simpleChoice identifier="idc561552b-ed48-46c3-b20d-873150dfd4a2">
<p>
  <video width="640" height="480" controls>
    <source src="AssetContent:cat_mp4" />
    <track src="" kind="subtitles" srclang="en" label="English" />
  </video>
</p>
</simpleChoice>"""

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
                    "text": choice_text}, {
                    "id": "ida86a26e0-a563-4e48-801a-ba9d171c24f7",
                    "text": """<simpleChoice identifier="ida86a26e0-a563-4e48-801a-ba9d171c24f7">
<p>|__|</p>
</simpleChoice>"""
                }],
                "genusTypeId": str(QTI_QUESTION_CHOICE_INTERACTION_GENUS),
                "shuffle": True,
                "fileIds": {
                    'cat_mp4': {
                        'assetId': asset['id'],
                        'assetContentId': asset['assetContents'][0]['id'],
                        'assetContentTypeId': asset['assetContents'][0]['genusTypeId']
                    },
                    'vtt_file_vtt': {
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

    def create_mc_item_with_video_and_transcript(self, asset, transcript_blank=False):
        url = '/api/v1/assessment/banks/{0}/items'.format(str(self._repo.ident))

        choice_text = """<simpleChoice identifier="idc561552b-ed48-46c3-b20d-873150dfd4a2">
<p>
  <video width="640" height="480" controls>
    <source src="AssetContent:cat_mp4" />
    <track src="AssetContent:vtt_file_vtt" kind="subtitles" srclang="en" label="English" />
  </video>
  <transcript src="AssetContent:transcript_txt" />
</p>
</simpleChoice>"""

        if transcript_blank:
            choice_text = """<simpleChoice identifier="idc561552b-ed48-46c3-b20d-873150dfd4a2">
<p>
  <video width="640" height="480" controls>
    <source src="AssetContent:cat_mp4" />
    <track src="AssetContent:vtt_file_vtt" kind="subtitles" srclang="en" label="English" />
  </video>
  <transcript src="" />
</p>
</simpleChoice>"""

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
                    "text": choice_text
                }, {
                    "id": "ida86a26e0-a563-4e48-801a-ba9d171c24f7",
                    "text": """<simpleChoice identifier="ida86a26e0-a563-4e48-801a-ba9d171c24f7">
<p>|__|</p>
</simpleChoice>"""
                }],
                "genusTypeId": str(QTI_QUESTION_CHOICE_INTERACTION_GENUS),
                "shuffle": True,
                "fileIds": {
                    'cat_mp4': {
                        'assetId': asset['id'],
                        'assetContentId': asset['assetContents'][0]['id'],
                        'assetContentTypeId': asset['assetContents'][0]['genusTypeId']
                    },
                    'vtt_file_vtt': {
                        'assetId': asset['id'],
                        'assetContentId': asset['assetContents'][1]['id'],
                        'assetContentTypeId': asset['assetContents'][1]['genusTypeId']
                    },
                    'transcript_txt': {
                        'assetId': asset['id'],
                        'assetContentId': asset['assetContents'][2]['id'],
                        'assetContentTypeId': asset['assetContents'][2]['genusTypeId']
                    }
                }
            },
            "answers": []
        }

        return self.json(self.app.post(url,
                                       params=json.dumps(payload),
                                       headers={'content-type': 'application/json'}))

    def create_mc_item_with_audio(self, asset):
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
  <audio controls>
    <source src="AssetContent:cat_mp3" />
    <p>Description</p>
  </audio>
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
                    'cat_mp3': {
                        'assetId': asset['id'],
                        'assetContentId': asset['assetContents'][0]['id'],
                        'assetContentTypeId': asset['assetContents'][0]['genusTypeId']
                    }
                }
            },
            "answers": []
        }

        return self.json(self.app.post(url,
                                       params=json.dumps(payload),
                                       headers={'content-type': 'application/json'}))

    def create_mc_item_with_audio_and_transcript(self, asset, transcript_blank=False):
        url = '/api/v1/assessment/banks/{0}/items'.format(str(self._repo.ident))

        choice_text = """<simpleChoice identifier="idc561552b-ed48-46c3-b20d-873150dfd4a2">
<p>
  <audio controls>
    <source src="AssetContent:cat_mp3" />
    <p>Description</p>
  </audio>
  <transcript src="AssetContent:transcript_txt" />
</p>
</simpleChoice>"""

        if transcript_blank:
            choice_text = """<simpleChoice identifier="idc561552b-ed48-46c3-b20d-873150dfd4a2">
<p>
  <audio controls>
    <source src="AssetContent:cat_mp3" />
    <p>Description</p>
  </audio>
  <transcript src="" />
</p>
</simpleChoice>"""

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
                    "text": choice_text
                }, {
                    "id": "ida86a26e0-a563-4e48-801a-ba9d171c24f7",
                    "text": """<simpleChoice identifier="ida86a26e0-a563-4e48-801a-ba9d171c24f7">
<p>|__|</p>
</simpleChoice>"""
                }],
                "genusTypeId": str(QTI_QUESTION_CHOICE_INTERACTION_GENUS),
                "shuffle": True,
                "fileIds": {
                    'cat_mp3': {
                        'assetId': asset['id'],
                        'assetContentId': asset['assetContents'][0]['id'],
                        'assetContentTypeId': asset['assetContents'][0]['genusTypeId']
                    },
                    'transcript_txt': {
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

    def remove_alt_text_language(self, data, locale):
        url = '{0}/{1}'.format(self.url,
                               data['id'])

        language_type = self._english_language_type
        if locale == 'hi':
            language_type = self._hindi_text['languageTypeId']

        payload = {
            'removeAltTextLanguage': language_type
        }
        req = self.app.put(url,
                           params=json.dumps(payload),
                           headers={'content-type': 'application/json'})
        self.ok(req)
        return self.json(req)

    def remove_media_description_language(self, data, locale):
        url = '{0}/{1}'.format(self.url,
                               data['id'])

        language_type = self._english_language_type
        if locale == 'hi':
            language_type = self._hindi_text['languageTypeId']

        payload = {
            'removeMediaDescriptionLanguage': language_type
        }
        req = self.app.put(url,
                           params=json.dumps(payload),
                           headers={'content-type': 'application/json'})
        self.ok(req)
        return self.json(req)

    def remove_transcript_language(self, data, locale):
        url = '{0}/{1}'.format(self.url,
                               data['id'])

        language_type = self._english_language_type
        if locale == 'hi':
            language_type = self._hindi_text['languageTypeId']

        payload = {
            'removeTranscriptFileLanguage': language_type
        }
        req = self.app.put(url,
                           params=json.dumps(payload),
                           headers={'content-type': 'application/json'})
        self.ok(req)
        return self.json(req)

    def remove_vtt_language(self, data, locale):
        url = '{0}/{1}'.format(self.url,
                               data['id'])

        language_type = self._english_language_type
        if locale == 'hi':
            language_type = self._hindi_text['languageTypeId']

        payload = {
            'removeVTTFileLanguage': language_type
        }
        req = self.app.put(url,
                           params=json.dumps(payload),
                           headers={'content-type': 'application/json'})
        self.ok(req)
        return self.json(req)

    def setUp(self):
        super(AssetAccessibilityCRUDTests, self).setUp()
        self.url = '{0}/repositories/{1}/assets'.format(self.url,
                                                        unquote(str(self._repo.ident)))

        self._video_upload_test_file = open('{0}/tests/files/video-js-test.mp4'.format(ABS_PATH), 'r')
        self._audio_upload_test_file = open('{0}/tests/files/audioTestFile_.mp3'.format(ABS_PATH), 'r')
        self._caption_upload_test_file = open('{0}/tests/files/video-js-test-en.vtt'.format(ABS_PATH), 'r')
        self._caption_hi_upload_test_file = open('{0}/tests/files/video-js-test-hi.vtt'.format(ABS_PATH), 'r')
        self._caption_te_upload_test_file = open('{0}/tests/files/video-js-test-te.vtt'.format(ABS_PATH), 'r')
        self._image_upload_test_file = open('{0}/tests/files/green_dot.png'.format(ABS_PATH), 'r')
        self._transcript_test_file = open('{0}/tests/files/transcript.txt'.format(ABS_PATH), 'r')
        self._transcript_hi_test_file = open('{0}/tests/files/transcript_hi.txt'.format(ABS_PATH), 'r')
        self._transcript_te_test_file = open('{0}/tests/files/transcript_te.txt'.format(ABS_PATH), 'r')

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
        self._audio_upload_test_file.close()
        self._caption_upload_test_file.close()
        self._caption_hi_upload_test_file.close()
        self._caption_te_upload_test_file.close()
        self._image_upload_test_file.close()
        self._transcript_test_file.close()
        self._transcript_hi_test_file.close()
        self._transcript_te_test_file.close()

    def upload_audio_with_transcripts(self):
        self._audio_upload_test_file.seek(0)
        self._transcript_test_file.seek(0)
        req = self.app.post(self.url,
                            upload_files=[('inputFile', self._filename(self._audio_upload_test_file), self._audio_upload_test_file.read()),
                                          ('transcriptFile', 'transcript.txt', self._transcript_test_file.read())])
        self.ok(req)
        data = self.json(req)
        self.assertEqual(len(data['assetContents']), 2)
        self.assertEqual(len(data['assetContents'][1]['fileIds']), 1)

        self._transcript_hi_test_file.seek(0)
        url = '{0}/{1}'.format(self.url,
                               data['id'])
        req = self.app.put(url,
                           params={'locale': 'hi'},
                           upload_files=[('transcriptFile', 'transcript_hi.txt', self._transcript_hi_test_file.read())])
        self.ok(req)
        data = self.json(req)
        self.assertEqual(len(data['assetContents']), 2)
        self.assertEqual(len(data['assetContents'][1]['fileIds']), 2)

        self._transcript_te_test_file.seek(0)
        req = self.app.put(url,
                           params={'locale': 'te'},
                           upload_files=[('transcriptFile', 'transcript_te.txt', self._transcript_te_test_file.read())])
        self.ok(req)
        data = self.json(req)
        self.assertEqual(len(data['assetContents']), 2)
        self.assertEqual(len(data['assetContents'][1]['fileIds']), 3)
        return data

    def upload_image_with_hindi_alt_text(self):
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
        return data

    def upload_video_with_captions(self):
        self._video_upload_test_file.seek(0)
        self._caption_upload_test_file.seek(0)
        req = self.app.post(self.url,
                            upload_files=[('inputFile', 'video-js-test.mp4', self._video_upload_test_file.read()),
                                          ('vttFile', 'video-js-test-en.vtt', self._caption_upload_test_file.read())])
        self.ok(req)
        data = self.json(req)
        self.assertEqual(len(data['assetContents']), 2)
        self.assertEqual(len(data['assetContents'][1]['fileIds']), 1)

        self._caption_hi_upload_test_file.seek(0)
        url = '{0}/{1}'.format(self.url,
                               data['id'])
        req = self.app.put(url,
                           params={'locale': 'hi'},
                           upload_files=[('vttFile', 'video-js-test-hi.vtt', self._caption_hi_upload_test_file.read())])
        self.ok(req)
        data = self.json(req)
        self.assertEqual(len(data['assetContents']), 2)
        self.assertEqual(len(data['assetContents'][1]['fileIds']), 2)

        self._caption_te_upload_test_file.seek(0)
        req = self.app.put(url,
                           params={'locale': 'te'},
                           upload_files=[('vttFile', 'video-js-test-te.vtt', self._caption_te_upload_test_file.read())])
        self.ok(req)
        data = self.json(req)
        self.assertEqual(len(data['assetContents']), 2)
        self.assertEqual(len(data['assetContents'][1]['fileIds']), 3)
        return data

    def upload_video_with_caption_and_transcripts(self):
        self._video_upload_test_file.seek(0)
        self._caption_upload_test_file.seek(0)
        self._transcript_test_file.seek(0)
        req = self.app.post(self.url,
                            upload_files=[('inputFile', 'video-js-test.mp4', self._video_upload_test_file.read()),
                                          ('vttFile', 'video-js-test-en.vtt', self._caption_upload_test_file.read()),
                                          ('transcriptFile', 'transcript.txt', self._transcript_test_file.read())])
        self.ok(req)
        data = self.json(req)
        self.assertEqual(len(data['assetContents']), 3)
        self.assertEqual(len(data['assetContents'][2]['fileIds']), 1)

        self._transcript_hi_test_file.seek(0)
        url = '{0}/{1}'.format(self.url,
                               data['id'])
        req = self.app.put(url,
                           params={'locale': 'hi'},
                           upload_files=[('transcriptFile', 'transcript_hi.txt', self._transcript_hi_test_file.read())])
        self.ok(req)
        data = self.json(req)
        self.assertEqual(len(data['assetContents']), 3)
        self.assertEqual(len(data['assetContents'][2]['fileIds']), 2)

        self._transcript_te_test_file.seek(0)
        req = self.app.put(url,
                           params={'locale': 'te'},
                           upload_files=[('transcriptFile', 'transcript_te.txt', self._transcript_te_test_file.read())])
        self.ok(req)
        data = self.json(req)
        self.assertEqual(len(data['assetContents']), 3)
        self.assertEqual(len(data['assetContents'][2]['fileIds']), 3)
        return data

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

    def test_can_create_asset_with_multi_language_media_description_in_form(self):
        self._image_upload_test_file.seek(0)
        req = self.app.post(self.url,
                            params={"mediaDescription": json.dumps(self._hindi_text)},
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
            self._hindi_text['text']
        )
        self.assertEqual(
            data['assetContents'][1]['mediaDescription']['text'],
            self._hindi_text['text']
        )
        self.assertEqual(
            data['assetContents'][1]['mediaDescription']['languageTypeId'],
            self._hindi_text['languageTypeId']
        )
        self.assertEqual(
            data['assetContents'][1]['mediaDescription']['scriptTypeId'],
            self._hindi_text['scriptTypeId']
        )
        self.assertEqual(
            data['assetContents'][1]['genusTypeId'],
            str(MEDIA_DESCRIPTION_ASSET_CONTENT_GENUS_TYPE)
        )

    def test_can_create_asset_with_multi_language_alt_text_in_form(self):
        self._image_upload_test_file.seek(0)
        req = self.app.post(self.url,
                            params={"altText": json.dumps(self._hindi_text)},
                            upload_files=[('inputFile', 'green_dot.png', self._image_upload_test_file.read())])
        self.ok(req)
        data = self.json(req)
        self.assertEqual(len(data['assetContents']), 2)
        self.assertEqual(
            len(data['assetContents'][1]['altTexts']),
            1
        )
        self.assertEqual(
            data['assetContents'][1]['altTexts'][0]['text'],
            self._hindi_text['text']
        )
        self.assertEqual(
            data['assetContents'][1]['altText']['text'],
            self._hindi_text['text']
        )
        self.assertEqual(
            data['assetContents'][1]['altText']['languageTypeId'],
            self._hindi_text['languageTypeId']
        )
        self.assertEqual(
            data['assetContents'][1]['altText']['scriptTypeId'],
            self._hindi_text['scriptTypeId']
        )
        self.assertEqual(
            data['assetContents'][1]['genusTypeId'],
            str(ALT_TEXT_ASSET_CONTENT_GENUS_TYPE)
        )

    def test_can_update_alt_text_with_new_language(self):
        data = self.upload_image_with_hindi_alt_text()

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
            'a green dot!'
        )

    def test_can_update_alt_text_with_new_language_in_form(self):
        self._image_upload_test_file.seek(0)
        alt_text = "a green dot!"
        req = self.app.post(self.url,
                            params={"altText": alt_text},
                            upload_files=[('inputFile', 'green_dot.png', self._image_upload_test_file.read())])
        self.ok(req)
        data = self.json(req)

        url = '{0}/{1}'.format(self.url,
                               data['id'])

        req = self.app.put(url,
                           params={'altText': json.dumps(self._hindi_text)})
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
            'a green dot!'
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

    def test_can_update_media_description_with_new_language_in_form(self):
        self._image_upload_test_file.seek(0)
        media_description = "a bright green dot"
        req = self.app.post(self.url,
                            params={"mediaDescription": media_description},
                            upload_files=[('inputFile', 'green_dot.png', self._image_upload_test_file.read())])
        self.ok(req)
        data = self.json(req)

        url = '{0}/{1}'.format(self.url,
                               data['id'])

        req = self.app.put(url,
                           params={'mediaDescription': json.dumps(self._hindi_text)})
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
        data = self.upload_image_with_hindi_alt_text()

        self.assertEqual(len(data['assetContents']), 2)
        self.assertEqual(len(data['assetContents'][1]['altTexts']), 2)

        data = self.remove_alt_text_language(data, 'en')
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

        data = self.remove_media_description_language(data, 'en')
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

        data = self.clear_alt_texts(data, False)
        self.assertEqual(len(data['assetContents']), 2)
        self.assertEqual(len(data['assetContents'][1]['altTexts']), 1)

        data = self.clear_alt_texts(data, True)
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

        data = self.clear_media_descriptions(data, False)
        self.assertEqual(len(data['assetContents']), 2)
        self.assertEqual(len(data['assetContents'][1]['mediaDescriptions']), 1)

        data = self.clear_media_descriptions(data, True)
        self.assertEqual(len(data['assetContents']), 2)
        self.assertEqual(len(data['assetContents'][1]['mediaDescriptions']), 0)

    def test_image_alt_tag_shows_up_in_requested_language(self):
        data = self.upload_image_with_hindi_alt_text()

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

    def test_image_alt_tag_empty_string_if_none_exist(self):
        data = self.upload_image_with_hindi_alt_text()
        self.clear_alt_texts(data, True)
        item = self.create_mc_item_with_image(data)

        url = '/api/v1/assessment/banks/{0}/items/{1}'.format(str(self._repo.ident),
                                                              item['id'])
        req = self.app.get(url,
                           headers={'x-api-locale': 'hi'})
        self.ok(req)
        data = self.json(req)

        choice_text = data['question']['multiLanguageChoices'][0]['texts'][0]['text']
        self.assertIn('alt=""', choice_text)
        self.assertNotIn('a green dot!', choice_text)
        self.assertNotIn(self._hindi_text['text'], choice_text)

    def test_image_alt_tag_defaults_eng_if_requested_lang_not_exist(self):
        data = self.upload_image_with_hindi_alt_text()
        data = self.remove_alt_text_language(data, 'hi')
        item = self.create_mc_item_with_image(data)

        url = '/api/v1/assessment/banks/{0}/items/{1}'.format(str(self._repo.ident),
                                                              item['id'])
        req = self.app.get(url,
                           headers={'x-api-locale': 'hi'})
        self.ok(req)
        data = self.json(req)

        self.assertIn('a green dot!',
                      data['question']['multiLanguageChoices'][0]['texts'][0]['text'])
        self.assertNotIn(self._hindi_text['text'],
                         data['question']['multiLanguageChoices'][0]['texts'][0]['text'])

    def test_image_alt_tag_uses_first_available_if_default_lang_not_exist(self):
        data = self.upload_image_with_hindi_alt_text()
        data = self.remove_alt_text_language(data, 'en')
        item = self.create_mc_item_with_image(data)

        url = '/api/v1/assessment/banks/{0}/items/{1}'.format(str(self._repo.ident),
                                                              item['id'])
        req = self.app.get(url)
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
        self._video_upload_test_file.seek(0)
        self._transcript_test_file.seek(0)
        req = self.app.post(self.url,
                            upload_files=[('inputFile', 'video-js-test.mp4', self._video_upload_test_file.read()),
                                          ('transcriptFile', 'transcript.txt', self._transcript_test_file.read())])
        self.ok(req)
        data = self.json(req)
        self.assertEqual(len(data['assetContents']), 2)
        self.assertEqual(len(data['assetContents'][1]['fileIds']), 1)
        self.assertEqual(
            data['assetContents'][1]['fileIds'].keys()[0],
            'ENG'
        )
        transcript_files = data['assetContents'][1]['fileIds']['ENG']
        self.assertIn('assetId', transcript_files)
        self.assertIn('assetContentId', transcript_files)
        self.assertIn('assetContentTypeId', transcript_files)
        self.assertEqual(
            data['assetContents'][1]['genusTypeId'],
            str(TRANSCRIPT_FILE_ASSET_CONTENT_GENUS_TYPE)
        )

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
        self._video_upload_test_file.seek(0)
        self._transcript_test_file.seek(0)
        req = self.app.post(self.url,
                            params={'locale': 'hi'},
                            upload_files=[('inputFile', 'video-js-test.mp4', self._video_upload_test_file.read()),
                                          ('transcriptFile', 'transcript.txt', self._transcript_test_file.read())])
        self.ok(req)
        data = self.json(req)
        self.assertEqual(len(data['assetContents']), 2)
        self.assertEqual(len(data['assetContents'][1]['fileIds']), 1)
        self.assertEqual(
            data['assetContents'][1]['fileIds'].keys()[0],
            'HIN'
        )
        transcript_files = data['assetContents'][1]['fileIds']['HIN']
        self.assertIn('assetId', transcript_files)
        self.assertIn('assetContentId', transcript_files)
        self.assertIn('assetContentTypeId', transcript_files)
        self.assertEqual(
            data['assetContents'][1]['genusTypeId'],
            str(TRANSCRIPT_FILE_ASSET_CONTENT_GENUS_TYPE)
        )

    def test_can_add_vtt_file_with_new_language(self):
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

        self._caption_upload_test_file.seek(0)
        url = '{0}/{1}'.format(self.url,
                               data['id'])
        req = self.app.put(url,
                           params={'locale': 'hi'},
                           upload_files=[('vttFile', 'video-js-test-hi.vtt', self._caption_upload_test_file.read())])
        self.ok(req)
        data = self.json(req)
        self.assertEqual(len(data['assetContents']), 2)
        self.assertEqual(len(data['assetContents'][1]['fileIds']), 2)

        self.assertEqual(
            data['assetContents'][1]['fileIds'].keys()[0],
            'HIN'
        )
        self.assertEqual(
            data['assetContents'][1]['fileIds'].keys()[1],
            'ENG'
        )
        vtt_files = data['assetContents'][1]['fileIds']['HIN']
        self.assertIn('assetId', vtt_files)
        self.assertIn('assetContentId', vtt_files)
        self.assertIn('assetContentTypeId', vtt_files)
        vtt_files = data['assetContents'][1]['fileIds']['ENG']
        self.assertIn('assetId', vtt_files)
        self.assertIn('assetContentId', vtt_files)
        self.assertIn('assetContentTypeId', vtt_files)
        self.assertEqual(
            data['assetContents'][1]['genusTypeId'],
            str(VTT_FILE_ASSET_CONTENT_GENUS_TYPE)
        )

    def test_can_update_transcript_file_with_new_language(self):
        self._video_upload_test_file.seek(0)
        self._transcript_test_file.seek(0)
        req = self.app.post(self.url,
                            upload_files=[('inputFile', 'video-js-test.mp4', self._video_upload_test_file.read()),
                                          ('transcriptFile', 'transcript.txt', self._transcript_test_file.read())])
        self.ok(req)
        data = self.json(req)
        self.assertEqual(len(data['assetContents']), 2)
        self.assertEqual(len(data['assetContents'][1]['fileIds']), 1)
        self.assertEqual(
            data['assetContents'][1]['fileIds'].keys()[0],
            'ENG'
        )

        self._caption_upload_test_file.seek(0)
        url = '{0}/{1}'.format(self.url,
                               data['id'])
        req = self.app.put(url,
                           params={'locale': 'hi'},
                           upload_files=[('transcriptFile', 'transcript.txt', self._transcript_test_file.read())])
        self.ok(req)
        data = self.json(req)
        self.assertEqual(len(data['assetContents']), 2)
        self.assertEqual(len(data['assetContents'][1]['fileIds']), 2)

        self.assertEqual(
            data['assetContents'][1]['fileIds'].keys()[0],
            'HIN'
        )
        self.assertEqual(
            data['assetContents'][1]['fileIds'].keys()[1],
            'ENG'
        )
        transcript_files = data['assetContents'][1]['fileIds']['HIN']
        self.assertIn('assetId', transcript_files)
        self.assertIn('assetContentId', transcript_files)
        self.assertIn('assetContentTypeId', transcript_files)
        transcript_files = data['assetContents'][1]['fileIds']['ENG']
        self.assertIn('assetId', transcript_files)
        self.assertIn('assetContentId', transcript_files)
        self.assertIn('assetContentTypeId', transcript_files)
        self.assertEqual(
            data['assetContents'][1]['genusTypeId'],
            str(TRANSCRIPT_FILE_ASSET_CONTENT_GENUS_TYPE)
        )

    def test_can_replace_existing_vtt_file_language(self):
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
        original_asset_id = data['assetContents'][1]['fileIds']['ENG']['assetId']

        self._caption_upload_test_file.seek(0)
        url = '{0}/{1}'.format(self.url,
                               data['id'])
        req = self.app.put(url,
                           upload_files=[('vttFile', 'video-js-test-hi.vtt', self._caption_upload_test_file.read())])
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
        self.assertNotEqual(vtt_files['assetId'], original_asset_id)
        self.assertIn('assetContentId', vtt_files)
        self.assertIn('assetContentTypeId', vtt_files)
        self.assertEqual(
            data['assetContents'][1]['genusTypeId'],
            str(VTT_FILE_ASSET_CONTENT_GENUS_TYPE)
        )

    def test_can_replace_existing_transcript_file_language(self):
        self._video_upload_test_file.seek(0)
        self._transcript_test_file.seek(0)
        req = self.app.post(self.url,
                            upload_files=[('inputFile', 'video-js-test.mp4', self._video_upload_test_file.read()),
                                          ('transcriptFile', 'transcript.txt', self._transcript_test_file.read())])
        self.ok(req)
        data = self.json(req)
        self.assertEqual(len(data['assetContents']), 2)
        self.assertEqual(len(data['assetContents'][1]['fileIds']), 1)
        self.assertEqual(
            data['assetContents'][1]['fileIds'].keys()[0],
            'ENG'
        )
        original_asset_id = data['assetContents'][1]['fileIds']['ENG']['assetId']

        self._caption_upload_test_file.seek(0)
        url = '{0}/{1}'.format(self.url,
                               data['id'])
        req = self.app.put(url,
                           upload_files=[('transcriptFile', 'transcript.txt', self._transcript_test_file.read())])
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
        self.assertNotEqual(vtt_files['assetId'], original_asset_id)
        self.assertIn('assetContentId', vtt_files)
        self.assertIn('assetContentTypeId', vtt_files)
        self.assertEqual(
            data['assetContents'][1]['genusTypeId'],
            str(TRANSCRIPT_FILE_ASSET_CONTENT_GENUS_TYPE)
        )

    def test_can_clear_all_transcript_files(self):
        self._video_upload_test_file.seek(0)
        self._transcript_test_file.seek(0)
        req = self.app.post(self.url,
                            params={'locale': 'hi'},
                            upload_files=[('inputFile', 'video-js-test.mp4', self._video_upload_test_file.read()),
                                          ('transcriptFile', 'transcript.txt', self._transcript_test_file.read())])
        self.ok(req)
        data = self.json(req)
        self.assertEqual(len(data['assetContents']), 2)
        self.assertEqual(len(data['assetContents'][1]['fileIds']), 1)

        data = self.clear_transcript_files(data, False)
        self.assertEqual(len(data['assetContents']), 2)
        self.assertEqual(len(data['assetContents'][1]['fileIds']), 1)

        data = self.clear_transcript_files(data, True)
        self.assertEqual(len(data['assetContents']), 2)
        self.assertEqual(len(data['assetContents'][1]['fileIds']), 0)

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

        data = self.clear_vtt_files(data, False)
        self.assertEqual(len(data['assetContents']), 2)
        self.assertEqual(len(data['assetContents'][1]['fileIds']), 1)

        data = self.clear_vtt_files(data, True)
        self.assertEqual(len(data['assetContents']), 2)
        self.assertEqual(len(data['assetContents'][1]['fileIds']), 0)

    def test_can_remove_vtt_file_by_language(self):
        self._video_upload_test_file.seek(0)
        self._caption_upload_test_file.seek(0)
        req = self.app.post(self.url,
                            upload_files=[('inputFile', 'video-js-test.mp4', self._video_upload_test_file.read()),
                                          ('vttFile', 'video-js-test-en.vtt', self._caption_upload_test_file.read())])
        self.ok(req)
        data = self.json(req)
        self.assertEqual(len(data['assetContents']), 2)
        self.assertEqual(len(data['assetContents'][1]['fileIds']), 1)

        self._caption_upload_test_file.seek(0)
        url = '{0}/{1}'.format(self.url,
                               data['id'])
        req = self.app.put(url,
                           params={'locale': 'hi'},
                           upload_files=[('vttFile', 'video-js-test-hi.vtt', self._caption_upload_test_file.read())])
        self.ok(req)
        data = self.json(req)
        self.assertEqual(len(data['assetContents']), 2)
        self.assertEqual(len(data['assetContents'][1]['fileIds']), 2)

        data = self.remove_vtt_language(data, 'en')

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

    def test_can_remove_transcript_file_by_language(self):
        self._video_upload_test_file.seek(0)
        self._transcript_test_file.seek(0)
        req = self.app.post(self.url,
                            upload_files=[('inputFile', 'video-js-test.mp4', self._video_upload_test_file.read()),
                                          ('transcriptFile', 'transcript.txt', self._transcript_test_file.read())])
        self.ok(req)
        data = self.json(req)
        self.assertEqual(len(data['assetContents']), 2)
        self.assertEqual(len(data['assetContents'][1]['fileIds']), 1)

        self._transcript_test_file.seek(0)
        url = '{0}/{1}'.format(self.url,
                               data['id'])
        req = self.app.put(url,
                           params={'locale': 'hi'},
                           upload_files=[('transcriptFile', 'transcript.txt', self._transcript_test_file.read())])
        self.ok(req)
        data = self.json(req)
        self.assertEqual(len(data['assetContents']), 2)
        self.assertEqual(len(data['assetContents'][1]['fileIds']), 2)

        data = self.remove_transcript_language(data, 'en')
        self.assertEqual(len(data['assetContents']), 2)
        self.assertEqual(len(data['assetContents'][1]['fileIds']), 1)

        self.assertEqual(
            data['assetContents'][1]['fileIds'].keys()[0],
            'HIN'
        )
        transcript_files = data['assetContents'][1]['fileIds']['HIN']
        self.assertIn('assetId', transcript_files)
        self.assertIn('assetContentId', transcript_files)
        self.assertIn('assetContentTypeId', transcript_files)
        self.assertEqual(
            data['assetContents'][1]['genusTypeId'],
            str(TRANSCRIPT_FILE_ASSET_CONTENT_GENUS_TYPE)
        )

    def test_video_caption_track_shows_up_in_requested_language(self):
        data = self.upload_video_with_captions()
        item = self.create_mc_item_with_video(data)

        url = '/api/v1/assessment/banks/{0}/items/{1}'.format(str(self._repo.ident),
                                                              item['id'])
        req = self.app.get(url)
        self.ok(req)
        data = self.json(req)

        choice_with_media = data['question']['multiLanguageChoices'][0]['texts'][0]['text']

        self.assertIn('srclang="en"', choice_with_media)
        self.assertIn('label="English"', choice_with_media)
        self.assertNotIn('srclang="hi"', choice_with_media)
        self.assertNotIn('label="Hindi"', choice_with_media)
        self.assertNotIn('srclang="te"', choice_with_media)
        self.assertNotIn('label="Telugu"', choice_with_media)
        self.assertIn('/stream', choice_with_media)
        self.assertNotIn('AssetContent:"', choice_with_media)

        req = self.app.get(url,
                           headers={'x-api-locale': 'hi'})
        self.ok(req)
        data = self.json(req)

        choice_with_media = data['question']['multiLanguageChoices'][0]['texts'][0]['text']

        self.assertNotIn('srclang="en"', choice_with_media)
        self.assertNotIn('label="English"', choice_with_media)
        self.assertIn('srclang="hi"', choice_with_media)
        self.assertIn('label="Hindi"', choice_with_media)
        self.assertNotIn('srclang="te"', choice_with_media)
        self.assertNotIn('label="Telugu"', choice_with_media)
        self.assertIn('/stream', choice_with_media)
        self.assertNotIn('AssetContent:"', choice_with_media)

        req = self.app.get(url,
                           headers={'x-api-locale': 'te'})
        self.ok(req)
        data = self.json(req)

        choice_with_media = data['question']['multiLanguageChoices'][0]['texts'][0]['text']

        self.assertNotIn('srclang="en"', choice_with_media)
        self.assertNotIn('label="English"', choice_with_media)
        self.assertNotIn('srclang="hi"', choice_with_media)
        self.assertNotIn('label="Hindi"', choice_with_media)
        self.assertIn('srclang="te"', choice_with_media)
        self.assertIn('label="Telugu"', choice_with_media)
        self.assertIn('/stream', choice_with_media)
        self.assertNotIn('AssetContent:"', choice_with_media)

    def test_video_caption_track_url_shows_with_right_asset_content_id(self):
        data = self.upload_video_with_captions()
        vtt_asset_content = [ac for ac in data['assetContents']
                             if ac['genusTypeId'] == str(VTT_FILE_ASSET_CONTENT_GENUS_TYPE)][0]
        item = self.create_mc_item_with_video(data)

        url = '/api/v1/assessment/banks/{0}/items/{1}'.format(str(self._repo.ident),
                                                              item['id'])
        req = self.app.get(url)
        self.ok(req)
        data = self.json(req)

        choice_with_media = data['question']['multiLanguageChoices'][0]['texts'][0]['text']

        self.assertIn(vtt_asset_content['id'], choice_with_media)

        soup = BeautifulSoup(choice_with_media, 'xml')
        src = soup.source['src']
        req = self.app.get(src)
        self.code(req, 206)

        req = self.app.get(url,
                           headers={'x-api-locale': 'hi'})
        self.ok(req)
        data = self.json(req)

        choice_with_media = data['question']['multiLanguageChoices'][0]['texts'][0]['text']

        self.assertIn(vtt_asset_content['id'], choice_with_media)

        soup = BeautifulSoup(choice_with_media, 'xml')
        src = soup.source['src']
        req = self.app.get(src)
        self.code(req, 206)

        req = self.app.get(url,
                           headers={'x-api-locale': 'te'})
        self.ok(req)
        data = self.json(req)

        choice_with_media = data['question']['multiLanguageChoices'][0]['texts'][0]['text']

        self.assertIn(vtt_asset_content['id'], choice_with_media)

        # Need to make sure this file is streamable / GET == 200 response
        soup = BeautifulSoup(choice_with_media, 'xml')
        src = soup.source['src']
        req = self.app.get(src)
        self.code(req, 206)

    def test_audio_transcript_shows_up_in_requested_language(self):
        data = self.upload_audio_with_transcripts()
        item = self.create_mc_item_with_audio_and_transcript(data)

        url = '/api/v1/assessment/banks/{0}/items/{1}'.format(str(self._repo.ident),
                                                              item['id'])
        req = self.app.get(url)
        self.ok(req)
        data = self.json(req)

        choice_text_with_audio = data['question']['multiLanguageChoices'][0]['texts'][0]['text']
        self.assertIn('transcript_txt', choice_text_with_audio)
        self.assertIn('transcriptWrapper', choice_text_with_audio)
        self.assertIn('transcript', choice_text_with_audio)
        self.assertIn('Transcript', choice_text_with_audio)
        self.assertIn('This is a test transcript.', choice_text_with_audio)

        req = self.app.get(url,
                           headers={'x-api-locale': 'hi'})
        self.ok(req)
        data = self.json(req)

        choice_text_with_audio = data['question']['multiLanguageChoices'][0]['texts'][0]['text']
        self.assertIn('transcript_txt', choice_text_with_audio)
        self.assertIn('transcriptWrapper', choice_text_with_audio)
        self.assertIn(u'वीडियो प्रतिलेख', choice_text_with_audio)
        self.assertIn(u'वीडियो प्रतिलेख', choice_text_with_audio)
        self.assertIn(u'यह एक परीक्षण प्रतिलेख है.', choice_text_with_audio)

        req = self.app.get(url,
                           headers={'x-api-locale': 'te'})
        self.ok(req)
        data = self.json(req)

        choice_text_with_audio = data['question']['multiLanguageChoices'][0]['texts'][0]['text']
        self.assertIn('transcript_txt', choice_text_with_audio)
        self.assertIn('transcriptWrapper', choice_text_with_audio)
        self.assertIn(u'వీడియో ట్రాన్స్క్రిప్ట్', choice_text_with_audio)
        self.assertIn(u'వీడియో ట్రాన్స్క్రిప్ట్', choice_text_with_audio)
        self.assertIn(u'ఈ పరీక్ష ట్రాన్స్క్రిప్ట్ ఉంది.', choice_text_with_audio)

    def test_audio_transcript_not_nested_in_p_tag(self):
        data = self.upload_audio_with_transcripts()
        item = self.create_mc_item_with_audio_and_transcript(data)

        url = '/api/v1/assessment/banks/{0}/items/{1}'.format(str(self._repo.ident),
                                                              item['id'])
        req = self.app.get(url)
        self.ok(req)
        data = self.json(req)
        choice_text_with_audio = data['question']['multiLanguageChoices'][0]['texts'][0]['text']
        soup = BeautifulSoup(choice_text_with_audio, 'xml')
        self.assertIsNone(soup.simpleChoice.p.div)
        div_text = str(soup.simpleChoice.div)
        self.assertIn('transcript_txt', div_text)
        self.assertIn('transcriptWrapper', div_text)
        self.assertIn('transcript', div_text)
        self.assertIn('Transcript', div_text)
        self.assertIn('This is a test transcript.', div_text)

    def test_video_transcript_shows_up_in_requested_language(self):
        data = self.upload_video_with_caption_and_transcripts()
        item = self.create_mc_item_with_video_and_transcript(data)

        url = '/api/v1/assessment/banks/{0}/items/{1}'.format(str(self._repo.ident),
                                                              item['id'])
        req = self.app.get(url)
        self.ok(req)
        data = self.json(req)

        choice_text_with_video = data['question']['multiLanguageChoices'][0]['texts'][0]['text']
        self.assertIn('transcript_txt', choice_text_with_video)
        self.assertIn('transcriptWrapper', choice_text_with_video)
        self.assertIn('transcript', choice_text_with_video)
        self.assertIn('Transcript', choice_text_with_video)
        self.assertIn('This is a test transcript.', choice_text_with_video)

        req = self.app.get(url,
                           headers={'x-api-locale': 'hi'})
        self.ok(req)
        data = self.json(req)

        choice_text_with_video = data['question']['multiLanguageChoices'][0]['texts'][0]['text']
        self.assertIn('transcript_txt', choice_text_with_video)
        self.assertIn('transcriptWrapper', choice_text_with_video)
        self.assertIn(u'वीडियो प्रतिलेख', choice_text_with_video)
        self.assertIn(u'वीडियो प्रतिलेख', choice_text_with_video)
        self.assertIn(u'यह एक परीक्षण प्रतिलेख है.', choice_text_with_video)

        req = self.app.get(url,
                           headers={'x-api-locale': 'te'})
        self.ok(req)
        data = self.json(req)

        choice_text_with_video = data['question']['multiLanguageChoices'][0]['texts'][0]['text']
        self.assertIn('transcript_txt', choice_text_with_video)
        self.assertIn('transcriptWrapper', choice_text_with_video)
        self.assertIn(u'వీడియో ట్రాన్స్క్రిప్ట్', choice_text_with_video)
        self.assertIn(u'వీడియో ట్రాన్స్క్రిప్ట్', choice_text_with_video)
        self.assertIn(u'ఈ పరీక్ష ట్రాన్స్క్రిప్ట్ ఉంది.', choice_text_with_video)

    def test_video_transcript_shows_up_not_nested_in_p_tag(self):
        data = self.upload_video_with_caption_and_transcripts()
        item = self.create_mc_item_with_video_and_transcript(data)

        url = '/api/v1/assessment/banks/{0}/items/{1}'.format(str(self._repo.ident),
                                                              item['id'])
        req = self.app.get(url)
        self.ok(req)
        data = self.json(req)

        choice_text_with_video = data['question']['multiLanguageChoices'][0]['texts'][0]['text']
        soup = BeautifulSoup(choice_text_with_video, 'xml')
        self.assertIsNone(soup.simpleChoice.p.div)
        div_text = str(soup.simpleChoice.div)
        self.assertIn('transcript_txt', div_text)
        self.assertIn('transcriptWrapper', div_text)
        self.assertIn('transcript', div_text)
        self.assertIn('Transcript', div_text)
        self.assertIn('This is a test transcript.', div_text)

    def test_can_get_video_question_even_if_transcript_src_blank(self):
        self._video_upload_test_file.seek(0)
        self._caption_upload_test_file.seek(0)
        self._transcript_test_file.seek(0)
        req = self.app.post(self.url,
                            upload_files=[('inputFile', 'video-js-test.mp4', self._video_upload_test_file.read()),
                                          ('vttFile', 'video-js-test-en.vtt', self._caption_upload_test_file.read()),
                                          ('transcriptFile', 'transcript.txt', self._transcript_test_file.read())])
        self.ok(req)
        data = self.json(req)
        self.assertEqual(len(data['assetContents']), 3)
        self.assertEqual(len(data['assetContents'][2]['fileIds']), 1)

        self._transcript_hi_test_file.seek(0)
        url = '{0}/{1}'.format(self.url,
                               data['id'])
        req = self.app.put(url,
                           params={'locale': 'hi'},
                           upload_files=[('transcriptFile', 'transcript_hi.txt', self._transcript_hi_test_file.read())])
        self.ok(req)
        data = self.json(req)
        self.assertEqual(len(data['assetContents']), 3)
        self.assertEqual(len(data['assetContents'][2]['fileIds']), 2)

        self._transcript_te_test_file.seek(0)
        req = self.app.put(url,
                           params={'locale': 'te'},
                           upload_files=[('transcriptFile', 'transcript_te.txt', self._transcript_te_test_file.read())])
        self.ok(req)
        data = self.json(req)
        self.assertEqual(len(data['assetContents']), 3)
        self.assertEqual(len(data['assetContents'][2]['fileIds']), 3)

        item = self.create_mc_item_with_video_and_transcript(data, transcript_blank=True)

        url = '/api/v1/assessment/banks/{0}/items/{1}'.format(str(self._repo.ident),
                                                              item['id'])
        req = self.app.get(url)
        self.ok(req)
        data = self.json(req)

        choice_text_with_video = data['question']['multiLanguageChoices'][0]['texts'][0]['text']
        self.assertIn('<transcript', choice_text_with_video)
        self.assertNotIn('transcriptWrapper', choice_text_with_video)
        self.assertNotIn('This is a test transcript.', choice_text_with_video)

        req = self.app.get(url,
                           headers={'x-api-locale': 'hi'})
        self.ok(req)
        data = self.json(req)

        choice_text_with_video = data['question']['multiLanguageChoices'][0]['texts'][0]['text']
        self.assertIn('<transcript', choice_text_with_video)
        self.assertNotIn('transcriptWrapper', choice_text_with_video)
        self.assertNotIn(u'वीडियो प्रतिलेख', choice_text_with_video)
        self.assertNotIn(u'वीडियो प्रतिलेख', choice_text_with_video)
        self.assertNotIn(u'यह एक परीक्षण प्रतिलेख है.', choice_text_with_video)

        req = self.app.get(url,
                           headers={'x-api-locale': 'te'})
        self.ok(req)
        data = self.json(req)

        choice_text_with_video = data['question']['multiLanguageChoices'][0]['texts'][0]['text']
        self.assertIn('<transcript', choice_text_with_video)
        self.assertNotIn('transcriptWrapper', choice_text_with_video)
        self.assertNotIn(u'వీడియో ట్రాన్స్క్రిప్ట్', choice_text_with_video)
        self.assertNotIn(u'వీడియో ట్రాన్స్క్రిప్ట్', choice_text_with_video)
        self.assertNotIn(u'ఈ పరీక్ష ట్రాన్స్క్రిప్ట్ ఉంది.', choice_text_with_video)

    def test_can_get_audio_question_even_if_transcript_src_blank(self):
        data = self.upload_audio_with_transcripts()
        item = self.create_mc_item_with_audio_and_transcript(data, transcript_blank=True)

        url = '/api/v1/assessment/banks/{0}/items/{1}'.format(str(self._repo.ident),
                                                              item['id'])
        req = self.app.get(url)
        self.ok(req)
        data = self.json(req)

        choice_text_with_audio = data['question']['multiLanguageChoices'][0]['texts'][0]['text']
        self.assertIn('<transcript', choice_text_with_audio)
        self.assertNotIn('transcriptWrapper', choice_text_with_audio)
        self.assertNotIn('This is a test transcript.', choice_text_with_audio)

        req = self.app.get(url,
                           headers={'x-api-locale': 'hi'})
        self.ok(req)
        data = self.json(req)

        choice_text_with_audio = data['question']['multiLanguageChoices'][0]['texts'][0]['text']
        self.assertIn('<transcript', choice_text_with_audio)
        self.assertNotIn('transcriptWrapper', choice_text_with_audio)
        self.assertNotIn(u'वीडियो प्रतिलेख', choice_text_with_audio)
        self.assertNotIn(u'वीडियो प्रतिलेख', choice_text_with_audio)
        self.assertNotIn(u'यह एक परीक्षण प्रतिलेख है.', choice_text_with_audio)

        req = self.app.get(url,
                           headers={'x-api-locale': 'te'})
        self.ok(req)
        data = self.json(req)

        choice_text_with_audio = data['question']['multiLanguageChoices'][0]['texts'][0]['text']
        self.assertIn('<transcript', choice_text_with_audio)
        self.assertNotIn('transcriptWrapper', choice_text_with_audio)
        self.assertNotIn(u'వీడియో ట్రాన్స్క్రిప్ట్', choice_text_with_audio)
        self.assertNotIn(u'వీడియో ట్రాన్స్క్రిప్ట్', choice_text_with_audio)
        self.assertNotIn(u'ఈ పరీక్ష ట్రాన్స్క్రిప్ట్ ఉంది.', choice_text_with_audio)

    def test_can_get_video_question_even_if_vtt_track_blank(self):
        data = self.upload_video_with_captions()
        item = self.create_mc_item_with_video(data, vtt_blank=True)

        url = '/api/v1/assessment/banks/{0}/items/{1}'.format(str(self._repo.ident),
                                                              item['id'])
        req = self.app.get(url)
        self.ok(req)
        data = self.json(req)

        choice_with_media = data['question']['multiLanguageChoices'][0]['texts'][0]['text']

        self.assertIn('srclang="en"', choice_with_media)
        self.assertIn('label="English"', choice_with_media)
        self.assertNotIn('srclang="hi"', choice_with_media)
        self.assertNotIn('label="Hindi"', choice_with_media)
        self.assertNotIn('srclang="te"', choice_with_media)
        self.assertNotIn('label="Telugu"', choice_with_media)
        self.assertIn('src=""', choice_with_media)
        self.assertNotIn('AssetContent:', choice_with_media)

        req = self.app.get(url,
                           headers={'x-api-locale': 'hi'})
        self.ok(req)
        data = self.json(req)

        choice_with_media = data['question']['multiLanguageChoices'][0]['texts'][0]['text']

        self.assertIn('srclang="en"', choice_with_media)
        self.assertIn('label="English"', choice_with_media)
        self.assertNotIn('srclang="hi"', choice_with_media)
        self.assertNotIn('label="Hindi"', choice_with_media)
        self.assertNotIn('srclang="te"', choice_with_media)
        self.assertNotIn('label="Telugu"', choice_with_media)
        self.assertIn('src=""', choice_with_media)
        self.assertNotIn('AssetContent:', choice_with_media)

        req = self.app.get(url,
                           headers={'x-api-locale': 'te'})
        self.ok(req)
        data = self.json(req)

        choice_with_media = data['question']['multiLanguageChoices'][0]['texts'][0]['text']

        self.assertIn('srclang="en"', choice_with_media)
        self.assertIn('label="English"', choice_with_media)
        self.assertNotIn('srclang="hi"', choice_with_media)
        self.assertNotIn('label="Hindi"', choice_with_media)
        self.assertNotIn('srclang="te"', choice_with_media)
        self.assertNotIn('label="Telugu"', choice_with_media)
        self.assertIn('src=""', choice_with_media)
        self.assertNotIn('AssetContent:', choice_with_media)

    def test_get_default_lang_vtt_text_when_requested_lang_not_there(self):
        data = self.upload_video_with_captions()
        self.remove_vtt_language(data, 'hi')

        transcript_ac = [ac
                         for ac in data['assetContents']
                         if ac['genusTypeId'] == str(VTT_FILE_ASSET_CONTENT_GENUS_TYPE)][0]

        url = '{0}/{1}/contents/{2}/stream'.format(self.url,
                                                   data['id'],
                                                   transcript_ac['id'])
        req = self.app.get(url,
                           headers={'x-api-locale': 'hi'})
        self.ok(req)
        data = req.body

        self.assertIn('Can I use webVTT?', data)

    def test_get_default_lang_vtt_file_when_requested_lang_not_there(self):
        data = self.upload_video_with_captions()
        self.remove_vtt_language(data, 'hi')
        item = self.create_mc_item_with_video(data)

        url = '/api/v1/assessment/banks/{0}/items/{1}'.format(str(self._repo.ident),
                                                              item['id'])
        req = self.app.get(url)
        self.ok(req)
        data = self.json(req)

        req = self.app.get(url,
                           headers={'x-api-locale': 'hi'})
        self.ok(req)
        data = self.json(req)

        choice_with_media = data['question']['multiLanguageChoices'][0]['texts'][0]['text']

        self.assertIn('srclang="en"', choice_with_media)
        self.assertIn('label="English"', choice_with_media)
        self.assertNotIn('srclang="hi"', choice_with_media)
        self.assertNotIn('label="Hindi"', choice_with_media)
        self.assertNotIn('srclang="te"', choice_with_media)
        self.assertNotIn('label="Telugu"', choice_with_media)
        self.assertIn('/stream', choice_with_media)
        self.assertNotIn('AssetContent:', choice_with_media)

    def test_no_replacement_when_no_vtt_files(self):
        data = self.upload_video_with_captions()
        self.clear_vtt_files(data, True)
        item = self.create_mc_item_with_video(data)

        url = '/api/v1/assessment/banks/{0}/items/{1}'.format(str(self._repo.ident),
                                                              item['id'])
        req = self.app.get(url)
        self.ok(req)
        data = self.json(req)

        choice_with_media = data['question']['multiLanguageChoices'][0]['texts'][0]['text']

        self.assertIn('srclang="en"', choice_with_media)
        self.assertIn('label="English"', choice_with_media)
        self.assertNotIn('srclang="hi"', choice_with_media)
        self.assertNotIn('label="Hindi"', choice_with_media)
        self.assertNotIn('srclang="te"', choice_with_media)
        self.assertNotIn('label="Telugu"', choice_with_media)
        self.assertIn('AssetContent:', choice_with_media)

    def test_get_first_vtt_text_when_default_lang_not_there(self):
        data = self.upload_video_with_captions()
        self.remove_vtt_language(data, 'en')

        transcript_ac = [ac
                         for ac in data['assetContents']
                         if ac['genusTypeId'] == str(VTT_FILE_ASSET_CONTENT_GENUS_TYPE)][0]

        url = '{0}/{1}/contents/{2}/stream'.format(self.url,
                                                   data['id'],
                                                   transcript_ac['id'])
        req = self.app.get(url)
        self.ok(req)
        data = req.body.decode('utf8')

        self.assertIn(u'నేను webVTT ఉపయోగించవచ్చా?', data)

    def test_get_first_vtt_file_when_default_lang_not_there(self):
        data = self.upload_video_with_captions()
        self.remove_vtt_language(data, 'en')
        item = self.create_mc_item_with_video(data)

        url = '/api/v1/assessment/banks/{0}/items/{1}'.format(str(self._repo.ident),
                                                              item['id'])
        req = self.app.get(url)
        self.ok(req)
        data = self.json(req)

        choice_with_media = data['question']['multiLanguageChoices'][0]['texts'][0]['text']

        self.assertNotIn('srclang="en"', choice_with_media)
        self.assertNotIn('label="English"', choice_with_media)
        self.assertNotIn('srclang="hi"', choice_with_media)
        self.assertNotIn('label="Hindi"', choice_with_media)
        self.assertIn('srclang="te"', choice_with_media)
        self.assertIn('label="Telugu"', choice_with_media)
        self.assertIn('/stream', choice_with_media)
        self.assertNotIn('AssetContent:', choice_with_media)

    def test_get_default_lang_transcript_stream_for_video_when_requested_lang_not_there(self):
        data = self.upload_video_with_caption_and_transcripts()
        data = self.remove_transcript_language(data, 'hi')

        transcript_ac = [ac
                         for ac in data['assetContents']
                         if ac['genusTypeId'] == str(TRANSCRIPT_FILE_ASSET_CONTENT_GENUS_TYPE)][0]

        url = '{0}/{1}/contents/{2}/stream'.format(self.url,
                                                   data['id'],
                                                   transcript_ac['id'])
        req = self.app.get(url,
                           headers={'x-api-locale': 'hi'})
        self.ok(req)
        data = req.body

        self.assertIn('This is a test transcript.', data)

    def test_get_default_lang_transcript_for_video_when_requested_lang_not_there(self):
        data = self.upload_video_with_caption_and_transcripts()
        data = self.remove_transcript_language(data, 'hi')
        item = self.create_mc_item_with_video_and_transcript(data)

        url = '/api/v1/assessment/banks/{0}/items/{1}'.format(str(self._repo.ident),
                                                              item['id'])

        req = self.app.get(url,
                           headers={'x-api-locale': 'hi'})
        self.ok(req)
        data = self.json(req)

        choice_text_with_video = data['question']['multiLanguageChoices'][0]['texts'][0]['text']
        self.assertIn('transcript_txt', choice_text_with_video)
        self.assertIn('transcriptWrapper', choice_text_with_video)
        self.assertIn('transcript', choice_text_with_video)
        self.assertIn('Transcript', choice_text_with_video)
        self.assertIn('This is a test transcript.', choice_text_with_video)

    def test_no_replacement_in_video_question_when_no_transcripts(self):
        data = self.upload_video_with_caption_and_transcripts()
        self.clear_transcript_files(data, True)
        item = self.create_mc_item_with_video_and_transcript(data)

        url = '/api/v1/assessment/banks/{0}/items/{1}'.format(str(self._repo.ident),
                                                              item['id'])

        req = self.app.get(url,
                           headers={'x-api-locale': 'hi'})
        self.ok(req)
        data = self.json(req)

        choice_text_with_media = data['question']['multiLanguageChoices'][0]['texts'][0]['text']
        self.assertIn('<transcript', choice_text_with_media)
        self.assertIn('AssetContent:transcript_txt', choice_text_with_media)
        self.assertNotIn('transcriptWrapper', choice_text_with_media)
        self.assertNotIn('This is a test transcript.', choice_text_with_media)

    def test_get_first_transcript_stream_for_video_when_default_lang_not_there(self):
        data = self.upload_video_with_caption_and_transcripts()
        data = self.remove_transcript_language(data, 'en')

        transcript_ac = [ac
                         for ac in data['assetContents']
                         if ac['genusTypeId'] == str(TRANSCRIPT_FILE_ASSET_CONTENT_GENUS_TYPE)][0]

        url = '{0}/{1}/contents/{2}/stream'.format(self.url,
                                                   data['id'],
                                                   transcript_ac['id'])
        req = self.app.get(url)
        self.ok(req)
        data = req.body.decode('utf8')

        self.assertIn(u'ఈ పరీక్ష ట్రాన్స్క్రిప్ట్ ఉంది.', data)

    def test_get_first_transcript_for_video_when_default_lang_not_there(self):
        data = self.upload_video_with_caption_and_transcripts()
        data = self.remove_transcript_language(data, 'en')
        item = self.create_mc_item_with_video_and_transcript(data)

        url = '/api/v1/assessment/banks/{0}/items/{1}'.format(str(self._repo.ident),
                                                              item['id'])

        req = self.app.get(url)
        self.ok(req)
        data = self.json(req)

        choice_text_with_video = data['question']['multiLanguageChoices'][0]['texts'][0]['text']
        self.assertNotIn('<transcript', choice_text_with_video)
        self.assertIn('transcript_txt', choice_text_with_video)
        self.assertIn('transcriptWrapper', choice_text_with_video)
        self.assertIn(u'వీడియో ట్రాన్స్క్రిప్ట్', choice_text_with_video)
        self.assertIn(u'వీడియో ట్రాన్స్క్రిప్ట్', choice_text_with_video)
        self.assertIn(u'ఈ పరీక్ష ట్రాన్స్క్రిప్ట్ ఉంది.', choice_text_with_video)

    def test_get_default_lang_transcript_stream_for_audio_when_requested_lang_not_there(self):
        data = self.upload_audio_with_transcripts()
        data = self.remove_transcript_language(data, 'hi')

        transcript_ac = [ac
                         for ac in data['assetContents']
                         if ac['genusTypeId'] == str(TRANSCRIPT_FILE_ASSET_CONTENT_GENUS_TYPE)][0]

        url = '{0}/{1}/contents/{2}/stream'.format(self.url,
                                                   data['id'],
                                                   transcript_ac['id'])
        req = self.app.get(url,
                           headers={'x-api-locale': 'hi'})
        self.ok(req)
        data = req.body

        self.assertIn('This is a test transcript.', data)

    def test_get_default_lang_transcript_for_audio_when_requested_lang_not_there(self):
        data = self.upload_audio_with_transcripts()
        data = self.remove_transcript_language(data, 'hi')
        item = self.create_mc_item_with_audio_and_transcript(data)

        url = '/api/v1/assessment/banks/{0}/items/{1}'.format(str(self._repo.ident),
                                                              item['id'])

        req = self.app.get(url,
                           headers={'x-api-locale': 'hi'})
        self.ok(req)
        data = self.json(req)

        choice_text_with_media = data['question']['multiLanguageChoices'][0]['texts'][0]['text']
        self.assertNotIn('<transcript', choice_text_with_media)
        self.assertIn('transcript_txt', choice_text_with_media)
        self.assertIn('transcriptWrapper', choice_text_with_media)
        self.assertIn('transcript', choice_text_with_media)
        self.assertIn('Transcript', choice_text_with_media)
        self.assertIn('This is a test transcript.', choice_text_with_media)

    def test_no_replacement_in_audio_question_when_no_transcripts(self):
        data = self.upload_audio_with_transcripts()
        self.clear_transcript_files(data, True)
        item = self.create_mc_item_with_audio_and_transcript(data)

        url = '/api/v1/assessment/banks/{0}/items/{1}'.format(str(self._repo.ident),
                                                              item['id'])

        req = self.app.get(url,
                           headers={'x-api-locale': 'hi'})
        self.ok(req)
        data = self.json(req)

        choice_text_with_media = data['question']['multiLanguageChoices'][0]['texts'][0]['text']
        self.assertIn('<transcript', choice_text_with_media)
        self.assertIn('AssetContent:transcript_txt', choice_text_with_media)
        self.assertNotIn('transcriptWrapper', choice_text_with_media)
        self.assertNotIn('This is a test transcript.', choice_text_with_media)

    def test_get_first_transcript_stream_for_audio_when_default_lang_not_there(self):
        data = self.upload_audio_with_transcripts()
        data = self.remove_transcript_language(data, 'en')

        transcript_ac = [ac
                         for ac in data['assetContents']
                         if ac['genusTypeId'] == str(TRANSCRIPT_FILE_ASSET_CONTENT_GENUS_TYPE)][0]

        url = '{0}/{1}/contents/{2}/stream'.format(self.url,
                                                   data['id'],
                                                   transcript_ac['id'])
        req = self.app.get(url)
        self.ok(req)
        data = req.body.decode('utf8')

        self.assertIn(u'ఈ పరీక్ష ట్రాన్స్క్రిప్ట్ ఉంది.', data)

    def test_get_first_transcript_for_audio_when_default_lang_not_there(self):
        data = self.upload_audio_with_transcripts()
        data = self.remove_transcript_language(data, 'en')
        item = self.create_mc_item_with_audio_and_transcript(data)

        url = '/api/v1/assessment/banks/{0}/items/{1}'.format(str(self._repo.ident),
                                                              item['id'])

        req = self.app.get(url)
        self.ok(req)
        data = self.json(req)

        choice_text_with_media = data['question']['multiLanguageChoices'][0]['texts'][0]['text']
        self.assertNotIn('<transcript', choice_text_with_media)
        self.assertIn('transcript_txt', choice_text_with_media)
        self.assertIn('transcriptWrapper', choice_text_with_media)
        self.assertIn(u'వీడియో ట్రాన్స్క్రిప్ట్', choice_text_with_media)
        self.assertIn(u'వీడియో ట్రాన్స్క్రిప్ట్', choice_text_with_media)
        self.assertIn(u'ఈ పరీక్ష ట్రాన్స్క్రిప్ట్ ఉంది.', choice_text_with_media)

    def test_can_still_get_all_assets_when_audio_with_transcripts_present(self):
        item = self.upload_audio_with_transcripts()
        url = '{0}?allAssets&fullUrls'.format(self.url)
        req = self.app.get(url)
        self.ok(req)
        data = self.json(req)
        self.assertEqual(len(data), 4)  # audio with 3 transcripts

        orig_item = [i for i in data if i['id'] == item['id']][0]
        self.assertEqual(len(orig_item['assetContents']), 2)

    # Not sure what to do with these, how we want to display them on the content side...
    # Fill in these tests once we figure that out
    # def test_default_lang_media_description_shows_up_in_audio(self):
    #     self.fail('finish writing the test')
    #
    # def test_media_description_shows_up_in_audio_for_requested_lang(self):
    #     self.fail('finish writing the test')
    #
    # def test_available_media_description_shows_up_in_audio_when_default_doesnt_exist(self):
    #     self.fail('finish writing the test')
    #
    # def test_empty_string_for_description_when_not_provided_audio(self):
    #     self.fail('finish writing hte test')
    #
    # def test_default_lang_media_description_shows_up_in_video(self):
    #     self.fail('finish writing the test')
    #
    # def test_media_description_shows_up_in_video_for_requested_lang(self):
    #     self.fail('finish writing the test')
    #
    # def test_available_media_description_shows_up_in_video_when_default_doesnt_exist(self):
    #     self.fail('finish writing the test')
    #
    # def test_empty_string_for_description_when_not_provided_video(self):
    #     self.fail('finish writing hte test')
