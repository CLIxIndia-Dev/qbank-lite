# -*- coding: utf-8 -*-
import json
from urllib import unquote

from bs4 import BeautifulSoup

import utilities
from testing_utilities import get_managers
from tests.test_assessment import ABS_PATH, BaseAssessmentTestCase,\
    SIMPLE_SEQUENCE_RECORD, REVIEWABLE_OFFERED, REVIEWABLE_TAKEN


class MultiLanguageTests(BaseAssessmentTestCase):
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

        form = bank.get_assessment_offered_form_for_create(new_assessment.ident, [REVIEWABLE_OFFERED])
        new_offered = bank.create_assessment_offered(form)

        return new_offered

    def create_fitb_item(self):
        url = '{0}/items'.format(self.url)
        self._mw_fitb_2_test_file.seek(0)
        req = self.app.post(url,
                            upload_files=[('qtiFile',
                                           self._filename(self._mw_fitb_2_test_file),
                                           self._mw_fitb_2_test_file.read())])
        self.ok(req)
        return self.json(req)

    def create_mc_feedback_item(self):
        url = '{0}/items'.format(self.url)
        self._mc_feedback_test_file.seek(0)
        req = self.app.post(url,
                            upload_files=[('qtiFile',
                                           self._filename(self._mc_feedback_test_file),
                                           self._mc_feedback_test_file.read())])
        self.ok(req)
        return self.json(req)

    def create_mc_multi_select_item(self):
        url = '{0}/items'.format(self.url)
        self._mc_multi_select_test_file.seek(0)
        req = self.app.post(url,
                            upload_files=[('qtiFile',
                                           self._filename(self._mc_multi_select_test_file),
                                           self._mc_multi_select_test_file.read())])
        self.ok(req)
        return self.json(req)

    def create_taken_for_item(self, bank_id, item_id):
        if isinstance(bank_id, basestring):
            bank_id = utilities.clean_id(bank_id)
        if isinstance(item_id, basestring):
            item_id = utilities.clean_id(item_id)

        bank = get_managers()['am'].get_bank(bank_id)

        new_offered = self.create_assessment_offered_for_item(bank_id, item_id)

        form = bank.get_assessment_taken_form_for_create(new_offered.ident, [REVIEWABLE_TAKEN])
        taken = bank.create_assessment_taken(form)
        return taken, new_offered

    def setUp(self):
        super(MultiLanguageTests, self).setUp()

        self._mw_sentence_test_file = open('{0}/tests/files/mw_sentence_with_audio_file.zip'.format(ABS_PATH), 'r')
        self._mc_feedback_test_file = open('{0}/tests/files/ee_u1l01a04q03_en.zip'.format(ABS_PATH), 'r')
        self._mc_multi_select_test_file = open('{0}/tests/files/mc_multi_select_test_file.zip'.format(ABS_PATH), 'r')
        self._short_answer_test_file = open('{0}/tests/files/short_answer_test_file.zip'.format(ABS_PATH), 'r')
        self._generic_upload_test_file = open('{0}/tests/files/generic_upload_test_file.zip'.format(ABS_PATH), 'r')
        self._simple_numeric_response_test_file = open('{0}/tests/files/new_numeric_response_format_test_file.zip'.format(ABS_PATH), 'r')
        self._floating_point_numeric_input_test_file = open('{0}/tests/files/new_floating_point_numeric_response_test_file.zip'.format(ABS_PATH), 'r')
        self._mw_fitb_2_test_file = open('{0}/tests/files/mw_fill_in_the_blank_example_2.zip'.format(ABS_PATH), 'r')
        self._audio_file = open('{0}/tests/files/audio_feedback.mp3'.format(ABS_PATH), 'r')

        self._english_text = 'english'
        self._hindi_text = u'हिंदी'
        self._telugu_text = u'తెలుగు'

        self._english_language_type = '639-2%3AENG%40ISO'
        self._english_script_type = '15924%3ALATN%40ISO'

        self._hindi_language_type = '639-2%3AHIN%40ISO'
        self._hindi_script_type = '15924%3ADEVA%40ISO'

        self._telugu_language_type = '639-2%3ATEL%40ISO'
        self._telugu_script_type = '15924%3ATELU%40ISO'

        self.url += '/banks/' + unquote(str(self._bank.ident))

    def tearDown(self):
        super(MultiLanguageTests, self).tearDown()

        self._mw_sentence_test_file.close()
        self._mc_feedback_test_file.close()
        self._mc_multi_select_test_file.close()
        self._short_answer_test_file.close()
        self._generic_upload_test_file.close()
        self._simple_numeric_response_test_file.close()
        self._floating_point_numeric_input_test_file.close()
        self._mw_fitb_2_test_file.close()
        self._audio_file.close()

    def test_can_set_multiple_display_texts(self):
        item = self.create_mc_multi_select_item()
        url = '{0}/items/{1}'.format(self.url,
                                     unquote(item['id']))
        payload = {
            'name': self._hindi_text
        }
        req = self.app.put(url,
                           params=json.dumps(payload),
                           headers=self._hindi_headers())
        self.ok(req)
        data = self.json(req)
        self.assertEqual(len(data['displayNames']), 2)
        self.assertEqual(data['displayNames'][1]['text'], self._hindi_text)
        self.assertEqual(data['displayNames'][1]['languageTypeId'], self._hindi_language_type)
        self.assertEqual(data['displayNames'][1]['scriptTypeId'], self._hindi_script_type)

    def test_sending_an_existing_language_replaces_display_name(self):
        item = self.create_mc_multi_select_item()
        url = '{0}/items/{1}'.format(self.url,
                                     unquote(item['id']))
        payload = {
            'name': self._hindi_text
        }
        req = self.app.put(url,
                           params=json.dumps(payload),
                           headers=self._english_headers())
        self.ok(req)
        data = self.json(req)
        self.assertEqual(len(data['displayNames']), 1)
        self.assertEqual(data['displayNames'][0]['text'], self._hindi_text)
        self.assertEqual(data['displayNames'][0]['languageTypeId'], self._english_language_type)
        self.assertEqual(data['displayNames'][0]['scriptTypeId'], self._english_script_type)

    def test_can_set_multiple_descriptions(self):
        item = self.create_mc_multi_select_item()
        url = '{0}/items/{1}'.format(self.url,
                                     unquote(item['id']))
        payload = {
            'description': self._hindi_text
        }
        req = self.app.put(url,
                           params=json.dumps(payload),
                           headers=self._hindi_headers())
        self.ok(req)
        data = self.json(req)
        self.assertEqual(len(data['descriptions']), 2)
        self.assertEqual(data['descriptions'][1]['text'], self._hindi_text)
        self.assertEqual(data['descriptions'][1]['languageTypeId'], self._hindi_language_type)
        self.assertEqual(data['descriptions'][1]['scriptTypeId'], self._hindi_script_type)

    def test_sending_an_existing_language_replaces_description(self):
        item = self.create_mc_multi_select_item()
        url = '{0}/items/{1}'.format(self.url,
                                     unquote(item['id']))
        payload = {
            'description': self._hindi_text
        }
        req = self.app.put(url,
                           params=json.dumps(payload),
                           headers=self._english_headers())
        self.ok(req)
        data = self.json(req)
        self.assertEqual(len(data['descriptions']), 1)
        self.assertEqual(data['descriptions'][0]['text'], self._hindi_text)
        self.assertEqual(data['descriptions'][0]['languageTypeId'], self._english_language_type)
        self.assertEqual(data['descriptions'][0]['scriptTypeId'], self._english_script_type)

    def test_can_remove_a_display_name(self):
        item = self.create_mc_multi_select_item()
        url = '{0}/items/{1}'.format(self.url,
                                     unquote(item['id']))
        payload = {
            'name': self._hindi_text
        }
        req = self.app.put(url,
                           params=json.dumps(payload),
                           headers=self._hindi_headers())
        self.ok(req)
        data = self.json(req)
        self.assertEqual(len(data['displayNames']), 2)
        self.assertEqual(data['displayNames'][1]['text'], self._hindi_text)
        self.assertEqual(data['displayNames'][1]['languageTypeId'], self._hindi_language_type)
        self.assertEqual(data['displayNames'][1]['scriptTypeId'], self._hindi_script_type)

        payload = {
            'removeName': data['displayNames'][0]
        }
        req = self.app.put(url,
                           params=json.dumps(payload),
                           headers=self._hindi_headers())
        self.ok(req)
        data = self.json(req)
        self.assertEqual(len(data['displayNames']), 1)
        self.assertEqual(data['displayNames'][0]['text'], self._hindi_text)
        self.assertEqual(data['displayNames'][0]['languageTypeId'], self._hindi_language_type)
        self.assertEqual(data['displayNames'][0]['scriptTypeId'], self._hindi_script_type)

    def test_can_remove_a_description(self):
        item = self.create_mc_multi_select_item()
        url = '{0}/items/{1}'.format(self.url,
                                     unquote(item['id']))
        payload = {
            'description': self._hindi_text
        }
        req = self.app.put(url,
                           params=json.dumps(payload),
                           headers=self._hindi_headers())
        self.ok(req)
        data = self.json(req)
        self.assertEqual(len(data['descriptions']), 2)
        self.assertEqual(data['descriptions'][1]['text'], self._hindi_text)
        self.assertEqual(data['descriptions'][1]['languageTypeId'], self._hindi_language_type)
        self.assertEqual(data['descriptions'][1]['scriptTypeId'], self._hindi_script_type)

        payload = {
            'removeDescription': data['descriptions'][0]
        }
        req = self.app.put(url,
                           params=json.dumps(payload),
                           headers=self._hindi_headers())  # this header should be ignored because we're passing in the entire DisplayText
        self.ok(req)
        data = self.json(req)
        self.assertEqual(len(data['descriptions']), 1)
        self.assertEqual(data['descriptions'][0]['text'], self._hindi_text)
        self.assertEqual(data['descriptions'][0]['languageTypeId'], self._hindi_language_type)
        self.assertEqual(data['descriptions'][0]['scriptTypeId'], self._hindi_script_type)

    def test_can_replace_a_display_name(self):
        item = self.create_mc_multi_select_item()
        url = '{0}/items/{1}'.format(self.url,
                                     unquote(item['id']))
        payload = {
            'name': self._hindi_text
        }
        req = self.app.put(url,
                           params=json.dumps(payload),
                           headers=self._hindi_headers())
        self.ok(req)
        data = self.json(req)
        self.assertEqual(len(data['displayNames']), 2)
        self.assertEqual(data['displayNames'][1]['text'], self._hindi_text)
        self.assertEqual(data['displayNames'][1]['languageTypeId'], self._hindi_language_type)
        self.assertEqual(data['displayNames'][1]['scriptTypeId'], self._hindi_script_type)

        payload = {
            'editName': [data['displayNames'][0], self._telugu_text]
        }
        req = self.app.put(url,
                           params=json.dumps(payload),
                           headers=self._telugu_headers())
        self.ok(req)
        data = self.json(req)
        self.assertEqual(len(data['displayNames']), 2)
        self.assertEqual(data['displayNames'][0]['text'], self._telugu_text)
        self.assertEqual(data['displayNames'][0]['languageTypeId'], self._telugu_language_type)
        self.assertEqual(data['displayNames'][0]['scriptTypeId'], self._telugu_script_type)
        self.assertEqual(data['displayNames'][1]['text'], self._hindi_text)
        self.assertEqual(data['displayNames'][1]['languageTypeId'], self._hindi_language_type)
        self.assertEqual(data['displayNames'][1]['scriptTypeId'], self._hindi_script_type)

    def test_can_replace_a_description(self):
        item = self.create_mc_multi_select_item()
        url = '{0}/items/{1}'.format(self.url,
                                     unquote(item['id']))
        payload = {
            'description': self._hindi_text
        }
        req = self.app.put(url,
                           params=json.dumps(payload),
                           headers=self._hindi_headers())
        self.ok(req)
        data = self.json(req)
        self.assertEqual(len(data['descriptions']), 2)
        self.assertEqual(data['descriptions'][1]['text'], self._hindi_text)
        self.assertEqual(data['descriptions'][1]['languageTypeId'], self._hindi_language_type)
        self.assertEqual(data['descriptions'][1]['scriptTypeId'], self._hindi_script_type)

        payload = {
            'editDescription': [data['descriptions'][0], self._telugu_text]
        }
        req = self.app.put(url,
                           params=json.dumps(payload),
                           headers=self._telugu_headers())  # now this header matters, because we're passing in a string only
        self.ok(req)
        data = self.json(req)
        self.assertEqual(len(data['descriptions']), 2)
        self.assertEqual(data['descriptions'][0]['text'], self._telugu_text)
        self.assertEqual(data['descriptions'][0]['languageTypeId'], self._telugu_language_type)
        self.assertEqual(data['descriptions'][0]['scriptTypeId'], self._telugu_script_type)
        self.assertEqual(data['descriptions'][1]['text'], self._hindi_text)
        self.assertEqual(data['descriptions'][1]['languageTypeId'], self._hindi_language_type)
        self.assertEqual(data['descriptions'][1]['scriptTypeId'], self._hindi_script_type)

    def test_item_details_has_all_languages_for_display_name(self):
        item = self.create_mc_multi_select_item()
        url = '{0}/items/{1}'.format(self.url,
                                     unquote(item['id']))
        payload = {
            'name': self._hindi_text
        }
        req = self.app.put(url,
                           params=json.dumps(payload),
                           headers=self._hindi_headers())
        self.ok(req)

        req = self.app.get(url)
        self.ok(req)
        data = self.json(req)
        self.assertIn('displayNames', data)
        self.assertEqual(len(data['displayNames']), 2)

    def test_setting_proxy_header_gets_display_name_in_specified_language(self):
        item = self.create_mc_multi_select_item()
        url = '{0}/items/{1}'.format(self.url,
                                     unquote(item['id']))
        payload = {
            'name': self._hindi_text
        }
        req = self.app.put(url,
                           params=json.dumps(payload),
                           headers=self._hindi_headers())
        self.ok(req)

        req = self.app.get(url,
                           headers=self._hindi_headers())
        self.ok(req)
        data = self.json(req)
        self.assertIn('displayNames', data)
        self.assertEqual(len(data['displayNames']), 2)
        self.assertEqual(data['displayName']['text'], self._hindi_text)
        self.assertEqual(data['displayName']['languageTypeId'], self._hindi_language_type)
        self.assertEqual(data['displayName']['scriptTypeId'], self._hindi_script_type)

    def test_english_default_display_name_if_header_language_code_not_available(self):
        item = self.create_mc_multi_select_item()
        original_display_name = item['displayName']['text']
        url = '{0}/items/{1}'.format(self.url,
                                     unquote(item['id']))
        payload = {
            'name': self._hindi_text
        }
        req = self.app.put(url,
                           params=json.dumps(payload),
                           headers=self._hindi_headers())
        self.ok(req)

        req = self.app.get(url,
                           headers=self._telugu_headers())
        self.ok(req)
        data = self.json(req)
        self.assertIn('displayNames', data)
        self.assertEqual(len(data['displayNames']), 2)
        self.assertEqual(data['displayName']['text'], original_display_name)
        self.assertEqual(data['displayName']['languageTypeId'], self._english_language_type)
        self.assertEqual(data['displayName']['scriptTypeId'], self._english_script_type)

    def test_first_available_display_name_if_header_language_code_and_english_not_available(self):
        item = self.create_mc_multi_select_item()
        url = '{0}/items/{1}'.format(self.url,
                                     unquote(item['id']))
        payload = {
            'name': self._hindi_text
        }
        req = self.app.put(url,
                           params=json.dumps(payload),
                           headers=self._hindi_headers())
        self.ok(req)
        data = self.json(req)
        self.assertEqual(len(data['displayNames']), 2)
        self.assertEqual(data['displayNames'][1]['text'], self._hindi_text)
        self.assertEqual(data['displayNames'][1]['languageTypeId'], self._hindi_language_type)
        self.assertEqual(data['displayNames'][1]['scriptTypeId'], self._hindi_script_type)

        payload = {
            'removeName': data['displayNames'][0]
        }
        req = self.app.put(url,
                           params=json.dumps(payload),
                           headers=self._hindi_headers())
        self.ok(req)

        req = self.app.get(url,
                           headers=self._telugu_headers())
        self.ok(req)
        data = self.json(req)
        self.assertEqual(len(data['displayNames']), 1)
        self.assertEqual(data['displayNames'][0]['text'], self._hindi_text)
        self.assertEqual(data['displayNames'][0]['languageTypeId'], self._hindi_language_type)
        self.assertEqual(data['displayNames'][0]['scriptTypeId'], self._hindi_script_type)

    def test_item_details_has_all_languages_for_description(self):
        item = self.create_mc_multi_select_item()
        url = '{0}/items/{1}'.format(self.url,
                                     unquote(item['id']))
        payload = {
            'description': self._hindi_text
        }
        req = self.app.put(url,
                           params=json.dumps(payload),
                           headers=self._hindi_headers())
        self.ok(req)

        req = self.app.get(url)
        self.ok(req)
        data = self.json(req)
        self.assertIn('descriptions', data)
        self.assertEqual(len(data['descriptions']), 2)

    def test_setting_proxy_header_gets_description_in_specified_language(self):
        item = self.create_mc_multi_select_item()
        url = '{0}/items/{1}'.format(self.url,
                                     unquote(item['id']))
        payload = {
            'description': self._hindi_text
        }
        req = self.app.put(url,
                           params=json.dumps(payload),
                           headers=self._hindi_headers())
        self.ok(req)

        req = self.app.get(url,
                           headers=self._hindi_headers())
        self.ok(req)
        data = self.json(req)
        self.assertIn('descriptions', data)
        self.assertEqual(len(data['descriptions']), 2)
        self.assertEqual(data['description']['text'], self._hindi_text)
        self.assertEqual(data['description']['languageTypeId'], self._hindi_language_type)
        self.assertEqual(data['description']['scriptTypeId'], self._hindi_script_type)

    def test_english_default_description_if_header_language_code_not_available(self):
        item = self.create_mc_multi_select_item()
        original_description = item['description']['text']
        url = '{0}/items/{1}'.format(self.url,
                                     unquote(item['id']))
        payload = {
            'description': self._hindi_text
        }
        req = self.app.put(url,
                           params=json.dumps(payload),
                           headers=self._hindi_headers())
        self.ok(req)

        req = self.app.get(url,
                           headers=self._telugu_headers())
        self.ok(req)
        data = self.json(req)
        self.assertIn('descriptions', data)
        self.assertEqual(len(data['descriptions']), 2)
        self.assertEqual(data['description']['text'], original_description)
        self.assertEqual(data['description']['languageTypeId'], self._english_language_type)
        self.assertEqual(data['description']['scriptTypeId'], self._english_script_type)

    def test_first_available_description_if_header_language_code_and_english_not_available(self):
        item = self.create_mc_multi_select_item()
        url = '{0}/items/{1}'.format(self.url,
                                     unquote(item['id']))
        payload = {
            'description': self._hindi_text
        }
        req = self.app.put(url,
                           params=json.dumps(payload),
                           headers=self._hindi_headers())
        self.ok(req)
        data = self.json(req)
        self.assertEqual(len(data['descriptions']), 2)
        self.assertEqual(data['descriptions'][1]['text'], self._hindi_text)
        self.assertEqual(data['descriptions'][1]['languageTypeId'], self._hindi_language_type)
        self.assertEqual(data['descriptions'][1]['scriptTypeId'], self._hindi_script_type)

        payload = {
            'removeDescription': data['descriptions'][0]
        }
        req = self.app.put(url,
                           params=json.dumps(payload),
                           headers=self._hindi_headers())
        self.ok(req)

        req = self.app.get(url,
                           headers=self._telugu_headers())
        self.ok(req)
        data = self.json(req)
        self.assertEqual(len(data['descriptions']), 1)
        self.assertEqual(data['descriptions'][0]['text'], self._hindi_text)
        self.assertEqual(data['descriptions'][0]['languageTypeId'], self._hindi_language_type)
        self.assertEqual(data['descriptions'][0]['scriptTypeId'], self._hindi_script_type)

    def test_can_set_multiple_question_texts(self):
        item = self.create_mc_multi_select_item()
        url = '{0}/items/{1}'.format(self.url,
                                     unquote(item['id']))
        payload = {
            'question': {
                'questionString': self._hindi_text,
                'type': 'qti'
            }
        }
        req = self.app.put(url,
                           params=json.dumps(payload),
                           headers=self._hindi_headers())
        self.ok(req)
        data = self.json(req)
        self.assertEqual(len(data['question']['texts']), 2)
        self.assertEqual(data['question']['texts'][1]['text'], self._hindi_text)
        self.assertEqual(data['question']['texts'][1]['languageTypeId'], self._hindi_language_type)
        self.assertEqual(data['question']['texts'][1]['scriptTypeId'], self._hindi_script_type)

    def test_sending_an_existing_language_replaces_question_text(self):
        item = self.create_mc_multi_select_item()
        url = '{0}/items/{1}'.format(self.url,
                                     unquote(item['id']))
        payload = {
            'question': {
                'questionString': self._hindi_text,
                'type': 'qti'
            }
        }
        req = self.app.put(url,
                           params=json.dumps(payload),
                           headers=self._english_headers())
        self.ok(req)
        data = self.json(req)
        self.assertEqual(len(data['question']['texts']), 1)
        self.assertEqual(data['question']['texts'][0]['text'], self._hindi_text)
        self.assertEqual(data['question']['texts'][0]['languageTypeId'], self._english_language_type)
        self.assertEqual(data['question']['texts'][0]['scriptTypeId'], self._english_script_type)

    def test_can_remove_a_question_text(self):
        item = self.create_mc_multi_select_item()
        url = '{0}/items/{1}'.format(self.url,
                                     unquote(item['id']))
        payload = {
            'question': {
                'questionString': self._hindi_text,
                'type': 'qti'
            }
        }
        req = self.app.put(url,
                           params=json.dumps(payload),
                           headers=self._hindi_headers())
        self.ok(req)
        data = self.json(req)
        self.assertEqual(len(data['question']['texts']), 2)
        self.assertEqual(data['question']['texts'][1]['text'], self._hindi_text)
        self.assertEqual(data['question']['texts'][1]['languageTypeId'], self._hindi_language_type)
        self.assertEqual(data['question']['texts'][1]['scriptTypeId'], self._hindi_script_type)

        payload = {
            'question': {
                'removeQuestionString': data['question']['texts'][0],
                'type': 'qti'
            }
        }
        req = self.app.put(url,
                           params=json.dumps(payload),
                           headers=self._hindi_headers())
        self.ok(req)
        data = self.json(req)
        self.assertEqual(len(data['question']['texts']), 1)
        self.assertEqual(data['question']['texts'][0]['text'], self._hindi_text)
        self.assertEqual(data['question']['texts'][0]['languageTypeId'], self._hindi_language_type)
        self.assertEqual(data['question']['texts'][0]['scriptTypeId'], self._hindi_script_type)

    def test_can_replace_a_question_text(self):
        item = self.create_mc_multi_select_item()
        url = '{0}/items/{1}'.format(self.url,
                                     unquote(item['id']))
        payload = {
            'question': {
                'questionString': self._hindi_text,
                'type': 'qti'
            }
        }
        req = self.app.put(url,
                           params=json.dumps(payload),
                           headers=self._hindi_headers())
        self.ok(req)
        data = self.json(req)
        self.assertEqual(len(data['question']['texts']), 2)
        self.assertEqual(data['question']['texts'][1]['text'], self._hindi_text)
        self.assertEqual(data['question']['texts'][1]['languageTypeId'], self._hindi_language_type)
        self.assertEqual(data['question']['texts'][1]['scriptTypeId'], self._hindi_script_type)

        payload = {
            'question': {
                'newQuestionString': self._telugu_text,
                'oldQuestionString': data['question']['texts'][0],
                'type': 'qti'
            }
        }
        req = self.app.put(url,
                           params=json.dumps(payload),
                           headers=self._telugu_headers())
        self.ok(req)
        data = self.json(req)
        self.assertEqual(len(data['question']['texts']), 2)
        self.assertEqual(data['question']['texts'][0]['text'], self._telugu_text)
        self.assertEqual(data['question']['texts'][0]['languageTypeId'], self._telugu_language_type)
        self.assertEqual(data['question']['texts'][0]['scriptTypeId'], self._telugu_script_type)
        self.assertEqual(data['question']['texts'][1]['text'], self._hindi_text)
        self.assertEqual(data['question']['texts'][1]['languageTypeId'], self._hindi_language_type)
        self.assertEqual(data['question']['texts'][1]['scriptTypeId'], self._hindi_script_type)

    def test_can_query_items_by_display_name(self):
        item = self.create_mc_feedback_item()
        url = '{0}/items?displayNames=ee_u1l01a04q03'.format(self.url)
        req = self.app.get(url)
        self.ok(req)
        data = self.json(req)
        self.assertEqual(len(data), 1)
        self.assertEqual(data[0]['id'], item['id'])

        url = '{0}/items?displayNames=foo'.format(self.url)
        req = self.app.get(url)
        self.ok(req)
        data = self.json(req)
        self.assertEqual(len(data), 0)

    def test_can_set_multiple_answer_feedbacks(self):
        item = self.create_mc_multi_select_item()
        url = '{0}/items/{1}'.format(self.url,
                                     unquote(item['id']))
        payload = {
            'answers': [{
                'id': item['answers'][0]['id'],
                'feedback': self._hindi_text,
                'type': 'qti'
            }]
        }
        req = self.app.put(url,
                           params=json.dumps(payload),
                           headers=self._hindi_headers())
        self.ok(req)
        data = self.json(req)
        self.assertEqual(len(data['answers'][0]['feedbacks']), 2)
        self.assertEqual(data['answers'][0]['feedbacks'][1]['text'], self._hindi_text)
        self.assertEqual(data['answers'][0]['feedbacks'][1]['languageTypeId'], self._hindi_language_type)
        self.assertEqual(data['answers'][0]['feedbacks'][1]['scriptTypeId'], self._hindi_script_type)
        self.assertEqual(data['answers'][0]['feedbacks'][0]['languageTypeId'], self._english_language_type)
        self.assertEqual(data['answers'][0]['feedbacks'][0]['scriptTypeId'], self._english_script_type)

        # Hindi because the PUT request was with Hindi headers
        self.assertEqual(data['answers'][0]['feedback']['text'], self._hindi_text)
        self.assertEqual(data['answers'][0]['feedback']['languageTypeId'], self._hindi_language_type)
        self.assertEqual(data['answers'][0]['feedback']['scriptTypeId'], self._hindi_script_type)

    def test_sending_an_existing_language_replaces_answer_feedback(self):
        item = self.create_mc_multi_select_item()
        url = '{0}/items/{1}'.format(self.url,
                                     unquote(item['id']))
        payload = {
            'answers': [{
                'id': item['answers'][0]['id'],
                'feedback': self._hindi_text,
                'type': 'qti'
            }]
        }
        req = self.app.put(url,
                           params=json.dumps(payload),
                           headers=self._english_headers())
        self.ok(req)
        data = self.json(req)
        self.assertEqual(len(data['answers'][0]['feedbacks']), 1)
        self.assertEqual(data['answers'][0]['feedbacks'][0]['text'], self._hindi_text)
        self.assertEqual(data['answers'][0]['feedbacks'][0]['languageTypeId'], self._english_language_type)
        self.assertEqual(data['answers'][0]['feedbacks'][0]['scriptTypeId'], self._english_script_type)

    def test_can_remove_an_answer_feedback(self):
        item = self.create_mc_multi_select_item()
        url = '{0}/items/{1}'.format(self.url,
                                     unquote(item['id']))
        payload = {
            'answers': [{
                'id': item['answers'][0]['id'],
                'feedback': self._hindi_text,
                'type': 'qti'
            }]
        }
        req = self.app.put(url,
                           params=json.dumps(payload),
                           headers=self._hindi_headers())
        self.ok(req)

        payload = {
            'answers': [{
                'id': item['answers'][0]['id'],
                'removeFeedback': item['answers'][0]['feedbacks'][0],
                'type': 'qti'
            }]
        }
        req = self.app.put(url,
                           params=json.dumps(payload),
                           headers=self._english_headers())
        self.ok(req)
        data = self.json(req)
        self.assertEqual(len(data['answers'][0]['feedbacks']), 1)
        self.assertEqual(data['answers'][0]['feedbacks'][0]['text'], self._hindi_text)
        self.assertEqual(data['answers'][0]['feedbacks'][0]['languageTypeId'], self._hindi_language_type)
        self.assertEqual(data['answers'][0]['feedbacks'][0]['scriptTypeId'], self._hindi_script_type)

    def test_can_replace_an_answer_feedback(self):
        item = self.create_mc_multi_select_item()
        url = '{0}/items/{1}'.format(self.url,
                                     unquote(item['id']))
        payload = {
            'answers': [{
                'id': item['answers'][0]['id'],
                'feedback': self._hindi_text,
                'type': 'qti'
            }]
        }
        req = self.app.put(url,
                           params=json.dumps(payload),
                           headers=self._hindi_headers())
        self.ok(req)

        payload = {
            'answers': [{
                'id': item['answers'][0]['id'],
                'newFeedback': self._telugu_text,
                'oldFeedback': item['answers'][0]['feedbacks'][0],
                'type': 'qti'
            }]
        }
        req = self.app.put(url,
                           params=json.dumps(payload),
                           headers=self._telugu_headers())
        self.ok(req)
        data = self.json(req)
        self.assertEqual(len(data['answers'][0]['feedbacks']), 2)
        self.assertEqual(data['answers'][0]['feedbacks'][1]['text'], self._hindi_text)
        self.assertEqual(data['answers'][0]['feedbacks'][1]['languageTypeId'], self._hindi_language_type)
        self.assertEqual(data['answers'][0]['feedbacks'][1]['scriptTypeId'], self._hindi_script_type)
        self.assertEqual(data['answers'][0]['feedbacks'][0]['text'], self._telugu_text)
        self.assertEqual(data['answers'][0]['feedbacks'][0]['languageTypeId'], self._telugu_language_type)
        self.assertEqual(data['answers'][0]['feedbacks'][0]['scriptTypeId'], self._telugu_script_type)

    def test_can_set_choice_texts(self):
        item = self.create_mc_multi_select_item()
        url = '{0}/items/{1}'.format(self.url,
                                     unquote(item['id']))
        payload = {
            'question': {
                'choices': [{
                    'id': item['question']['choices'][0]['id'],
                    'text': self._hindi_text
                }],
                'type': 'qti'
            }
        }
        req = self.app.put(url,
                           params=json.dumps(payload),
                           headers=self._hindi_headers())
        self.ok(req)
        data = self.json(req)
        self.assertEqual(len(data['question']['multiLanguageChoices'][0]['texts']), 2)
        self.assertEqual(data['question']['multiLanguageChoices'][0]['texts'][1]['text'], self._hindi_text)
        self.assertEqual(data['question']['multiLanguageChoices'][0]['texts'][1]['languageTypeId'], self._hindi_language_type)
        self.assertEqual(data['question']['multiLanguageChoices'][0]['texts'][1]['scriptTypeId'], self._hindi_script_type)

        self.assertEqual(data['question']['choices'][0]['text'], self._hindi_text)
        self.assertEqual(data['question']['choices'][0]['id'],
                         data['question']['multiLanguageChoices'][0]['id'])

    def test_sending_an_existing_language_replaces_choice_text(self):
        item = self.create_mc_multi_select_item()
        url = '{0}/items/{1}'.format(self.url,
                                     unquote(item['id']))
        payload = {
            'question': {
                'choices': [{
                    'id': item['question']['choices'][0]['id'],
                    'text': self._hindi_text
                }],
                'type': 'qti'
            }
        }
        req = self.app.put(url,
                           params=json.dumps(payload),
                           headers=self._english_headers())
        self.ok(req)
        data = self.json(req)
        self.assertEqual(len(data['question']['multiLanguageChoices'][0]['texts']), 1)
        self.assertEqual(data['question']['multiLanguageChoices'][0]['texts'][0]['text'], self._hindi_text)
        self.assertEqual(data['question']['multiLanguageChoices'][0]['texts'][0]['languageTypeId'], self._english_language_type)
        self.assertEqual(data['question']['multiLanguageChoices'][0]['texts'][0]['scriptTypeId'], self._english_script_type)

    def test_can_remove_choice_texts(self):
        item = self.create_mc_multi_select_item()
        url = '{0}/items/{1}'.format(self.url,
                                     unquote(item['id']))
        payload = {
            'question': {
                'choices': [{
                    'id': item['question']['choices'][0]['id'],
                    'text': self._hindi_text
                }],
                'type': 'qti'
            }
        }
        req = self.app.put(url,
                           params=json.dumps(payload),
                           headers=self._hindi_headers())
        self.ok(req)

        payload = {
            'question': {
                'choices': [{
                    'id': item['question']['multiLanguageChoices'][0]['id'],
                    'removeText': item['question']['multiLanguageChoices'][0]['texts'][0]
                }],
                'type': 'qti'
            }
        }
        req = self.app.put(url,
                           params=json.dumps(payload),
                           headers=self._hindi_headers())
        self.ok(req)
        data = self.json(req)
        self.assertEqual(len(data['question']['multiLanguageChoices'][0]['texts']), 1)
        self.assertEqual(data['question']['multiLanguageChoices'][0]['texts'][0]['text'], self._hindi_text)
        self.assertEqual(data['question']['multiLanguageChoices'][0]['texts'][0]['languageTypeId'], self._hindi_language_type)
        self.assertEqual(data['question']['multiLanguageChoices'][0]['texts'][0]['scriptTypeId'], self._hindi_script_type)

    def test_can_replace_choice_text(self):
        item = self.create_mc_multi_select_item()
        url = '{0}/items/{1}'.format(self.url,
                                     unquote(item['id']))
        payload = {
            'question': {
                'choices': [{
                    'id': item['question']['choices'][0]['id'],
                    'text': self._hindi_text
                }],
                'type': 'qti'
            }
        }
        req = self.app.put(url,
                           params=json.dumps(payload),
                           headers=self._hindi_headers())
        self.ok(req)

        payload = {
            'question': {
                'choices': [{
                    'id': item['question']['multiLanguageChoices'][0]['id'],
                    'newText': self._telugu_text,
                    'oldText': item['question']['multiLanguageChoices'][0]['texts'][0]
                }],
                'type': 'qti'
            }
        }
        req = self.app.put(url,
                           params=json.dumps(payload),
                           headers=self._telugu_headers())
        self.ok(req)
        data = self.json(req)
        self.assertEqual(len(data['question']['multiLanguageChoices'][0]['texts']), 2)
        self.assertEqual(data['question']['multiLanguageChoices'][0]['texts'][0]['text'], self._telugu_text)
        self.assertEqual(data['question']['multiLanguageChoices'][0]['texts'][0]['languageTypeId'], self._telugu_language_type)
        self.assertEqual(data['question']['multiLanguageChoices'][0]['texts'][0]['scriptTypeId'], self._telugu_script_type)

        self.assertEqual(data['question']['multiLanguageChoices'][0]['texts'][1]['text'], self._hindi_text)
        self.assertEqual(data['question']['multiLanguageChoices'][0]['texts'][1]['languageTypeId'], self._hindi_language_type)
        self.assertEqual(data['question']['multiLanguageChoices'][0]['texts'][1]['scriptTypeId'], self._hindi_script_type)

    def test_can_set_inline_choice_texts(self):
        item = self.create_fitb_item()
        url = '{0}/items/{1}'.format(self.url,
                                     unquote(item['id']))
        region = "RESPONSE_1"
        desired_choice_id = item['question']['multiLanguageChoices'][region][0]['id']

        payload = {
            'question': {
                'inlineRegions': {
                    region: {
                        'choices': [{
                            'id': desired_choice_id,
                            'text': self._hindi_text
                        }],
                    }
                },
                'type': 'qti'
            }
        }
        req = self.app.put(url,
                           params=json.dumps(payload),
                           headers=self._hindi_headers())
        self.ok(req)
        data = self.json(req)

        self.assertEqual(len(data['question']['multiLanguageChoices'][region][0]['texts']), 2)
        self.assertEqual(data['question']['multiLanguageChoices'][region][0]['texts'][1]['text'], self._hindi_text)
        self.assertEqual(data['question']['multiLanguageChoices'][region][0]['texts'][1]['languageTypeId'], self._hindi_language_type)
        self.assertEqual(data['question']['multiLanguageChoices'][region][0]['texts'][1]['scriptTypeId'], self._hindi_script_type)

        # because the choices are randomized
        matching_choice = [c for c in data['question']['choices'][region] if c['id'] == desired_choice_id][0]

        self.assertEqual(matching_choice['text'], self._hindi_text)

    def test_sending_an_existing_language_replaces_inline_choice_text(self):
        item = self.create_fitb_item()
        region = "RESPONSE_1"
        desired_choice_id = item['question']['multiLanguageChoices'][region][0]['id']

        url = '{0}/items/{1}'.format(self.url,
                                     unquote(item['id']))
        payload = {
            'question': {
                'inlineRegions': {
                    region: {
                        'choices': [{
                            'id': desired_choice_id,
                            'text': self._hindi_text
                        }],
                    }
                },
                'type': 'qti'
            }
        }
        req = self.app.put(url,
                           params=json.dumps(payload),
                           headers=self._english_headers())
        self.ok(req)
        data = self.json(req)
        self.assertEqual(len(data['question']['multiLanguageChoices'][region][0]['texts']), 1)
        self.assertEqual(data['question']['multiLanguageChoices'][region][0]['texts'][0]['text'], self._hindi_text)
        self.assertEqual(data['question']['multiLanguageChoices'][region][0]['texts'][0]['languageTypeId'], self._english_language_type)
        self.assertEqual(data['question']['multiLanguageChoices'][region][0]['texts'][0]['scriptTypeId'], self._english_script_type)

    def test_can_remove_inline_choice_texts(self):
        item = self.create_fitb_item()
        url = '{0}/items/{1}'.format(self.url,
                                     unquote(item['id']))
        region = "RESPONSE_1"
        desired_choice_id = item['question']['multiLanguageChoices'][region][0]['id']

        payload = {
            'question': {
                'inlineRegions': {
                    region: {
                        'choices': [{
                            'id': desired_choice_id,
                            'text': self._hindi_text
                        }],
                    }
                },
                'type': 'qti'
            }
        }
        req = self.app.put(url,
                           params=json.dumps(payload),
                           headers=self._hindi_headers())
        self.ok(req)

        payload = {
            'question': {
                'inlineRegions': {
                    region: {
                        'choices': [{
                            'id': desired_choice_id,
                            'removeText': item['question']['multiLanguageChoices'][region][0]['texts'][0]
                        }],
                    }
                },
                'type': 'qti'
            }
        }
        req = self.app.put(url,
                           params=json.dumps(payload),
                           headers=self._hindi_headers())
        self.ok(req)
        data = self.json(req)

        self.assertEqual(len(data['question']['multiLanguageChoices'][region][0]['texts']), 1)
        self.assertEqual(data['question']['multiLanguageChoices'][region][0]['texts'][0]['text'], self._hindi_text)
        self.assertEqual(data['question']['multiLanguageChoices'][region][0]['texts'][0]['languageTypeId'], self._hindi_language_type)
        self.assertEqual(data['question']['multiLanguageChoices'][region][0]['texts'][0]['scriptTypeId'], self._hindi_script_type)

        # because the choices are randomized
        matching_choice = [c for c in data['question']['choices'][region] if c['id'] == desired_choice_id][0]

        self.assertEqual(matching_choice['text'], self._hindi_text)

    def test_can_replace_inline_choice_text(self):
        item = self.create_fitb_item()
        url = '{0}/items/{1}'.format(self.url,
                                     unquote(item['id']))
        region = "RESPONSE_1"
        desired_choice_id = item['question']['multiLanguageChoices'][region][0]['id']

        payload = {
            'question': {
                'inlineRegions': {
                    region: {
                        'choices': [{
                            'id': desired_choice_id,
                            'text': self._hindi_text
                        }],
                    }
                },
                'type': 'qti'
            }
        }
        req = self.app.put(url,
                           params=json.dumps(payload),
                           headers=self._hindi_headers())
        self.ok(req)

        payload = {
            'question': {
                'inlineRegions': {
                    region: {
                        'choices': [{
                            'id': desired_choice_id,
                            'newText': self._telugu_text,
                            'oldText': item['question']['multiLanguageChoices'][region][0]['texts'][0]
                        }],
                    }
                },
                'type': 'qti'
            }
        }
        req = self.app.put(url,
                           params=json.dumps(payload),
                           headers=self._telugu_headers())
        self.ok(req)
        data = self.json(req)

        self.assertEqual(len(data['question']['multiLanguageChoices'][region][0]['texts']), 2)
        self.assertEqual(data['question']['multiLanguageChoices'][region][0]['texts'][0]['text'], self._telugu_text)
        self.assertEqual(data['question']['multiLanguageChoices'][region][0]['texts'][0]['languageTypeId'], self._telugu_language_type)
        self.assertEqual(data['question']['multiLanguageChoices'][region][0]['texts'][0]['scriptTypeId'], self._telugu_script_type)
        self.assertEqual(data['question']['multiLanguageChoices'][region][0]['texts'][1]['text'], self._hindi_text)
        self.assertEqual(data['question']['multiLanguageChoices'][region][0]['texts'][1]['languageTypeId'], self._hindi_language_type)
        self.assertEqual(data['question']['multiLanguageChoices'][region][0]['texts'][1]['scriptTypeId'], self._hindi_script_type)

        # because the choices are randomized
        matching_choice = [c for c in data['question']['choices'][region] if c['id'] == desired_choice_id][0]

        self.assertEqual(matching_choice['text'], self._telugu_text)

    def test_answer_feedback_from_taken_follows_proxy_locale(self):
        item = self.create_mc_multi_select_item()
        url = '{0}/items/{1}'.format(self.url,
                                     unquote(item['id']))
        payload = {
            'answers': [{
                'id': item['answers'][0]['id'],
                'feedback': self._hindi_text,
                'type': 'qti'
            }]
        }
        req = self.app.put(url,
                           params=json.dumps(payload),
                           headers=self._hindi_headers())
        self.ok(req)

        payload = {
            'answers': [{
                'id': item['answers'][0]['id'],
                'feedback': self._telugu_text,
                'type': 'qti'
            }]
        }
        req = self.app.put(url,
                           params=json.dumps(payload),
                           headers=self._telugu_headers())
        self.ok(req)
        data = self.json(req)
        self.assertEqual(len(data['answers'][0]['feedbacks']), 3)
        self.assertEqual(data['answers'][0]['feedbacks'][2]['text'], self._telugu_text)
        self.assertEqual(data['answers'][0]['feedbacks'][2]['languageTypeId'], self._telugu_language_type)
        self.assertEqual(data['answers'][0]['feedbacks'][2]['scriptTypeId'], self._telugu_script_type)
        self.assertEqual(data['answers'][0]['feedbacks'][1]['text'], self._hindi_text)
        self.assertEqual(data['answers'][0]['feedbacks'][1]['languageTypeId'], self._hindi_language_type)
        self.assertEqual(data['answers'][0]['feedbacks'][1]['scriptTypeId'], self._hindi_script_type)
        self.assertEqual(data['answers'][0]['feedbacks'][0]['languageTypeId'], self._english_language_type)
        self.assertEqual(data['answers'][0]['feedbacks'][0]['scriptTypeId'], self._english_script_type)

        taken, offered = self.create_taken_for_item(self._bank.ident, item['id'])

        url = '{0}/assessmentstaken/{1}/questions'.format(self.url,
                                                          unquote(str(taken.ident)))
        req = self.app.get(url)
        self.ok(req)
        data = self.json(req)
        question_1_id = data['data'][0]['id']

        url = '{0}/{1}/submit'.format(url,
                                      question_1_id)
        payload = {
            'choiceIds': ['idb5345daa-a5c2-4924-a92b-e326886b5d1d',
                          'id47e56db8-ee16-4111-9bcc-b8ac9716bcd4',
                          'id4f525d00-e24c-4ac3-a104-848a2cd686c0'],
            'type': 'answer-type%3Aqti-choice-interaction-multi-select%40ODL.MIT.EDU'
        }
        req = self.app.post(url,
                            params=json.dumps(payload),
                            headers=self._hindi_headers())
        self.ok(req)
        data = self.json(req)
        self.assertTrue(data['correct'])
        self.assertIn(self._hindi_text, data['feedback'])

        req = self.app.post(url,
                            params=json.dumps(payload),
                            headers=self._telugu_headers())
        self.ok(req)
        data = self.json(req)
        self.assertTrue(data['correct'])
        self.assertIn(self._telugu_text, data['feedback'])

    def test_answer_feedback_english_default_if_header_language_code_not_available(self):
        item = self.create_mc_multi_select_item()
        url = '{0}/items/{1}'.format(self.url,
                                     unquote(item['id']))
        payload = {
            'answers': [{
                'id': item['answers'][0]['id'],
                'newFeedback': self._english_text,
                'oldFeedback': item['answers'][0]['feedbacks'][0],
                'type': 'qti'
            }]
        }
        req = self.app.put(url,
                           params=json.dumps(payload),
                           headers=self._english_headers())
        self.ok(req)
        data = self.json(req)
        self.assertEqual(len(data['answers'][0]['feedbacks']), 1)
        self.assertEqual(data['answers'][0]['feedbacks'][0]['text'], self._english_text)
        self.assertEqual(data['answers'][0]['feedbacks'][0]['languageTypeId'], self._english_language_type)
        self.assertEqual(data['answers'][0]['feedbacks'][0]['scriptTypeId'], self._english_script_type)

        taken, offered = self.create_taken_for_item(self._bank.ident, item['id'])

        url = '{0}/assessmentstaken/{1}/questions'.format(self.url,
                                                          unquote(str(taken.ident)))
        req = self.app.get(url)
        self.ok(req)
        data = self.json(req)
        question_1_id = data['data'][0]['id']

        url = '{0}/{1}/submit'.format(url,
                                      question_1_id)
        payload = {
            'choiceIds': ['idb5345daa-a5c2-4924-a92b-e326886b5d1d',
                          'id47e56db8-ee16-4111-9bcc-b8ac9716bcd4',
                          'id4f525d00-e24c-4ac3-a104-848a2cd686c0'],
            'type': 'answer-type%3Aqti-choice-interaction-multi-select%40ODL.MIT.EDU'
        }
        req = self.app.post(url,
                            params=json.dumps(payload),
                            headers=self._hindi_headers())
        self.ok(req)
        data = self.json(req)
        self.assertTrue(data['correct'])
        self.assertIn(self._english_text, data['feedback'])

        req = self.app.post(url,
                            params=json.dumps(payload),
                            headers=self._telugu_headers())
        self.ok(req)
        data = self.json(req)
        self.assertTrue(data['correct'])
        self.assertIn(self._english_text, data['feedback'])

    def test_answer_feedback_first_available_if_header_language_code_and_english_not_available(self):
        item = self.create_mc_multi_select_item()
        url = '{0}/items/{1}'.format(self.url,
                                     unquote(item['id']))
        payload = {
            'answers': [{
                'id': item['answers'][0]['id'],
                'newFeedback': self._telugu_text,
                'oldFeedback': item['answers'][0]['feedbacks'][0],
                'type': 'qti'
            }]
        }
        req = self.app.put(url,
                           params=json.dumps(payload),
                           headers=self._telugu_headers())
        self.ok(req)
        data = self.json(req)
        self.assertEqual(len(data['answers'][0]['feedbacks']), 1)
        self.assertEqual(data['answers'][0]['feedbacks'][0]['text'], self._telugu_text)
        self.assertEqual(data['answers'][0]['feedbacks'][0]['languageTypeId'], self._telugu_language_type)
        self.assertEqual(data['answers'][0]['feedbacks'][0]['scriptTypeId'], self._telugu_script_type)

        taken, offered = self.create_taken_for_item(self._bank.ident, item['id'])

        url = '{0}/assessmentstaken/{1}/questions'.format(self.url,
                                                          unquote(str(taken.ident)))
        req = self.app.get(url)
        self.ok(req)
        data = self.json(req)
        question_1_id = data['data'][0]['id']

        url = '{0}/{1}/submit'.format(url,
                                      question_1_id)
        payload = {
            'choiceIds': ['idb5345daa-a5c2-4924-a92b-e326886b5d1d',
                          'id47e56db8-ee16-4111-9bcc-b8ac9716bcd4',
                          'id4f525d00-e24c-4ac3-a104-848a2cd686c0'],
            'type': 'answer-type%3Aqti-choice-interaction-multi-select%40ODL.MIT.EDU'
        }
        req = self.app.post(url,
                            params=json.dumps(payload),
                            headers=self._hindi_headers())
        self.ok(req)
        data = self.json(req)
        self.assertTrue(data['correct'])
        self.assertIn(self._telugu_text, data['feedback'])

        req = self.app.post(url,
                            params=json.dumps(payload),
                            headers=self._english_headers())
        self.ok(req)
        data = self.json(req)
        self.assertTrue(data['correct'])
        self.assertIn(self._telugu_text, data['feedback'])

    def test_setting_proxy_header_gets_item_in_specified_language_in_taken(self):
        item = self.create_mc_multi_select_item()
        url = '{0}/items/{1}'.format(self.url,
                                     unquote(item['id']))
        payload = {
            'question': {
                'questionString': self._hindi_text,
                'type': 'qti'
            }
        }
        req = self.app.put(url,
                           params=json.dumps(payload),
                           headers=self._hindi_headers())
        self.ok(req)

        payload = {
            'question': {
                'questionString': self._telugu_text,
                'type': 'qti'
            }
        }
        req = self.app.put(url,
                           params=json.dumps(payload),
                           headers=self._telugu_headers())
        self.ok(req)

        payload = {
            'question': {
                'newQuestionString': self._english_text,
                'oldQuestionString': item['question']['texts'][0],
                'type': 'qti'
            }
        }
        req = self.app.put(url,
                           params=json.dumps(payload),
                           headers=self._english_headers())
        self.ok(req)

        data = self.json(req)
        self.assertEqual(len(data['question']['texts']), 3)
        self.assertEqual(data['question']['texts'][2]['text'], self._telugu_text)
        self.assertEqual(data['question']['texts'][2]['languageTypeId'], self._telugu_language_type)
        self.assertEqual(data['question']['texts'][2]['scriptTypeId'], self._telugu_script_type)
        self.assertEqual(data['question']['texts'][1]['text'], self._hindi_text)
        self.assertEqual(data['question']['texts'][1]['languageTypeId'], self._hindi_language_type)
        self.assertEqual(data['question']['texts'][1]['scriptTypeId'], self._hindi_script_type)
        self.assertEqual(data['question']['texts'][0]['text'], self._english_text)
        self.assertEqual(data['question']['texts'][0]['languageTypeId'], self._english_language_type)
        self.assertEqual(data['question']['texts'][0]['scriptTypeId'], self._english_script_type)

        taken, offered = self.create_taken_for_item(self._bank.ident, item['id'])

        url = '{0}/assessmentstaken/{1}/questions'.format(self.url,
                                                          unquote(str(taken.ident)))
        req = self.app.get(url,
                           headers=self._english_headers())
        self.ok(req)
        data = self.json(req)

        self.assertEqual(data['data'][0]['text']['text'], self._english_text)
        self.assertEqual(data['data'][0]['text']['languageTypeId'], self._english_language_type)
        self.assertEqual(data['data'][0]['text']['scriptTypeId'], self._english_script_type)

        req = self.app.get(url,
                           headers=self._hindi_headers())
        self.ok(req)
        data = self.json(req)
        self.assertEqual(data['data'][0]['text']['text'], self._hindi_text)
        self.assertEqual(data['data'][0]['text']['languageTypeId'], self._hindi_language_type)
        self.assertEqual(data['data'][0]['text']['scriptTypeId'], self._hindi_script_type)

        req = self.app.get(url,
                           headers=self._telugu_headers())
        self.ok(req)
        data = self.json(req)
        self.assertEqual(data['data'][0]['text']['text'], self._telugu_text)
        self.assertEqual(data['data'][0]['text']['languageTypeId'], self._telugu_language_type)
        self.assertEqual(data['data'][0]['text']['scriptTypeId'], self._telugu_script_type)

    def test_english_default_if_header_language_code_not_available_in_taken(self):
        item = self.create_mc_multi_select_item()
        url = '{0}/items/{1}'.format(self.url,
                                     unquote(item['id']))

        payload = {
            'question': {
                'newQuestionString': self._english_text,
                'oldQuestionString': item['question']['texts'][0],
                'type': 'qti'
            }
        }
        req = self.app.put(url,
                           params=json.dumps(payload),
                           headers=self._english_headers())
        self.ok(req)

        data = self.json(req)
        self.assertEqual(len(data['question']['texts']), 1)
        self.assertEqual(data['question']['texts'][0]['text'], self._english_text)
        self.assertEqual(data['question']['texts'][0]['languageTypeId'], self._english_language_type)
        self.assertEqual(data['question']['texts'][0]['scriptTypeId'], self._english_script_type)

        taken, offered = self.create_taken_for_item(self._bank.ident, item['id'])

        url = '{0}/assessmentstaken/{1}/questions'.format(self.url,
                                                          unquote(str(taken.ident)))
        req = self.app.get(url,
                           headers=self._english_headers())
        self.ok(req)
        data = self.json(req)

        self.assertEqual(data['data'][0]['text']['text'], self._english_text)
        self.assertEqual(data['data'][0]['text']['languageTypeId'], self._english_language_type)
        self.assertEqual(data['data'][0]['text']['scriptTypeId'], self._english_script_type)

        req = self.app.get(url,
                           headers=self._hindi_headers())
        self.ok(req)
        data = self.json(req)
        self.assertEqual(data['data'][0]['text']['text'], self._english_text)
        self.assertEqual(data['data'][0]['text']['languageTypeId'], self._english_language_type)
        self.assertEqual(data['data'][0]['text']['scriptTypeId'], self._english_script_type)

        req = self.app.get(url,
                           headers=self._telugu_headers())
        self.ok(req)
        data = self.json(req)
        self.assertEqual(data['data'][0]['text']['text'], self._english_text)
        self.assertEqual(data['data'][0]['text']['languageTypeId'], self._english_language_type)
        self.assertEqual(data['data'][0]['text']['scriptTypeId'], self._english_script_type)

    def test_first_available_if_header_language_code_and_english_not_available_in_taken(self):
        item = self.create_mc_multi_select_item()
        url = '{0}/items/{1}'.format(self.url,
                                     unquote(item['id']))

        payload = {
            'question': {
                'newQuestionString': self._telugu_text,
                'oldQuestionString': item['question']['texts'][0],
                'type': 'qti'
            }
        }
        req = self.app.put(url,
                           params=json.dumps(payload),
                           headers=self._telugu_headers())
        self.ok(req)

        data = self.json(req)
        self.assertEqual(len(data['question']['texts']), 1)
        self.assertEqual(data['question']['texts'][0]['text'], self._telugu_text)
        self.assertEqual(data['question']['texts'][0]['languageTypeId'], self._telugu_language_type)
        self.assertEqual(data['question']['texts'][0]['scriptTypeId'], self._telugu_script_type)

        taken, offered = self.create_taken_for_item(self._bank.ident, item['id'])

        url = '{0}/assessmentstaken/{1}/questions'.format(self.url,
                                                          unquote(str(taken.ident)))
        req = self.app.get(url,
                           headers=self._english_headers())
        self.ok(req)
        data = self.json(req)

        self.assertEqual(data['data'][0]['text']['text'], self._telugu_text)
        self.assertEqual(data['data'][0]['text']['languageTypeId'], self._telugu_language_type)
        self.assertEqual(data['data'][0]['text']['scriptTypeId'], self._telugu_script_type)

        req = self.app.get(url,
                           headers=self._hindi_headers())
        self.ok(req)
        data = self.json(req)
        self.assertEqual(data['data'][0]['text']['text'], self._telugu_text)
        self.assertEqual(data['data'][0]['text']['languageTypeId'], self._telugu_language_type)
        self.assertEqual(data['data'][0]['text']['scriptTypeId'], self._telugu_script_type)

        req = self.app.get(url,
                           headers=self._telugu_headers())
        self.ok(req)
        data = self.json(req)
        self.assertEqual(data['data'][0]['text']['text'], self._telugu_text)
        self.assertEqual(data['data'][0]['text']['languageTypeId'], self._telugu_language_type)
        self.assertEqual(data['data'][0]['text']['scriptTypeId'], self._telugu_script_type)

    def test_can_add_media_files_to_question(self):
        item = self.create_mc_multi_select_item()

        url = '{0}/items/{1}'.format(self.url,
                                     unquote(item['id']))
        payload = {
            'question': {
                'questionString': self._hindi_text,
                'type': 'qti'
            }
        }
        req = self.app.put(url,
                           params=json.dumps(payload),
                           headers=self._hindi_headers())
        self.ok(req)

        payload = {
            'question': {
                'questionString': self._telugu_text,
                'type': 'qti'
            }
        }
        req = self.app.put(url,
                           params=json.dumps(payload),
                           headers=self._telugu_headers())
        self.ok(req)

        payload = {
            'question': {
                'newQuestionString': self._english_text,
                'oldQuestionString': item['question']['texts'][0],
                'type': 'qti'
            }
        }
        req = self.app.put(url,
                           params=json.dumps(payload),
                           headers=self._english_headers())
        self.ok(req)

        assets_endpoint = '/api/v1/repository/repositories/{0}/assets'.format(unquote(str(self._bank.ident)))
        self._audio_file.seek(0)
        req = self.app.post(assets_endpoint,
                            upload_files=[('inputFile',
                                           self._filename(self._audio_file),
                                           self._audio_file.read())])
        self.ok(req)
        asset = self.json(req)
        label = asset['displayName']['text'].replace('.', '_')

        self.assertNotIn(label, item['question']['fileIds'].keys())

        asset_payload = {
            'question': {
                'fileIds': {
                },
                'type': 'qti'
            }
        }
        asset_payload['question']['fileIds'][label] = {
            'assetId': asset['id'],
            'assetContentId': asset['assetContents'][0]['id'],
            'assetContentTypeId': asset['assetContents'][0]['genusTypeId']
        }

        req = self.app.put(url,
                           params=json.dumps(asset_payload),
                           headers={'content-type': 'application/json'})
        self.ok(req)
        data = self.json(req)
        self.assertIn(label, data['question']['fileIds'].keys())
        self.assertEqual(
            data['question']['fileIds'][label]['assetId'],
            asset['id']
        )
        self.assertEqual(
            data['question']['fileIds'][label]['assetContentId'],
            asset['assetContents'][0]['id']
        )
        self.assertEqual(
            data['question']['fileIds'][label]['assetContentTypeId'],
            asset['assetContents'][0]['genusTypeId']
        )

    def test_item_display_name_has_no_language_code(self):
        item = self.create_mc_feedback_item()
        url = '{0}/items/{1}'.format(self.url,
                                     unquote(item['id']))

        self.assertEqual(item['displayName']['text'], 'ee_u1l01a04q03')
        req = self.app.get(url)
        self.ok(req)
        data = self.json(req)
        self.assertEqual(data['displayName']['text'], 'ee_u1l01a04q03')

    def test_can_set_alias_id_on_update(self):
        item = self.create_mc_multi_select_item()
        url = '{0}/items/{1}'.format(self.url,
                                     unquote(item['id']))

        alias = 'foo%3A1%40MIT.EDU'
        payload = {
            'aliasId': alias
        }
        req = self.app.put(url,
                           params=json.dumps(payload),
                           headers=self._hindi_headers())
        self.ok(req)

        url = '{0}/items/{1}'.format(self.url,
                                     alias)
        req = self.app.get(url)
        self.ok(req)
        data = self.json(req)
        self.assertEqual(data['id'], item['id'])

    def test_multi_language_choices_matches_original_order(self):
        item = self.create_mc_multi_select_item()
        url = '{0}/items/{1}'.format(self.url,
                                     unquote(item['id']))

        at_least_one_difference = False
        for i in range(0, 10):
            req = self.app.get(url)
            self.ok(req)
            data = self.json(req)

            if data['question']['choices'] != data['question']['multiLanguageChoices']:
                at_least_one_difference = True

            original_choice_ids = [c['id'] for c in data['question']['multiLanguageChoices']]
            self.assertEqual(
                original_choice_ids,
                ['idb5345daa-a5c2-4924-a92b-e326886b5d1d',
                 'id47e56db8-ee16-4111-9bcc-b8ac9716bcd4',
                 'id01913fba-e66d-4a01-9625-94102847faac',
                 'id4f525d00-e24c-4ac3-a104-848a2cd686c0',
                 'id18c8cc80-68d1-4c1f-b9f0-cb345bad2862']
            )
        self.assertTrue(at_least_one_difference)

    def test_multi_language_choice_ids_match_original(self):
        item = self.create_mc_multi_select_item()
        url = '{0}/items/{1}'.format(self.url,
                                     unquote(item['id']))

        original_identifier = item['question']['multiLanguageChoices'][0]['id']
        wrong_identifier = u"id4f525d00-e24c-4ac3-a104-111111111"
        hindi_text = u"""<simpleChoice identifier="{0}">
  <p>
    {1}
  </p>
</simpleChoice>""".format(wrong_identifier,
                          self._hindi_text)

        payload = {
            'question': {
                'choices': [{
                    'id': original_identifier,
                    'text': hindi_text
                }],
                'type': 'qti'
            }
        }
        req = self.app.put(url,
                           params=json.dumps(payload),
                           headers=self._hindi_headers())
        self.ok(req)

        url = '{0}/qti'.format(url)
        req = self.app.get(url,
                           headers=self._hindi_headers())
        self.ok(req)

        soup = BeautifulSoup(req.body, 'xml')
        matching_choice = soup.find(identifier=original_identifier)
        self.assertIn(self._hindi_text, unicode(matching_choice))
        self.assertNotIn(wrong_identifier, unicode(soup))
