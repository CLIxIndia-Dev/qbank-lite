# -*- coding: utf-8 -*-
import csv
import json
import os
from urllib import unquote, quote

from bs4 import BeautifulSoup
from paste.fixture import AppError
from sympy import sympify

import utilities
from dlkit_runtime.primordium import Id, Type
from records.assessment.qti.basic import _stringify
from records.registry import ITEM_GENUS_TYPES, ITEM_RECORD_TYPES,\
    ANSWER_RECORD_TYPES, QUESTION_RECORD_TYPES, ANSWER_GENUS_TYPES,\
    ASSESSMENT_OFFERED_RECORD_TYPES, ASSESSMENT_TAKEN_RECORD_TYPES,\
    QUESTION_GENUS_TYPES, ASSESSMENT_RECORD_TYPES
from testing_utilities import BaseTestCase, get_managers, get_fixture_bank,\
    create_new_bank

EDX_ITEM_RECORD_TYPE = Type(**ITEM_RECORD_TYPES['edx_item'])
NUMERIC_RESPONSE_ITEM_GENUS_TYPE = Type(**ITEM_GENUS_TYPES['numeric-response-edx'])
NUMERIC_RESPONSE_ANSWER_RECORD_TYPE = Type(**ANSWER_RECORD_TYPES['numeric-response-edx'])
NUMERIC_RESPONSE_QUESTION_RECORD_TYPE = Type(**QUESTION_RECORD_TYPES['numeric-response-edx'])

RIGHT_ANSWER_GENUS = Type(**ANSWER_GENUS_TYPES['right-answer'])
WRONG_ANSWER_GENUS = Type(**ANSWER_GENUS_TYPES['wrong-answer'])

QTI_ANSWER_CHOICE_INTERACTION_GENUS = Type(**ANSWER_GENUS_TYPES['qti-choice-interaction'])
QTI_ANSWER_CHOICE_INTERACTION_MULTI_GENUS = Type(**ANSWER_GENUS_TYPES['qti-choice-interaction-multi-select'])
QTI_ANSWER_EXTENDED_TEXT_INTERACTION_GENUS = Type(**ANSWER_GENUS_TYPES['qti-extended-text-interaction'])
QTI_ANSWER_INLINE_CHOICE_INTERACTION_GENUS = Type(**ANSWER_GENUS_TYPES['qti-inline-choice-interaction-mw-fill-in-the-blank'])
QTI_ANSWER_NUMERIC_RESPONSE_INTERACTION_GENUS = Type(**ANSWER_GENUS_TYPES['qti-numeric-response'])
QTI_ANSWER_ORDER_INTERACTION_MW_SENTENCE_GENUS = Type(**ANSWER_GENUS_TYPES['qti-order-interaction-mw-sentence'])
QTI_ANSWER_ORDER_INTERACTION_MW_SANDBOX_GENUS = Type(**ANSWER_GENUS_TYPES['qti-order-interaction-mw-sandbox'])
QTI_ANSWER_ORDER_INTERACTION_OBJECT_MANIPULATION_GENUS = Type(**ANSWER_GENUS_TYPES['qti-order-interaction-object-manipulation'])
QTI_ANSWER_UPLOAD_INTERACTION_AUDIO_GENUS = Type(**ANSWER_GENUS_TYPES['qti-upload-interaction-audio'])
QTI_ANSWER_UPLOAD_INTERACTION_GENERIC_GENUS = Type(**ANSWER_GENUS_TYPES['qti-upload-interaction-generic'])
QTI_ANSWER_RECORD = Type(**ANSWER_RECORD_TYPES['qti'])
QTI_ITEM_CHOICE_INTERACTION_GENUS = Type(**ITEM_GENUS_TYPES['qti-choice-interaction'])
QTI_ITEM_CHOICE_INTERACTION_SURVEY_GENUS = Type(**ITEM_GENUS_TYPES['qti-choice-interaction-survey'])
QTI_ITEM_CHOICE_INTERACTION_MULTI_GENUS = Type(**ITEM_GENUS_TYPES['qti-choice-interaction-multi-select'])
QTI_ITEM_CHOICE_INTERACTION_MULTI_SELECT_SURVEY_GENUS = Type(**ITEM_GENUS_TYPES['qti-choice-interaction-multi-select-survey'])
QTI_ITEM_EXTENDED_TEXT_INTERACTION_GENUS = Type(**ITEM_GENUS_TYPES['qti-extended-text-interaction'])
QTI_ITEM_INLINE_CHOICE_INTERACTION_GENUS = Type(**ITEM_GENUS_TYPES['qti-inline-choice-interaction-mw-fill-in-the-blank'])
QTI_ITEM_NUMERIC_RESPONSE_INTERACTION_GENUS = Type(**ITEM_GENUS_TYPES['qti-numeric-response'])
QTI_ITEM_ORDER_INTERACTION_MW_SENTENCE_GENUS = Type(**ITEM_GENUS_TYPES['qti-order-interaction-mw-sentence'])
QTI_ITEM_ORDER_INTERACTION_MW_SANDBOX_GENUS = Type(**ITEM_GENUS_TYPES['qti-order-interaction-mw-sandbox'])
QTI_ITEM_ORDER_INTERACTION_OBJECT_MANIPULATION_GENUS = Type(**ITEM_GENUS_TYPES['qti-order-interaction-object-manipulation'])
QTI_ITEM_UPLOAD_INTERACTION_AUDIO_GENUS = Type(**ITEM_GENUS_TYPES['qti-upload-interaction-audio'])
QTI_ITEM_UPLOAD_INTERACTION_GENERIC_GENUS = Type(**ITEM_GENUS_TYPES['qti-upload-interaction-generic'])
QTI_ITEM_RECORD = Type(**ITEM_RECORD_TYPES['qti'])
QTI_QUESTION_CHOICE_INTERACTION_GENUS = Type(**QUESTION_GENUS_TYPES['qti-choice-interaction'])
QTI_QUESTION_CHOICE_INTERACTION_SURVEY_GENUS = Type(**QUESTION_GENUS_TYPES['qti-choice-interaction-survey'])
QTI_QUESTION_CHOICE_INTERACTION_MULTI_GENUS = Type(**QUESTION_GENUS_TYPES['qti-choice-interaction-multi-select'])
QTI_QUESTION_CHOICE_INTERACTION_MULTI_SELECT_SURVEY_GENUS = Type(**QUESTION_GENUS_TYPES['qti-choice-interaction-multi-select-survey'])
QTI_QUESTION_EXTENDED_TEXT_INTERACTION_GENUS = Type(**QUESTION_GENUS_TYPES['qti-extended-text-interaction'])
QTI_QUESTION_INLINE_CHOICE_INTERACTION_GENUS = Type(**QUESTION_GENUS_TYPES['qti-inline-choice-interaction-mw-fill-in-the-blank'])
QTI_QUESTION_NUMERIC_RESPONSE_INTERACTION_GENUS = Type(**QUESTION_GENUS_TYPES['qti-numeric-response'])
QTI_QUESTION_ORDER_INTERACTION_MW_SENTENCE_GENUS = Type(**QUESTION_GENUS_TYPES['qti-order-interaction-mw-sentence'])
QTI_QUESTION_ORDER_INTERACTION_MW_SANDBOX_GENUS = Type(**QUESTION_GENUS_TYPES['qti-order-interaction-mw-sandbox'])
QTI_QUESTION_ORDER_INTERACTION_OBJECT_MANIPULATION_GENUS = Type(**QUESTION_GENUS_TYPES['qti-order-interaction-object-manipulation'])
QTI_QUESTION_UPLOAD_INTERACTION_AUDIO_GENUS = Type(**QUESTION_GENUS_TYPES['qti-upload-interaction-audio'])
QTI_QUESTION_UPLOAD_INTERACTION_GENERIC_GENUS = Type(**QUESTION_GENUS_TYPES['qti-upload-interaction-generic'])
QTI_QUESTION_RECORD = Type(**QUESTION_RECORD_TYPES['qti'])

REVIEWABLE_OFFERED = Type(**ASSESSMENT_OFFERED_RECORD_TYPES['review-options'])
N_OF_M_OFFERED = Type(**ASSESSMENT_OFFERED_RECORD_TYPES['n-of-m'])
REVIEWABLE_TAKEN = Type(**ASSESSMENT_TAKEN_RECORD_TYPES['review-options'])

SIMPLE_SEQUENCE_RECORD = Type(**ASSESSMENT_RECORD_TYPES['simple-child-sequencing'])

MULTI_LANGUAGE_ITEM_RECORD = Type(**ITEM_RECORD_TYPES['multi-language'])
MULTI_LANGUAGE_QUESTION_RECORD = Type(**QUESTION_RECORD_TYPES['multi-language'])
MULTI_LANGUAGE_FEEDBACK_ANSWER_RECORD = Type(**ANSWER_RECORD_TYPES['multi-language-answer-with-feedback'])
FILES_ANSWER_RECORD = Type(**ANSWER_RECORD_TYPES['files'])


PROJECT_PATH = os.path.dirname(os.path.abspath(__file__))
ABS_PATH = os.path.abspath(os.path.join(PROJECT_PATH, os.pardir))


class BaseAssessmentTestCase(BaseTestCase):
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

        form = bank.get_assessment_offered_form_for_create(new_assessment.ident,
                                                           [REVIEWABLE_OFFERED])
        new_offered = bank.create_assessment_offered(form)

        return new_offered

    def create_item(self, bank_id):
        if isinstance(bank_id, basestring):
            bank_id = utilities.clean_id(bank_id)

        bank = get_managers()['am'].get_bank(bank_id)
        form = bank.get_item_form_for_create([EDX_ITEM_RECORD_TYPE])
        form.display_name = 'a test item!'
        form.description = 'for testing with'
        form.set_genus_type(NUMERIC_RESPONSE_ITEM_GENUS_TYPE)
        new_item = bank.create_item(form)

        form = bank.get_question_form_for_create(item_id=new_item.ident,
                                                 question_record_types=[NUMERIC_RESPONSE_QUESTION_RECORD_TYPE])
        form.set_text('foo?')
        bank.create_question(form)

        self.right_answer = float(2.04)
        self.tolerance = float(0.71)
        form = bank.get_answer_form_for_create(item_id=new_item.ident,
                                               answer_record_types=[NUMERIC_RESPONSE_ANSWER_RECORD_TYPE])
        form.set_decimal_value(self.right_answer)
        form.set_tolerance_value(self.tolerance)

        bank.create_answer(form)

        return bank.get_item(new_item.ident)

    def create_taken_for_item(self, bank_id, item_id):
        if isinstance(bank_id, basestring):
            bank_id = utilities.clean_id(bank_id)
        if isinstance(item_id, basestring):
            item_id = utilities.clean_id(item_id)

        bank = get_managers()['am'].get_bank(bank_id)

        new_offered = self.create_assessment_offered_for_item(bank_id, item_id)

        form = bank.get_assessment_taken_form_for_create(new_offered.ident,
                                                         [REVIEWABLE_TAKEN])
        taken = bank.create_assessment_taken(form)
        return taken, new_offered

    def extract_answers(self, item):
        """
        Extract the answer part of an item
        """
        if 'answers' in item:
            return item['answers']
        else:
            return item[0]['answers']

    def extract_question(self, item):
        """
        Extract the question part of an item
        """
        if 'question' in item:
            return item['question']
        else:
            return item[0]['question']

    def setUp(self):
        super(BaseAssessmentTestCase, self).setUp()
        self.url = '/api/v1/assessment'
        self._bank = get_fixture_bank()

    def tearDown(self):
        super(BaseAssessmentTestCase, self).tearDown()

    def verify_no_data(self, _req):
        """
        Verify that the data object in _req is empty
        """
        data = json.loads(_req.body)
        self.assertEqual(
            data,
            []
        )

    def verify_offerings(self, _req, _type, _data):
        """
        Check that the offerings match...
        _type may not be used here; assume AssessmentOffered always?
        _data objects need to have an offering ID in them
        """
        def check_expected_against_one_item(expected, item):
            for key, value in expected.iteritems():
                if isinstance(value, basestring):
                    if key == 'name':
                        self.assertEqual(
                            item['displayName']['text'],
                            value
                        )
                    elif key == 'description':
                        self.assertEqual(
                            item['description']['text'],
                            value
                        )
                    else:
                        self.assertEqual(
                            item[key],
                            value
                        )
                elif isinstance(value, dict):
                    for inner_key, inner_value in value.iteritems():
                        self.assertEqual(
                            item[key][inner_key],
                            inner_value
                        )

        data = json.loads(_req.body)
        if 'data' in data:
            data = data['data']['results']
        elif 'results' in data:
            data = data['results']

        if isinstance(_data, list):
            for expected in _data:
                if isinstance(data, list):
                    for item in data:
                        if item['id'] == expected['id']:
                            check_expected_against_one_item(expected, item)
                            break
                else:
                    check_expected_against_one_item(expected, data)
        elif isinstance(_data, dict):
            if isinstance(data, list):
                for item in data:
                    if item['id'] == _data['id']:
                        check_expected_against_one_item(_data, item)
                        break
            else:
                check_expected_against_one_item(_data, data)

    def verify_question(self, _data, _q_str, _q_type):
        """
        verify just the question part of an item. Should allow you to pass
        in either a request response or a json object...load if needed
        """
        try:
            try:
                data = json.loads(_data.body)
            except:
                data = json.loads(_data)
        except:
            data = _data
        if 'question' in data:
            question = data['question']
        elif isinstance(data, list):
            try:
                question = data[0]['question']
            except:
                question = data[0]
        else:
            question = data

        self.assertEqual(
            question['text']['text'],
            _q_str
        )
        self.assertIn(
            _q_type,
            question['recordTypeIds']
        )

    def verify_submission(self, _req, _expected_result, _has_next=None):
        data = json.loads(_req.body)
        self.assertEqual(
            data['correct'],
            _expected_result
        )
        if _has_next:
            self.assertEqual(
                data['hasNext'],
                _has_next
            )

    def verify_text(self, _req, _type, _name, _desc, _id=None, _genus=None):
        """
        helper method to verify the text in a returned object
        takes care of all the language stuff
        """
        req = json.loads(_req.body)
        if _id:
            data = None
            if isinstance(req, list):
                for item in req:
                    if (
                        item['id'] == _id or
                        item['id'] == quote(_id)
                    ):
                        data = item
            elif isinstance(req, dict):
                if (req['id'] == _id or
                        req['id'] == quote(_id)):
                    data = req
            if not data:
                raise LookupError('Item with id: ' + _id + ' not found.')
        else:
            data = req
        self.assertEqual(
            data['displayName']['text'],
            _name
        )
        self.assertEqual(
            data['description']['text'],
            _desc
        )
        self.assertEqual(
            data['type'],
            _type
        )

        if _genus:
            self.assertEqual(
                data['genusTypeId'],
                _genus
            )


class AnswerTypeTests(BaseAssessmentTestCase):
    def item_payload(self):
        item_name = 'a really complicated item'
        item_desc = 'meant to differentiate students'
        question_body = 'can you manipulate this?'
        question_choices = [
            'yes',
            'no',
            'maybe'
        ]
        question_type = 'question-record-type%3Amulti-choice-edx%40ODL.MIT.EDU'
        answer = 2
        answer_type = 'answer-record-type%3Amulti-choice-edx%40ODL.MIT.EDU'

        return {
            "name"               : item_name,
            "description"        : item_desc,
            "question"           : {
                "type"           : question_type,
                "questionString" : question_body,
                "choices"        : question_choices
            },
            "answers"       : [{
                "type"      : answer_type,
                "choiceId"  : answer
            }],
        }

    def setUp(self):
        super(AnswerTypeTests, self).setUp()
        self.url += '/banks/' + unquote(str(self._bank.ident)) + '/items'
        self._audio_file = open('{0}/tests/files/audio_feedback.mp3'.format(ABS_PATH), 'r')

    def tearDown(self):
        """
        Remove the test user from all groups in Membership
        Start from the smallest groupId because need to
        remove "parental" roles like for DepartmentAdmin / DepartmentOfficer
        """
        super(AnswerTypeTests, self).tearDown()
        self._audio_file.close()

    def test_can_explicitly_set_right_answer(self):
        payload = self.item_payload()
        payload['answers'][0].update({
            'genus': str(Type(**ANSWER_GENUS_TYPES['right-answer']))
        })

        req = self.app.post(self.url,
                            params=json.dumps(payload),
                            headers={'content-type': 'application/json'})
        self.ok(req)
        item = self.json(req)
        self.assertEqual(
            item['answers'][0]['genusTypeId'],
            str(Type(**ANSWER_GENUS_TYPES['right-answer']))
        )

    def test_default_answer_genus_is_right_answer_when_not_specified(self):
        payload = self.item_payload()

        req = self.app.post(self.url,
                            params=json.dumps(payload),
                            headers={'content-type': 'application/json'})
        self.ok(req)
        item = self.json(req)
        self.assertEqual(
            item['answers'][0]['genusTypeId'],
            str(Type(**ANSWER_GENUS_TYPES['right-answer']))
        )

    def test_can_set_wrong_answers_when_creating_answer(self):
        payload = self.item_payload()
        payload['answers'][0].update({
            'genus': str(Type(**ANSWER_GENUS_TYPES['wrong-answer']))
        })

        req = self.app.post(self.url,
                            params=json.dumps(payload),
                            headers={'content-type': 'application/json'})
        self.ok(req)
        item = self.json(req)
        self.assertEqual(
            item['answers'][0]['genusTypeId'],
            str(Type(**ANSWER_GENUS_TYPES['wrong-answer']))
        )

    def test_can_change_answer_genus_from_wrong_to_right(self):
        payload = self.item_payload()
        payload['answers'][0].update({
            'genus': str(Type(**ANSWER_GENUS_TYPES['wrong-answer']))
        })

        req = self.app.post(self.url,
                            params=json.dumps(payload),
                            headers={'content-type': 'application/json'})
        self.ok(req)
        item = self.json(req)

        self.assertEqual(
            item['answers'][0]['genusTypeId'],
            payload['answers'][0]['genus']
        )

        item_id = unquote(item['id'])
        answer_id = unquote(item['answers'][0]['id'])
        item_details_endpoint = '{0}/{1}'.format(self.url,
                                                 item_id)
        updated_payload = {
            'answers': [{
                'genus': str(Type(**ANSWER_GENUS_TYPES['right-answer'])),
                'id': answer_id,
                'type': payload['answers'][0]['type']
            }]
        }
        req = self.app.put(item_details_endpoint,
                           params=json.dumps(updated_payload),
                           headers={'content-type': 'application/json'})
        self.ok(req)
        updated_answer = self.json(req)['answers'][0]
        self.assertEqual(
            updated_answer['genusTypeId'],
            updated_payload['answers'][0]['genus']
        )

    def test_can_change_answer_genus_from_right_to_wrong(self):
        payload = self.item_payload()

        req = self.app.post(self.url,
                            params=json.dumps(payload),
                            headers={'content-type': 'application/json'})
        self.ok(req)
        item = self.json(req)

        self.assertEqual(
            item['answers'][0]['genusTypeId'],
            str(RIGHT_ANSWER_GENUS)
        )

        item_id = unquote(item['id'])
        answer_id = unquote(item['answers'][0]['id'])
        item_details_endpoint = '{0}/{1}'.format(self.url,
                                                 item_id)
        updated_payload = {
            'answers': [{
                'genus': str(WRONG_ANSWER_GENUS),
                'id': answer_id,
                'feedback': 'bazz',
                'type': payload['answers'][0]['type']
            }]
        }

        req = self.app.put(item_details_endpoint,
                           params=json.dumps(updated_payload),
                           headers={'content-type': 'application/json'})
        self.ok(req)
        updated_answer = self.json(req)['answers'][0]
        self.assertEqual(
            updated_answer['genusTypeId'],
            updated_payload['answers'][0]['genus']
        )
        self.assertEqual(
            updated_answer['feedback']['text'],
            updated_payload['answers'][0]['feedback']
        )

    def test_can_edit_feedback_for_wrong_answers(self):
        payload = self.item_payload()
        payload['answers'][0].update({
            'genus': str(Type(**ANSWER_GENUS_TYPES['wrong-answer']))
        })

        req = self.app.post(self.url,
                            params=json.dumps(payload),
                            headers={'content-type': 'application/json'})
        self.ok(req)
        item = self.json(req)

        self.assertEqual(
            item['answers'][0]['genusTypeId'],
            payload['answers'][0]['genus']
        )

        self.assertEqual(
            item['answers'][0]['feedback']['text'],
            ''
        )

        item_id = unquote(item['id'])
        answer_id = unquote(item['answers'][0]['id'])
        item_details_endpoint = '{0}/{1}'.format(self.url,
                                                 item_id)
        updated_payload = {
            'answers': [{
                'genus': str(Type(**ANSWER_GENUS_TYPES['wrong-answer'])),
                'id': answer_id,
                'feedback': 'bazz',
                'type': payload['answers'][0]['type']
            }]
        }

        req = self.app.put(item_details_endpoint,
                           params=json.dumps(updated_payload),
                           headers={'content-type': 'application/json'})
        self.ok(req)
        updated_answer = self.json(req)['answers'][0]

        self.assertEqual(
            updated_answer['genusTypeId'],
            updated_payload['answers'][0]['genus']
        )
        self.assertEqual(
            updated_answer['feedback']['text'],
            updated_payload['answers'][0]['feedback']
        )

    def test_can_add_audio_file_to_wrong_feedback(self):
        payload = self.item_payload()
        payload['answers'][0].update({
            'genus': str(Type(**ANSWER_GENUS_TYPES['wrong-answer']))
        })

        req = self.app.post(self.url,
                            params=json.dumps(payload),
                            headers={'content-type': 'application/json'})
        self.ok(req)
        item = self.json(req)
        item_id = unquote(item['id'])
        answer_id = unquote(item['answers'][0]['id'])
        item_details_endpoint = '{0}/{1}'.format(self.url,
                                                 item_id)
        updated_payload = {
            'answers': [{
                'genus': str(Type(**ANSWER_GENUS_TYPES['wrong-answer'])),
                'id': answer_id,
                'feedback': 'bazz',
                'type': payload['answers'][0]['type']
            }]
        }

        req = self.app.put(item_details_endpoint,
                           params=json.dumps(updated_payload),
                           headers={'content-type': 'application/json'})
        self.ok(req)
        updated_answer = self.json(req)['answers'][0]

        self.assertNotIn('fileIds', updated_answer)

        assets_endpoint = '/api/v1/repository/repositories/{0}/assets'.format(unquote(str(self._bank.ident)))
        self._audio_file.seek(0)
        req = self.app.post(assets_endpoint,
                            upload_files=[('inputFile',
                                           self._filename(self._audio_file),
                                           self._audio_file.read())])
        self.ok(req)
        asset = self.json(req)
        label = asset['displayName']['text'].replace('.', '_')
        asset_payload = {
            'answers': [{
                'id': updated_answer['id'],
                'fileIds': {
                },
                'feedback': 'bazz with <audio autoplay="true"><source src="AssetContent:{0}"></audio>'.format(label),
                'type': payload['answers'][0]['type']
            }]
        }
        asset_payload['answers'][0]['fileIds'][label] = {
            'assetId': asset['id'],
            'assetContentId': asset['assetContents'][0]['id'],
            'assetContentTypeId': asset['assetContents'][0]['genusTypeId']
        }
        req = self.app.put(item_details_endpoint,
                           params=json.dumps(asset_payload),
                           headers={'content-type': 'application/json'})
        self.ok(req)
        req = self.app.get(item_details_endpoint)
        self.ok(req)
        item = self.json(req)
        self.assertEqual(
            item['answers'][0]['fileIds'],
            asset_payload['answers'][0]['fileIds']
        )
        self.assertEqual(
            item['answers'][0]['feedback']['text'],
            asset_payload['answers'][0]['feedback']
        )
        self.assertEqual(
            item['answers'][0]['genusTypeId'],
            str(WRONG_ANSWER_GENUS)
        )

    def test_can_add_audio_file_to_correct_feedback(self):
        payload = self.item_payload()
        req = self.app.post(self.url,
                            params=json.dumps(payload),
                            headers={'content-type': 'application/json'})
        self.ok(req)
        item = self.json(req)
        item_id = unquote(item['id'])
        answer_id = unquote(item['answers'][0]['id'])
        item_details_endpoint = '{0}/{1}'.format(self.url,
                                                 item_id)
        updated_payload = {
            'answers': [{
                'genus': str(Type(**ANSWER_GENUS_TYPES['right-answer'])),
                'id': answer_id,
                'feedback': 'bazz',
                'type': payload['answers'][0]['type']
            }]
        }

        req = self.app.put(item_details_endpoint,
                           params=json.dumps(updated_payload),
                           headers={'content-type': 'application/json'})
        self.ok(req)
        updated_answer = self.json(req)['answers'][0]

        self.assertNotIn('fileIds', updated_answer)

        assets_endpoint = '/api/v1/repository/repositories/{0}/assets'.format(unquote(str(self._bank.ident)))
        self._audio_file.seek(0)
        req = self.app.post(assets_endpoint,
                            upload_files=[('inputFile',
                                           self._filename(self._audio_file),
                                           self._audio_file.read())])
        self.ok(req)
        asset = self.json(req)
        label = asset['displayName']['text'].replace('.', '_')
        asset_payload = {
            'answers': [{
                'id': updated_answer['id'],
                'fileIds': {
                },
                'feedback': 'bazz with <audio autoplay="true"><source src="AssetContent:{0}"></audio>'.format(label),
                'type': payload['answers'][0]['type']
            }]
        }
        asset_payload['answers'][0]['fileIds'][label] = {
            'assetId': asset['id'],
            'assetContentId': asset['assetContents'][0]['id'],
            'assetContentTypeId': asset['assetContents'][0]['genusTypeId']
        }
        req = self.app.put(item_details_endpoint,
                           params=json.dumps(asset_payload),
                           headers={'content-type': 'application/json'})
        self.ok(req)

        req = self.app.get(item_details_endpoint)
        self.ok(req)
        item = self.json(req)
        self.assertEqual(
            item['answers'][0]['fileIds'],
            asset_payload['answers'][0]['fileIds']
        )
        self.assertEqual(
            item['answers'][0]['feedback']['text'],
            asset_payload['answers'][0]['feedback']
        )
        self.assertEqual(
            item['answers'][0]['genusTypeId'],
            str(RIGHT_ANSWER_GENUS)
        )

    def test_can_add_wrong_answers_when_updating_item(self):
        payload = self.item_payload()

        req = self.app.post(self.url,
                            params=json.dumps(payload),
                            headers={'content-type': 'application/json'})
        self.ok(req)
        item_id = self.json(req)['id']

        new_answer_payload = {
            'answers': [{
                'genus': str(Type(**ANSWER_GENUS_TYPES['wrong-answer'])),
                'type': payload['answers'][0]['type'],
                'choiceId': 1
            }]
        }

        item_details_endpoint = self.url + '/' + unquote(item_id)
        req = self.app.put(item_details_endpoint,
                           params=json.dumps(new_answer_payload),
                           headers={'content-type': 'application/json'})
        self.ok(req)
        updated_item = self.json(req)
        self.assertEqual(
            len(updated_item['answers']),
            2
        )

        new_answer = [a for a in updated_item['answers']
                      if a['genusTypeId'] == new_answer_payload['answers'][0]['genus']][0]
        self.assertEqual(
            new_answer['choiceIds'][0],
            updated_item['question']['choices'][0]['id']
        )

    def test_can_set_feedback_text_on_wrong_answer_on_item_create(self):
        payload = self.item_payload()
        payload['answers'][0].update({
            'genus': str(Type(**ANSWER_GENUS_TYPES['wrong-answer'])),
            'feedback': 'foobar'
        })

        req = self.app.post(self.url,
                            params=json.dumps(payload),
                            headers={'content-type': 'application/json'})
        self.ok(req)
        item = self.json(req)
        self.assertEqual(
            item['answers'][0]['genusTypeId'],
            str(Type(**ANSWER_GENUS_TYPES['wrong-answer']))
        )
        self.assertEqual(
            item['answers'][0]['feedback']['text'],
            payload['answers'][0]['feedback']
        )

    def test_feedback_returned_when_student_submits_wrong_answer(self):
        payload = self.item_payload()
        payload['answers'][0].update({
            'genus': str(Type(**ANSWER_GENUS_TYPES['wrong-answer'])),
            'feedback': 'what a novel idea'
        })

        req = self.app.post(self.url,
                            params=json.dumps(payload),
                            headers={'content-type': 'application/json'})
        self.ok(req)
        item = self.json(req)

        self.assertEqual(
            item['answers'][0]['feedback']['text'],
            payload['answers'][0]['feedback']
        )

        item_id = item['id']
        wrong_choice_id = item['question']['choices'][1]['id']

        taken, offered = self.create_taken_for_item(self._bank.ident, item_id)

        url = '/api/v1/assessment/banks/{0}/assessmentstaken/{1}/questions/{2}/submit'.format(unquote(str(self._bank.ident)),
                                                                                              unquote(str(taken.ident)),
                                                                                              unquote(item_id))
        wrong_answer_payload = {
            'choiceIds': [wrong_choice_id]
        }

        req = self.app.post(url,
                            params=json.dumps(wrong_answer_payload),
                            headers={'content-type': 'application/json'})

        self.ok(req)
        data = self.json(req)
        self.assertFalse(data['correct'])
        self.assertEqual(
            data['feedback'],
            payload['answers'][0]['feedback']
        )

    def test_solution_returned_when_student_submits_right_answer(self):
        payload = self.item_payload()
        payload['solution'] = 'basket weaving'

        req = self.app.post(self.url,
                            params=json.dumps(payload),
                            headers={'content-type': 'application/json'})
        self.ok(req)
        item = self.json(req)

        self.assertEqual(
            item['texts']['solution']['text'],
            payload['solution']
        )

        item_id = item['id']
        right_choice_id = item['question']['choices'][1]['id']

        taken, offered = self.create_taken_for_item(self._bank.ident, item_id)

        url = '/api/v1/assessment/banks/{0}/assessmentstaken/{1}/questions'.format(unquote(str(self._bank.ident)),
                                                                                   unquote(str(taken.ident)))
        req = self.app.get(url)
        self.ok(req)
        data = self.json(req)
        question_id = data['data'][0]['id']

        url = '/api/v1/assessment/banks/{0}/assessmentstaken/{1}/questions/{2}/submit'.format(unquote(str(self._bank.ident)),
                                                                                              unquote(str(taken.ident)),
                                                                                              unquote(question_id))
        right_answer_payload = {
            'choiceIds': [right_choice_id]
        }

        req = self.app.post(url,
                            params=json.dumps(right_answer_payload),
                            headers={'content-type': 'application/json'})

        self.ok(req)
        data = self.json(req)
        self.assertTrue(data['correct'])
        self.assertEqual(
            data['feedback']['text'],
            payload['solution']
        )

    def test_can_add_confused_learning_objectives_to_wrong_answer(self):
        payload = self.item_payload()
        payload['answers'][0].update({
            'genus': str(Type(**ANSWER_GENUS_TYPES['wrong-answer'])),
            'feedback': 'foobar',
            'confusedLearningObjectiveIds': ['foo%3A1%40MIT', 'baz%3A2%40ODL']
        })

        req = self.app.post(self.url,
                            params=json.dumps(payload),
                            headers={'content-type': 'application/json'})
        self.ok(req)
        item = self.json(req)
        self.assertEqual(
            item['answers'][0]['genusTypeId'],
            str(Type(**ANSWER_GENUS_TYPES['wrong-answer']))
        )
        self.assertEqual(
            item['answers'][0]['confusedLearningObjectiveIds'],
            payload['answers'][0]['confusedLearningObjectiveIds']
        )

    def test_wrong_answer_submission_returns_confused_los(self):
        payload = self.item_payload()
        payload['answers'][0].update({
            'genus': str(Type(**ANSWER_GENUS_TYPES['wrong-answer'])),
            'feedback': 'what a novel idea',
            'confusedLearningObjectiveIds': ['foo%3A1%40MIT', 'baz%3A2%40ODL']
        })

        req = self.app.post(self.url,
                            params=json.dumps(payload),
                            headers={'content-type': 'application/json'})
        self.ok(req)
        item = self.json(req)

        self.assertEqual(
            item['answers'][0]['confusedLearningObjectiveIds'],
            payload['answers'][0]['confusedLearningObjectiveIds']
        )

        item_id = item['id']
        wrong_choice_id = item['question']['choices'][1]['id']

        taken, offered = self.create_taken_for_item(self._bank.ident, item_id)

        url = '/api/v1/assessment/banks/{0}/assessmentstaken/{1}/questions/{2}/submit'.format(unquote(str(self._bank.ident)),
                                                                                              unquote(str(taken.ident)),
                                                                                              unquote(item_id))
        wrong_answer_payload = {
            'choiceIds': [wrong_choice_id]
        }

        req = self.app.post(url,
                            params=json.dumps(wrong_answer_payload),
                            headers={'content-type': 'application/json'})

        self.ok(req)
        data = self.json(req)
        self.assertFalse(data['correct'])
        self.assertEqual(
            data['confusedLearningObjectiveIds'],
            payload['answers'][0]['confusedLearningObjectiveIds']
        )

    def test_can_delete_right_answer(self):
        payload = self.item_payload()
        payload['answers'][0].update({
            'genus': str(Type(**ANSWER_GENUS_TYPES['right-answer']))
        })

        req = self.app.post(self.url,
                            params=json.dumps(payload),
                            headers={'content-type': 'application/json'})
        self.ok(req)
        item = self.json(req)

        self.assertEqual(
            item['answers'][0]['genusTypeId'],
            payload['answers'][0]['genus']
        )

        url = '{0}/{1}'.format(self.url, item['id'])
        payload = {
            'answers': [{
                'id': item['answers'][0]['id'],
                'delete': True
            }]
        }
        req = self.app.put(url,
                           params=json.dumps(payload),
                           headers={'content-type': 'application/json'})
        self.ok(req)
        item = self.json(req)

        self.assertEqual(len(item['answers']), 0)

    def test_can_delete_wrong_answer(self):
        payload = self.item_payload()
        payload['answers'][0].update({
            'genus': str(Type(**ANSWER_GENUS_TYPES['wrong-answer']))
        })

        req = self.app.post(self.url,
                            params=json.dumps(payload),
                            headers={'content-type': 'application/json'})
        self.ok(req)
        item = self.json(req)

        self.assertEqual(
            item['answers'][0]['genusTypeId'],
            payload['answers'][0]['genus']
        )

        url = '{0}/{1}'.format(self.url, item['id'])
        payload = {
            'answers': [{
                'id': item['answers'][0]['id'],
                'delete': True
            }]
        }
        req = self.app.put(url,
                           params=json.dumps(payload),
                           headers={'content-type': 'application/json'})
        self.ok(req)
        item = self.json(req)

        self.assertEqual(len(item['answers']), 0)


class AssessmentOfferedTests(BaseAssessmentTestCase):
    def create_assessment(self):
        # Now create an assessment, link the item to it,
        # and create an offering.
        # Use the offering_id to create the taken
        assessments_endpoint = self.url + '/assessments'
        assessment_name = 'a really hard assessment'
        assessment_desc = 'meant to differentiate students'
        payload = {
            "name": assessment_name,
            "description": assessment_desc
        }
        req = self.app.post(assessments_endpoint,
                            params=json.dumps(payload),
                            headers={'content-type': 'application/json'})
        self.ok(req)
        return self.json(req)

    def create_item(self):
        items_endpoint = self.url + '/items'

        # Use POST to create an item
        item_name = 'a really complicated item'
        item_desc = 'meant to differentiate students'
        question_string = 'can you manipulate this?'
        question_type = 'question-record-type%3Amulti-choice-edx%40ODL.MIT.EDU'
        answer_string = 'yes!'
        answer_type = 'answer-record-type%3Amulti-choice-edx%40ODL.MIT.EDU'
        payload = {
            "name": item_name,
            "description": item_desc,
            "question": {
                "type": question_type,
                "questionString": question_string,
                "choices": ['1', '2', '3']
            },
            "answers": [{
                "type": answer_type,
                "choiceId": 1
            }],
        }
        req = self.app.post(items_endpoint,
                            params=json.dumps(payload),
                            headers={'content-type': 'application/json'})
        self.ok(req)

        item = json.loads(req.body)
        return item

    def item_payload(self):
        item_name = 'a really complicated item'
        item_desc = 'meant to differentiate students'
        question_body = 'can you manipulate this?'
        question_choices = [
            'yes',
            'no',
            'maybe'
        ]
        question_type = 'question-record-type%3Amulti-choice-edx%40ODL.MIT.EDU'
        answer = 2
        answer_type = 'answer-record-type%3Amulti-choice-edx%40ODL.MIT.EDU'

        return {
            "name":                   item_name,
            "description":            item_desc,
            "question":               {
                "type":            question_type,
                "questionString":  question_body,
                "choices":         question_choices
            },
            "answers":                [{
                "type":       answer_type,
                "choiceId":   answer
            }],
        }

    def link_item_to_assessment(self, item, assessment):
        assessment_items_endpoint = '{0}/assessments/{1}/items'.format(self.url,
                                                                       unquote(assessment['id']))

        # POST should create the linkage
        payload = {
            'itemIds': [unquote(item['id'])]
        }
        req = self.app.post(assessment_items_endpoint,
                            params=json.dumps(payload),
                            headers={'content-type': 'application/json'})
        self.ok(req)

    def setUp(self):
        super(AssessmentOfferedTests, self).setUp()
        self.url += '/banks/' + unquote(str(self._bank.ident))

    def tearDown(self):
        """
        Remove the test user from all groups in Membership
        Start from the smallest groupId because need to
        remove "parental" roles like for DepartmentAdmin / DepartmentOfficer
        """
        super(AssessmentOfferedTests, self).tearDown()

    def test_can_set_max_attempts_on_assessment_offered(self):
        items_endpoint = self.url + '/items'

        item = self.create_item()

        req = self.app.get(items_endpoint)
        self.ok(req)

        # Now create an assessment, link the item to it,
        # and create an offering.
        # Use the offering_id to create the taken
        assessments_endpoint = self.url + '/assessments'

        assessment = self.create_assessment()
        assessment_id = unquote(assessment['id'])

        assessment_detail_endpoint = assessments_endpoint + '/' + assessment_id
        assessment_offering_endpoint = assessment_detail_endpoint + '/assessmentsoffered'
        self.link_item_to_assessment(item, assessment)

        # Use POST to create an offering
        payload = {
            "startTime":  {
                "day":    1,
                "month":  1,
                "year":   2015
            },
            "duration":   {
                "days":   2
            }
        }
        req = self.app.post(assessment_offering_endpoint,
                            params=json.dumps(payload),
                            headers={'content-type': 'application/json'})
        self.ok(req)
        offering = json.loads(req.body)
        offering_id = unquote(offering['id'])

        # verify that the offering has defaulted to maxAttempts = None
        self.assertIsNone(offering['maxAttempts'])

        assessment_offering_detail_endpoint = self.url + '/assessmentsoffered/' + offering_id
        self.app.delete(assessment_offering_detail_endpoint)

        # try again, but set maxAttempts on create
        payload = {
            "startTime":      {
                "day":    1,
                "month":  1,
                "year":   2015
            },
            "duration":       {
                "days":   2
            },
            "maxAttempts":  2
        }
        req = self.app.post(assessment_offering_endpoint,
                            params=json.dumps(payload),
                            headers={'content-type': 'application/json'})
        self.ok(req)
        offering = json.loads(req.body)
        offering_id = unquote(offering['id'])

        # verify that the offering has maxAttempts == 2
        self.assertEqual(offering['maxAttempts'],
                         2)

    def test_can_update_max_attempts_on_assessment_offered(self):
        items_endpoint = self.url + '/items'

        item = self.create_item()

        req = self.app.get(items_endpoint)
        self.ok(req)

        # Now create an assessment, link the item to it,
        # and create an offering.
        # Use the offering_id to create the taken
        assessments_endpoint = self.url + '/assessments'

        assessment = self.create_assessment()
        assessment_id = unquote(assessment['id'])

        assessment_detail_endpoint = assessments_endpoint + '/' + assessment_id
        assessment_offering_endpoint = assessment_detail_endpoint + '/assessmentsoffered'
        self.link_item_to_assessment(item, assessment)

        # Use POST to create an offering
        payload = {
            "startTime":  {
                "day":    1,
                "month":  1,
                "year":   2015
            },
            "duration":   {
                "days":   2
            }
        }

        req = self.app.post(assessment_offering_endpoint,
                            params=json.dumps(payload),
                            headers={'content-type': 'application/json'})
        self.ok(req)
        offering = json.loads(req.body)
        offering_id = unquote(offering['id'])

        # verify that the offering has defaulted to maxAttempts = None
        self.assertIsNone(offering['maxAttempts'])

        assessment_offering_detail_endpoint = self.url + '/assessmentsoffered/' + offering_id

        # try again, but set maxAttempts on update
        payload = {
            "maxAttempts": 2
        }
        req = self.app.put(assessment_offering_detail_endpoint,
                           params=json.dumps(payload),
                           headers={'content-type': 'application/json'})
        self.ok(req)
        offering = json.loads(req.body)

        # verify that the offering has maxAttempts == 2
        self.assertEqual(offering['maxAttempts'],
                         2)

    def test_default_max_attempts_allows_infinite_attempts(self):
        # ok, don't really test to infinity, but test several
        item = self.create_item()
        assessment = self.create_assessment()
        assessment_id = unquote(assessment['id'])

        assessment_detail_endpoint = '{0}/assessments/{1}'.format(self.url,
                                                                  assessment_id)
        assessment_offering_endpoint = assessment_detail_endpoint + '/assessmentsoffered'

        # POST should create the linkage
        self.link_item_to_assessment(item, assessment)

        # Use POST to create an offering
        payload = {
            "startTime":  {
                "day":    1,
                "month":  1,
                "year":   2015
            },
            "duration":   {
                "days":   2
            }
        }

        req = self.app.post(assessment_offering_endpoint,
                            params=json.dumps(payload),
                            headers={'content-type': 'application/json'})
        self.ok(req)
        offering = json.loads(req.body)
        offering_id = unquote(offering['id'])

        # verify that the offering has defaulted to maxAttempts = None
        self.assertIsNone(offering['maxAttempts'])

        assessment_offering_detail_endpoint = self.url + '/assessmentsoffered/' + offering_id

        num_attempts = 25
        # for deleting
        taken_endpoints = []
        assessment_offering_takens_endpoint = assessment_offering_detail_endpoint + '/assessmentstaken'

        for attempt in range(0, num_attempts):
            # Can POST to create a new taken
            req = self.app.post(assessment_offering_takens_endpoint)
            self.ok(req)
            taken = json.loads(req.body)
            taken_id = unquote(taken['id'])

            taken_endpoint = self.url + '/assessmentstaken/' + taken_id
            taken_endpoints.append(taken_endpoint)
            taken_finish_endpoint = taken_endpoint + '/finish'
            req = self.app.post(taken_finish_endpoint)
            self.ok(req)
            # finish the assessment taken, so next time we create one, it should
            # create a new one

    def test_max_attempts_throws_exception_if_taker_tries_to_exceed(self):
        item = self.create_item()
        item_1_id = unquote(item['id'])

        assessment = self.create_assessment()
        assessment_id = unquote(assessment['id'])

        assessment_detail_endpoint = '{0}/assessments/{1}'.format(self.url,
                                                                  assessment_id)
        assessment_offering_endpoint = assessment_detail_endpoint + '/assessmentsoffered'
        self.link_item_to_assessment(item, assessment)

        # Use POST to create an offering
        payload = {
            "startTime":  {
                "day":    1,
                "month":  1,
                "year":   2015
            },
            "duration"  : {
                "days"  : 2
            },
            "maxAttempts" : 2
        }
        req = self.app.post(assessment_offering_endpoint,
                            params=json.dumps(payload),
                            headers={'content-type': 'application/json'})
        self.ok(req)
        offering = json.loads(req.body)
        offering_id = unquote(offering['id'])

        # verify that the offering has defaulted to maxAttempts == 2
        self.assertEquals(offering['maxAttempts'], 2)

        assessment_offering_detail_endpoint = self.url + '/assessmentsoffered/' + offering_id

        num_attempts = 5
        # for deleting
        taken_endpoints = []
        assessment_offering_takens_endpoint = assessment_offering_detail_endpoint + '/assessmentstaken'

        for attempt in range(0, num_attempts):
            # Can POST to create a new taken
            if attempt >= payload['maxAttempts']:
                self.assertRaises(AppError,
                                  self.app.post,
                                  assessment_offering_takens_endpoint)
            else:
                req = self.app.post(assessment_offering_takens_endpoint)

                self.ok(req)
                taken = json.loads(req.body)
                taken_id = unquote(taken['id'])

                taken_endpoint = self.url + '/assessmentstaken/' + taken_id
                taken_endpoints.append(taken_endpoint)
                taken_finish_endpoint = taken_endpoint + '/finish'
                req = self.app.post(taken_finish_endpoint)
                self.ok(req)
                # finish the assessment taken, so next time we create one, it should
                # create a new one

    def test_can_update_review_options_flag(self):
        """
        For the Reviewable offered and taken records, can  change the reviewOptions
        flag on a created item
        :return:
        """
        item = self.create_item()
        item_1_id = unquote(item['id'])

        assessment = self.create_assessment()
        assessment_id = unquote(assessment['id'])

        assessment_detail_endpoint = '{0}/assessments/{1}'.format(self.url,
                                                                  assessment_id)
        assessment_offering_endpoint = assessment_detail_endpoint + '/assessmentsoffered'
        self.link_item_to_assessment(item, assessment)

        # Use POST to create an offering
        payload = {
            "startTime" : {
                "day"   : 1,
                "month" : 1,
                "year"  : 2015
            },
            "duration"  : {
                "days"  : 2
            }
        }

        req = self.app.post(assessment_offering_endpoint,
                            params=json.dumps(payload),
                            headers={'content-type': 'application/json'})
        self.ok(req)
        offering = json.loads(req.body)
        offering_id = unquote(offering['id'])

        # verify that the offering has defaulted to reviewOptions all true
        review_options = ['afterAttempt', 'afterDeadline', 'beforeDeadline', 'duringAttempt']
        for opt in review_options:
            self.assertTrue(offering['reviewOptions']['whetherCorrect'][opt])

        payload = {
            "reviewOptions": {
                "whetherCorrect": {
                    "duringAttempt": False
                }
            }
        }
        assessment_offering_detail_endpoint = self.url + '/assessmentsoffered/' + offering_id

        req = self.app.put(assessment_offering_detail_endpoint,
                           params=json.dumps(payload),
                           headers={'content-type': 'application/json'})

        self.ok(req)
        offering = json.loads(req.body)

        # verify that the offering has duringAttempt = False
        review_options = ['afterAttempt', 'afterDeadline', 'beforeDeadline', 'duringAttempt']
        for opt in review_options:
            if opt == 'duringAttempt':
                self.assertFalse(offering['reviewOptions']['whetherCorrect'][opt])
            else:
                self.assertTrue(offering['reviewOptions']['whetherCorrect'][opt])

    def test_review_options_flag_works_for_during_and_after_attempt(self):
        """
        For the Reviewable offered and taken records
        :return:
        """
        item = self.create_item()
        correct_choice = item['answers'][0]['choiceIds'][0]
        question_1_id = unquote(self.extract_question(item)['id'])

        assessment = self.create_assessment()
        assessment_id = unquote(assessment['id'])

        assessment_detail_endpoint = self.url + '/assessments/' + assessment_id
        assessment_offering_endpoint = assessment_detail_endpoint + '/assessmentsoffered'

        self.link_item_to_assessment(item, assessment)

        # Use POST to create an offering
        payload = {
            "startTime" : {
                "day"   : 1,
                "month" : 1,
                "year"  : 2015
            },
            "duration"  : {
                "days"  : 2
            }
        }

        req = self.app.post(assessment_offering_endpoint,
                            params=json.dumps(payload),
                            headers={'content-type': 'application/json'})
        self.ok(req)
        offering = json.loads(req.body)
        offering_id = unquote(offering['id'])

        # verify that the offering has defaulted to reviewOptions all true
        review_options = ['afterAttempt', 'afterDeadline', 'beforeDeadline', 'duringAttempt']
        for opt in review_options:
            self.assertTrue(offering['reviewOptions']['whetherCorrect'][opt])

        assessment_offering_detail_endpoint = self.url + '/assessmentsoffered/' + offering_id

        # Convert to a learner to test the rest of this
        # Can POST to create a new taken
        assessment_offering_takens_endpoint = assessment_offering_detail_endpoint + '/assessmentstaken'
        req = self.app.post(assessment_offering_takens_endpoint)
        self.ok(req)
        taken = json.loads(req.body)

        # verify the "reviewWhetherCorrect" is True
        self.assertTrue(taken['reviewWhetherCorrect'])

        # try again, but set to only view correct after attempt
        payload = {
            "startTime" : {
                "day"   : 1,
                "month" : 1,
                "year"  : 2015
            },
            "duration"  : {
                "days"  : 2
            },
            "reviewOptions": {
                "whetherCorrect": {
                    "duringAttempt": False
                }
            }
        }

        req = self.app.post(assessment_offering_endpoint,
                            params=json.dumps(payload),
                            headers={'content-type': 'application/json'})
        self.ok(req)
        offering = json.loads(req.body)
        offering_id = unquote(offering['id'])

        # verify that the offering has duringAttempt = False
        review_options = ['afterAttempt', 'afterDeadline', 'beforeDeadline', 'duringAttempt']
        for opt in review_options:
            if opt == 'duringAttempt':
                self.assertFalse(offering['reviewOptions']['whetherCorrect'][opt])
            else:
                self.assertTrue(offering['reviewOptions']['whetherCorrect'][opt])

        assessment_offering_detail_endpoint = self.url + '/assessmentsoffered/' + offering_id

        # Can POST to create a new taken
        assessment_offering_takens_endpoint = assessment_offering_detail_endpoint + '/assessmentstaken'
        req = self.app.post(assessment_offering_takens_endpoint)
        self.ok(req)
        taken = json.loads(req.body)
        taken_id = unquote(taken['id'])
        taken_endpoint = self.url + '/assessmentstaken/' + taken_id

        # verify the "reviewWhetherCorrect" is False
        self.assertFalse(taken['reviewWhetherCorrect'])

        # now submitting an answer should let reviewWhetherCorrect be True
        right_response = {
            "choiceIds": [correct_choice]
        }

        finish_taken_endpoint = taken_endpoint + '/finish'
        taken_questions_endpoint = taken_endpoint + '/questions'
        question_1_endpoint = taken_questions_endpoint + '/' + question_1_id
        question_1_submit_endpoint = question_1_endpoint + '/submit'

        req = self.app.post(question_1_submit_endpoint,
                            params=json.dumps(right_response),
                            headers={'content-type': 'application/json'})
        self.ok(req)

        req = self.app.post(finish_taken_endpoint)
        self.ok(req)

        req = self.app.get(taken_endpoint)
        self.ok(req)
        taken = json.loads(req.body)

        self.assertTrue(taken['reviewWhetherCorrect'])

    def test_can_set_n_of_m_on_create(self):
        item = self.create_item()

        assessment = self.create_assessment()
        assessment_id = unquote(assessment['id'])

        assessment_detail_endpoint = '{0}/assessments/{1}'.format(self.url,
                                                                  assessment_id)
        assessment_offering_endpoint = assessment_detail_endpoint + '/assessmentsoffered'
        self.link_item_to_assessment(item, assessment)

        # Use POST to create an offering
        payload = {
            "startTime" : {
                "day"   : 1,
                "month" : 1,
                "year"  : 2015
            },
            "duration"  : {
                "days"  : 2
            },
            "nOfM" : 2
        }
        req = self.app.post(assessment_offering_endpoint,
                            params=json.dumps(payload),
                            headers={'content-type': 'application/json'})
        self.ok(req)
        offering = json.loads(req.body)
        self.assertEquals(offering['nOfM'], 2)

    def test_can_update_n_of_m_on_update(self):
        item = self.create_item()

        assessment = self.create_assessment()
        assessment_id = unquote(assessment['id'])

        assessment_detail_endpoint = '{0}/assessments/{1}'.format(self.url,
                                                                  assessment_id)
        assessment_offering_endpoint = assessment_detail_endpoint + '/assessmentsoffered'
        self.link_item_to_assessment(item, assessment)

        # Use POST to create an offering
        payload = {
            "startTime" : {
                "day"   : 1,
                "month" : 1,
                "year"  : 2015
            },
            "duration"  : {
                "days"  : 2
            }
        }
        req = self.app.post(assessment_offering_endpoint,
                            params=json.dumps(payload),
                            headers={'content-type': 'application/json'})
        self.ok(req)
        offering = json.loads(req.body)
        self.assertEquals(offering['nOfM'], -1)

        payload = {
            "nOfM": 5
        }

        assessment_offering_details_endpoint = '{0}/{1}'.format(assessment_offering_endpoint,
                                                                unquote(offering['id']))

        req = self.app.put(assessment_offering_details_endpoint,
                           params=json.dumps(payload),
                           headers={'content-type': 'application/json'})
        self.ok(req)
        offering = json.loads(req.body)
        self.assertEquals(offering['nOfM'], payload['nOfM'])

    def test_can_see_n_of_m_when_getting_taken_questions(self):
        item = self.create_item()

        assessment = self.create_assessment()
        assessment_id = unquote(assessment['id'])

        assessment_detail_endpoint = '{0}/assessments/{1}'.format(self.url,
                                                                  assessment_id)
        assessment_offering_endpoint = assessment_detail_endpoint + '/assessmentsoffered'
        self.link_item_to_assessment(item, assessment)

        # Use POST to create an offering
        payload = {
            "startTime" : {
                "day"   : 1,
                "month" : 1,
                "year"  : 2015
            },
            "duration"  : {
                "days"  : 2
            },
            "nOfM" : 2
        }
        req = self.app.post(assessment_offering_endpoint,
                            params=json.dumps(payload),
                            headers={'content-type': 'application/json'})
        self.ok(req)
        offered = json.loads(req.body)
        self.assertEquals(offered['nOfM'], 2)

        assessment_offering_detail_endpoint = self.url + '/assessmentsoffered/' + unquote(str(offered['id']))

        # Can POST to create a new taken
        assessment_offering_takens_endpoint = assessment_offering_detail_endpoint + '/assessmentstaken'
        req = self.app.post(assessment_offering_takens_endpoint)
        self.ok(req)
        taken = json.loads(req.body)
        taken_id = unquote(taken['id'])

        # Instructor can now take the assessment
        taken_endpoint = self.url + '/assessmentstaken/' + taken_id

        # Only GET of this endpoint is supported
        taken_questions_endpoint = taken_endpoint + '/questions'

        req = self.app.get(taken_questions_endpoint)
        self.ok(req)
        data = json.loads(req.body)
        self.assertIn('nOfM', data)
        self.assertEqual(data['nOfM'], payload['nOfM'])

    def test_can_set_genus_type_on_create(self):
        item = self.create_item()

        assessment = self.create_assessment()
        assessment_id = unquote(assessment['id'])

        assessment_detail_endpoint = '{0}/assessments/{1}'.format(self.url,
                                                                  assessment_id)
        assessment_offering_endpoint = assessment_detail_endpoint + '/assessmentsoffered'
        self.link_item_to_assessment(item, assessment)

        payload = {
            "genusTypeId": "offered-genus-type%3Asingle-page%40ODL.MIT.EDU"
        }
        req = self.app.post(assessment_offering_endpoint,
                            params=json.dumps(payload),
                            headers={'content-type': 'application/json'})
        self.ok(req)
        offered = json.loads(req.body)
        self.assertEqual(payload['genusTypeId'], offered['genusTypeId'])

    def test_can_update_genus_type(self):
        single_page_genus = "offered-genus-type%3Asingle-page%40ODL.MIT.EDU"
        item = self.create_item()

        assessment = self.create_assessment()
        assessment_id = unquote(assessment['id'])

        assessment_detail_endpoint = '{0}/assessments/{1}'.format(self.url,
                                                                  assessment_id)
        assessment_offering_endpoint = assessment_detail_endpoint + '/assessmentsoffered'
        self.link_item_to_assessment(item, assessment)

        payload = {
            "startTime" : {
                "day"   : 1,
                "month" : 1,
                "year"  : 2015
            }
        }
        req = self.app.post(assessment_offering_endpoint,
                            params=json.dumps(payload),
                            headers={'content-type': 'application/json'})
        self.ok(req)
        offered = json.loads(req.body)
        self.assertNotEqual(single_page_genus, offered['genusTypeId'])

        payload = {
            "genusTypeId": single_page_genus
        }

        url = '{0}/assessmentsoffered/{1}'.format(self.url, offered['id'])
        req = self.app.put(url,
                           params=json.dumps(payload),
                           headers={'content-type': 'application/json'})
        self.ok(req)
        updated_offered = self.json(req)
        self.assertEqual(offered['id'], updated_offered['id'])
        self.assertEqual(updated_offered['genusTypeId'], single_page_genus)


class AssessmentTakingTests(BaseAssessmentTestCase):
    def create_assessment(self):
        # Now create an assessment, link the item to it,
        # and create an offering.
        # Use the offering_id to create the taken
        assessments_endpoint = self.url + '/assessments'
        assessment_name = 'a really hard assessment'
        assessment_desc = 'meant to differentiate students'
        payload = {
            "name": assessment_name,
            "description": assessment_desc
        }
        req = self.app.post(assessments_endpoint,
                            params=json.dumps(payload),
                            headers={'content-type': 'application/json'})
        self.ok(req)
        return self.json(req)

    def create_item(self):
        items_endpoint = self.url + '/items'

        # Use POST to create an item
        payload = self.item_payload()
        req = self.app.post(items_endpoint,
                            params=json.dumps(payload),
                            headers={'content-type': 'application/json'})
        self.ok(req)

        item = json.loads(req.body)
        return item

    def create_offered(self):
        url = '{0}/assessments/{1}/assessmentsoffered'.format(self.url,
                                                              unquote(self.assessment['id']))
        payload = {
            "startTime" : {
                "day"   : 1,
                "month" : 1,
                "year"  : 2015
            },
            "duration"  : {
                "days"  : 2
            }
        }

        req = self.app.post(url,
                            params=json.dumps(payload),
                            headers={'content-type': 'application/json'})
        self.ok(req)
        return json.loads(req.body)

    def item_payload(self):
        item_name = 'a really complicated item'
        item_desc = 'meant to differentiate students'
        question_string = 'can you manipulate this?'
        question_type = 'question-record-type%3Amulti-choice-edx%40ODL.MIT.EDU'
        answer_string = 'yes!'
        answer_type = 'answer-record-type%3Amulti-choice-edx%40ODL.MIT.EDU'
        return {
            "name": item_name,
            "description": item_desc,
            "question": {
                "type": question_type,
                "questionString": question_string,
                "choices": ['1', '2', '3']
            },
            "answers": [{
                "type": answer_type,
                "choiceId": 1
            }],
        }

    def link_item_to_assessment(self, item, assessment):
        assessment_items_endpoint = '{0}/assessments/{1}/items'.format(self.url,
                                                                       unquote(assessment['id']))

        # POST should create the linkage
        payload = {
            'itemIds': [unquote(item['id'])]
        }
        req = self.app.post(assessment_items_endpoint,
                            params=json.dumps(payload),
                            headers={'content-type': 'application/json'})
        self.ok(req)

    def responded(self, _req, _correct=False):
        expected_response = {
            "responded" : True,
            "correct"   : _correct
        }
        self.ok(_req)
        self.assertEqual(
            json.loads(_req.body),
            expected_response
        )

    def setUp(self):
        super(AssessmentTakingTests, self).setUp()
        self.url += '/banks/' + unquote(str(self._bank.ident))
        self.item = self.create_item()
        self.assessment = self.create_assessment()
        self.link_item_to_assessment(self.item, self.assessment)

        self.offered = self.create_offered()

    def tearDown(self):
        """
        Remove the test user from all groups in Membership
        Start from the smallest groupId because need to
        remove "parental" roles like for DepartmentAdmin / DepartmentOfficer
        """
        super(AssessmentTakingTests, self).tearDown()

    def test_multi_question_taking(self):
        """
        Creating an assessment with multiple questions
        allows consumer to pick and choose which one is taken

        NOTE: this tests the simple, question-dump (client in control)
        for taking assessments
        :return:
        """
        assessment_offering_detail_endpoint = self.url + '/assessmentsoffered/' + unquote(str(self.offered['id']))

        # Can POST to create a new taken
        assessment_offering_takens_endpoint = assessment_offering_detail_endpoint + '/assessmentstaken'
        req = self.app.post(assessment_offering_takens_endpoint)
        self.ok(req)
        taken = json.loads(req.body)
        taken_id = unquote(taken['id'])

        # Instructor can now take the assessment
        taken_endpoint = self.url + '/assessmentstaken/' + taken_id

        # Only GET of this endpoint is supported
        taken_questions_endpoint = taken_endpoint + '/questions'

        # Check that DELETE returns error code 405--we don't support this
        self.assertRaises(AppError,
                          self.app.delete,
                          taken_questions_endpoint)

        # PUT to this root url also returns a 405
        self.assertRaises(AppError,
                          self.app.put,
                          taken_questions_endpoint)

        # POST to this root url also returns a 405
        self.assertRaises(AppError,
                          self.app.post,
                          taken_questions_endpoint)

        req = self.app.get(taken_questions_endpoint)
        self.ok(req)
        questions = json.loads(req.body)['data']
        question = questions[0]

        question_submit_endpoint = '{0}/assessmentstaken/{1}/questions/{2}/submit'.format(self.url,
                                                                                          taken_id,
                                                                                          unquote(question['id']))

        item_definition = self.item_payload()

        self.verify_question(question,
                             item_definition['question']['questionString'],
                             item_definition['question']['type'])

        wrong_choice = question['choices'][1]['id']
        # Can submit a wrong response
        wrong_response = {
            "choiceIds": [wrong_choice]
        }

        # Check that DELETE returns error code 405--we don't support this
        self.assertRaises(AppError,
                          self.app.delete,
                          question_submit_endpoint)

        # PUT to this root url also returns a 405
        self.assertRaises(AppError,
                          self.app.put,
                          question_submit_endpoint)

        # GET to this root url also returns a 405
        self.assertRaises(AppError,
                          self.app.get,
                          question_submit_endpoint)

        req = self.app.post(question_submit_endpoint,
                            params=json.dumps(wrong_response),
                            headers={'content-type': 'application/json'})
        self.ok(req)
        self.verify_submission(req, _expected_result=False)

        question_status_endpoint = '{0}/assessmentstaken/{1}/questions/{2}/status'.format(self.url,
                                                                                          taken_id,
                                                                                          unquote(question['id']))

        # checking on the question status now should return a responded but wrong
        req = self.app.get(question_status_endpoint)
        self.responded(req, False)

        # can resubmit using the specific ID
        right_choice = question['choices'][0]['id']
        right_response = {
            "choiceIds": [right_choice]
        }
        req = self.app.post(question_submit_endpoint,
                            params=json.dumps(right_response),
                            headers={'content-type': 'application/json'})
        self.ok(req)
        self.verify_submission(req, _expected_result=True)

        # checking on the question status now should return a responded, right
        req = self.app.get(question_status_endpoint)
        self.responded(req, True)

    def test_mit_format_tag_included(self):
        assessment_offering_detail_endpoint = self.url + '/assessmentsoffered/' + unquote(str(self.offered['id']))

        # Can POST to create a new taken
        assessment_offering_takens_endpoint = assessment_offering_detail_endpoint + '/assessmentstaken'
        req = self.app.post(assessment_offering_takens_endpoint)
        self.ok(req)
        taken = json.loads(req.body)
        taken_id = unquote(taken['id'])

        # Instructor can now take the assessment
        taken_endpoint = self.url + '/assessmentstaken/' + taken_id

        # Only GET of this endpoint is supported
        taken_questions_endpoint = taken_endpoint + '/questions'

        req = self.app.get(taken_questions_endpoint)
        self.ok(req)
        data = json.loads(req.body)
        self.assertIn('data', data)
        self.assertIn('format', data)
        self.assertEqual(data['format'], 'MIT-CLIx-OEA')

    def test_can_set_username_in_header(self):
        assessment_offering_detail_endpoint = self.url + '/assessmentsoffered/' + unquote(str(self.offered['id']))
        test_student = 'student@tiss.edu'  # this is what we have authz set up for
        # Can POST to create a new taken
        assessment_offering_takens_endpoint = assessment_offering_detail_endpoint + '/assessmentstaken'
        req = self.app.post(assessment_offering_takens_endpoint,
                            headers={
                                'x-api-proxy': test_student
                            })
        self.ok(req)
        taken = json.loads(req.body)
        taken_id = unquote(taken['id'])
        self.assertIn(quote(quote(test_student)), taken['takingAgentId'])

        # Student can now take the assessment
        taken_endpoint = self.url + '/assessmentstaken/' + taken_id

        # Only GET of this endpoint is supported
        taken_questions_endpoint = taken_endpoint + '/questions'

        req = self.app.get(taken_questions_endpoint,
                           headers={
                               'x-api-proxy': test_student
                           })
        self.ok(req)
        questions = json.loads(req.body)['data']
        question = questions[0]

        question_submit_endpoint = '{0}/assessmentstaken/{1}/questions/{2}/submit'.format(self.url,
                                                                                          taken_id,
                                                                                          unquote(question['id']))

        item_definition = self.item_payload()

        self.verify_question(question,
                             item_definition['question']['questionString'],
                             item_definition['question']['type'])

        wrong_choice = question['choices'][1]['id']
        # Can submit a wrong response
        wrong_response = {
            "choiceIds": [wrong_choice]
        }

        req = self.app.post(question_submit_endpoint,
                            params=json.dumps(wrong_response),
                            headers={
                                'content-type': 'application/json',
                                'x-api-proxy': test_student
                            })
        self.ok(req)
        self.verify_submission(req, _expected_result=False)

        question_status_endpoint = '{0}/assessmentstaken/{1}/questions/{2}/status'.format(self.url,
                                                                                          taken_id,
                                                                                          unquote(question['id']))

        # checking on the question status now should return a responded but wrong
        req = self.app.get(question_status_endpoint)
        self.responded(req, False)

        # can resubmit using the specific ID
        right_choice = question['choices'][0]['id']
        right_response = {
            "choiceIds": [right_choice]
        }
        req = self.app.post(question_submit_endpoint,
                            params=json.dumps(right_response),
                            headers={
                                'content-type': 'application/json',
                                'x-api-proxy': test_student
                            })
        self.ok(req)
        self.verify_submission(req, _expected_result=True)

        # checking on the question status now should return a responded, right
        req = self.app.get(question_status_endpoint)
        self.responded(req, True)

        req = self.app.get(taken_endpoint)
        data = self.json(req)
        self.assertIn(quote(quote(test_student)), data['takingAgentId'])

    def test_can_finish_taken_to_get_new_taken(self):
        assessment_offering_detail_endpoint = self.url + '/assessmentsoffered/' + unquote(str(self.offered['id']))
        test_student = 'student@tiss.edu'  # this is what we have authz set up for
        # Can POST to create a new taken
        assessment_offering_takens_endpoint = assessment_offering_detail_endpoint + '/assessmentstaken'
        req = self.app.post(assessment_offering_takens_endpoint,
                            headers={
                                'x-api-proxy': test_student
                            })
        self.ok(req)
        taken = json.loads(req.body)
        taken_id = unquote(taken['id'])

        url = '{0}/assessmentstaken/{1}/finish'.format(self.url,
                                                       taken_id)

        req = self.app.post(url,
                            headers={
                                'x-api-proxy': test_student
                            })
        self.ok(req)
        data = self.json(req)
        self.assertTrue(data['success'])
        req = self.app.post(assessment_offering_takens_endpoint,
                            headers={
                                'x-api-proxy': test_student
                            })
        self.ok(req)
        taken2 = json.loads(req.body)
        taken2_id = unquote(taken2['id'])

        self.assertNotEqual(taken_id, taken2_id)

    def test_can_get_results_for_offered(self):
        assessment_offering_detail_endpoint = self.url + '/assessmentsoffered/' + unquote(str(self.offered['id']))
        test_student = 'student@tiss.edu'  # this is what we have authz set up for
        # Can POST to create a new taken
        assessment_offering_takens_endpoint = assessment_offering_detail_endpoint + '/assessmentstaken'
        req = self.app.post(assessment_offering_takens_endpoint,
                            headers={
                                'x-api-proxy': test_student
                            })
        self.ok(req)
        taken = json.loads(req.body)
        taken_id = unquote(taken['id'])
        taken_questions_url = '{0}/assessmentstaken/{1}/questions'.format(self.url,
                                                                          taken_id)
        req = self.app.get(taken_questions_url)
        self.ok(req)
        data = self.json(req)['data']
        question_1 = data[0]
        question_1_id = question_1['id']

        url = '{0}/{1}/submit'.format(taken_questions_url,
                                      question_1_id)
        choices = question_1['choices']
        wrong_answer = [c for c in choices if c['name'] == 'Choice 2'][0]
        payload = {
            'choiceIds': [wrong_answer['id']]
        }
        req = self.app.post(url,
                            params=json.dumps(payload),
                            headers={'content-type': 'application/json'})
        self.ok(req)
        data = self.json(req)
        self.assertFalse(data['correct'])

        results_url = '{0}/assessmentsoffered/{1}/results'.format(self.url,
                                                                  unquote(self.offered['id']))
        req = self.app.get(results_url)
        self.ok(req)
        data = self.json(req)
        self.assertEqual(len(data), 1)
        for index, question in enumerate(data[0]['questions']):
            self.assertIn('learningObjectiveIds', question)
            self.assertEqual(
                question['responses'][0]['choiceIds'],
                [wrong_answer['id']]
            )
            self.assertFalse(question['responses'][0]['isCorrect'])

        self.assertEqual(
            data[0]['questions'][0]['learningObjectiveIds'],
            []
        )


class BankTests(BaseAssessmentTestCase):
    def setUp(self):
        super(BankTests, self).setUp()
        self.url += '/banks'

    def tearDown(self):
        """
        Remove the test user from all groups in Membership
        Start from the smallest groupId because need to
        remove "parental" roles like for DepartmentAdmin / DepartmentOfficer
        """
        super(BankTests, self).tearDown()

    def test_can_set_bank_alias_on_create(self):
        payload = {
            "name": "New bank",
            "aliasId": "assessment.Bank%3Apublished-012345678910111213141516%40ODL.MIT.EDU"
        }
        req = self.app.post(self.url,
                            params=json.dumps(payload),
                            headers={'content-type': 'application/json'})
        self.ok(req)
        new_bank = self.json(req)

        url = '{0}/{1}'.format(self.url,
                               payload['aliasId'])
        req = self.app.get(url)
        self.ok(req)
        fetched_bank = self.json(req)
        self.assertEqual(new_bank['id'], fetched_bank['id'])
        self.assertEqual(new_bank['displayName']['text'], payload['name'])

    def test_can_query_on_bank_genus_type(self):
        genus_type = "assessment-bank-type%3Aedit%40ODL.MIT.EDU"
        payload = {
            "name": "New bank",
            "genusTypeId": genus_type
        }
        req = self.app.post(self.url,
                            params=json.dumps(payload),
                            headers={'content-type': 'application/json'})
        self.ok(req)
        new_bank = self.json(req)

        url = '{0}?genusTypeId={1}'.format(self.url,
                                           genus_type)
        req = self.app.get(url)
        self.ok(req)
        data = self.json(req)
        self.assertEqual(len(data), 1)
        self.assertEqual(new_bank['id'], data[0]['id'])
        self.assertEqual(data[0]['genusTypeId'], genus_type)

        url = '{0}?genusTypeId=foo'.format(self.url)
        req = self.app.get(url)
        self.ok(req)
        data = self.json(req)
        self.assertEqual(len(data), 0)

    def test_can_update_bank_alias(self):
        alias_id = "assessment.Bank%3Apublished-012345678910111213141516%40ODL.MIT.EDU"
        name = "New Bank"
        payload = {
            "name": name
        }
        req = self.app.post(self.url,
                            params=json.dumps(payload),
                            headers={'content-type': 'application/json'})
        self.ok(req)
        new_bank = self.json(req)

        url = '{0}/{1}'.format(self.url,
                               alias_id)
        self.assertRaises(AppError,
                          self.app.get,
                          url)

        payload = {
            "aliasId": alias_id
        }
        url = '{0}/{1}'.format(self.url,
                               new_bank['id'])

        req = self.app.put(url,
                           params=json.dumps(payload),
                           headers={'content-type': 'application/json'})
        self.ok(req)

        url = '{0}/{1}'.format(self.url,
                               alias_id)

        req = self.app.get(url)
        self.ok(req)
        fetched_bank = self.json(req)
        self.assertEqual(new_bank['id'], fetched_bank['id'])
        self.assertEqual(new_bank['displayName']['text'], name)


class BasicServiceTests(BaseAssessmentTestCase):
    """Test the views for getting the basic service calls

    """
    def setUp(self):
        super(BasicServiceTests, self).setUp()

    def tearDown(self):
        super(BasicServiceTests, self).tearDown()

    def test_users_can_get_list_of_banks(self):
        url = self.url + '/banks'
        req = self.app.get(url)
        self.ok(req)
        self.message(req, '[]')


class DragAndDropTests(BaseAssessmentTestCase):
    def setUp(self):
        super(DragAndDropTests, self).setUp()

        self._item = self.create_item(self._bank.ident)
        self._taken, self._offered = self.create_taken_for_item(self._bank.ident, self._item.ident)

        self.url += '/banks/' + unquote(str(self._bank.ident)) + '/items'

    def tearDown(self):
        super(DragAndDropTests, self).tearDown()


class HierarchyTests(BaseAssessmentTestCase):
    def add_root_bank(self, bank_id):
        if isinstance(bank_id, basestring):
            bank_id = utilities.clean_id(bank_id)
        am = get_managers()['am']
        am.add_root_bank(bank_id)

    def create_item(self, bank_id):
        if isinstance(bank_id, basestring):
            bank_id = utilities.clean_id(bank_id)

        bank = get_managers()['am'].get_bank(bank_id)
        form = bank.get_item_form_for_create([EDX_ITEM_RECORD_TYPE])
        form.display_name = 'a test item!'
        form.description = 'for testing with'
        form.set_genus_type(NUMERIC_RESPONSE_ITEM_GENUS_TYPE)
        new_item = bank.create_item(form)

        return new_item

    def num_banks(self, val):
        am = get_managers()['am']
        self.assertEqual(
            am.banks.available(),
            val
        )

    def query_node_hierarchy(self, bank_id, query_type='ancestors', value=1, expected_ids=()):
        query_url = '{0}/hierarchies/nodes/{1}?{2}={3}'.format(self.url,
                                                               unquote(str(bank_id)),
                                                               query_type,
                                                               value)
        req = self.app.get(query_url)
        self.ok(req)
        data = self.json(req)
        if query_type == 'ancestors':
            key = 'parentNodes'
        else:
            key = 'childNodes'
        self.assertEqual(
            len(data[key]),
            len(expected_ids)
        )
        if len(expected_ids) > 0:
            self.assertEqual(
                data[key][0]['id'],
                expected_ids[0]
            )

    def setUp(self):
        super(HierarchyTests, self).setUp()

    def tearDown(self):
        """
        Remove the test user from all groups in Membership
        Start from the smallest groupId because need to
        remove "parental" roles like for DepartmentAdmin / DepartmentOfficer
        """
        super(HierarchyTests, self).tearDown()

    def test_can_add_root_bank_to_hierarchy(self):
        self.num_banks(1)
        url = self.url + '/hierarchies/roots'

        payload = {
            'id'    : str(self._bank.ident)
        }

        req = self.app.post(url,
                            params=json.dumps(payload),
                            headers={
                                'content-type': 'application/json'
                            })

        self.ok(req)
        data = self.json(req)
        self.assertTrue(data['success'])
        self.num_banks(1)

    def test_can_remove_root_bank_from_hierarchy(self):
        self.num_banks(1)
        self.add_root_bank(self._bank.ident)
        url = self.url + '/hierarchies/roots/' + unquote(str(self._bank.ident))
        req = self.app.delete(url)
        self.ok(req)
        data = self.json(req)
        self.assertTrue(data['success'])
        self.num_banks(1)

    def test_removing_non_root_bank_from_hierarchy_throws_exception(self):
        self.num_banks(1)
        second_bank = create_new_bank()
        self.num_banks(2)
        self.add_root_bank(self._bank.ident)

        url = self.url + '/hierarchies/roots/' + unquote(str(second_bank.ident))
        self.assertRaises(AppError,
                          self.app.delete,
                          url)

        self.num_banks(2)

    def test_can_get_root_bank_list(self):
        self.add_root_bank(self._bank.ident)
        url = self.url + '/hierarchies/roots'
        req = self.app.get(url)
        self.ok(req)
        data = self.json(req)
        self.assertEqual(
            len(data),
            1
        )

        self.assertEqual(
            unquote(data[0]['id']),
            unquote(str(self._bank.ident))
        )

    def test_can_get_root_bank_details(self):
        self.add_root_bank(self._bank.ident)
        url = self.url + '/hierarchies/roots/' + unquote(str(self._bank.ident))
        req = self.app.get(url)
        self.ok(req)
        data = self.json(req)
        self.assertEqual(
            unquote(data['id']),
            unquote(str(self._bank.ident))
        )

    def test_getting_details_for_non_root_bank_throws_exception(self):
        second_bank = create_new_bank()
        self.add_root_bank(self._bank.ident)

        url = self.url + '/hierarchies/roots/' + unquote(str(second_bank.ident))
        self.assertRaises(AppError,
                          self.app.get,
                          url)

    def test_can_get_children_banks(self):
        second_bank = create_new_bank()
        self.add_root_bank(self._bank.ident)

        url = self.url + '/hierarchies/nodes/' + unquote(str(self._bank.ident)) + '/children'

        payload = {
            'ids'   : [str(second_bank.ident)]
        }

        req = self.app.post(url,
                            params=json.dumps(payload),
                            headers={
                                'content-type': 'application/json'
                            })
        self.ok(req)
        data = self.json(req)
        self.assertTrue(data['success'])

        url = self.url + '/hierarchies/nodes/' + unquote(str(self._bank.ident)) + '/children'
        req = self.app.get(url)
        self.ok(req)
        data = self.json(req)
        self.assertEqual(
            len(data),
            1
        )
        self.assertEqual(
            unquote(data[0]['id']),
            unquote(str(second_bank.ident))
        )

    def test_trying_to_add_child_to_non_root_bank_works(self):
        second_bank = create_new_bank()
        self.add_root_bank(self._bank.ident)

        url = self.url + '/hierarchies/nodes/' + unquote(str(second_bank.ident)) + '/children'

        payload = {
            'ids'   : [str(self._bank.ident)]
        }

        req = self.app.post(url,
                            params=json.dumps(payload),
                            headers={
                                'content-type': 'application/json'
                            })
        self.ok(req)
        data = self.json(req)
        self.assertTrue(data['success'])

        req = self.app.get(url)
        self.ok(req)
        data = self.json(req)
        self.assertEqual(
            len(data),
            1
        )
        self.assertEqual(
            unquote(data[0]['id']),
            unquote(str(self._bank.ident))
        )

    def test_trying_to_add_non_existent_child_to_node_throws_exception(self):
        self.add_root_bank(self._bank.ident)
        url = self.url + '/hierarchies/nodes/' + unquote(str(self._bank.ident)) + '/children'

        payload = {
            'ids'   : ['fake.MoreFake%3A1234567890abcdefabcdef12%40MIT']
        }

        self.assertRaises(AppError,
                          self.app.post,
                          url,
                          params=json.dumps(payload),
                          headers={'content-type': 'application/json'})

    def test_child_id_required_to_add_child_bank(self):
        second_bank = create_new_bank()
        self.add_root_bank(self._bank.ident)

        url = self.url + '/hierarchies/nodes/' + unquote(str(self._bank.ident)) + '/children'

        payload = {
            'oops'   : str(second_bank.ident)
        }

        self.assertRaises(AppError,
                          self.app.post,
                          url,
                          params=json.dumps(payload),
                          headers={'content-type': 'application/json'})

    def test_can_add_child_bank_to_node(self):
        second_bank = create_new_bank()
        self.add_root_bank(self._bank.ident)

        url = self.url + '/hierarchies/nodes/' + unquote(str(self._bank.ident)) + '/children'

        payload = {
            'ids'   : [str(second_bank.ident)]
        }

        req = self.app.post(url,
                            params=json.dumps(payload),
                            headers={
                                'content-type': 'application/json'
                            })
        self.ok(req)
        data = self.json(req)
        self.assertTrue(data['success'])

    def test_can_remove_child_from_node(self):
        second_bank = create_new_bank()
        self.add_root_bank(self._bank.ident)

        url = self.url + '/hierarchies/nodes/' + unquote(str(self._bank.ident)) + '/children'

        payload = {
            'ids'   : [str(second_bank.ident)]
        }

        req = self.app.post(url,
                            params=json.dumps(payload),
                            headers={
                                'content-type': 'application/json'
                            })
        self.ok(req)
        data = self.json(req)
        self.assertTrue(data['success'])

        req = self.app.get(url)
        self.ok(req)
        data = self.json(req)
        self.assertEqual(
            len(data),
            1
        )

        payload = {
            'ids': []
        }

        req = self.app.post(url,
                            params=json.dumps(payload),
                            headers={
                                'content-type': 'application/json'
                            })
        self.ok(req)
        data = self.json(req)
        self.assertTrue(data['success'])

        req = self.app.get(url)
        self.ok(req)
        data = self.json(req)
        self.assertEqual(
            len(data),
            0
        )

    def test_can_get_ancestor_and_descendant_levels(self):
        second_bank = create_new_bank()
        self.add_root_bank(self._bank.ident)

        url = self.url + '/hierarchies/nodes/' + unquote(str(self._bank.ident)) + '/children'

        payload = {
            'ids'   : [str(second_bank.ident)]
        }

        req = self.app.post(url,
                            params=json.dumps(payload),
                            headers={
                                'content-type': 'application/json'
                            })
        self.ok(req)
        data = self.json(req)
        self.assertTrue(data['success'])

        self.query_node_hierarchy(second_bank.ident, 'ancestors', 1, [str(self._bank.ident)])
        self.query_node_hierarchy(self._bank.ident, 'ancestors', 1, [])
        self.query_node_hierarchy(second_bank.ident, 'descendants', 1, [])
        self.query_node_hierarchy(self._bank.ident, 'descendants', 1, [str(second_bank.ident)])

    def test_can_query_hierarchy_nodes_with_descendants(self):
        second_bank = create_new_bank()
        self.add_root_bank(self._bank.ident)

        url = self.url + '/hierarchies/nodes/' + unquote(str(self._bank.ident)) + '/children'

        payload = {
            'ids'   : [str(second_bank.ident)]
        }

        req = self.app.post(url,
                            params=json.dumps(payload),
                            headers={
                                'content-type': 'application/json'
                            })
        self.ok(req)
        data = self.json(req)
        self.assertTrue(data['success'])

        third_bank = create_new_bank()

        url = self.url + '/hierarchies/nodes/' + unquote(str(second_bank.ident)) + '/children'

        payload = {
            'ids'   : [str(third_bank.ident)]
        }

        req = self.app.post(url,
                            params=json.dumps(payload),
                            headers={
                                'content-type': 'application/json'
                            })
        self.ok(req)
        data = self.json(req)
        self.assertTrue(data['success'])

        url = self.url + '/hierarchies/nodes/' + unquote(str(self._bank.ident)) + '/children?descendants=2'
        req = self.app.get(url)
        self.ok(req)
        data = self.json(req)[0]
        self.assertTrue(len(data['childNodes']) == 1)
        self.assertTrue(data['id'] == str(second_bank.ident))
        self.assertTrue(data['childNodes'][0]['id'] == str(third_bank.ident))

    def test_display_names_flag_shows_in_hierarchy_descendants(self):
        second_bank = create_new_bank()
        self.add_root_bank(self._bank.ident)

        url = self.url + '/hierarchies/nodes/' + unquote(str(self._bank.ident)) + '/children'

        payload = {
            'ids'   : [str(second_bank.ident)]
        }

        req = self.app.post(url,
                            params=json.dumps(payload),
                            headers={
                                'content-type': 'application/json'
                            })
        self.ok(req)
        data = self.json(req)
        self.assertTrue(data['success'])

        third_bank = create_new_bank()

        url = self.url + '/hierarchies/nodes/' + unquote(str(second_bank.ident)) + '/children'

        payload = {
            'ids'   : [str(third_bank.ident)]
        }

        req = self.app.post(url,
                            params=json.dumps(payload),
                            headers={
                                'content-type': 'application/json'
                            })
        self.ok(req)
        data = self.json(req)
        self.assertTrue(data['success'])

        url = self.url + '/hierarchies/nodes/' + unquote(str(self._bank.ident)) + '/children?descendants=2&display_names'
        req = self.app.get(url)
        self.ok(req)
        data = self.json(req)[0]
        self.assertTrue(len(data['childNodes']) == 1)
        self.assertTrue(data['id'] == str(second_bank.ident))
        self.assertTrue(data['displayName']['text'] == second_bank.display_name.text)
        self.assertTrue(data['childNodes'][0]['id'] == str(third_bank.ident))
        self.assertTrue(data['childNodes'][0]['displayName']['text'] == third_bank.display_name.text)

    def test_using_isolated_flag_for_assessments_returns_only_assessments_in_bank(self):
        second_bank = create_new_bank()
        self.add_root_bank(self._bank.ident)

        url = self.url + '/hierarchies/nodes/' + unquote(str(self._bank.ident)) + '/children'

        payload = {
            'ids'   : [str(second_bank.ident)]
        }

        req = self.app.post(url,
                            params=json.dumps(payload),
                            headers={
                                'content-type': 'application/json'
                            })
        self.ok(req)
        data = self.json(req)
        self.assertTrue(data['success'])

        url = '{0}/banks/{1}/assessments'.format(self.url,
                                                 str(second_bank.ident))
        payload = {
            "name": "for testing"
        }
        req = self.app.post(url,
                            params=json.dumps(payload),
                            headers={
                                'content-type': 'application/json'
                            })
        self.ok(req)
        assessment = self.json(req)

        url = '{0}/banks/{1}/assessments'.format(self.url,
                                                 str(self._bank.ident))

        req = self.app.get(url)
        self.ok(req)
        data = self.json(req)
        self.assertEqual(len(data), 1)

        self.assertEqual(data[0]['id'], assessment['id'])

        url = '{0}/banks/{1}/assessments?isolated'.format(self.url,
                                                          str(self._bank.ident))

        req = self.app.get(url)
        self.ok(req)
        data = self.json(req)
        self.assertEqual(len(data), 0)

    def test_using_isolated_flag_for_items_returns_only_items_in_bank(self):
        second_bank = create_new_bank()
        self.add_root_bank(self._bank.ident)

        url = self.url + '/hierarchies/nodes/' + unquote(str(self._bank.ident)) + '/children'

        payload = {
            'ids'   : [str(second_bank.ident)]
        }

        req = self.app.post(url,
                            params=json.dumps(payload),
                            headers={
                                'content-type': 'application/json'
                            })
        self.ok(req)
        data = self.json(req)
        self.assertTrue(data['success'])

        item = self.create_item(second_bank.ident)

        url = '{0}/banks/{1}/items'.format(self.url,
                                           str(self._bank.ident))

        req = self.app.get(url)
        self.ok(req)
        data = self.json(req)
        self.assertEqual(len(data), 1)

        self.assertEqual(data[0]['id'], str(item.ident))

        url = '{0}/banks/{1}/items?isolated'.format(self.url,
                                                    str(self._bank.ident))
        req = self.app.get(url)
        self.ok(req)
        data = self.json(req)
        self.assertEqual(len(data), 0)


class NumericAnswerTests(BaseAssessmentTestCase):
    def _grab_expression(self, text):
        soup = BeautifulSoup(text, 'xml')
        numeric_choice_wrapper = None
        interaction = soup.itemBody.textEntryInteraction
        for parent in interaction.parents:
            if parent.name == 'p':
                numeric_choice_wrapper = parent
                break

        numeric_choice_line_str = _stringify(numeric_choice_wrapper)
        return numeric_choice_line_str[3:numeric_choice_line_str.index('=')].strip()  # skip the opening <p> tag

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

        form = bank.get_assessment_offered_form_for_create(new_assessment.ident, [REVIEWABLE_OFFERED,
                                                                                  N_OF_M_OFFERED])
        new_offered = bank.create_assessment_offered(form)

        return new_offered

    def create_float_numeric_response_item(self):
        url = '{0}items'.format(self.url)
        self._float_numeric_response_test_file.seek(0)
        req = self.app.post(url,
                            upload_files=[('qtiFile', 'testFile', self._float_numeric_response_test_file.read())])
        self.ok(req)
        return self.json(req)

    def create_item(self, bank_id):
        if isinstance(bank_id, basestring):
            bank_id = utilities.clean_id(bank_id)

        bank = get_managers()['am'].get_bank(bank_id)
        form = bank.get_item_form_for_create([EDX_ITEM_RECORD_TYPE])
        form.display_name = 'a test item!'
        form.description = 'for testing with'
        form.set_genus_type(NUMERIC_RESPONSE_ITEM_GENUS_TYPE)
        new_item = bank.create_item(form)

        form = bank.get_question_form_for_create(item_id=new_item.ident,
                                                 question_record_types=[NUMERIC_RESPONSE_QUESTION_RECORD_TYPE])
        form.set_text('foo?')
        bank.create_question(form)

        self.right_answer = float(2.04)
        self.tolerance = float(0.71)
        form = bank.get_answer_form_for_create(item_id=new_item.ident,
                                               answer_record_types=[NUMERIC_RESPONSE_ANSWER_RECORD_TYPE])
        form.set_decimal_value(self.right_answer)
        form.set_tolerance_value(self.tolerance)

        bank.create_answer(form)

        return bank.get_item(new_item.ident)

    def create_simple_numeric_response_item(self):
        url = '{0}items'.format(self.url)
        self._simple_numeric_response_test_file.seek(0)
        req = self.app.post(url,
                            upload_files=[('qtiFile', 'testFile', self._simple_numeric_response_test_file.read())])
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
        super(NumericAnswerTests, self).setUp()

        self._item = self.create_item(self._bank.ident)
        self._taken, self._offered = self.create_taken_for_item(self._bank.ident, self._item.ident)

        self._simple_numeric_response_test_file = open('{0}/tests/files/new_numeric_response_format_test_file.zip'.format(ABS_PATH), 'r')
        # self._simple_numeric_response_test_file = open('{0}/tests/files/numeric_response_test_file.zip'.format(ABS_PATH), 'r')
        self._float_numeric_response_test_file = open('{0}/tests/files/new_floating_point_numeric_response_test_file.zip'.format(ABS_PATH), 'r')
        # self._float_numeric_response_test_file = open('{0}/tests/files/floating_point_numeric_input_test_file.zip'.format(ABS_PATH), 'r')

        self.url += '/banks/' + unquote(str(self._bank.ident)) + '/'

    def tearDown(self):
        super(NumericAnswerTests, self).tearDown()

        self._simple_numeric_response_test_file.close()
        self._float_numeric_response_test_file.close()

    def test_can_create_item(self):
        self.assertEqual(
            str(self._item.ident),
            str(self._item.ident)
        )

    def test_can_create_item_via_rest(self):
        payload = {
            'name': 'a clix testing question',
            'description': 'for testing clix items',
            'question': {
                'type': 'question-record-type%3Anumeric-response-edx%40ODL.MIT.EDU',
                'questionString': 'give me a number'
            },
            'answers': [{
                'decimalValue': -10.01,
                'tolerance': 0.1,
                'type': 'answer-record-type%3Anumeric-response-edx%40ODL.MIT.EDU'
            }]
        }
        req = self.app.post(self.url + 'items',
                            params=json.dumps(payload),
                            headers={'content-type': 'application/json'})
        self.ok(req)
        data = self.json(req)
        self.assertEqual(
            data['displayName']['text'],
            payload['name']
        )
        self.assertEqual(
            data['question']['text']['text'],
            payload['question']['questionString']
        )

        self.assertEqual(
            data['answers'][0]['decimalValue'],
            payload['answers'][0]['decimalValue']
        )

        self.assertEqual(
            data['answers'][0]['decimalValues']['tolerance'],
            payload['answers'][0]['tolerance']
        )

    def test_can_update_item_via_rest(self):
        url = '{0}items/{1}'.format(self.url,
                                    unquote(str(self._item.ident)))
        payload = {
            'answers': [{
                'id': str(self._item.get_answers().next().ident),
                'decimalValue': -10.01,
                'tolerance': 0.1,
                'type': 'answer-record-type%3Anumeric-response-edx%40ODL.MIT.EDU'
            }]
        }

        req = self.app.put(url,
                           params=json.dumps(payload),
                           headers={'content-type': 'application/json'})
        self.ok(req)
        data = self.json(req)
        self.assertEqual(
            data['id'],
            str(self._item.ident)
        )

        self.assertEqual(
            data['answers'][0]['decimalValue'],
            payload['answers'][0]['decimalValue']
        )

        self.assertEqual(
            data['answers'][0]['decimalValues']['tolerance'],
            payload['answers'][0]['tolerance']
        )

    def test_valid_response_returns_correct(self):
        url = '{0}assessmentstaken/{1}/questions/{2}/submit'.format(self.url,
                                                                    unquote(str(self._taken.ident)),
                                                                    unquote(str(self._item.ident)))
        payload = {
            'decimalValue': 1.5,
            'type': 'answer-record-type%3Anumeric-response-edx%40ODL.MIT.EDU'
        }

        req = self.app.post(url,
                            params=json.dumps(payload),
                            headers={'content-type': 'application/json'})
        self.ok(req)
        data = self.json(req)
        self.assertTrue(data['correct'])
        # don't use feedback.text here because OEA expects a string
        self.assertEqual(
            data['feedback'],
            'No feedback available.'
        )

    def test_invalid_response_returns_incorrect(self):
        url = '{0}assessmentstaken/{1}/questions/{2}/submit'.format(self.url,
                                                                    unquote(str(self._taken.ident)),
                                                                    unquote(str(self._item.ident)))
        payload = {
            'decimalValue': 1.2,
            'type': 'answer-record-type%3Anumeric-response-edx%40ODL.MIT.EDU'
        }

        req = self.app.post(url,
                            params=json.dumps(payload),
                            headers={'content-type': 'application/json'})
        self.ok(req)
        data = self.json(req)
        self.assertFalse(data['correct'])
        # don't use feedback.text here because OEA expects a string
        self.assertEqual(
            data['feedback'],
            'No feedback available.'
        )

    def test_can_submit_right_answer_simple_numeric(self):
        nr_item = self.create_simple_numeric_response_item()
        taken, offered = self.create_taken_for_item(self._bank.ident, Id(nr_item['id']))

        url = '{0}/assessmentstaken/{1}/questions'.format(self.url,
                                                          unquote(str(taken.ident)))
        req = self.app.get(url)
        self.ok(req)
        data = self.json(req)
        question_id = data['data'][0]['id']
        expression = self._grab_expression(data['data'][0]['texts'][0]['text'])
        right_answer = sympify(expression)

        url = '{0}/assessmentstaken/{1}/questions/{2}/submit'.format(self.url,
                                                                     unquote(str(taken.ident)),
                                                                     question_id)

        payload = {
            'RESPONSE_1': str(right_answer),
            'type': 'answer-type%3Aqti-numeric-response%40ODL.MIT.EDU'
        }
        req = self.app.post(url,
                            params=json.dumps(payload),
                            headers={'content-type': 'application/json'})
        self.ok(req)
        data = self.json(req)
        self.assertTrue(data['correct'])
        self.assertIn('<p/>', data['feedback'])

    def test_can_submit_wrong_answer_simple_numeric(self):
        mc_item = self.create_simple_numeric_response_item()
        taken, offered = self.create_taken_for_item(self._bank.ident, Id(mc_item['id']))

        url = '{0}/assessmentstaken/{1}/questions'.format(self.url,
                                                          unquote(str(taken.ident)))
        req = self.app.get(url)
        self.ok(req)
        data = self.json(req)
        question_id = data['data'][0]['id']
        expression = self._grab_expression(data['data'][0]['texts'][0]['text'])
        right_answer = sympify(expression)

        url = '{0}/assessmentstaken/{1}/questions/{2}/submit'.format(self.url,
                                                                     unquote(str(taken.ident)),
                                                                     question_id)
        payload = {
            'RESPONSE_1': str(right_answer + 1),
            'type': 'answer-type%3Aqti-numeric-response%40ODL.MIT.EDU'
        }
        req = self.app.post(url,
                            params=json.dumps(payload),
                            headers={'content-type': 'application/json'})
        self.ok(req)
        data = self.json(req)
        self.assertFalse(data['correct'])
        # self.assertNotIn('Correct!', data['feedback'])
        self.assertIn('<p/>', data['feedback'])

    def test_empty_string_evaluates_as_wrong_answer_simple_numeric(self):
        nr_item = self.create_simple_numeric_response_item()
        taken, offered = self.create_taken_for_item(self._bank.ident, Id(nr_item['id']))

        url = '{0}/assessmentstaken/{1}/questions'.format(self.url,
                                                          unquote(str(taken.ident)))
        req = self.app.get(url)
        self.ok(req)
        data = self.json(req)
        question_id = data['data'][0]['id']
        expression = self._grab_expression(data['data'][0]['texts'][0]['text'])
        right_answer = sympify(expression)

        url = '{0}/assessmentstaken/{1}/questions/{2}/submit'.format(self.url,
                                                                     unquote(str(taken.ident)),
                                                                     question_id)

        payload = {
            'RESPONSE_1': "",
            'type': 'answer-type%3Aqti-numeric-response%40ODL.MIT.EDU'
        }
        req = self.app.post(url,
                            params=json.dumps(payload),
                            headers={'content-type': 'application/json'})
        self.ok(req)
        data = self.json(req)
        self.assertFalse(data['correct'])
        # self.assertNotIn('Correct!', data['feedback'])
        self.assertIn('<p/>', data['feedback'])

    def test_cannot_submit_non_integer_to_simple_numeric(self):
        mc_item = self.create_simple_numeric_response_item()
        taken, offered = self.create_taken_for_item(self._bank.ident, Id(mc_item['id']))
        url = '{0}/assessmentstaken/{1}/questions'.format(self.url,
                                                          unquote(str(taken.ident)))
        req = self.app.get(url)
        self.ok(req)
        data = self.json(req)
        question_id = data['data'][0]['id']
        expression = self._grab_expression(data['data'][0]['texts'][0]['text'])
        right_answer = sympify(expression)

        url = '{0}/assessmentstaken/{1}/questions/{2}/submit'.format(self.url,
                                                                     unquote(str(taken.ident)),
                                                                     question_id)
        payload = {
            'RESPONSE_1': str(right_answer) + '.0',
            'type': 'answer-type%3Aqti-numeric-response%40ODL.MIT.EDU'
        }
        req = self.app.post(url,
                            params=json.dumps(payload),
                            headers={'content-type': 'application/json'})
        self.ok(req)
        data = self.json(req)
        self.assertFalse(data['correct'])
        # self.assertNotIn('Correct!', data['feedback'])
        self.assertIn('<p/>', data['feedback'])

    def test_getting_same_question_twice_returns_same_parameter_values_simple_numeric(self):
        nr_item = self.create_simple_numeric_response_item()
        taken, offered = self.create_taken_for_item(self._bank.ident, Id(nr_item['id']))
        url = '{0}assessmentstaken/{1}/questions'.format(self.url,
                                                         unquote(str(taken.ident)))
        req = self.app.get(url)
        self.ok(req)
        data = self.json(req)
        question_1_id = data['data'][0]['id']

        # deprecate this part of the test ... we have no access to the internal
        # magic ID because of the unique assessment-session question IDs
        # make sure the text matches the ID params
        # question_1_params = json.loads(unquote(Id(question_1_id).identifier).split('?')[-1])
        # question_expression = data['data'][0]['text']['text'].split(':')[-1].split('=')[0].strip()
        # expected_expression = '{0} + {1}'.format(question_1_params['var1'],
        #                                          question_1_params['var2'])
        # self.assertEqual(
        #     question_expression,
        #     expected_expression
        # )

        url = '{0}/assessmentstaken/{1}/questions/{2}'.format(self.url,
                                                              unquote(str(taken.ident)),
                                                              question_1_id)

        req = self.app.get(url)
        self.ok(req)
        data1 = self.json(req)
        q1 = data1['texts'][0]['text']
        self.assertNotEqual(q1, '')

        for i in range(0, 10):
            req = self.app.get(url)
            self.ok(req)
            data2 = self.json(req)
            q2 = data2['texts'][0]['text']
            self.assertEqual(q1, q2)

    def test_can_submit_right_answer_float_numeric(self):
        nr_item = self.create_float_numeric_response_item()
        taken, offered = self.create_taken_for_item(self._bank.ident, Id(nr_item['id']))

        url = '{0}/assessmentstaken/{1}/questions'.format(self.url,
                                                          unquote(str(taken.ident)))
        req = self.app.get(url)
        self.ok(req)
        data = self.json(req)
        question_id = data['data'][0]['id']
        expression = self._grab_expression(data['data'][0]['texts'][0]['text'])
        right_answer = sympify(expression)

        url = '{0}/assessmentstaken/{1}/questions/{2}/submit'.format(self.url,
                                                                     unquote(str(taken.ident)),
                                                                     question_id)

        payload = {
            'RESPONSE_1': str(right_answer),
            'type': 'answer-type%3Aqti-numeric-response%40ODL.MIT.EDU'
        }
        req = self.app.post(url,
                            params=json.dumps(payload),
                            headers={'content-type': 'application/json'})
        self.ok(req)
        data = self.json(req)
        self.assertTrue(data['correct'])
        self.assertIn('<p/>', data['feedback'])

    def test_can_submit_wrong_answer_float_numeric(self):
        nr_item = self.create_float_numeric_response_item()
        taken, offered = self.create_taken_for_item(self._bank.ident, Id(nr_item['id']))

        url = '{0}/assessmentstaken/{1}/questions'.format(self.url,
                                                          unquote(str(taken.ident)))
        req = self.app.get(url)
        self.ok(req)
        data = self.json(req)
        question_id = data['data'][0]['id']
        expression = self._grab_expression(data['data'][0]['texts'][0]['text'])
        right_answer = sympify(expression)

        url = '{0}/assessmentstaken/{1}/questions/{2}/submit'.format(self.url,
                                                                     unquote(str(taken.ident)),
                                                                     question_id)

        payload = {
            'RESPONSE_1': str(right_answer - 0.1),
            'type': 'answer-type%3Aqti-numeric-response%40ODL.MIT.EDU'
        }
        req = self.app.post(url,
                            params=json.dumps(payload),
                            headers={'content-type': 'application/json'})
        self.ok(req)
        data = self.json(req)
        self.assertFalse(data['correct'])
        # self.assertNotIn('Correct!', data['feedback'])
        self.assertIn('<p/>', data['feedback'])

    def test_empty_string_evaluates_as_wrong_answer_float_numeric(self):
        nr_item = self.create_float_numeric_response_item()
        taken, offered = self.create_taken_for_item(self._bank.ident, Id(nr_item['id']))

        url = '{0}/assessmentstaken/{1}/questions'.format(self.url,
                                                          unquote(str(taken.ident)))
        req = self.app.get(url)
        self.ok(req)
        data = self.json(req)
        question_id = data['data'][0]['id']
        expression = self._grab_expression(data['data'][0]['texts'][0]['text'])
        right_answer = sympify(expression)

        url = '{0}/assessmentstaken/{1}/questions/{2}/submit'.format(self.url,
                                                                     unquote(str(taken.ident)),
                                                                     question_id)

        payload = {
            'RESPONSE_1': "",
            'type': 'answer-type%3Aqti-numeric-response%40ODL.MIT.EDU'
        }
        req = self.app.post(url,
                            params=json.dumps(payload),
                            headers={'content-type': 'application/json'})
        self.ok(req)
        data = self.json(req)
        self.assertFalse(data['correct'])
        # self.assertNotIn('Correct!', data['feedback'])
        self.assertIn('<p/>', data['feedback'])

    def test_cannot_submit_non_float_to_float_numeric(self):
        nr_item = self.create_float_numeric_response_item()
        taken, offered = self.create_taken_for_item(self._bank.ident, Id(nr_item['id']))

        url = '{0}/assessmentstaken/{1}/questions'.format(self.url,
                                                          unquote(str(taken.ident)))
        req = self.app.get(url)
        self.ok(req)
        data = self.json(req)
        question_id = data['data'][0]['id']
        expression = self._grab_expression(data['data'][0]['texts'][0]['text'])
        right_answer = sympify(expression)

        url = '{0}/assessmentstaken/{1}/questions/{2}/submit'.format(self.url,
                                                                     unquote(str(taken.ident)),
                                                                     question_id)

        payload = {
            'RESPONSE_1': str(int(right_answer)),
            'type': 'answer-type%3Aqti-numeric-response%40ODL.MIT.EDU'
        }
        req = self.app.post(url,
                            params=json.dumps(payload),
                            headers={'content-type': 'application/json'})
        self.ok(req)
        data = self.json(req)
        self.assertFalse(data['correct'])
        # self.assertNotIn('Correct!', data['feedback'])
        self.assertIn('<p/>', data['feedback'])

    def test_getting_same_question_twice_returns_same_parameter_values_float_numeric(self):
        nr_item = self.create_float_numeric_response_item()
        taken, offered = self.create_taken_for_item(self._bank.ident, Id(nr_item['id']))
        url = '{0}/assessmentstaken/{1}/questions'.format(self.url,
                                                          unquote(str(taken.ident)))
        req = self.app.get(url)
        self.ok(req)
        data = self.json(req)
        question_1_id = data['data'][0]['id']

        # deprecate this part of the test ... we have no access to the internal
        # magic ID because of the unique assessment-session question IDs
        # make sure the text matches the ID params
        # question_1_params = json.loads(unquote(Id(question_1_id).identifier).split('?')[-1])
        # question_expression = data['data'][0]['text']['text'].split(':')[-1].split('=')[0].strip()
        # expected_expression = '{0} + {1}'.format("%.4f" % (question_1_params['var1'],),
        #                                          question_1_params['var2'])
        # self.assertEqual(
        #     question_expression,
        #     expected_expression
        # )

        url = '{0}/assessmentstaken/{1}/questions/{2}'.format(self.url,
                                                              unquote(str(taken.ident)),
                                                              question_1_id)

        req = self.app.get(url)
        self.ok(req)
        data1 = self.json(req)
        q1 = data1['texts'][0]['text']
        self.assertNotEqual(q1, '')

        for i in range(0, 10):
            req = self.app.get(url)
            self.ok(req)
            data2 = self.json(req)
            q2 = data2['texts'][0]['text']
            self.assertEqual(q1, q2)


class FileUploadTests(BaseAssessmentTestCase):
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

        return new_assessment, new_offered

    def create_item(self, bank_id):
        if isinstance(bank_id, basestring):
            bank_id = utilities.clean_id(bank_id)

        bank = get_managers()['am'].get_bank(bank_id)
        form = bank.get_item_form_for_create([QTI_ITEM_RECORD])
        form.display_name = 'a test item!'
        form.description = 'for testing with'
        form.load_from_qti_item(self._test_xml)
        new_item = bank.create_item(form)

        form = bank.get_question_form_for_create(item_id=new_item.ident,
                                                 question_record_types=[QTI_QUESTION_RECORD])
        form.load_from_qti_item(self._test_xml)
        bank.create_question(form)

        form = bank.get_answer_form_for_create(item_id=new_item.ident,
                                               answer_record_types=[QTI_ANSWER_RECORD])
        form.load_from_qti_item(self._test_xml)
        bank.create_answer(form)

        return bank.get_item(new_item.ident)

    def create_mw_sandbox_item(self):
        url = '{0}/items'.format(self.url)
        self._mw_sandbox_test_file.seek(0)
        req = self.app.post(url,
                            upload_files=[('qtiFile', 'testFile', self._mw_sandbox_test_file.read())])
        self.ok(req)
        return self.json(req)

    def get_question_id(self, taken):
        url = '{0}/assessmentstaken/{1}/questions'.format(self.url,
                                                          unquote(str(taken.ident)))
        req = self.app.get(url)
        self.ok(req)
        data = self.json(req)
        return data['data'][0]['id']

    def create_taken_for_item(self, bank_id, item_id):
        if isinstance(bank_id, basestring):
            bank_id = utilities.clean_id(bank_id)
        if isinstance(item_id, basestring):
            item_id = utilities.clean_id(item_id)

        bank = get_managers()['am'].get_bank(bank_id)

        new_assessment, new_offered = self.create_assessment_offered_for_item(bank_id, item_id)

        form = bank.get_assessment_taken_form_for_create(new_offered.ident, [])
        taken = bank.create_assessment_taken(form)
        return taken, new_offered, new_assessment

    def setUp(self):
        super(FileUploadTests, self).setUp()

        self._audio_recording_test_file = open('{0}/tests/files/Social_Introductions_Role_Play.zip'.format(ABS_PATH), 'r')
        self._audio_response_file = open('{0}/tests/files/349398__sevenbsb__air-impact-wrench.wav'.format(ABS_PATH), 'r')
        self._generic_upload_test_file = open('{0}/tests/files/generic_upload_test_file.zip'.format(ABS_PATH), 'r')
        self._generic_upload_response_test_file = open('{0}/tests/files/Epidemic2.sltng'.format(ABS_PATH), 'r')
        self._mw_sandbox_test_file = open('{0}/tests/files/mw_sandbox.zip'.format(ABS_PATH), 'r')

        self.url += '/banks/' + unquote(str(self._bank.ident))

    def tearDown(self):
        super(FileUploadTests, self).tearDown()

        self._audio_response_file.close()
        self._audio_recording_test_file.close()
        self._generic_upload_test_file.close()
        self._generic_upload_response_test_file.close()
        self._mw_sandbox_test_file.close()

    def test_can_send_audio_file_response_for_audio_rt(self):
        url = '{0}/items'.format(self.url)
        self._audio_recording_test_file.seek(0)
        req = self.app.post(url,
                            upload_files=[('qtiFile', 'testFile', self._audio_recording_test_file.read())])
        self.ok(req)
        item = self.json(req)
        self._taken, self._offered, self._assessment = self.create_taken_for_item(self._bank.ident, utilities.clean_id(item['id']))
        url = '{0}/assessmentstaken/{1}/questions/{2}/submit'.format(self.url,
                                                                     unquote(str(self._taken.ident)),
                                                                     unquote(item['id']))
        self._audio_response_file.seek(0)
        req = self.app.post(url,
                            upload_files=[('submission', 'submissionFile.wav', self._audio_response_file.read())])
        self.ok(req)
        data = self.json(req)
        self.assertTrue(data['correct'])
        self.assertIn('<p/>', data['feedback'])

    def test_can_send_file_with_no_extension_for_audio_rt(self):
        url = '{0}/items'.format(self.url)
        self._audio_recording_test_file.seek(0)
        req = self.app.post(url,
                            upload_files=[('qtiFile', 'testFile', self._audio_recording_test_file.read())])
        self.ok(req)
        item = self.json(req)
        self._taken, self._offered, self._assessment = self.create_taken_for_item(self._bank.ident, utilities.clean_id(item['id']))
        url = '{0}/assessmentstaken/{1}/questions/{2}/submit'.format(self.url,
                                                                     unquote(str(self._taken.ident)),
                                                                     unquote(item['id']))
        self._audio_response_file.seek(0)
        req = self.app.post(url,
                            upload_files=[('submission', 'submissionFile', self._audio_response_file.read())])
        self.ok(req)
        data = self.json(req)
        self.assertTrue(data['correct'])
        self.assertIn('<p/>', data['feedback'])
        # TODO: no way to check if that file now has an extension, on disk?

    def test_can_send_generic_file_response_for_generic_file_upload(self):
        url = '{0}/items'.format(self.url)
        self._generic_upload_test_file.seek(0)
        req = self.app.post(url,
                            upload_files=[('qtiFile', 'testFile', self._generic_upload_test_file.read())])
        self.ok(req)
        item = self.json(req)
        self._taken, self._offered, self._assessment = self.create_taken_for_item(self._bank.ident, utilities.clean_id(item['id']))
        url = '{0}/assessmentstaken/{1}/questions/{2}/submit'.format(self.url,
                                                                     unquote(str(self._taken.ident)),
                                                                     unquote(item['id']))
        self._generic_upload_response_test_file.seek(0)
        req = self.app.post(url,
                            upload_files=[('submission', 'Epidemic2.sltng', self._generic_upload_response_test_file.read())])
        self.ok(req)
        data = self.json(req)
        self.assertTrue(data['correct'])
        self.assertEqual('<?xml version="1.0" encoding="utf-8"?>\n<modalFeedback identifier="Feedback464983843" outcomeIdentifier="FEEDBACKMODAL" showHide="show">\n <p>\n  <strong>\n   <span id="docs-internal-guid-46f83555-04c5-8000-2639-b910cd8704bf">\n    Upload successful!\n   </span>\n   <br/>\n  </strong>\n </p>\n</modalFeedback>',
                         data['feedback'])

    def test_empty_response_without_file_throws_error(self):
        url = '{0}/items'.format(self.url)
        self._generic_upload_test_file.seek(0)
        req = self.app.post(url,
                            upload_files=[('qtiFile', 'testFile', self._generic_upload_test_file.read())])
        self.ok(req)
        item = self.json(req)
        self._taken, self._offered, self._assessment = self.create_taken_for_item(self._bank.ident, utilities.clean_id(item['id']))
        url = '{0}/assessmentstaken/{1}/questions/{2}/submit'.format(self.url,
                                                                     unquote(str(self._taken.ident)),
                                                                     unquote(item['id']))
        self.assertRaises(AppError,
                          self.app.post,
                          url)

    def test_can_submit_file_to_mw_sandbox(self):
        sandbox = self.create_mw_sandbox_item()
        self._taken, self._offered, self._assessment = self.create_taken_for_item(self._bank.ident, utilities.clean_id(sandbox['id']))

        question_id = self.get_question_id(self._taken)

        url = '{0}/assessmentstaken/{1}/questions/{2}/submit'.format(self.url,
                                                                     unquote(str(self._taken.ident)),
                                                                     question_id)
        self._audio_recording_test_file.seek(0)
        req = self.app.post(url,
                            upload_files=[('submission', 'myRecording.wav', self._audio_recording_test_file.read())])
        self.ok(req)
        data = self.json(req)
        self.assertTrue(data['correct'])
        self.assertIn('<p/>', data['feedback'])

    def test_can_do_empty_response_for_mw_sandbox(self):
        sandbox = self.create_mw_sandbox_item()
        self._taken, self._offered, self._assessment = self.create_taken_for_item(self._bank.ident, utilities.clean_id(sandbox['id']))

        question_id = self.get_question_id(self._taken)

        url = '{0}/assessmentstaken/{1}/questions/{2}/submit'.format(self.url,
                                                                     unquote(str(self._taken.ident)),
                                                                     question_id)
        req = self.app.post(url)
        self.ok(req)
        data = self.json(req)
        self.assertTrue(data['correct'])
        self.assertIn('<p/>', data['feedback'])


class ExtendedTextInteractionTests(BaseAssessmentTestCase):
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

        return new_assessment, new_offered

    def create_item(self):
        url = '{0}/items'.format(self.url)
        self._short_answer_test_file.seek(0)
        req = self.app.post(url,
                            upload_files=[('qtiFile', 'testFile', self._short_answer_test_file.read())])
        self.ok(req)
        return self.json(req)

    def create_taken_for_item(self, bank_id, item_id):
        if isinstance(bank_id, basestring):
            bank_id = utilities.clean_id(bank_id)
        if isinstance(item_id, basestring):
            item_id = utilities.clean_id(item_id)

        bank = get_managers()['am'].get_bank(bank_id)

        new_assessment, new_offered = self.create_assessment_offered_for_item(bank_id, item_id)

        form = bank.get_assessment_taken_form_for_create(new_offered.ident, [])
        taken = bank.create_assessment_taken(form)
        return taken, new_offered, new_assessment

    def setUp(self):
        super(ExtendedTextInteractionTests, self).setUp()

        self._short_answer_test_file = open('{0}/tests/files/short_answer_test_file.zip'.format(ABS_PATH), 'r')

        self.url += '/banks/' + unquote(str(self._bank.ident))
        self._telugu_text = u'తెలుగు'

    def tearDown(self):
        super(ExtendedTextInteractionTests, self).tearDown()

        self._short_answer_test_file.close()

    def test_can_send_text_response(self):
        item = self.create_item()
        self._taken, self._offered, self._assessment = self.create_taken_for_item(self._bank.ident,
                                                                                  utilities.clean_id(item['id']))
        url = '{0}/assessmentstaken/{1}/questions/{2}/submit'.format(self.url,
                                                                     unquote(str(self._taken.ident)),
                                                                     unquote(item['id']))
        payload = {
            'text': 'lorem ipsum foo bar baz'
        }
        req = self.app.post(url,
                            params=json.dumps(payload),
                            headers={'content-type': 'application/json'})
        self.ok(req)

        data = self.json(req)
        self.assertTrue(data['correct'])
        self.assertIn('<p/>', data['feedback'])

    def test_can_submit_foreign_language_text_response(self):
        item = self.create_item()
        self._taken, self._offered, self._assessment = self.create_taken_for_item(self._bank.ident,
                                                                                  utilities.clean_id(item['id']))
        url = '{0}/assessmentstaken/{1}/questions/{2}/submit'.format(self.url,
                                                                     unquote(str(self._taken.ident)),
                                                                     unquote(item['id']))
        payload = {
            'text': self._telugu_text
        }
        req = self.app.post(url,
                            params=json.dumps(payload),
                            headers=self._telugu_headers())
        self.ok(req)

        data = self.json(req)
        self.assertTrue(data['correct'])
        self.assertIn('<p/>', data['feedback'])

    def test_can_edit_max_strings(self):
        item = self.create_item()
        old_max_strings = item['question']['maxStrings']
        url = '{0}/items/{1}'.format(self.url, item['id'])
        payload = {
            'question': {'maxStrings': 55}
        }
        self.assertNotEqual(55, old_max_strings)
        req = self.app.put(url,
                           params=json.dumps(payload),
                           headers={'content-type': 'application/json'})
        self.ok(req)
        url = '{0}/qti'.format(url)
        req = self.app.get(url)
        self.ok(req)
        soup = BeautifulSoup(req.body, 'xml')
        self.assertEqual(soup.extendedTextInteraction['maxStrings'], '55')

    def test_can_edit_expected_length(self):
        item = self.create_item()
        old_expected_length = item['question']['expectedLength']
        url = '{0}/items/{1}'.format(self.url, item['id'])
        payload = {
            'question': {'expectedLength': 55}
        }
        self.assertNotEqual(55, old_expected_length)
        req = self.app.put(url,
                           params=json.dumps(payload),
                           headers={'content-type': 'application/json'})
        self.ok(req)
        url = '{0}/qti'.format(url)
        req = self.app.get(url)
        self.ok(req)
        soup = BeautifulSoup(req.body, 'xml')
        self.assertEqual(soup.extendedTextInteraction['expectedLength'], '55')

    def test_can_edit_expected_lines(self):
        item = self.create_item()
        old_expected_lines = item['question']['expectedLines']
        url = '{0}/items/{1}'.format(self.url, item['id'])
        payload = {
            'question': {'expectedLines': 55}
        }
        self.assertNotEqual(55, old_expected_lines)
        req = self.app.put(url,
                           params=json.dumps(payload),
                           headers={'content-type': 'application/json'})
        self.ok(req)
        url = '{0}/qti'.format(url)
        req = self.app.get(url)
        self.ok(req)
        soup = BeautifulSoup(req.body, 'xml')
        self.assertEqual(soup.extendedTextInteraction['expectedLines'], '55')


class VideoTagReplacementTests(BaseAssessmentTestCase):
    def create_video_question(self):
        url = '{0}/items'.format(self.url)
        self._video_test_file.seek(0)
        req = self.app.post(url,
                            upload_files=[('qtiFile', 'testFile.zip', self._video_test_file.read())])
        self.ok(req)
        return self.json(req)

    def markup(self):
        reader = csv.reader(self._video_matrix_test_file, delimiter='\t')
        for index, row in enumerate(reader):
            if index > 0:
                return row[3]

    def setUp(self):
        super(VideoTagReplacementTests, self).setUp()

        self._video_test_file = open('{0}/tests/files/video_test_file.zip'.format(ABS_PATH), 'r')
        self._video_matrix_test_file = open('{0}/tests/files/video_upload_matrix.tsv'.format(ABS_PATH), 'r')
        self._video_upload_test_file = open('{0}/tests/files/video-js-test.mp4'.format(ABS_PATH), 'r')
        self._caption_upload_test_file = open('{0}/tests/files/video-js-test-en.vtt'.format(ABS_PATH), 'r')

        self.url += '/banks/' + unquote(str(self._bank.ident))

    def tearDown(self):
        super(VideoTagReplacementTests, self).tearDown()

        self._video_test_file.close()
        self._video_matrix_test_file.close()
        self._video_upload_test_file.close()
        self._caption_upload_test_file.close()

    def upload_video_and_caption_files(self):
        url = '/api/v1/repository/repositories/{0}/assets'.format(unquote(str(self._bank.ident)))
        self._video_upload_test_file.seek(0)
        req = self.app.post(url,
                            upload_files=[('inputFile', 'video-js-test.mp4', self._video_upload_test_file.read())])
        self.ok(req)
        data = self.json(req)

        self._caption_upload_test_file.seek(0)
        req = self.app.post(url,
                            upload_files=[('inputFile', 'video-js-test-en.vtt', self._caption_upload_test_file.read())])
        self.ok(req)
        data = self.json(req)
        return data

    def test_can_replace_video_tag_in_qti_with_supplied_html(self):
        item = self.create_video_question()
        asset = self.upload_video_and_caption_files()

        url = '{0}/items/{1}'.format(self.url,
                                     unquote(item['id']))

        req = self.app.get(url)
        self.ok(req)
        data = self.json(req)
        self.assertNotIn('<video', data['question']['text']['text'])
        self.assertNotIn('</video>', data['question']['text']['text'])
        self.assertNotIn('<aside class="transcript">', data['question']['text']['text'])
        self.assertNotIn('</aside>', data['question']['text']['text'])

        url = '{0}/items/{1}/videoreplacement'.format(self.url,
                                                      unquote(item['id']))

        payload = {
            'assetId': asset['id'],
            'html': self.markup()
        }
        req = self.app.post(url,
                            params=json.dumps(payload),
                            headers={'content-type': 'application/json'})
        self.ok(req)
        data = self.json(req)
        self.assertIn('<video', data['question']['texts'][0]['text'])
        self.assertIn('</video>', data['question']['texts'][0]['text'])
        self.assertIn('<aside class="transcript">', data['question']['texts'][0]['text'])
        self.assertIn('</aside>', data['question']['texts'][0]['text'])

    def test_video_source_in_html_replaced_with_asset_content_reference(self):
        item = self.create_video_question()
        asset = self.upload_video_and_caption_files()
        url = '{0}/items/{1}/videoreplacement'.format(self.url,
                                                      unquote(item['id']))

        payload = {
            'assetId': asset['id'],
            'html': self.markup()
        }
        req = self.app.post(url,
                            params=json.dumps(payload),
                            headers={'content-type': 'application/json'})
        self.ok(req)
        data = self.json(req)
        soup = BeautifulSoup(data['question']['texts'][0]['text'], 'lxml-xml')
        source = soup.find('source')
        self.assertEqual('AssetContent:video-js-test_mp4', source['src'])
        self.assertIn(
            'fileIds',
            data['question']
        )
        self.assertIn(
            'video-js-test_mp4',
            data['question']['fileIds']
        )

    def test_can_replace_caption_vtt_files_in_supplied_html_with_asset_content_reference(self):
        item = self.create_video_question()
        asset = self.upload_video_and_caption_files()
        url = '{0}/items/{1}/videoreplacement'.format(self.url,
                                                      unquote(item['id']))

        payload = {
            'assetId': asset['id'],
            'html': self.markup()
        }
        req = self.app.post(url,
                            params=json.dumps(payload),
                            headers={'content-type': 'application/json'})
        self.ok(req)
        data = self.json(req)
        soup = BeautifulSoup(data['question']['texts'][0]['text'], 'lxml-xml')
        track = soup.find('track', label="English")
        self.assertEqual('AssetContent:video-js-test-en_vtt', track['src'])
        self.assertIn(
            'fileIds',
            data['question']
        )
        self.assertIn(
            'video-js-test_mp4',
            data['question']['fileIds']
        )

    def test_video_and_transcript_asset_content_ids_replaced_in_output_qti(self):
        item = self.create_video_question()
        asset = self.upload_video_and_caption_files()
        url = '{0}/items/{1}/videoreplacement'.format(self.url,
                                                      unquote(item['id']))

        payload = {
            'assetId': asset['id'],
            'html': self.markup()
        }
        req = self.app.post(url,
                            params=json.dumps(payload),
                            headers={'content-type': 'application/json'})
        self.ok(req)

        url = '{0}/items/{1}/qti'.format(self.url,
                                         unquote(item['id']))
        req = self.app.get(url)
        self.ok(req)
        soup = BeautifulSoup(req.body, 'lxml-xml')
        source = soup.find('source')

        asset_contents = asset['assetContents']
        video_asset_content = None
        caption_asset_content = None
        for asset_content in asset_contents:
            if 'mp4' in asset_content['genusTypeId']:
                video_asset_content = asset_content
            elif 'vtt' in asset_content['genusTypeId']:
                caption_asset_content = asset_content

        repo_id = str(self._bank.ident).replace('assessment.Bank', 'repository.Repository')
        self.assertIn('api/v1/repository/repositories/{0}/assets/{1}/contents/{2}/stream'.format(repo_id,
                                                                                                 asset['id'],
                                                                                                 video_asset_content['id']),
                      source['src'])
        track = soup.find('track', label='English')
        self.assertIn('api/v1/repository/repositories/{0}/assets/{1}/contents/{2}/stream'.format(repo_id,
                                                                                                 asset['id'],
                                                                                                 caption_asset_content['id']),
                      track['src'])

    def test_can_get_item_without_bank_id(self):
        item = self.create_video_question()
        url = '/api/v1/assessment/banks/foo/items/{0}'.format(item['id'])
        req = self.app.get(url)
        self.ok(req)
        data = self.json(req)
        self.assertEqual(
            item['id'],
            data['id']
        )
        self.assertNotEqual(
            data['bankId'],
            'foo'
        )

    def test_crossorigin_attribute_injected_into_video_tag(self):
        item = self.create_video_question()
        asset = self.upload_video_and_caption_files()
        url = '{0}/items/{1}/videoreplacement'.format(self.url,
                                                      unquote(item['id']))

        payload = {
            'assetId': asset['id'],
            'html': self.markup()
        }
        req = self.app.post(url,
                            params=json.dumps(payload),
                            headers={'content-type': 'application/json'})
        self.ok(req)
        url = '{0}/items/{1}/qti'.format(self.url,
                                         unquote(item['id']))
        req = self.app.get(url)
        self.ok(req)
        soup = BeautifulSoup(req.body, 'lxml-xml')
        for video in soup.find_all('video'):
            self.assertIn('crossorigin', video.attrs)
            self.assertEqual(
                video['crossorigin'],
                'anonymous'
            )
