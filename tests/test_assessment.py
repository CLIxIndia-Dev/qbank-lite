# -*- coding: utf-8 -*-
import csv
import json
import os

from bs4 import BeautifulSoup, Tag

from copy import deepcopy

from dlkit_runtime.primordium import Id, Type

from nose.tools import *

from paste.fixture import AppError

from records.assessment.qti.basic import _stringify
from records.registry import ITEM_GENUS_TYPES, ITEM_RECORD_TYPES,\
    ANSWER_RECORD_TYPES, QUESTION_RECORD_TYPES, ANSWER_GENUS_TYPES,\
    ASSESSMENT_OFFERED_RECORD_TYPES, ASSESSMENT_TAKEN_RECORD_TYPES,\
    QUESTION_GENUS_TYPES, ASSESSMENT_RECORD_TYPES

from sympy import sympify

from testing_utilities import BaseTestCase, get_managers, get_fixture_bank,\
    create_new_bank, get_valid_contents, get_fixture_repository, update_soup_with_url
from urllib import unquote, quote

import utilities

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
        self._repo = get_fixture_repository()

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

        asset_content = self._repo.get_asset_content(Id(asset['assetContents'][0]['id']))
        self.assertEqual(
            item['answers'][0]['feedback']['text'],
            update_soup_with_url(asset_payload['answers'][0]['feedback'], asset_content)
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

        asset_content = self._repo.get_asset_content(Id(asset['assetContents'][0]['id']))
        self.assertEqual(
            item['answers'][0]['feedback']['text'],
            update_soup_with_url(asset_payload['answers'][0]['feedback'], asset_content)
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


class AssessmentCrUDTests(BaseAssessmentTestCase):
    def create_bank(self):
        self._alias = "assessment.Bank%3Afoo%40ODL.MIT.EDU"
        payload = {
            "name": "test bank 2",
            "aliasId": self._alias
        }
        url = '/api/v1/assessment/banks'
        req = self.app.post(url,
                            params=json.dumps(payload),
                            headers={'content-type': 'application/json'})
        return self.json(req)

    def create_mw_sentence_item(self):
        url = '{0}/items'.format(self.url)
        self._mw_sentence_test_file.seek(0)
        req = self.app.post(url,
                            upload_files=[('qtiFile', 'testFile', self._mw_sentence_test_file.read())])
        self.ok(req)
        return self.json(req)

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
        super(AssessmentCrUDTests, self).setUp()
        self.url += '/banks/' + unquote(str(self._bank.ident))

        self._mw_sentence_test_file = open('{0}/tests/files/mw_sentence_with_audio_file.zip'.format(ABS_PATH), 'rb')

    def tearDown(self):
        """
        Remove the test user from all groups in Membership
        Start from the smallest groupId because need to
        remove "parental" roles like for DepartmentAdmin / DepartmentOfficer
        """
        super(AssessmentCrUDTests, self).tearDown()

        self._mw_sentence_test_file.close()

    def test_assessment_offered_crud(self):
        """
        Instructors should be able to add assessment offered.
        Cannot create offered unless an assessment has items

        """
        # Use POST to create an assessment
        assessment_name = 'a really hard assessment'
        assessment_desc = 'meant to differentiate students'
        payload = {
            "name": assessment_name,
            "description": assessment_desc
        }
        req = self.app.post(self.url + '/assessments',
                            params=json.dumps(payload),
                            headers={'content-type': 'application/json'})
        self.ok(req)
        assessment_id = unquote(json.loads(req.body)['id'])
        assessment_detail_endpoint = self.url + '/assessments/' + assessment_id
        self.verify_text(req,
                         'Assessment',
                         assessment_name,
                         assessment_desc)

        assessment_offering_endpoint = assessment_detail_endpoint + '/assessmentsoffered'
        # PUT and DELETE should not work on this endpoint
        self.assertRaises(AppError,
                          self.app.put,
                          assessment_offering_endpoint)
        self.assertRaises(AppError,
                          self.app.delete,
                          assessment_offering_endpoint)

        # GET should return an empty list
        req = self.app.get(assessment_offering_endpoint)
        self.ok(req)

        # Use POST to create an offering
        # Inputting something other than a list or dict object should result in an error
        bad_payload = 'this is a bad input format'
        self.assertRaises(AppError,
                          self.app.post,
                          assessment_offering_endpoint,
                          params=bad_payload,
                          headers={'content-type': 'application/json'})

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
        # POST at this point should throw an exception -- no items in the assessment
        self.assertRaises(AppError,
                          self.app.post,
                          assessment_offering_endpoint,
                          params=payload,
                          headers={'content-type': 'application/json'})

        items_endpoint = '{0}/items'.format(self.url)

        item_name = 'a really complicated item'
        item_desc = 'meant to differentiate students'
        payload = {
            "name": item_name,
            "description": item_desc
        }

        req = self.app.post(items_endpoint,
                            params=json.dumps(payload),
                            headers={'content-type': 'application/json'})
        self.ok(req)
        item_id = unquote(json.loads(req.body)['id'])

        assessment_items_endpoint = assessment_detail_endpoint + '/items'

        # POST should also work and create the linkage
        payload = {
            'itemIds' : [item_id]
        }
        req = self.app.post(assessment_items_endpoint,
                            params=json.dumps(payload),
                            headers={'content-type': 'application/json'})
        self.ok(req)

        # Now POST to offerings should work
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
        quote_safe_offering_id = offering['id']
        payload.update({
            'id'    : quote_safe_offering_id
        })
        self.verify_offerings(req,
                              'AssessmentOffering',
                              [payload])

        assessment_offering_detail_endpoint = '{0}/assessmentsoffered/{1}'.format(self.url,
                                                                                  offering_id)

        req = self.app.get(assessment_offering_endpoint)
        self.ok(req)
        self.verify_offerings(req,
                              'AssessmentOffering',
                              [payload])

        # For the offering detail endpoint, GET, PUT, DELETE should work
        # Check that POST returns error code 405--we don't support this
        self.assertRaises(AppError,
                          self.app.post,
                          assessment_offering_detail_endpoint)
        req = self.app.get(assessment_offering_detail_endpoint)
        self.ok(req)
        self.verify_offerings(req, 'AssessmentOffering', [payload])

        # PUT to the offering URL should modify the start time or duration
        new_start_time = {
            "startTime" : {
                "day"   : 1,
                "month" : 2,
                "year"  : 2015
            }
        }
        expected_payload = new_start_time
        expected_payload.update({
            "duration"  : {
                "days"  : 2
            },
            "id"        : quote_safe_offering_id
        })

        req = self.app.put(assessment_offering_detail_endpoint,
                           params=json.dumps(new_start_time),
                           headers={'content-type': 'application/json'})
        self.ok(req)
        self.verify_offerings(req, 'AssessmentOffered', [expected_payload])

        # PUT with a list of length 1 should also work
        new_duration = [{
            "duration"  : {
                "days"      : 5,
                "minutes"   : 120
            }
        }]
        expected_payload = new_duration
        expected_payload[0].update(new_start_time)
        expected_payload[0].update({
            "id"    : quote_safe_offering_id
        })
        req = self.app.put(assessment_offering_detail_endpoint,
                           params=json.dumps(new_duration),
                           headers={'content-type': 'application/json'})
        self.ok(req)
        self.verify_offerings(req, 'AssessmentOffered', expected_payload)

        funny_payload = {
            "duration"  : {
                "hours"   : 2
            }
        }
        expected_converted_payload = funny_payload
        expected_converted_payload.update(new_start_time)
        expected_converted_payload.update({
            "id": quote_safe_offering_id
        })
        req = self.app.put(assessment_offering_detail_endpoint,
                           params=json.dumps(funny_payload),
                           headers={'content-type': 'application/json'})
        self.ok(req)
        self.verify_offerings(req, 'AssessmentOffering', expected_converted_payload)

        # check that the attributes changed in GET
        req = self.app.get(assessment_offering_detail_endpoint)
        self.ok(req)
        self.verify_offerings(req, 'AssessmentOffered', expected_converted_payload)

        # Delete the offering now
        req = self.app.delete(assessment_offering_detail_endpoint)
        self.ok(req)
        data = self.json(req)
        self.assertTrue(data['success'])

        req = self.app.get(assessment_offering_endpoint)
        self.ok(req)
        self.verify_no_data(req)

        # test that you can POST / create multiple offerings with a list
        bad_payload = 'this is a bad input format'
        self.assertRaises(AppError,
                          self.app.post,
                          assessment_offering_endpoint,
                          params=bad_payload,
                          headers={'content-type': 'application/json'})

        payload = [{
            "startTime" : {
                "day"   : 1,
                "month" : 1,
                "year"  : 2015
            },
            "duration"  : {
                "days"  : 2
            }
        }, {
            "startTime" : {
                "day"   : 9,
                "month" : 1,
                "year"  : 2015
            },
            "duration"  : {
                "days"  : 20
            }
        }]
        req = self.app.post(assessment_offering_endpoint,
                            params=json.dumps(payload),
                            headers={'content-type': 'application/json'})
        self.ok(req)

        offering = json.loads(req.body)
        offering1_id = unquote(offering[0]['id'])
        offering2_id = unquote(offering[1]['id'])

        payload[0].update({
            'id'    : offering1_id
        })
        payload[1].update({
            'id'    : offering2_id
        })

        req = self.app.get(assessment_offering_endpoint)
        self.ok(req)
        self.verify_offerings(req,
                              'AssessmentOffering',
                              payload)

    def test_assessment_taking(self):
        """
        POSTing to takens should create a new one.
        Should only be able to POST from the /assessmentsoffered/ endpoint
        But can GET from the /assessments/ endpoint, too.

        Without submitting a response, POSTing again should
        return the same one.

         -- Check that for Ortho3D types, a taken has files.

        Submitting and then POSTing should return a new
        taken.

        This should work for both instructors and learners

        NOTE: this tests the obfuscated way of taking assessments (no list of questions)
        """
        items_endpoint = self.url + '/items'

        # Use POST to create an item
        item_name = 'a really complicated item'
        item_desc = 'meant to differentiate students'
        question_string = 'can you manipulate this?'
        question_type = 'question-record-type%3Alabel-ortho-faces%40ODL.MIT.EDU'
        answer_string = 'yes!'
        answer_type = 'answer-record-type%3Alabel-ortho-faces%40ODL.MIT.EDU'
        payload = {
            "name": item_name,
            "description": item_desc,
            "question": {
                "type": question_type,
                "questionString": question_string
            },
            "answers": [{
                "type": answer_type,
                "integerValues": {
                    "frontFaceValue": 1,
                    "sideFaceValue" : 2,
                    "topFaceValue"  : 3
                }
            }],
        }
        req = self.app.post(items_endpoint,
                            params=json.dumps(payload),
                            headers={'content-type': 'application/json'})
        self.ok(req)

        item = json.loads(req.body)
        item_id = unquote(item['id'])

        item_detail_endpoint = items_endpoint + '/' + item_id
        req = self.app.get(item_detail_endpoint)
        self.ok(req)

        req = self.app.get(items_endpoint)
        self.ok(req)
        self.assertEqual(
            len(self.json(req)),
            1
        )

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
        assessment_id = unquote(json.loads(req.body)['id'])

        assessment_detail_endpoint = assessments_endpoint + '/' + assessment_id
        assessment_offering_endpoint = assessment_detail_endpoint + '/assessmentsoffered'
        assessment_items_endpoint = assessment_detail_endpoint + '/items'

        # POST should create the linkage
        payload = {
            'itemIds' : [item_id]
        }
        req = self.app.post(assessment_items_endpoint,
                            params=json.dumps(payload),
                            headers={'content-type': 'application/json'})
        self.ok(req)

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
        quote_safe_offering_id = offering['id']

        assessments_offered_endpoint = self.url + '/assessmentsoffered'
        assessment_offering_detail_endpoint = assessments_offered_endpoint + '/' + offering_id

        # Can GET and POST. PUT and DELETE not supported
        assessment_takens_endpoint = assessment_offering_detail_endpoint + '/assessmentstaken'
        req = self.app.get(assessment_takens_endpoint)
        self.ok(req)

        # Check that DELETE returns error code 405--we don't support this
        self.assertRaises(AppError,
                          self.app.delete,
                          assessment_takens_endpoint)

        # PUT to this root url also returns a 405
        self.assertRaises(AppError,
                          self.app.put,
                          assessment_takens_endpoint)

        req = self.app.post(assessment_takens_endpoint)
        self.ok(req)
        taken = json.loads(req.body)
        taken_id = unquote(taken['id'])

        # Instructor can GET the taken details (learner cannot).
        # POST, PUT, DELETE not supported
        taken_endpoint = self.url + '/assessmentstaken/' + taken_id
        req = self.app.get(taken_endpoint)
        self.ok(req)

        # PUT to this root url also returns a 405
        self.assertRaises(AppError,
                          self.app.put,
                          taken_endpoint)

        # POST to this root url also returns a 405
        self.assertRaises(AppError,
                          self.app.post,
                          taken_endpoint)

        # POSTing to assessment_offering_takens_endpoint
        # returns the same taken
        req = self.app.post(assessment_takens_endpoint)
        self.ok(req)
        taken_copy = json.loads(req.body)
        taken_copy_id = unquote(taken_copy['id'])
        self.assertEqual(taken_id, taken_copy_id)

        # Can submit a wrong response
        submit_endpoint = taken_endpoint + '/questions/{0}/submit'.format(item_id)
        wrong_response = {
            "integerValues": {
                "frontFaceValue" : 0,
                "sideFaceValue"  : 1,
                "topFaceValue"   : 2
            }
        }

        # Check that DELETE returns error code 405--we don't support this
        self.assertRaises(AppError,
                          self.app.delete,
                          submit_endpoint)

        # PUT to this root url also returns a 405
        self.assertRaises(AppError,
                          self.app.put,
                          submit_endpoint)

        # GET to this root url also returns a 405
        self.assertRaises(AppError,
                          self.app.get,
                          submit_endpoint)

        req = self.app.post(submit_endpoint,
                            params=json.dumps(wrong_response),
                            headers={'content-type': 'application/json'})
        self.ok(req)
        self.verify_submission(req, _expected_result=False, _has_next=False)

        # to submit again, have to get a new taken
        # Now getting another taken will return a new one
        # POSTing to assessment_offering_takens_endpoint
        # returns the same taken
        req = self.app.post(assessment_takens_endpoint)
        self.ok(req)
        new_taken = json.loads(req.body)
        quoted_new_taken_id = new_taken['id']
        new_taken_id = unquote(quoted_new_taken_id)
        self.assertNotEqual(taken_id, quoted_new_taken_id)

        new_taken_endpoint = self.url + '/assessmentstaken/' + new_taken_id
        new_submit_endpoint = new_taken_endpoint + '/questions/{0}/submit'.format(item_id)
        right_response = {
            "integerValues": {
                "frontFaceValue" : 1,
                "sideFaceValue"  : 2,
                "topFaceValue"   : 3
            }
        }
        req = self.app.post(new_submit_endpoint,
                            params=json.dumps(right_response),
                            headers={'content-type': 'application/json'})
        self.ok(req)
        self.verify_submission(req, _expected_result=True, _has_next=False)

    def test_assessments_crud(self):
        """
        Create a test bank and test all things associated with assessments
        and a single assessment
        DELETE on root assessments/ does nothing. Error code 405.
        GET on root assessments/ gets you a list
        POST on root assessments/ creates a new assessment
        PUT on root assessments/ does nothing. Error code 405.

        For a single assessment detail:
        DELETE will delete that assessment
        GET brings up the assessment details with offerings and taken
        POST does nothing. Error code 405.
        PUT lets user update the name or description
        """
        assessment_endpoint = self.url + '/assessments'

        # Check that DELETE returns error code 405--we don't support this
        self.assertRaises(AppError,
                          self.app.delete,
                          assessment_endpoint)

        # PUT to this root url also returns a 405
        self.assertRaises(AppError,
                          self.app.put,
                          assessment_endpoint)

        # GET should return 0 results
        req = self.app.get(assessment_endpoint)
        self.verify_no_data(req)

        # Use POST to create an assessment
        assessment_name = 'a really hard assessment'
        assessment_desc = 'meant to differentiate students'
        payload = {
            "name": assessment_name,
            "description": assessment_desc
        }
        req = self.app.post(assessment_endpoint,
                            params=json.dumps(payload),
                            headers={'content-type': 'application/json'})
        self.ok(req)
        assessment_id = unquote(json.loads(req.body)['id'])

        assessment_details_endpoint = '{0}/{1}'.format(assessment_endpoint,
                                                       assessment_id)
        self.verify_text(req,
                         'Assessment',
                         assessment_name,
                         assessment_desc)

        req = self.app.get(assessment_details_endpoint)
        self.ok(req)
        self.verify_text(req,
                         'Assessment',
                         assessment_name,
                         assessment_desc,
                         assessment_id)

        # Now test PUT / GET / POST / DELETE on the new assessment item
        # POST does nothing
        assessment_detail_endpoint = assessment_endpoint + '/' + assessment_id
        self.assertRaises(AppError,
                          self.app.post,
                          assessment_detail_endpoint)

        # GET displays it, with self link. Allowed for Instructor
        req = self.app.get(assessment_detail_endpoint)
        self.ok(req)
        self.verify_text(req,
                         'Assessment',
                         assessment_name,
                         assessment_desc)

        new_assessment_name = 'a new assessment name'
        new_assessment_desc = 'to trick students'
        payload = {
            "name": new_assessment_name
        }
        req = self.app.put(assessment_detail_endpoint,
                           params=json.dumps(payload),
                           headers={'content-type': 'application/json'})
        self.ok(req)
        self.verify_text(req,
                         'Assessment',
                         new_assessment_name,
                         assessment_desc)

        req = self.app.get(assessment_detail_endpoint)
        self.ok(req)
        self.verify_text(req,
                         'Assessment',
                         new_assessment_name,
                         assessment_desc)

        payload = {
            "description": new_assessment_desc
        }
        req = self.app.put(assessment_detail_endpoint,
                           params=json.dumps(payload),
                           headers={'content-type': 'application/json'})
        self.ok(req)
        self.verify_text(req,
                         'Assessment',
                         new_assessment_name,
                         new_assessment_desc)

        req = self.app.get(assessment_detail_endpoint)
        self.ok(req)
        self.verify_text(req,
                         'Assessment',
                         new_assessment_name,
                         new_assessment_desc)

        # trying to delete the bank with assessments should throw an error
        self.assertRaises(AppError,
                          self.app.delete,
                          self.url)

    def test_banks_get(self):
        """
        Should give you a list of banks and links.
        """
        req = self.app.get('/api/v1/assessment/banks')
        self.ok(req)
        self.assertIn(
            '"displayName": ',
            req.body
        )  # this only really tests that at least one bank exists...not great.

    def test_bank_post_and_crud(self):
        """
        User can create a new assessment bank. Need to do self-cleanup,
        because the Mongo backend is not part of the test database...that
        means Django will not wipe it clean after every test!
        Once a bank is created, user can GET it, PUT to update it, and
        DELETE it. POST should return an error code 405.
        Do these bank detail tests here, because we have a known
        bank ID
        """
        # verify that the bank now appears in the bank_details call
        req = self.app.get(self.url)
        self.ok(req)
        self.verify_text(req,
                         'Bank',
                         self._bank.display_name.text,
                         self._bank.description.text)

        new_name = 'a new bank name'
        payload = {
            "name": new_name
        }
        # DepartmentAdmin should be able to edit the bank
        req = self.app.put(self.url,
                           params=json.dumps(payload),
                           headers={'content-type': 'application/json'})
        self.ok(req)
        self.verify_text(req, 'Bank', new_name, self._bank.description.text)

        req = self.app.get(self.url)
        self.ok(req)
        self.verify_text(req, 'Bank', new_name, self._bank.description.text)

        new_desc = 'a new bank description'
        payload = {
            "description": new_desc
        }
        req = self.app.put(self.url,
                           params=json.dumps(payload),
                           headers={'content-type': 'application/json'})
        self.ok(req)
        self.verify_text(req, 'Bank', new_name, new_desc)

        req = self.app.get(self.url)
        self.ok(req)
        self.verify_text(req, 'Bank', new_name, new_desc)

    def test_can_set_item_genus_type_and_file_names(self):
        """
        When creating a new item, can define a specific genus type
        """
        items_endpoint = self.url + '/items'

        # Use POST to create an item--right now user is Instructor,
        # so this should show up in GET
        item_genus = 'item-genus-type%3Aedx-multi-choice-problem-type%40ODL.MIT.EDU'
        item_name = 'a really complicated item'
        item_desc = 'meant to differentiate students'
        question_string = 'can you manipulate this?'
        question_type = 'question-record-type%3Amulti-choice-edx%40ODL.MIT.EDU'
        manip_name = 'A bracket'
        answer_string = 'yes!'
        answer_type = 'answer-record-type%3Amulti-choice-edx%40ODL.MIT.EDU'
        payload = {
            "name"          : item_name,
            "description"   : item_desc,
            "genus"         : item_genus,
            "question"      : {
                "choices"   : [
                    'yes',
                    'no',
                    'maybe'
                ],
                "genus"         : item_genus,
                "promptName"    : manip_name,
                "type"          : question_type,
                "questionString": question_string
            },
            "answers": [{
                "genus"     : item_genus,
                "type"      : answer_type,
                "choiceId"  : 1
            }],
        }
        req = self.app.post(items_endpoint,
                            params=json.dumps(payload),
                            headers={'content-type': 'application/json'})
        self.ok(req)
        item_id = unquote(json.loads(req.body)['id'])
        item = json.loads(req.body)
        question = self.extract_question(item)
        answer = self.extract_answers(item)[0]
        self.assertEqual(
            question['genusTypeId'],
            item_genus
        )
        self.assertEqual(
            answer['genusTypeId'],
            item_genus
        )
        self.verify_text(req,
                         'Item',
                         item_name,
                         item_desc,
                         _genus=item_genus)

        req = self.app.get(items_endpoint)
        self.ok(req)
        self.verify_text(req,
                         'Item',
                         item_name,
                         item_desc,
                         _id=item_id,
                         _genus=item_genus)
        item = json.loads(req.body)
        question = self.extract_question(item)
        answer = self.extract_answers(item)[0]
        self.assertEqual(
            question['genusTypeId'],
            item_genus
        )
        self.assertEqual(
            answer['genusTypeId'],
            item_genus
        )

    def test_link_items_to_assessment(self):
        """
        Test link, view, delete of items to assessments
        """
        assessments_endpoint = self.url + '/assessments'
        items_endpoint = self.url + '/items'

        # Use POST to create an assessment
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
        assessment_id = unquote(json.loads(req.body)['id'])
        assessment_detail_endpoint = assessments_endpoint + '/' + assessment_id
        self.verify_text(req,
                         'Assessment',
                         assessment_name,
                         assessment_desc)

        req = self.app.get(assessments_endpoint)
        self.ok(req)
        self.verify_text(req,
                         'Assessment',
                         assessment_name,
                         assessment_desc,
                         assessment_id)

        # Use POST to create an item
        item_name = 'a really complicated item'
        item_desc = 'meant to differentiate students'
        question_string = 'what is pi?'
        question_type = 'question-record-type%3Amulti-choice-edx%40ODL.MIT.EDU'
        # answer_string = 'dessert'
        # answer_type = 'answer-record-type%3Alabel-ortho-faces%40ODL.MIT.EDU'
        payload = {
            "name": item_name,
            "description": item_desc,
            "question": {
                "type": question_type,
                "questionString": question_string,
                "choices": ['1', '2']
            }
        }
        req = self.app.post(items_endpoint,
                            params=json.dumps(payload),
                            headers={'content-type': 'application/json'})
        self.ok(req)
        item = json.loads(req.body)
        item_id = unquote(item['id'])
        item_detail_endpoint = items_endpoint + '/' + item_id
        question_id = self.extract_question(item)['id']
        self.verify_text(req,
                         'Item',
                         item_name,
                         item_desc)
        self.verify_question(req,
                             question_string,
                             question_type)

        req = self.app.get(items_endpoint)
        self.ok(req)
        self.verify_text(req,
                         'Item',
                         item_name,
                         item_desc,
                         item_id)
        self.verify_question(req,
                             question_string,
                             question_type)

        # Now start working on the assessment/items endpoint, to test
        # GET, POST for the items/ endpoint (others should throw error)
        # GET, DELETE for the items/<id> endpoint (others should throw error)
        assessment_items_endpoint = assessment_detail_endpoint + '/items'

        # Check that DELETE returns error code 405--we don't support this
        self.assertRaises(AppError,
                          self.app.delete,
                          assessment_items_endpoint)

        req = self.app.get(assessment_items_endpoint)
        self.ok(req)
        self.verify_no_data(req)

        # POST should also work and create the linkage
        payload = {
            'itemIds' : [item_id]
        }
        req = self.app.post(assessment_items_endpoint,
                            params=json.dumps(payload),
                            headers={'content-type': 'application/json'})
        self.ok(req)
        self.verify_text(req,
                         'Item',
                         item_name,
                         item_desc,
                         item_id)
        self.verify_question(req,
                             question_string,
                             question_type)

        # should now appear in the Assessment Items List
        req = self.app.get(assessment_items_endpoint)
        self.ok(req)
        self.verify_text(req,
                         'Item',
                         item_name,
                         item_desc,
                         item_id)
        self.verify_question(req,
                             question_string,
                             question_type)

        # Trying to delete the item now
        # should raise an error--cannot delete an item that is
        # assigned to an assignment!
        self.assertRaises(AppError,
                          self.app.delete,
                          item_detail_endpoint)

        assessment_item_details_endpoint = assessment_items_endpoint + '/' + item_id
        req = self.app.delete(assessment_item_details_endpoint)
        self.ok(req)
        data = self.json(req)
        self.assertTrue(data['success'])

        req = self.app.get(assessment_items_endpoint)
        self.ok(req)
        self.verify_no_data(req)

    def test_can_get_multiple_assessment_items(self):
        """
        Test view multiple items in an assessment
        """
        assessments_endpoint = self.url + '/assessments'
        items_endpoint = self.url + '/items'

        # Use POST to create an assessment
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
        assessment_id = unquote(json.loads(req.body)['id'])
        assessment_detail_endpoint = assessments_endpoint + '/' + assessment_id
        self.verify_text(req,
                         'Assessment',
                         assessment_name,
                         assessment_desc)

        req = self.app.get(assessments_endpoint)
        self.ok(req)
        self.verify_text(req,
                         'Assessment',
                         assessment_name,
                         assessment_desc,
                         assessment_id)

        # Use POST to create items
        item_name = 'a really complicated item'
        item_desc = 'meant to differentiate students'
        question_string = 'what is pi?'
        question_type = 'question-record-type%3Amulti-choice-edx%40ODL.MIT.EDU'
        # answer_string = 'dessert'
        # answer_type = 'answer-record-type%3Alabel-ortho-faces%40ODL.MIT.EDU'
        payload = {
            "name": item_name,
            "description": item_desc,
            "question": {
                "type": question_type,
                "questionString": question_string,
                "choices": ['1', '2']
            }
        }
        req = self.app.post(items_endpoint,
                            params=json.dumps(payload),
                            headers={'content-type': 'application/json'})
        self.ok(req)
        item1 = json.loads(req.body)
        item1_id = item1['id']

        item_name = 'a really complicated item 2'
        item_desc = 'meant to differentiate students 2'
        question_string = 'what is pi?'
        question_type = 'question-record-type%3Amulti-choice-edx%40ODL.MIT.EDU'
        # answer_string = 'dessert'
        # answer_type = 'answer-record-type%3Alabel-ortho-faces%40ODL.MIT.EDU'
        payload = {
            "name": item_name,
            "description": item_desc,
            "question": {
                "type": question_type,
                "questionString": question_string,
                "choices": ['1', '2']
            }
        }
        req = self.app.post(items_endpoint,
                            params=json.dumps(payload),
                            headers={'content-type': 'application/json'})
        self.ok(req)
        item2 = json.loads(req.body)
        item2_id = item2['id']

        self.assertNotEqual(item1_id, item2_id)

        # Now start working on the assessment/items endpoint, to test
        # GET
        assessment_items_endpoint = assessment_detail_endpoint + '/items'

        # POST should also work and create the linkage
        payload = {
            'itemIds' : [item1_id, item2_id]
        }
        req = self.app.post(assessment_items_endpoint,
                            params=json.dumps(payload),
                            headers={'content-type': 'application/json'})
        self.ok(req)

        # should now appear in the Assessment Items List
        req = self.app.get(assessment_items_endpoint)
        self.ok(req)
        data = self.json(req)
        self.assertEqual(len(data), 2)
        self.assertEqual(data[0]['id'], item1_id)
        self.assertEqual(data[1]['id'], item2_id)

    def test_can_get_assessment_item_wrong_answers(self):
        mc_sentence = self.create_mw_sentence_item()

        assessments_endpoint = self.url + '/assessments'

        # Use POST to create an assessment
        assessment_name = 'a really hard assessment'
        assessment_desc = 'meant to differentiate students'
        payload = {
            "name": assessment_name,
            "description": assessment_desc,
            "itemIds": [mc_sentence['id']]
        }
        req = self.app.post(assessments_endpoint,
                            params=json.dumps(payload),
                            headers={'content-type': 'application/json'})
        self.ok(req)
        assessment_id = unquote(json.loads(req.body)['id'])
        assessment_detail_endpoint = assessments_endpoint + '/' + assessment_id
        assessment_items_endpoint = assessment_detail_endpoint + '/items?wronganswers'

        # should now appear in the Assessment Items List
        req = self.app.get(assessment_items_endpoint)
        self.ok(req)
        data = self.json(req)

        item = [i for i in data if i['id'] == mc_sentence['id']][0]
        self.assertEqual(len(item['answers']),
                         len(mc_sentence['answers']))
        self.assertTrue(any(answer['genusTypeId'] == str(WRONG_ANSWER_GENUS)
                            for answer in item['answers']))

        url = assessment_detail_endpoint + '/items'
        req = self.app.get(url)
        data = self.json(req)
        item = [i for i in data if i['id'] == mc_sentence['id']][0]

        self.assertEqual(len(item['answers']),
                         1)

        self.assertFalse(any(answer['genusTypeId'] == str(WRONG_ANSWER_GENUS) for
                             answer in item['answers']))

    def test_can_get_assessment_item_qti(self):
        mc_sentence = self.create_mw_sentence_item()

        assessments_endpoint = self.url + '/assessments'

        # Use POST to create an assessment
        assessment_name = 'a really hard assessment'
        assessment_desc = 'meant to differentiate students'
        payload = {
            "name": assessment_name,
            "description": assessment_desc,
            "itemIds": [mc_sentence['id']]
        }
        req = self.app.post(assessments_endpoint,
                            params=json.dumps(payload),
                            headers={'content-type': 'application/json'})
        self.ok(req)
        assessment_id = unquote(json.loads(req.body)['id'])
        assessment_detail_endpoint = assessments_endpoint + '/' + assessment_id
        assessment_items_endpoint = assessment_detail_endpoint + '/items?qti'

        # should now appear in the Assessment Items List
        req = self.app.get(assessment_items_endpoint)
        self.ok(req)
        data = self.json(req)
        self.assertEqual(len(data), 1)
        self.assertIn('qti', data[0])

        item = data[0]

        item_qti = BeautifulSoup(item['qti'], 'lxml-xml').assessmentItem
        expected_values = ['id51b2feca-d407-46d5-b548-d6645a021008',
                           'id881a8e9c-844b-4394-be62-d28a5fda5296',
                           'idcccac9f8-3b85-4a2f-a95c-1922dec5d04a',
                           'id28a924d9-32ac-4ac5-a4b2-1b1cfe2caba0',
                           'id78ce22bf-559f-44a4-95ee-156f222ad510',
                           'id3045d860-24b4-4b30-9ca1-72408a3bcc9b',
                           'id2cad48be-2782-4625-9669-dfcb2062bf3c']
        for index, value in enumerate(item_qti.responseDeclaration.correctResponse.find_all('value')):
            self.assertEqual(value.string.strip(), expected_values[index])

        item_body = item_qti.itemBody

        order_interaction = item_body.orderInteraction.extract()

        audio_asset_label = 'ee_u1l01a01r05__mp3'
        image_asset_label = 'medium8081173379968782030intersection_png'
        audio_asset_id = item['question']['fileIds'][audio_asset_label]['assetId']
        audio_asset_content_id = item['question']['fileIds'][audio_asset_label]['assetContentId']
        image_asset_id = item['question']['fileIds'][image_asset_label]['assetId']
        image_asset_content_id = item['question']['fileIds'][image_asset_label]['assetContentId']

        expected_string = """<itemBody>
<p>
   Where are Raju's bags?
  </p>
<p>
</p>
<p>
<audio autoplay="autoplay" controls="controls" style="width: 125px">
<source src="/api/v1/repository/repositories/{0}/assets/{1}/contents/{2}/stream" type="audio/mpeg"/>
</audio>
</p>
<p>
<img alt="This is a drawing of a busy intersection." height="100" src="/api/v1/repository/repositories/{0}/assets/{3}/contents/{4}/stream" width="100"/>
</p>

</itemBody>""".format(str(self._bank.ident).replace('assessment.Bank', 'repository.Repository'),
                      audio_asset_id,
                      audio_asset_content_id,
                      image_asset_id,
                      image_asset_content_id)

        self.assertEqual(
            str(item_body),
            expected_string
        )

        self.assertEqual(
            len(order_interaction.find_all('simpleChoice')),
            7
        )
        self.assertEqual(
            order_interaction['responseIdentifier'],
            'RESPONSE_1'
        )
        self.assertEqual(
            order_interaction['shuffle'],
            'true'
        )

        expected_choices = {
            "id51b2feca-d407-46d5-b548-d6645a021008": """<simpleChoice identifier="id51b2feca-d407-46d5-b548-d6645a021008">
<p class="noun">
     Raju
    </p>
</simpleChoice>""",
            "id881a8e9c-844b-4394-be62-d28a5fda5296": """<simpleChoice identifier="id881a8e9c-844b-4394-be62-d28a5fda5296">
<p class="verb">
     left
    </p>
</simpleChoice>""",
            "idcccac9f8-3b85-4a2f-a95c-1922dec5d04a": """<simpleChoice identifier="idcccac9f8-3b85-4a2f-a95c-1922dec5d04a">
<p class="noun">
     the bags
    </p>
</simpleChoice>""",
            "id28a924d9-32ac-4ac5-a4b2-1b1cfe2caba0": """<simpleChoice identifier="id28a924d9-32ac-4ac5-a4b2-1b1cfe2caba0">
<p class="adverb">
     under
    </p>
</simpleChoice>""",
            "id78ce22bf-559f-44a4-95ee-156f222ad510": """<simpleChoice identifier="id78ce22bf-559f-44a4-95ee-156f222ad510">
<p class="noun">
     the seat
    </p>
</simpleChoice>""",
            "id3045d860-24b4-4b30-9ca1-72408a3bcc9b": """<simpleChoice identifier="id3045d860-24b4-4b30-9ca1-72408a3bcc9b">
<p class="prep">
     on
    </p>
</simpleChoice>""",
            "id2cad48be-2782-4625-9669-dfcb2062bf3c": """<simpleChoice identifier="id2cad48be-2782-4625-9669-dfcb2062bf3c">
<p class="noun">
     the bus
    </p>
</simpleChoice>"""
        }

        for choice in order_interaction.find_all('simpleChoice'):
            choice_id = choice['identifier']
            self.assertEqual(
                str(choice),
                expected_choices[choice_id]
            )

    def test_can_assign_to_banks_on_create(self):
        new_bank = self.create_bank()

        assessments_endpoint = self.url + '/assessments'

        assessment_name = 'a really hard assessment'
        assessment_desc = 'meant to differentiate students'
        payload = {
            "name": assessment_name,
            "description": assessment_desc,
            "assignedBankIds": [self._alias]
        }
        req = self.app.post(assessments_endpoint,
                            params=json.dumps(payload),
                            headers={'content-type': 'application/json'})
        self.ok(req)
        assessment = self.json(req)
        self.assertEqual(len(assessment['assignedBankIds']), 2)
        self.assertEqual(assessment['assignedBankIds'][0], str(self._bank.ident))
        self.assertEqual(assessment['assignedBankIds'][1], new_bank['id'])

    def test_can_assign_to_banks_as_update(self):
        new_bank = self.create_bank()

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
        assessment = self.json(req)
        self.assertEqual(len(assessment['assignedBankIds']), 1)
        self.assertEqual(assessment['assignedBankIds'][0], str(self._bank.ident))

        url = '{0}/{1}/assignedbankids'.format(assessments_endpoint,
                                               assessment['id'])
        payload = {
            'assignedBankIds': [self._alias]
        }
        req = self.app.post(url,
                            params=json.dumps(payload),
                            headers={'content-type': 'application/json'})
        self.ok(req)
        data = self.json(req)
        self.assertTrue(data['success'])

        url = '{0}/{1}'.format(assessments_endpoint,
                               assessment['id'])
        req = self.app.get(url)
        self.ok(req)
        data = self.json(req)

        self.assertEqual(len(data['assignedBankIds']), 2)
        self.assertEqual(data['assignedBankIds'][0], str(self._bank.ident))
        self.assertEqual(data['assignedBankIds'][1], new_bank['id'])

    def test_can_get_assessments_in_aliased_bank(self):
        new_bank = self.create_bank()

        assessments_endpoint = self.url + '/assessments'

        assessment_name = 'a really hard assessment'
        assessment_desc = 'meant to differentiate students'
        payload = {
            "name": assessment_name,
            "description": assessment_desc,
            "assignedBankIds": [self._alias]
        }
        req = self.app.post(assessments_endpoint,
                            params=json.dumps(payload),
                            headers={'content-type': 'application/json'})
        self.ok(req)
        assessment = self.json(req)

        url = '/api/v1/assessment/banks/{0}/assessments'.format(new_bank['id'])
        req = self.app.get(url)
        self.ok(req)
        data = self.json(req)
        self.assertEqual(len(data), 1)
        self.assertEqual(data[0]['id'], assessment['id'])

    def test_can_remove_bank_assignment(self):
        new_bank = self.create_bank()

        assessments_endpoint = self.url + '/assessments'

        assessment_name = 'a really hard assessment'
        assessment_desc = 'meant to differentiate students'
        payload = {
            "name": assessment_name,
            "description": assessment_desc,
            "assignedBankIds": [self._alias]
        }
        req = self.app.post(assessments_endpoint,
                            params=json.dumps(payload),
                            headers={'content-type': 'application/json'})
        self.ok(req)
        assessment = self.json(req)
        self.assertEqual(len(assessment['assignedBankIds']), 2)
        self.assertEqual(assessment['assignedBankIds'][0], str(self._bank.ident))
        self.assertEqual(assessment['assignedBankIds'][1], new_bank['id'])

        url = "{0}/{1}/assignedbankids/{2}".format(assessments_endpoint,
                                                   assessment['id'],
                                                   self._alias)
        req = self.app.delete(url)
        self.ok(req)
        data = self.json(req)
        self.assertTrue(data['success'])

        url = '{0}/{1}'.format(assessments_endpoint,
                               assessment['id'])
        req = self.app.get(url)
        self.ok(req)
        data = self.json(req)

        self.assertEqual(len(data['assignedBankIds']), 1)
        self.assertEqual(data['assignedBankIds'][0], str(self._bank.ident))

    def test_cannot_remove_from_all_banks(self):
        assessments_endpoint = self.url + '/assessments'

        # Use POST to create an assessment
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
        assessment = self.json(req)

        url = "{0}/{1}/assignedbankids/{2}".format(assessments_endpoint,
                                                   assessment['id'],
                                                   assessment['assignedBankIds'][0])
        self.assertRaises(AppError,
                          self.app.delete,
                          url)


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
            "name"                  : item_name,
            "description"           : item_desc,
            "question"              : {
                "type"           : question_type,
                "questionString" : question_body,
                "choices"        : question_choices
            },
            "answers"               : [{
                "type"      : answer_type,
                "choiceId"  : answer
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

        # verify that the offering has defaulted to maxAttempts = None
        self.assertIsNone(offering['maxAttempts'])

        assessment_offering_detail_endpoint = self.url + '/assessmentsoffered/' + offering_id
        self.app.delete(assessment_offering_detail_endpoint)

        # try again, but set maxAttempts on create
        payload = {
            "startTime"     : {
                "day"   : 1,
                "month" : 1,
                "year"  : 2015
            },
            "duration"      : {
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

        # verify that the offering has defaulted to maxAttempts = None
        self.assertIsNone(offering['maxAttempts'])

        assessment_offering_detail_endpoint = self.url + '/assessmentsoffered/' + offering_id

        # try again, but set maxAttempts on update
        payload = {
            "maxAttempts" : 2
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
            "startTime" : {
                "day"   : 1,
                "month" : 1,
                "year"  : 2015
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
            "startTime"     : {
                "day"   : 1,
                "month" : 1,
                "year"  : 2015
            },
            "duration"      : {
                "days"  : 2
            },
            "reviewOptions" : {
                "whetherCorrect" : {
                    "duringAttempt" : False
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
            'ids'   : ['assessment.Bank%3A1234567890abcdefabcdef12%40ODL.MIT.EDU']
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


class MultipleChoiceAndMWTests(BaseAssessmentTestCase):
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

    def create_drag_and_drop_item(self):
        url = '{0}/items'.format(self.url)
        self._drag_and_drop_test_file.seek(0)
        req = self.app.post(url,
                            upload_files=[('qtiFile', 'testFile', self._drag_and_drop_test_file.read())])
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

    def create_mc_item_for_feedback_testing(self):
        url = '{0}/items'.format(self.url)
        self._number_of_feedback_test_file.seek(0)
        req = self.app.post(url,
                            upload_files=[('qtiFile', 'testFile', self._number_of_feedback_test_file.read())])
        self.ok(req)
        return self.json(req)

    def create_mc_multi_select_item(self):
        url = '{0}/items'.format(self.url)
        self._mc_multi_select_test_file.seek(0)
        req = self.app.post(url,
                            upload_files=[('qtiFile', 'testFile', self._mc_multi_select_test_file.read())])
        self.ok(req)
        return self.json(req)

    def create_mw_fitb_item(self):
        url = '{0}/items'.format(self.url)
        self._mw_fill_in_the_blank_test_file.seek(0)
        req = self.app.post(url,
                            upload_files=[('qtiFile', 'testFile', self._mw_fill_in_the_blank_test_file.read())])
        self.ok(req)
        return self.json(req)

    def create_mc_multi_select_survey_item(self):
        url = '{0}/items'.format(self.url)
        self._multi_select_survey_question_test_file.seek(0)
        req = self.app.post(url,
                            upload_files=[('qtiFile',
                                           self._filename(self._multi_select_survey_question_test_file),
                                           self._multi_select_survey_question_test_file.read())])
        self.ok(req)
        return self.json(req)

    def create_mc_survey_item(self):
        url = '{0}/items'.format(self.url)
        self._survey_question_test_file.seek(0)
        req = self.app.post(url,
                            upload_files=[('qtiFile',
                                           self._filename(self._survey_question_test_file),
                                           self._survey_question_test_file.read())])
        self.ok(req)
        return self.json(req)

    def create_mw_sentence_item(self):
        url = '{0}/items'.format(self.url)
        self._mw_sentence_test_file.seek(0)
        req = self.app.post(url,
                            upload_files=[('qtiFile', 'testFile', self._mw_sentence_test_file.read())])
        self.ok(req)
        return self.json(req)

    def create_question_with_images_in_feedback(self):
        url = '{0}/items'.format(self.url)
        self._image_in_feedback_test_file.seek(0)
        req = self.app.post(url,
                            upload_files=[('qtiFile',
                                           self._filename(self._image_in_feedback_test_file),
                                           self._image_in_feedback_test_file.read())])
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

    def create_unicode_feedback_item(self):
        url = '{0}/items'.format(self.url)
        self._unicode_feedback_test_file.seek(0)
        req = self.app.post(url,
                            upload_files=[('qtiFile',
                                           self._filename(self._unicode_feedback_test_file),
                                           self._unicode_feedback_test_file.read())])
        self.ok(req)
        return self.json(req)

    def create_unshuffled_fitb_item(self):
        url = '{0}/items'.format(self.url)
        self._unshuffled_inline_choice_question_test_file.seek(0)
        req = self.app.post(url,
                            upload_files=[('qtiFile',
                                           self._filename(self._unshuffled_inline_choice_question_test_file),
                                           self._unshuffled_inline_choice_question_test_file.read())])
        self.ok(req)
        return self.json(req)

    def create_unshuffled_mc_item(self):
        url = '{0}/items'.format(self.url)
        self._unshuffled_mc_question_test_file.seek(0)
        req = self.app.post(url,
                            upload_files=[('qtiFile',
                                           self._filename(self._unshuffled_mc_question_test_file),
                                           self._unshuffled_mc_question_test_file.read())])
        self.ok(req)
        return self.json(req)

    def create_unshuffled_order_interaction_item(self):
        url = '{0}/items'.format(self.url)
        self._unshuffled_order_interaction_question_test_file.seek(0)
        req = self.app.post(url,
                            upload_files=[('qtiFile',
                                           self._filename(self._unshuffled_order_interaction_question_test_file),
                                           self._unshuffled_order_interaction_question_test_file.read())])
        self.ok(req)
        return self.json(req)

    def get_question_id(self, taken):
        url = '{0}/assessmentstaken/{1}/questions'.format(self.url,
                                                          unquote(str(taken.ident)))
        req = self.app.get(url)
        self.ok(req)
        data = self.json(req)
        return data['data'][0]['id']

    def setUp(self):
        super(MultipleChoiceAndMWTests, self).setUp()

        self._item = self.create_item(self._bank.ident)
        self._taken, self._offered = self.create_taken_for_item(self._bank.ident, self._item.ident)

        self._mw_sentence_test_file = open('{0}/tests/files/mw_sentence_with_audio_file.zip'.format(ABS_PATH), 'r')
        self._mc_multi_select_test_file = open('{0}/tests/files/mc_multi_select_test_file.zip'.format(ABS_PATH), 'r')
        self._number_of_feedback_test_file = open('{0}/tests/files/ee_u1l01a04q01_en.zip'.format(ABS_PATH), 'r')
        self._mw_fill_in_the_blank_test_file = open('{0}/tests/files/mw_fill_in_the_blank_test_file.zip'.format(ABS_PATH), 'r')
        self._drag_and_drop_test_file = open('{0}/tests/files/drag_and_drop_test_file.zip'.format(ABS_PATH), 'r')
        self._image_in_feedback_test_file = open('{0}/tests/files/image_feedback_test_file.zip'.format(ABS_PATH), 'r')
        self._survey_question_test_file = open('{0}/tests/files/survey_question_test_file.zip'.format(ABS_PATH), 'r')
        self._multi_select_survey_question_test_file = open('{0}/tests/files/survey_question_multi_select_test_file.zip'.format(ABS_PATH), 'r')
        self._unshuffled_mc_question_test_file = open('{0}/tests/files/no_shuffle_mc_test_file.zip'.format(ABS_PATH), 'r')
        self._unshuffled_order_interaction_question_test_file = open('{0}/tests/files/order_interaction_no_shuffle_test_file.zip'.format(ABS_PATH), 'r')
        self._unshuffled_inline_choice_question_test_file = open('{0}/tests/files/fitb_no_shuffle_test_file.zip'.format(ABS_PATH), 'r')
        self._unicode_feedback_test_file = open('{0}/tests/files/ee_u1l05a04q01_en.zip'.format(ABS_PATH), 'r')

        self.url += '/banks/' + unquote(str(self._bank.ident))

    def tearDown(self):
        super(MultipleChoiceAndMWTests, self).tearDown()

        self._mw_sentence_test_file.close()
        self._mc_multi_select_test_file.close()
        self._number_of_feedback_test_file.close()
        self._mw_fill_in_the_blank_test_file.close()
        self._drag_and_drop_test_file.close()
        self._image_in_feedback_test_file.close()
        self._survey_question_test_file.close()
        self._multi_select_survey_question_test_file.close()
        self._unshuffled_mc_question_test_file.close()
        self._unshuffled_order_interaction_question_test_file.close()
        self._unshuffled_inline_choice_question_test_file.close()
        self._unicode_feedback_test_file.close()

    def verify_answers(self, _data, _a_strs, _a_types):
        """
        verify just the answers part of an item. Should allow you to pass
        in either a request response or a json object...load if needed
        """
        try:
            try:
                data = json.loads(_data.body)
                if 'data' in data:
                    data = data['data']['results']
            except:
                data = json.loads(_data)
        except:
            data = _data

        if 'answers' in data:
            answers = data['answers']
        elif 'results' in data:
            answers = data['results']
        else:
            answers = data

        if isinstance(answers, list):
            ind = 0
            for _a in _a_strs:
                if _a_types[ind] == 'answer-record-type%3Ashort-text-answer%40ODL.MIT.EDU':
                    self.assertEqual(
                        answers[ind]['text']['text'],
                        _a
                    )
                self.assertIn(
                    _a_types[ind],
                    answers[ind]['recordTypeIds']
                )
                ind += 1
        elif isinstance(answers, dict):
            if _a_types[0] == 'answer-record-type%3Ashort-text-answer%40ODL.MIT.EDU':
                self.assertEqual(
                    answers['text']['text'],
                    _a_strs[0]
                )
            self.assertIn(
                _a_types[0],
                answers['recordTypeIds']
            )
        else:
            self.fail('Bad answer format.')

    def verify_questions_answers(self, _req, _q_str, _q_type, _a_str, _a_type, _id=None):
        """
        helper method to verify the questions & answers in a returned item
        takes care of all the language stuff
        Assumes multiple answers, to _a_str and _a_type must be lists
        """
        req = json.loads(_req.body)
        if _id:
            data = None
            for item in req:
                if (item['id'] == _id or
                        item['id'] == quote(_id)):
                    data = item
            if not data:
                raise LookupError('Item with id: ' + _id + ' not found.')
        else:
            data = req

        self.verify_question(data, _q_str, _q_type)

        self.verify_answers(data, _a_str, _a_type)

    def test_multiple_choice_questions_are_randomized_if_flag_set(self):
        edx_mc_q = Type(**QUESTION_RECORD_TYPES['multi-choice-edx'])
        edx_mc_a = Type(**ANSWER_RECORD_TYPES['multi-choice-edx'])

        item_name = 'a really complicated item'
        item_desc = 'meant to differentiate students'
        question_body = 'can you manipulate this?'
        question_choices = [
            'yes',
            'no',
            'maybe'
        ]
        question_type = str(edx_mc_q)
        answer = 2
        answer_type = str(edx_mc_a)
        payload = {
            "name"          : item_name,
            "description"   : item_desc,
            "question"      : {
                "type"           : question_type,
                "rerandomize"    : "always",
                "questionString" : question_body,
                "choices"        : question_choices
            },
            "answers"       : [{
                "type"      : answer_type,
                "choiceId"  : answer
            }],
        }
        req = self.app.post(self.url + '/items',
                            params=json.dumps(payload),
                            headers={'content-type': 'application/json'})

        self.ok(req)
        item = self.json(req)
        taken, offered = self.create_taken_for_item(self._bank.ident, item['id'])
        taken_url = '{0}/assessmentstaken/{2}/questions'.format(self.url,
                                                                unquote(str(self._bank.ident)),
                                                                unquote(str(taken.ident)))
        req = self.app.get(taken_url)
        self.ok(req)
        data = self.json(req)['data']
        order_1 = data[0]['choices']

        num_different = 0

        for i in range(0, 15):
            req2 = self.app.get(taken_url)
            self.ok(req)
            data2 = self.json(req2)['data']
            order_2 = data2[0]['choices']

            if order_1 != order_2:
                num_different += 1
        self.assertTrue(num_different > 0)

    def test_edx_multi_choice_answer_index_too_high(self):
        items_endpoint = '{0}/items'.format(self.url)

        # Use POST to create an item--right now user is Learner,
        # so this should throw unauthorized
        item_name = 'a really complicated item'
        item_desc = 'meant to differentiate students'
        question_body = 'can you answer this?'
        question_choices = [
            'yes',
            'no',
            'maybe'
        ]
        question_type = 'question-record-type%3Amulti-choice-edx%40ODL.MIT.EDU'
        answer = 4
        answer_type = 'answer-record-type%3Amulti-choice-edx%40ODL.MIT.EDU'
        payload = {
            "name"          : item_name,
            "description"   : item_desc,
            "question"      : {
                "type"           : question_type,
                "questionString" : question_body,
                "choices"        : question_choices
            },
            "answers"       : [{
                "type"      : answer_type,
                "choiceId"  : answer
            }],
        }

        self.assertRaises(AppError,
                          self.app.post,
                          items_endpoint,
                          params=json.dumps(payload),
                          headers={'content-type': 'application/json'})

    def test_edx_multi_choice_answer_index_too_low(self):
        items_endpoint = '{0}/items'.format(self.url)

        # Use POST to create an item--right now user is Learner,
        # so this should throw unauthorized
        item_name = 'a really complicated item'
        item_desc = 'meant to differentiate students'
        question_body = 'can you answer this?'
        question_choices = [
            'yes',
            'no',
            'maybe'
        ]
        question_type = 'question-record-type%3Amulti-choice-edx%40ODL.MIT.EDU'
        answer = 0
        answer_type = 'answer-record-type%3Amulti-choice-edx%40ODL.MIT.EDU'
        payload = {
            "name"          : item_name,
            "description"   : item_desc,
            "question"      : {
                "type"           : question_type,
                "questionString" : question_body,
                "choices"        : question_choices
            },
            "answers"       : [{
                "type"      : answer_type,
                "choiceId"  : answer
            }],
        }

        self.assertRaises(AppError,
                          self.app.post,
                          items_endpoint,
                          params=json.dumps(payload),
                          headers={'content-type': 'application/json'})

    def test_edx_multi_choice_answer_not_enough_choices(self):
        items_endpoint = '{0}/items'.format(self.url)

        item_name = 'a really complicated item'
        item_desc = 'meant to differentiate students'
        question_body = 'can you answer this?'
        question_choices = [
            'yes'
        ]
        question_type = 'question-record-type%3Amulti-choice-edx%40ODL.MIT.EDU'
        answer = 1
        answer_type = 'answer-record-type%3Amulti-choice-edx%40ODL.MIT.EDU'
        payload = {
            "name"          : item_name,
            "description"   : item_desc,
            "question"      : {
                "type"           : question_type,
                "questionString" : question_body,
                "choices"        : question_choices
            },
            "answers"       : [{
                "type"      : answer_type,
                "choiceId"  : answer
            }],
        }

        self.assertRaises(AppError,
                          self.app.post,
                          items_endpoint,
                          params=json.dumps(payload),
                          headers={'content-type': 'application/json'})

    def test_edx_multi_choice_crud(self):
        """
        Test an instructor can create and respond to an edX multiple choice
        type question.
        """
        items_endpoint = '{0}/items'.format(self.url)

        # Use POST to create an item--right now user is Learner,
        # so this should throw unauthorized
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
        payload = {
            "name"          : item_name,
            "description"   : item_desc,
            "question"      : {
                "type"           : question_type,
                "questionString" : question_body,
                "choices"        : question_choices
            },
            "answers"       : [{
                "type"      : answer_type,
                "choiceId"  : answer
            }],
        }
        req = self.app.post(items_endpoint,
                            params=json.dumps(payload),
                            headers={'content-type': 'application/json'})
        self.ok(req)
        item = self.json(req)
        item_id = unquote(item['id'])
        item_details_endpoint = '{0}/items/{1}'.format(self.url,
                                                       item_id)

        expected_answers = item['answers'][0]['choiceIds']

        # attach to an assessment -> offering -> taken
        # The user can now respond to the question and submit a response
        # first attach the item to an assessment
        # and create an offering.
        # Use the offering_id to create the taken
        assessments_endpoint = '{0}/assessments'.format(self.url)
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
        assessment_id = unquote(json.loads(req.body)['id'])

        assessment_detail_endpoint = assessments_endpoint + '/' + assessment_id
        assessment_offering_endpoint = assessment_detail_endpoint + '/assessmentsoffered'
        assessment_items_endpoint = assessment_detail_endpoint + '/items'

        # POST should create the linkage
        payload = {
            'itemIds' : [item_id]
        }
        req = self.app.post(assessment_items_endpoint,
                            params=json.dumps(payload),
                            headers={'content-type': 'application/json'})
        self.ok(req)

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

        assessment_offering_detail_endpoint = '{0}/assessmentsoffered/{1}'.format(self.url,
                                                                                  offering_id)

        # Can POST to create a new taken
        assessment_offering_takens_endpoint = assessment_offering_detail_endpoint + '/assessmentstaken'
        req = self.app.post(assessment_offering_takens_endpoint)
        self.ok(req)
        taken = json.loads(req.body)
        taken_id = unquote(taken['id'])

        # Instructor can now take the assessment
        taken_endpoint = '{0}/assessmentstaken/{1}'.format(self.url,
                                                           taken_id)

        # Only GET of this endpoint is supported
        taken_questions_endpoint = taken_endpoint + '/questions'
        # Submitting a non-list response is okay, if it is right, because
        # service will listify it
        bad_response = {
            'choiceIds': expected_answers[0]
        }
        taken_question_details_endpoint = taken_questions_endpoint + '/' + item_id
        taken_submit_endpoint = taken_question_details_endpoint + '/submit'
        req = self.app.post(taken_submit_endpoint,
                            params=json.dumps(bad_response),
                            headers={'content-type': 'application/json'})
        self.ok(req)
        self.verify_submission(req, _expected_result=True)

        # Now can submit a list response to this endpoint
        response = {
            'choiceIds': expected_answers
        }
        req = self.app.post(taken_submit_endpoint,
                            params=json.dumps(response),
                            headers={'content-type': 'application/json'})
        self.ok(req)
        self.verify_submission(req, _expected_result=True)

    def test_edx_multi_choice_missing_parameters(self):
        items_endpoint = '{0}/items'.format(self.url)

        # Use POST to create an item--right now user is Learner,
        # so this should throw unauthorized
        item_name = 'a really complicated item'
        item_desc = 'meant to differentiate students'
        question_body = 'can you answer this?'
        question_choices = [
            'yes',
            'no',
            'maybe'
        ]
        question_type = 'question-record-type%3Amulti-choice-edx%40ODL.MIT.EDU'
        answer = 2
        answer_type = 'answer-record-type%3Amulti-choice-edx%40ODL.MIT.EDU'
        payload = {
            "name"          : item_name,
            "description"   : item_desc,
            "question"      : {
                "type"           : question_type,
                "questionString" : question_body,
                "choices"        : question_choices
            },
            "answers"       : [{
                "type"      : answer_type,
                "choiceId"  : answer
            }],
        }

        params = ['questionString', 'choices', 'choiceId']
        for param in params:
            test_payload = deepcopy(payload)
            if param == 'choiceId':
                del test_payload['answers'][0][param]
            else:
                del test_payload['question'][param]

            self.assertRaises(AppError,
                              self.app.post,
                              items_endpoint,
                              params=json.dumps(test_payload),
                              headers={'content-type': 'application/json'})

    def test_edx_multi_choice_with_named_choices(self):
        """
        Test an instructor can create named choices with a dict
        """
        items_endpoint = '{0}/items'.format(self.url)

        # Use POST to create an item--right now user is Learner,
        # so this should throw unauthorized
        item_name = 'a really complicated item'
        item_desc = 'meant to differentiate students'
        question_body = 'can you manipulate this?'
        question_choices = [
            {'text' : 'I hope so.',
             'name' : 'yes'},
            {'text' : 'I don\'t think I can.',
             'name' : 'no'},
            {'text' : 'Maybe tomorrow.',
             'name' : 'maybe'}
        ]
        question_type = 'question-record-type%3Amulti-choice-edx%40ODL.MIT.EDU'
        answer = 2
        answer_type = 'answer-record-type%3Amulti-choice-edx%40ODL.MIT.EDU'
        payload = {
            "name"          : item_name,
            "description"   : item_desc,
            "question"      : {
                "type"           : question_type,
                "questionString" : question_body,
                "choices"        : question_choices
            },
            "answers"       : [{
                "type"      : answer_type,
                "choiceId"  : answer
            }],
        }
        req = self.app.post(items_endpoint,
                            params=json.dumps(payload),
                            headers={'content-type': 'application/json'})
        self.ok(req)

    def test_items_crud(self):
        """
        Create a test bank and test all things associated with items
        and a single item
        DELETE on root items/ does nothing. Error code 405.
        GET on root items/ gets you a list
        POST on root items/ creates a new item
        PUT on root items/ does nothing. Error code 405.

        For a single item detail:
        DELETE will delete that item
        GET brings up the item details with offerings and taken
        POST does nothing. Error code 405.
        PUT lets user update the name or description
        """
        items_endpoint = '{0}/items'.format(self.url)

        # Check that DELETE returns error code 405--we don't support this
        self.assertRaises(AppError,
                          self.app.delete,
                          items_endpoint)

        # PUT to this root url also returns a 405
        self.assertRaises(AppError,
                          self.app.put,
                          items_endpoint)

        # GET for a Learner is unauthorized, should get 0 results back.
        req = self.app.get(items_endpoint)
        self.assertEqual(
            len(self.json(req)),
            1
        )

        # Use POST to create an item
        item_name = 'a really complicated item'
        item_desc = 'meant to differentiate students'
        payload = {
            "name": item_name,
            "description": item_desc
        }
        req = self.app.post(items_endpoint,
                            params=json.dumps(payload),
                            headers={'content-type': 'application/json'})
        self.ok(req)
        item_id = unquote(json.loads(req.body)['id'])
        self.verify_text(req,
                         'Item',
                         item_name,
                         item_desc)

        req = self.app.get(items_endpoint)
        self.ok(req)
        self.verify_text(req,
                         'Item',
                         item_name,
                         item_desc,
                         item_id)

        # Now test PUT / GET / POST / DELETE on the new item
        # POST does nothing
        item_detail_endpoint = items_endpoint + '/' + item_id
        self.assertRaises(AppError,
                          self.app.post,
                          item_detail_endpoint)

        # GET displays it, with self link
        req = self.app.get(item_detail_endpoint)

        self.ok(req)
        self.verify_text(req,
                         'Item',
                         item_name,
                         item_desc)

        new_item_name = 'a new item name'
        new_item_desc = 'to trick students'
        payload = {
            "name": new_item_name
        }
        req = self.app.put(item_detail_endpoint,
                           params=json.dumps(payload),
                           headers={'content-type': 'application/json'})
        self.ok(req)
        self.verify_text(req,
                         'Item',
                         new_item_name,
                         item_desc)

        req = self.app.get(item_detail_endpoint)
        self.ok(req)
        self.verify_text(req,
                         'Item',
                         new_item_name,
                         item_desc)

        payload = {
            "description": new_item_desc
        }
        req = self.app.put(item_detail_endpoint,
                           params=json.dumps(payload),
                           headers={'content-type': 'application/json'})
        self.ok(req)
        self.verify_text(req,
                         'Item',
                         new_item_name,
                         new_item_desc)

        req = self.app.get(item_detail_endpoint)
        self.ok(req)
        self.verify_text(req,
                         'Item',
                         new_item_name,
                         new_item_desc)

        # trying to delete the bank with items should throw an error
        self.assertRaises(AppError,
                          self.app.delete,
                          self.url)

    def test_question_string_item_crud(self):
        """
        Test ability for user to POST a new question string and
        response string item
        """
        items_endpoint = '{0}/items'.format(self.url)

        # Use POST to create an item--right now user is Learner,
        # so this should throw unauthorized
        item_name = 'a really complicated item'
        item_desc = 'meant to differentiate students'
        question_string = 'what is pi?'
        question_type = 'question-record-type%3Ashort-text-answer%40ODL.MIT.EDU'
        answer_string = 'dessert'
        answer_type = 'answer-record-type%3Ashort-text-answer%40ODL.MIT.EDU'
        payload = {
            "name": item_name,
            "description": item_desc,
            "question": {
                "type": question_type,
                "questionString": question_string
            },
            "answers": [{
                "type": answer_type,
                "responseString": answer_string
            }]
        }

        # Use POST to create an item--right now user is Instructor,
        # so this should show up in GET
        req = self.app.post(items_endpoint,
                            params=json.dumps(payload),
                            headers={'content-type': 'application/json'})
        self.ok(req)
        item = json.loads(req.body)
        item_id = unquote(item['id'])
        question_id = self.extract_question(item)['id']
        answer_id = self.extract_answers(item)[0]['id']
        self.verify_text(req,
                         'Item',
                         item_name,
                         item_desc)
        self.verify_questions_answers(req,
                                      question_string,
                                      question_type,
                                      [answer_string],
                                      [answer_type])

        req = self.app.get(items_endpoint)
        self.ok(req)
        self.verify_text(req,
                         'Item',
                         item_name,
                         item_desc,
                         item_id)
        self.verify_questions_answers(req,
                                      question_string,
                                      question_type,
                                      [answer_string],
                                      [answer_type],
                                      item_id)

        # Now test PUT / GET / POST / DELETE on the new item
        # POST does nothing
        item_detail_endpoint = items_endpoint + '/' + item_id

        self.assertRaises(AppError,
                          self.app.post,
                          item_detail_endpoint)

        # GET displays it, with self link
        req = self.app.get(item_detail_endpoint)
        self.ok(req)
        self.verify_text(req,
                         'Item',
                         item_name,
                         item_desc)
        self.verify_questions_answers(req,
                                      question_string,
                                      question_type,
                                      [answer_string],
                                      [answer_type])

        # PUT should work for Instructor.
        # Can modify the question and answers, reflected in GET
        new_question_string = 'what day is it?'
        new_answer_string = 'Saturday'

        payload = {
            'question': {
                'id' : question_id,
                'questionString': new_question_string,
                'type': question_type
            }
        }
        req = self.app.put(item_detail_endpoint,
                           params=json.dumps(payload),
                           headers={'content-type': 'application/json'})
        self.ok(req)
        self.verify_questions_answers(req,
                                      new_question_string,
                                      question_type,
                                      [answer_string],
                                      [answer_type])
        req = self.app.get(item_detail_endpoint)
        self.ok(req)
        self.verify_questions_answers(req,
                                      new_question_string,
                                      question_type,
                                      [answer_string],
                                      [answer_type])

        payload = {
            'answers': [{
                'id' : answer_id,
                'responseString': new_answer_string,
                'type': answer_type
            }]
        }
        req = self.app.put(item_detail_endpoint,
                           params=json.dumps(payload),
                           headers={'content-type': 'application/json'})
        self.ok(req)
        self.verify_questions_answers(req,
                                      new_question_string,
                                      question_type,
                                      [new_answer_string],
                                      [answer_type])

        req = self.app.get(item_detail_endpoint)
        self.ok(req)
        self.verify_questions_answers(req,
                                      new_question_string,
                                      question_type,
                                      [new_answer_string],
                                      [answer_type])

    def test_can_submit_right_answer_mw_sentence(self):
        mc_item = self.create_mw_sentence_item()
        taken, offered = self.create_taken_for_item(self._bank.ident, Id(mc_item['id']))

        question_id = self.get_question_id(taken)

        url = '{0}/assessmentstaken/{1}/questions/{2}/submit'.format(self.url,
                                                                     unquote(str(taken.ident)),
                                                                     question_id)
        payload = {
            'choiceIds': ['id51b2feca-d407-46d5-b548-d6645a021008',
                          'id881a8e9c-844b-4394-be62-d28a5fda5296',
                          'idcccac9f8-3b85-4a2f-a95c-1922dec5d04a',
                          'id28a924d9-32ac-4ac5-a4b2-1b1cfe2caba0',
                          'id78ce22bf-559f-44a4-95ee-156f222ad510',
                          'id3045d860-24b4-4b30-9ca1-72408a3bcc9b',
                          'id2cad48be-2782-4625-9669-dfcb2062bf3c'],
            'type': 'answer-type%3Aqti-order-interaction-mw-sentence%40ODL.MIT.EDU'
        }
        req = self.app.post(url,
                            params=json.dumps(payload),
                            headers={'content-type': 'application/json'})
        self.ok(req)
        data = self.json(req)
        self.assertTrue(data['correct'])
        self.assertIn('Correct Feedback goes here!', data['feedback'])
        self.assertNotIn('Wrong...Feedback goes here!', data['feedback'])

    def test_can_submit_wrong_answer_mw_sentence(self):
        mc_item = self.create_mw_sentence_item()
        taken, offered = self.create_taken_for_item(self._bank.ident, Id(mc_item['id']))

        question_id = self.get_question_id(taken)

        url = '{0}/assessmentstaken/{1}/questions/{2}/submit'.format(self.url,
                                                                     unquote(str(taken.ident)),
                                                                     question_id)
        payload = {
            'choiceIds': ['id51b2feca-d407-46d5-b548-d6645a021008',
                          'id881a8e9c-844b-4394-be62-d28a5fda5296',
                          'id28a924d9-32ac-4ac5-a4b2-1b1cfe2caba0',  # swapped the order
                          'idcccac9f8-3b85-4a2f-a95c-1922dec5d04a',  # swapped the order
                          'id78ce22bf-559f-44a4-95ee-156f222ad510',
                          'id3045d860-24b4-4b30-9ca1-72408a3bcc9b',
                          'id2cad48be-2782-4625-9669-dfcb2062bf3c'],
            'type': 'answer-type%3Aqti-order-interaction-mw-sentence%40ODL.MIT.EDU'
        }
        req = self.app.post(url,
                            params=json.dumps(payload),
                            headers={'content-type': 'application/json'})
        self.ok(req)
        data = self.json(req)
        self.assertFalse(data['correct'])
        self.assertNotIn('Correct Feedback goes here!', data['feedback'])
        self.assertIn('Wrong...Feedback goes here!', data['feedback'])

    def test_cannot_submit_too_many_choices_even_if_partially_correct_mw_sentence(self):
        mc_item = self.create_mw_sentence_item()
        taken, offered = self.create_taken_for_item(self._bank.ident, Id(mc_item['id']))

        question_id = self.get_question_id(taken)

        url = '{0}/assessmentstaken/{1}/questions/{2}/submit'.format(self.url,
                                                                     unquote(str(taken.ident)),
                                                                     question_id)
        payload = {
            'choiceIds': ['id51b2feca-d407-46d5-b548-d6645a021008',
                          'id881a8e9c-844b-4394-be62-d28a5fda5296',
                          'idcccac9f8-3b85-4a2f-a95c-1922dec5d04a',
                          'id28a924d9-32ac-4ac5-a4b2-1b1cfe2caba0',
                          'id78ce22bf-559f-44a4-95ee-156f222ad510',
                          'id3045d860-24b4-4b30-9ca1-72408a3bcc9b',
                          'id2cad48be-2782-4625-9669-dfcb2062bf3c',
                          'a',
                          'b'],
            'type': 'answer-type%3Aqti-order-interaction-mw-sentence%40ODL.MIT.EDU'
        }
        req = self.app.post(url,
                            params=json.dumps(payload),
                            headers={'content-type': 'application/json'})
        self.ok(req)
        data = self.json(req)
        self.assertFalse(data['correct'])
        self.assertNotIn('Correct Feedback goes here!', data['feedback'])
        self.assertIn('Wrong...Feedback goes here!', data['feedback'])

    def test_submitting_too_few_answers_returns_incorrect_mw_sentence(self):
        mc_item = self.create_mw_sentence_item()
        taken, offered = self.create_taken_for_item(self._bank.ident, Id(mc_item['id']))

        url = '{0}/assessmentstaken/{1}/questions'.format(self.url,
                                                          unquote(str(taken.ident)))
        req = self.app.get(url)
        self.ok(req)
        data = self.json(req)
        question_id = data['data'][0]['id']

        url = '{0}/assessmentstaken/{1}/questions/{2}/submit'.format(self.url,
                                                                     unquote(str(taken.ident)),
                                                                     question_id)
        payload = {
            'choiceIds': ['a',
                          'b'],
            'type': 'answer-type%3Aqti-order-interaction-mw-sentence%40ODL.MIT.EDU'
        }
        req = self.app.post(url,
                            params=json.dumps(payload),
                            headers={'content-type': 'application/json'})
        self.ok(req)
        data = self.json(req)
        self.assertFalse(data['correct'])
        self.assertNotIn('Correct Feedback goes here!', data['feedback'])
        self.assertIn('Wrong...Feedback goes here!', data['feedback'])

    def test_can_submit_right_answer_mc_multi_select(self):
        mc_item = self.create_mc_multi_select_item()
        taken, offered = self.create_taken_for_item(self._bank.ident, Id(mc_item['id']))
        url = '{0}/assessmentstaken/{1}/questions/{2}/submit'.format(self.url,
                                                                     unquote(str(taken.ident)),
                                                                     unquote(mc_item['id']))
        payload = {
            'choiceIds': ['idb5345daa-a5c2-4924-a92b-e326886b5d1d',
                          'id47e56db8-ee16-4111-9bcc-b8ac9716bcd4',
                          'id4f525d00-e24c-4ac3-a104-848a2cd686c0'],
            'type': 'answer-type%3Aqti-choice-interaction-multi-select%40ODL.MIT.EDU'
        }
        req = self.app.post(url,
                            params=json.dumps(payload),
                            headers={'content-type': 'application/json'})
        self.ok(req)
        data = self.json(req)
        self.assertTrue(data['correct'])
        self.assertIn('You are correct! A square has the properties of both a rectangle, and a rhombus. Hence, it can also occupy the shaded region.', data['feedback'])
        self.assertNotIn('Please try again!', data['feedback'])

    def test_can_edit_multi_language_choice_images_via_rest_mc(self):
        """the image reloading script can strip out the height and width attributes"""
        mc_item = self.create_mc_multi_select_item()
        url = '{0}/items/{1}'.format(self.url,
                                     unquote(mc_item['id']))

        req = self.app.get(url)
        self.ok(req)
        data = self.json(req)

        payload = {
            'type': mc_item['genusTypeId'],
            'question': {
                'choices': []
            }
        }

        for choice in data['question']['multiLanguageChoices']:
            for text in choice['texts']:
                choice_xml = BeautifulSoup(text['text'], 'xml')

                if choice_xml.find('img'):
                    self.assertIn('height=', text['text'])
                    self.assertIn('width=', text['text'])
                    for img in choice_xml.find_all('img'):
                        del img['height']
                        del img['width']
                    payload['question']['choices'].append({
                        'id': choice['id'],
                        'updatedText': str(choice_xml.simpleChoice)
                    })

        req = self.app.put(url,
                           params=json.dumps(payload),
                           headers={'content-type': 'application/json'})
        self.ok(req)

        req = self.app.get(url)
        self.ok(req)
        data = self.json(req)

        for choice in data['question']['multiLanguageChoices']:
            for text in choice['texts']:
                choice_xml = BeautifulSoup(text['text'], 'xml')

                if choice_xml.find('img'):
                    self.assertNotIn('height=', text['text'])
                    self.assertNotIn('width=', text['text'])
        for choice in data['question']['choices']:
            choice_xml = BeautifulSoup(choice['text'], 'xml')

            if choice_xml.find('img'):
                self.assertNotIn('height=', choice['text'])
                self.assertNotIn('width=', choice['text'])

    def test_can_edit_question_images_via_rest_fitb(self):
        """the image reloading script can strip out the height and width attributes"""
        mw_item = self.create_mw_fitb_item()
        url = '{0}/items/{1}'.format(self.url,
                                     unquote(mw_item['id']))

        req = self.app.get(url)
        self.ok(req)
        data = self.json(req)

        payload = {
            'type': mw_item['genusTypeId'],
            'question': {
                'updatedQuestionString': ''
            }
        }

        question_xml = BeautifulSoup(data['question']['texts'][0]['text'], 'xml')
        self.assertIn('height=', data['question']['texts'][0]['text'])
        self.assertIn('width=', data['question']['texts'][0]['text'])

        for img in question_xml.find_all('img'):
            del img['height']
            del img['width']
        payload['question']['updatedQuestionString'] = str(question_xml.itemBody)

        req = self.app.put(url,
                           params=json.dumps(payload),
                           headers={'content-type': 'application/json'})
        self.ok(req)

        req = self.app.get(url)
        self.ok(req)
        data = self.json(req)

        self.assertNotIn('height=', data['question']['texts'][0]['text'])
        self.assertNotIn('width=', data['question']['texts'][0]['text'])

    def test_can_edit_feedback_images_via_rest_mc(self):
        """the image reloading script can strip out the height and width attributes"""
        mc_item = self.create_question_with_images_in_feedback()
        url = '{0}/items/{1}'.format(self.url,
                                     unquote(mc_item['id']))

        req = self.app.get(url)
        self.ok(req)
        data = self.json(req)

        payload = {
            'type': mc_item['genusTypeId'],
            'answers': []
        }

        for answer in data['answers']:
            answer_xml = BeautifulSoup(answer['feedbacks'][0]['text'], 'xml')
            self.assertIn('height=', answer['feedbacks'][0]['text'])
            self.assertIn('width=', answer['feedbacks'][0]['text'])

            for img in answer_xml.find_all('img'):
                del img['height']
                del img['width']
            payload['answers'].append({
                'id': answer['id'],
                'updatedFeedback': str(answer_xml.modalFeedback),
                'type': mc_item['genusTypeId'].replace('assessment-item', 'answer')
            })

        req = self.app.put(url,
                           params=json.dumps(payload),
                           headers={'content-type': 'application/json'})
        self.ok(req)

        req = self.app.get(url)
        self.ok(req)
        data = self.json(req)

        for answer in data['answers']:
            self.assertNotIn('height=', answer['feedbacks'][0]['text'])
            self.assertNotIn('width=', answer['feedbacks'][0]['text'])

    def test_can_edit_shuffle_option_for_qti_question_via_rest_mw(self):
        mc_item = self.create_mw_sentence_item()
        self.assertTrue(mc_item['question']['shuffle'])
        url = '{0}/items/{1}'.format(self.url,
                                     mc_item['id'])
        payload = {
            "question": {
                "shuffle": False
            }
        }

        req = self.app.put(url,
                           params=json.dumps(payload),
                           headers={'content-type': 'application/json'})
        self.ok(req)
        req = self.app.get(url)
        self.ok(req)
        data = self.json(req)
        self.assertFalse(data['question']['shuffle'])

        url = '{0}/qti'.format(url)
        req = self.app.get(url)
        self.ok(req)
        soup = BeautifulSoup(req.body, 'xml')
        self.assertEqual(soup.orderInteraction['shuffle'], 'false')

    def test_can_edit_shuffle_option_for_qti_question_via_rest_mc(self):
        mc_item = self.create_mc_multi_select_item()
        self.assertFalse(mc_item['question']['shuffle'])
        url = '{0}/items/{1}'.format(self.url,
                                     mc_item['id'])
        payload = {
            "question": {
                "shuffle": True
            }
        }

        req = self.app.put(url,
                           params=json.dumps(payload),
                           headers={'content-type': 'application/json'})
        self.ok(req)
        req = self.app.get(url)
        self.ok(req)
        data = self.json(req)
        self.assertTrue(data['question']['shuffle'])

        url = '{0}/qti'.format(url)
        req = self.app.get(url)
        self.ok(req)
        soup = BeautifulSoup(req.body, 'xml')
        self.assertEqual(soup.choiceInteraction['shuffle'], 'true')

    def test_can_edit_unicode_feedback_via_rest_mc(self):
        """the audio feedback script can send back unicode values"""
        mc_item = self.create_unicode_feedback_item()
        url = '{0}/items/{1}'.format(self.url,
                                     unquote(mc_item['id']))

        req = self.app.get(url)
        self.ok(req)
        data = self.json(req)

        payload = {
            'type': mc_item['genusTypeId'],
            'answers': []
        }

        for answer in data['answers']:
            answer_xml = BeautifulSoup(answer['feedbacks'][0]['text'], 'xml')
            audio_tag = answer_xml.new_tag('audio')
            answer_xml.modalFeedback.append(audio_tag)
            payload['answers'].append({
                'id': answer['id'],
                'updatedFeedback': str(answer_xml.modalFeedback),
                'type': mc_item['genusTypeId'].replace('item-genus-type', 'answer')
            })

        req = self.app.put(url,
                           params=json.dumps(payload),
                           headers={'content-type': 'application/json'})
        self.ok(req)

        req = self.app.get(url)
        self.ok(req)
        data = self.json(req)

        for answer in data['answers']:
            self.assertIn('<audio/>', answer['feedbacks'][0]['text'])

    def test_order_does_not_matter_mc_multi_select(self):
        mc_item = self.create_mc_multi_select_item()
        taken, offered = self.create_taken_for_item(self._bank.ident, Id(mc_item['id']))
        url = '{0}/assessmentstaken/{1}/questions/{2}/submit'.format(self.url,
                                                                     unquote(str(taken.ident)),
                                                                     unquote(mc_item['id']))
        payload = {
            'choiceIds': ['id47e56db8-ee16-4111-9bcc-b8ac9716bcd4',  # swapped order
                          'idb5345daa-a5c2-4924-a92b-e326886b5d1d',  # swapped order
                          'id4f525d00-e24c-4ac3-a104-848a2cd686c0'],
            'type': 'answer-type%3Aqti-choice-interaction-multi-select%40ODL.MIT.EDU'
        }
        req = self.app.post(url,
                            params=json.dumps(payload),
                            headers={'content-type': 'application/json'})
        self.ok(req)
        data = self.json(req)
        self.assertTrue(data['correct'])
        self.assertIn('You are correct! A square has the properties of both a rectangle, and a rhombus. Hence, it can also occupy the shaded region.', data['feedback'])
        self.assertNotIn('Please try again!', data['feedback'])

    def test_can_submit_wrong_answer_mc_multi_select(self):
        mc_item = self.create_mc_multi_select_item()
        taken, offered = self.create_taken_for_item(self._bank.ident, Id(mc_item['id']))
        url = '{0}/assessmentstaken/{1}/questions/{2}/submit'.format(self.url,
                                                                     unquote(str(taken.ident)),
                                                                     unquote(mc_item['id']))
        payload = {
            'choiceIds': ['id47e56db8-ee16-4111-9bcc-b8ac9716bcd4',
                          'id4f525d00-e24c-4ac3-a104-848a2cd686c0'],
            'type': 'answer-type%3Aqti-choice-interaction-multi-select%40ODL.MIT.EDU'
        }
        req = self.app.post(url,
                            params=json.dumps(payload),
                            headers={'content-type': 'application/json'})
        self.ok(req)
        data = self.json(req)
        self.assertFalse(data['correct'])
        self.assertNotIn('You are correct! A square has the properties of both a rectangle, and a rhombus. Hence, it can also occupy the shaded region.', data['feedback'])
        self.assertIn('Please try again!', data['feedback'])

    def test_cannot_submit_too_many_choices_even_if_partially_correct_mc_multi_select(self):
        mc_item = self.create_mc_multi_select_item()
        taken, offered = self.create_taken_for_item(self._bank.ident, Id(mc_item['id']))
        url = '{0}/assessmentstaken/{1}/questions/{2}/submit'.format(self.url,
                                                                     unquote(str(taken.ident)),
                                                                     unquote(mc_item['id']))
        payload = {
            'choiceIds': ['idb5345daa-a5c2-4924-a92b-e326886b5d1d',
                          'id47e56db8-ee16-4111-9bcc-b8ac9716bcd4',
                          'id4f525d00-e24c-4ac3-a104-848a2cd686c0',
                          'id01913fba-e66d-4a01-9625-94102847faac'],
            'type': 'answer-type%3Aqti-choice-interaction-multi-select%40ODL.MIT.EDU'
        }
        req = self.app.post(url,
                            params=json.dumps(payload),
                            headers={'content-type': 'application/json'})
        self.ok(req)
        data = self.json(req)
        self.assertFalse(data['correct'])
        self.assertNotIn('You are correct! A square has the properties of both a rectangle, and a rhombus. Hence, it can also occupy the shaded region.', data['feedback'])
        self.assertIn('Please try again!', data['feedback'])

    def test_submitting_too_few_answers_returns_incorrect_mc_multi_select(self):
        mc_item = self.create_mc_multi_select_item()
        taken, offered = self.create_taken_for_item(self._bank.ident, Id(mc_item['id']))
        url = '{0}/assessmentstaken/{1}/questions/{2}/submit'.format(self.url,
                                                                     unquote(str(taken.ident)),
                                                                     unquote(mc_item['id']))
        payload = {
            'choiceIds': ['a',
                          'b'],
            'type': 'answer-type%3Aqti-choice-interaction-multi-select%40ODL.MIT.EDU'
        }
        req = self.app.post(url,
                            params=json.dumps(payload),
                            headers={'content-type': 'application/json'})
        self.ok(req)
        data = self.json(req)
        self.assertFalse(data['correct'])
        self.assertNotIn('You are correct! A square has the properties of both a rectangle, and a rhombus. Hence, it can also occupy the shaded region.', data['feedback'])
        self.assertIn('Please try again!', data['feedback'])

    def test_only_one_feedback_provided(self):
        item = self.create_mc_item_for_feedback_testing()
        taken, offered = self.create_taken_for_item(self._bank.ident, Id(item['id']))

        questions_url = '{0}/assessmentstaken/{1}/questions'.format(self.url,
                                                                    unquote(str(taken.ident)))
        req = self.app.get(questions_url)
        self.ok(req)
        data = self.json(req)
        question_id = data['data'][0]['id']

        url = '{0}/assessmentstaken/{1}/questions/{2}/submit'.format(self.url,
                                                                     unquote(str(taken.ident)),
                                                                     question_id)
        payload = {
            'choiceIds': ['a'],
            'type': 'answer-type%3Aqti-choice-interaction%40ODL.MIT.EDU'
        }
        req = self.app.post(url,
                            params=json.dumps(payload),
                            headers={'content-type': 'application/json'})
        self.ok(req)
        data = self.json(req)
        self.assertFalse(data['correct'])
        self.assertNotIn('Well done!', data['feedback'])
        self.assertNotIn(';', data['feedback'])
        self.assertIn('Listen carefully', data['feedback'])
        self.assertEqual(data['feedback'].count('Listen carefully'), 1)

    def test_all_answers_correct_for_survey_question(self):
        survey_item = self.create_mc_survey_item()
        taken, offered = self.create_taken_for_item(self._bank.ident, Id(survey_item['id']))

        questions_url = '{0}/assessmentstaken/{1}/questions'.format(self.url,
                                                                    unquote(str(taken.ident)))

        req = self.app.get(questions_url)
        self.ok(req)
        data = self.json(req)

        question_id = data['data'][0]['id']

        url = '{0}/assessmentstaken/{1}/questions/{2}/submit'.format(self.url,
                                                                     unquote(str(taken.ident)),
                                                                     question_id)
        choice_ids = ['id5f1fc52a-a04e-4fa1-b855-51da24967a31',
                      'id31392307-c87e-476b-8f92-b0f12ed66300',
                      'id8188b5cd-89b0-4140-b12a-aed5426bd81b']
        for choice_id in choice_ids:
            payload = {
                'choiceIds': [choice_id],
                'type': 'answer-type%3Aqti-choice-interaction-survey%40ODL.MIT.EDU'
            }
            req = self.app.post(url,
                                params=json.dumps(payload),
                                headers={'content-type': 'application/json'})
            self.ok(req)
            data = self.json(req)
            self.assertTrue(data['correct'])
            self.assertIn('Thank you for your participation.', data['feedback'])
            self.assertNotIn('Incorrect ...', data['feedback'])

    def test_all_answers_correct_for_multi_select_survey_question(self):
        survey_item = self.create_mc_multi_select_survey_item()
        taken, offered = self.create_taken_for_item(self._bank.ident, Id(survey_item['id']))

        questions_url = '{0}/assessmentstaken/{1}/questions'.format(self.url,
                                                                    unquote(str(taken.ident)))

        req = self.app.get(questions_url)
        self.ok(req)
        data = self.json(req)

        question_id = data['data'][0]['id']

        url = '{0}/assessmentstaken/{1}/questions/{2}/submit'.format(self.url,
                                                                     unquote(str(taken.ident)),
                                                                     question_id)
        choice_ids = ['id5f1fc52a-a04e-4fa1-b855-51da24967a31',
                      'id31392307-c87e-476b-8f92-b0f12ed66300',
                      'id8188b5cd-89b0-4140-b12a-aed5426bd81b']
        for choice_id in choice_ids:
            payload = {
                'choiceIds': [choice_id],
                'type': 'answer-type%3Aqti-choice-interaction-multi-select-survey%40ODL.MIT.EDU'
            }
            req = self.app.post(url,
                                params=json.dumps(payload),
                                headers={'content-type': 'application/json'})
            self.ok(req)
            data = self.json(req)
            self.assertTrue(data['correct'])
            self.assertIn('Thank you for your participation.', data['feedback'])
            self.assertNotIn('Incorrect ...', data['feedback'])

    def test_all_answer_combos_correct_for_multi_select_survey_question(self):
        survey_item = self.create_mc_multi_select_survey_item()
        taken, offered = self.create_taken_for_item(self._bank.ident, Id(survey_item['id']))

        questions_url = '{0}/assessmentstaken/{1}/questions'.format(self.url,
                                                                    unquote(str(taken.ident)))

        req = self.app.get(questions_url)
        self.ok(req)
        data = self.json(req)

        question_id = data['data'][0]['id']

        url = '{0}/assessmentstaken/{1}/questions/{2}/submit'.format(self.url,
                                                                     unquote(str(taken.ident)),
                                                                     question_id)
        # choice_ids = ['id5f1fc52a-a04e-4fa1-b855-51da24967a31',
        #               'id31392307-c87e-476b-8f92-b0f12ed66300',
        #               'id8188b5cd-89b0-4140-b12a-aed5426bd81b']
        test_payloads = [['id5f1fc52a-a04e-4fa1-b855-51da24967a31',
                          'id31392307-c87e-476b-8f92-b0f12ed66300'],
                         ['id8188b5cd-89b0-4140-b12a-aed5426bd81b',
                          'id5f1fc52a-a04e-4fa1-b855-51da24967a31'],
                         ['id5f1fc52a-a04e-4fa1-b855-51da24967a31',
                          'id31392307-c87e-476b-8f92-b0f12ed66300',
                          'id8188b5cd-89b0-4140-b12a-aed5426bd81b']]
        for choice_payload in test_payloads:
            payload = {
                'choiceIds': choice_payload,
                'type': 'answer-type%3Aqti-choice-interaction-multi-select-survey%40ODL.MIT.EDU'
            }
            req = self.app.post(url,
                                params=json.dumps(payload),
                                headers={'content-type': 'application/json'})
            self.ok(req)
            data = self.json(req)
            self.assertTrue(data['correct'])
            self.assertIn('Thank you for your participation.', data['feedback'])
            self.assertNotIn('Incorrect ...', data['feedback'])

    def test_can_submit_right_answer_mw_fill_in_the_blank(self):
        mc_item = self.create_mw_fitb_item()
        taken, offered = self.create_taken_for_item(self._bank.ident, Id(mc_item['id']))
        question_id = self.get_question_id(taken)
        url = '{0}/assessmentstaken/{1}/questions/{2}/submit'.format(self.url,
                                                                     unquote(str(taken.ident)),
                                                                     question_id)
        payload = {
            'inlineRegions': {
                'RESPONSE_1': {
                    'choiceIds': ['[_1_1_1_1_1_1_1']
                },
                'RESPONSE_2': {
                    'choiceIds': ['[_1_1_1_1_1_1']
                }
            },
            'type': 'answer-type%3Aqti-inline-choice-interaction-mw-fill-in-the-blank%40ODL.MIT.EDU'
        }
        req = self.app.post(url,
                            params=json.dumps(payload),
                            headers={'content-type': 'application/json'})
        self.ok(req)
        data = self.json(req)
        self.assertTrue(data['correct'])
        self.assertIn('Yes, you are correct.', data['feedback'])
        self.assertIn('This is an image of a brown bunny.', data['feedback'])
        self.assertNotIn('No, please listen to the story again.', data['feedback'])
        self.assertNotIn('This is a drawing of a goldfish.', data['feedback'])

    def test_region_does_matter_mw_fill_in_the_blank(self):
        mc_item = self.create_mw_fitb_item()
        taken, offered = self.create_taken_for_item(self._bank.ident, Id(mc_item['id']))
        question_id = self.get_question_id(taken)
        url = '{0}/assessmentstaken/{1}/questions/{2}/submit'.format(self.url,
                                                                     unquote(str(taken.ident)),
                                                                     question_id)
        payload = {
            'inlineRegions': {
                'RESPONSE_1': {
                    'choiceIds': ['[_1_1_1_1_1_1']
                },
                'RESPONSE_2': {
                    'choiceIds': ['[_1_1_1_1_1_1_1']
                }
            },
            'type': 'answer-type%3Aqti-inline-choice-interaction-mw-fill-in-the-blank%40ODL.MIT.EDU'
        }
        req = self.app.post(url,
                            params=json.dumps(payload),
                            headers={'content-type': 'application/json'})
        self.ok(req)
        data = self.json(req)
        self.assertFalse(data['correct'])
        self.assertNotIn('Yes, you are correct.', data['feedback'])
        self.assertNotIn('This is an image of a brown bunny.', data['feedback'])
        self.assertIn('No, please listen to the story again.', data['feedback'])
        self.assertIn('This is a drawing of a goldfish.', data['feedback'])

    def test_can_submit_wrong_answer_mw_fill_in_the_blank(self):
        mc_item = self.create_mw_fitb_item()
        taken, offered = self.create_taken_for_item(self._bank.ident, Id(mc_item['id']))
        question_id = self.get_question_id(taken)
        url = '{0}/assessmentstaken/{1}/questions/{2}/submit'.format(self.url,
                                                                     unquote(str(taken.ident)),
                                                                     question_id)
        payload = {
            'inlineRegions': {
                'RESPONSE_1': {
                    'choiceIds': ['a']
                },
                'RESPONSE_2': {
                    'choiceIds': ['b']
                }
            },
            'type': 'answer-type%3Aqti-inline-choice-interaction-mw-fill-in-the-blank%40ODL.MIT.EDU'
        }
        req = self.app.post(url,
                            params=json.dumps(payload),
                            headers={'content-type': 'application/json'})
        self.ok(req)
        data = self.json(req)
        self.assertFalse(data['correct'])
        self.assertNotIn('Yes, you are correct.', data['feedback'])
        self.assertNotIn('This is an image of a brown bunny.', data['feedback'])
        self.assertIn('No, please listen to the story again.', data['feedback'])
        self.assertIn('This is a drawing of a goldfish.', data['feedback'])

    def test_cannot_submit_too_many_choices_even_if_partially_correct_mw_fill_in_the_blank(self):
        mc_item = self.create_mw_fitb_item()
        taken, offered = self.create_taken_for_item(self._bank.ident, Id(mc_item['id']))
        question_id = self.get_question_id(taken)
        url = '{0}/assessmentstaken/{1}/questions/{2}/submit'.format(self.url,
                                                                     unquote(str(taken.ident)),
                                                                     question_id)
        payload = {
            'inlineRegions': {
                'RESPONSE_1': {
                    'choiceIds': ['[_1_1_1_1_1_1_1', 'a']
                },
                'RESPONSE_2': {
                    'choiceIds': ['[_1_1_1_1_1_1']
                }
            },
            'type': 'answer-type%3Aqti-inline-choice-interaction-mw-fill-in-the-blank%40ODL.MIT.EDU'
        }
        req = self.app.post(url,
                            params=json.dumps(payload),
                            headers={'content-type': 'application/json'})
        self.ok(req)
        data = self.json(req)
        self.assertFalse(data['correct'])
        self.assertNotIn('Yes, you are correct.', data['feedback'])
        self.assertNotIn('This is an image of a brown bunny.', data['feedback'])
        self.assertIn('No, please listen to the story again.', data['feedback'])
        self.assertIn('This is a drawing of a goldfish.', data['feedback'])

    def test_submitting_too_few_answers_returns_incorrect_mw_fill_in_the_blank(self):
        mc_item = self.create_mw_fitb_item()
        taken, offered = self.create_taken_for_item(self._bank.ident, Id(mc_item['id']))
        question_id = self.get_question_id(taken)

        url = '{0}/assessmentstaken/{1}/questions/{2}/submit'.format(self.url,
                                                                     unquote(str(taken.ident)),
                                                                     question_id)
        payload = {
            'inlineRegions': {
                'RESPONSE_1': {
                    'choiceIds': ['[_1_1_1_1_1_1_1']
                },
                'RESPONSE_2': {
                    'choiceIds': []
                }
            },
            'type': 'answer-type%3Aqti-inline-choice-interaction-mw-fill-in-the-blank%40ODL.MIT.EDU'
        }
        req = self.app.post(url,
                            params=json.dumps(payload),
                            headers={'content-type': 'application/json'})
        self.ok(req)
        data = self.json(req)
        self.assertFalse(data['correct'])
        self.assertNotIn('Yes, you are correct.', data['feedback'])
        self.assertNotIn('This is an image of a brown bunny.', data['feedback'])
        self.assertIn('No, please listen to the story again.', data['feedback'])
        self.assertIn('This is a drawing of a goldfish.', data['feedback'])

    def test_can_submit_right_answer_drag_and_drop(self):
        mc_item = self.create_drag_and_drop_item()
        taken, offered = self.create_taken_for_item(self._bank.ident, Id(mc_item['id']))
        question_id = self.get_question_id(taken)
        url = '{0}/assessmentstaken/{1}/questions/{2}/submit'.format(self.url,
                                                                     unquote(str(taken.ident)),
                                                                     question_id)
        payload = {
            'choiceIds': ['id127df214-2a19-44da-894a-853948313dae',
                          'iddcbf40ab-782e-4d4f-9020-6b8414699a72',
                          'idb4f6cd03-cf58-4391-9ca2-44b7bded3d4b',
                          'ide576c9cc-d20e-4ba3-8881-716100b796a0'],
            'type': 'answer-type%3Aqti-order-interaction-object-manipulation%40ODL.MIT.EDU'
        }
        req = self.app.post(url,
                            params=json.dumps(payload),
                            headers={'content-type': 'application/json'})
        self.ok(req)
        data = self.json(req)
        self.assertTrue(data['correct'])
        self.assertIn('You are correct!', data['feedback'])
        self.assertNotIn('Please try again.', data['feedback'])

    def test_can_submit_wrong_answer_drag_and_drop(self):
        mc_item = self.create_drag_and_drop_item()
        taken, offered = self.create_taken_for_item(self._bank.ident, Id(mc_item['id']))

        question_id = self.get_question_id(taken)

        url = '{0}/assessmentstaken/{1}/questions/{2}/submit'.format(self.url,
                                                                     unquote(str(taken.ident)),
                                                                     question_id)
        payload = {
            'choiceIds': ['id127df214-2a19-44da-894a-853948313dae',
                          'idb4f6cd03-cf58-4391-9ca2-44b7bded3d4b',  # swapped the order
                          'iddcbf40ab-782e-4d4f-9020-6b8414699a72',  # swapped the order
                          'ide576c9cc-d20e-4ba3-8881-716100b796a0'],
            'type': 'answer-type%3Aqti-order-interaction-object-manipulation%40ODL.MIT.EDU'
        }
        req = self.app.post(url,
                            params=json.dumps(payload),
                            headers={'content-type': 'application/json'})
        self.ok(req)
        data = self.json(req)
        self.assertFalse(data['correct'])
        self.assertNotIn('You are correct!', data['feedback'])
        self.assertIn('Please try again.', data['feedback'])

    def test_cannot_submit_too_many_choices_even_if_partially_correct_drag_and_drop(self):
        mc_item = self.create_drag_and_drop_item()
        taken, offered = self.create_taken_for_item(self._bank.ident, Id(mc_item['id']))

        question_id = self.get_question_id(taken)

        url = '{0}/assessmentstaken/{1}/questions/{2}/submit'.format(self.url,
                                                                     unquote(str(taken.ident)),
                                                                     question_id)
        payload = {
            'choiceIds': ['id127df214-2a19-44da-894a-853948313dae',
                          'iddcbf40ab-782e-4d4f-9020-6b8414699a72',
                          'idb4f6cd03-cf58-4391-9ca2-44b7bded3d4b',
                          'ide576c9cc-d20e-4ba3-8881-716100b796a0',
                          'a'],
            'type': 'answer-type%3Aqti-order-interaction-object-manipulation%40ODL.MIT.EDU'
        }
        req = self.app.post(url,
                            params=json.dumps(payload),
                            headers={'content-type': 'application/json'})
        self.ok(req)
        data = self.json(req)
        self.assertFalse(data['correct'])
        self.assertNotIn('You are correct!', data['feedback'])
        self.assertIn('Please try again.', data['feedback'])

    def test_submitting_too_few_answers_returns_incorrect_drag_and_drop(self):
        mc_item = self.create_drag_and_drop_item()
        taken, offered = self.create_taken_for_item(self._bank.ident, Id(mc_item['id']))

        url = '{0}/assessmentstaken/{1}/questions'.format(self.url,
                                                          unquote(str(taken.ident)))
        req = self.app.get(url)
        self.ok(req)
        data = self.json(req)
        question_id = data['data'][0]['id']

        url = '{0}/assessmentstaken/{1}/questions/{2}/submit'.format(self.url,
                                                                     unquote(str(taken.ident)),
                                                                     question_id)
        payload = {
            'choiceIds': ['a',
                          'b'],
            'type': 'answer-type%3Aqti-order-interaction-object-manipulation%40ODL.MIT.EDU'
        }
        req = self.app.post(url,
                            params=json.dumps(payload),
                            headers={'content-type': 'application/json'})
        self.ok(req)
        data = self.json(req)
        self.assertFalse(data['correct'])
        self.assertNotIn('You are correct!', data['feedback'])
        self.assertIn('Please try again.', data['feedback'])

    def test_images_in_correct_feedback_are_converted_to_urls(self):
        mc_item = self.create_question_with_images_in_feedback()
        expected_content_id = mc_item['answers'][0]['fileIds']['medium849946232588888784replacement_image_png']['assetContentId']
        taken, offered = self.create_taken_for_item(self._bank.ident, Id(mc_item['id']))

        questions_url = '{0}/assessmentstaken/{1}/questions'.format(self.url,
                                                                    unquote(str(taken.ident)))

        req = self.app.get(questions_url)
        self.ok(req)
        data = self.json(req)

        question_id = data['data'][0]['id']

        url = '{0}/assessmentstaken/{1}/questions/{2}/submit'.format(self.url,
                                                                     unquote(str(taken.ident)),
                                                                     question_id)
        payload = {
            'choiceIds': ['ida31f7834-716c-4f0d-96ec-d8d0ccc7a5ec'],
            'type': 'answer-type%3Aqti-choice-interaction%40ODL.MIT.EDU'
        }
        req = self.app.post(url,
                            params=json.dumps(payload),
                            headers={'content-type': 'application/json'})
        self.ok(req)
        data = self.json(req)
        self.assertTrue(data['correct'])
        self.assertIn('You did it!', data['feedback'])
        self.assertIn('', data['feedback'])
        self.assertIn(expected_content_id, data['feedback'])
        self.assertNotIn('Sorry, bad choice', data['feedback'])

    def test_images_in_incorrect_feedback_are_converted_to_urls(self):
        mc_item = self.create_question_with_images_in_feedback()

        wrong_choice_id = 'id49eb6d09-8c34-4e5d-8e31-77604208f872'

        matching_wrong_choice = [a for a in mc_item['answers'] if a['choiceIds'][0] == wrong_choice_id][0]
        expected_content_id = matching_wrong_choice['fileIds']['medium534315617922181373draggable_red_dot_png']['assetContentId']
        taken, offered = self.create_taken_for_item(self._bank.ident, Id(mc_item['id']))

        questions_url = '{0}/assessmentstaken/{1}/questions'.format(self.url,
                                                                    unquote(str(taken.ident)))

        req = self.app.get(questions_url)
        self.ok(req)
        data = self.json(req)
        question_id = data['data'][0]['id']

        url = '{0}/assessmentstaken/{1}/questions/{2}/submit'.format(self.url,
                                                                     unquote(str(taken.ident)),
                                                                     question_id)
        payload = {
            'choiceIds': [wrong_choice_id],
            'type': 'answer-type%3Aqti-choice-interaction%40ODL.MIT.EDU'
        }
        req = self.app.post(url,
                            params=json.dumps(payload),
                            headers={'content-type': 'application/json'})
        self.ok(req)
        data = self.json(req)
        self.assertFalse(data['correct'])
        self.assertNotIn('You did it!', data['feedback'])
        self.assertIn('', data['feedback'])
        self.assertIn(expected_content_id, data['feedback'])
        self.assertIn('Sorry, bad choice', data['feedback'])

    def test_mc_choices_are_shuffled_if_flag_set(self):
        survey_item = self.create_mc_survey_item()
        taken, offered = self.create_taken_for_item(self._bank.ident, Id(survey_item['id']))

        questions_url = '{0}/assessmentstaken/{1}/questions'.format(self.url,
                                                                    unquote(str(taken.ident)))

        req = self.app.get(questions_url)
        self.ok(req)
        data = self.json(req)
        original_order = data['data'][0]['choices']

        different_order_count = 0
        taken_map = taken.object_map
        for i in range(0, 10):
            delete_taken_url = '{0}/assessmentstaken/{1}'.format(self.url,
                                                                 taken_map['id'])
            req = self.app.delete(delete_taken_url)
            self.ok(req)
            data = self.json(req)
            self.assertTrue(data['success'])
            create_taken_url = '{0}/assessmentsoffered/{1}/assessmentstaken'.format(self.url,
                                                                                    unquote(str(offered.ident)))
            req = self.app.post(create_taken_url)
            self.ok(req)
            taken_map = self.json(req)
            questions_url = '{0}/assessmentstaken/{1}/questions'.format(self.url,
                                                                        taken_map['id'])
            req = self.app.get(questions_url)
            self.ok(req)
            data = self.json(req)
            if original_order != data['data'][0]['choices']:
                different_order_count += 1

        self.assertTrue(different_order_count > 0)

    def test_mc_choices_are_not_shuffled_if_flag_not_set(self):
        unshuffled_item = self.create_unshuffled_mc_item()
        taken, offered = self.create_taken_for_item(self._bank.ident, Id(unshuffled_item['id']))

        questions_url = '{0}/assessmentstaken/{1}/questions'.format(self.url,
                                                                    unquote(str(taken.ident)))

        req = self.app.get(questions_url)
        self.ok(req)
        data = self.json(req)
        original_order = data['data'][0]['choices']

        same_order_count = 0
        taken_map = taken.object_map
        for i in range(0, 10):
            delete_taken_url = '{0}/assessmentstaken/{1}'.format(self.url,
                                                                 taken_map['id'])
            req = self.app.delete(delete_taken_url)
            self.ok(req)
            data = self.json(req)
            self.assertTrue(data['success'])
            create_taken_url = '{0}/assessmentsoffered/{1}/assessmentstaken'.format(self.url,
                                                                                    unquote(str(offered.ident)))
            req = self.app.post(create_taken_url)
            self.ok(req)
            taken_map = self.json(req)
            questions_url = '{0}/assessmentstaken/{1}/questions'.format(self.url,
                                                                        taken_map['id'])
            req = self.app.get(questions_url)
            self.ok(req)
            data = self.json(req)
            if original_order == data['data'][0]['choices']:
                same_order_count += 1

        # they should all be equal
        self.assertTrue(same_order_count == 10)

    def test_order_interaction_choices_are_not_shuffled_if_flag_not_set(self):
        unshuffled_item = self.create_unshuffled_order_interaction_item()
        taken, offered = self.create_taken_for_item(self._bank.ident, Id(unshuffled_item['id']))

        questions_url = '{0}/assessmentstaken/{1}/questions'.format(self.url,
                                                                    unquote(str(taken.ident)))

        req = self.app.get(questions_url)
        self.ok(req)
        data = self.json(req)
        original_order = data['data'][0]['choices']

        same_order_count = 0
        taken_map = taken.object_map
        for i in range(0, 10):
            delete_taken_url = '{0}/assessmentstaken/{1}'.format(self.url,
                                                                 taken_map['id'])
            req = self.app.delete(delete_taken_url)
            self.ok(req)
            data = self.json(req)
            self.assertTrue(data['success'])
            create_taken_url = '{0}/assessmentsoffered/{1}/assessmentstaken'.format(self.url,
                                                                                    unquote(str(offered.ident)))
            req = self.app.post(create_taken_url)
            self.ok(req)
            taken_map = self.json(req)
            questions_url = '{0}/assessmentstaken/{1}/questions'.format(self.url,
                                                                        taken_map['id'])
            req = self.app.get(questions_url)
            self.ok(req)
            data = self.json(req)
            if original_order == data['data'][0]['choices']:
                same_order_count += 1

        # they should all be equal
        self.assertTrue(same_order_count == 10)

    def test_order_interaction_choices_are_shuffled_if_flag_set(self):
        mw_item = self.create_mw_sentence_item()
        taken, offered = self.create_taken_for_item(self._bank.ident, Id(mw_item['id']))

        questions_url = '{0}/assessmentstaken/{1}/questions'.format(self.url,
                                                                    unquote(str(taken.ident)))

        req = self.app.get(questions_url)
        self.ok(req)
        data = self.json(req)
        original_order = data['data'][0]['choices']

        different_order_count = 0
        taken_map = taken.object_map
        for i in range(0, 10):
            delete_taken_url = '{0}/assessmentstaken/{1}'.format(self.url,
                                                                 taken_map['id'])
            req = self.app.delete(delete_taken_url)
            self.ok(req)
            data = self.json(req)
            self.assertTrue(data['success'])
            create_taken_url = '{0}/assessmentsoffered/{1}/assessmentstaken'.format(self.url,
                                                                                    unquote(str(offered.ident)))
            req = self.app.post(create_taken_url)
            self.ok(req)
            taken_map = self.json(req)
            questions_url = '{0}/assessmentstaken/{1}/questions'.format(self.url,
                                                                        taken_map['id'])
            req = self.app.get(questions_url)
            self.ok(req)
            data = self.json(req)
            if original_order != data['data'][0]['choices']:
                different_order_count += 1

        self.assertTrue(different_order_count > 0)

    def test_inline_choice_interaction_shuffled_if_flag_set(self):
        mw_item = self.create_mw_fitb_item()
        taken, offered = self.create_taken_for_item(self._bank.ident, Id(mw_item['id']))

        questions_url = '{0}/assessmentstaken/{1}/questions'.format(self.url,
                                                                    unquote(str(taken.ident)))

        req = self.app.get(questions_url)
        self.ok(req)
        data = self.json(req)
        original_order = data['data'][0]['choices']

        different_order_count = 0
        taken_map = taken.object_map
        for i in range(0, 10):
            delete_taken_url = '{0}/assessmentstaken/{1}'.format(self.url,
                                                                 taken_map['id'])
            req = self.app.delete(delete_taken_url)
            self.ok(req)
            data = self.json(req)
            self.assertTrue(data['success'])
            create_taken_url = '{0}/assessmentsoffered/{1}/assessmentstaken'.format(self.url,
                                                                                    unquote(str(offered.ident)))
            req = self.app.post(create_taken_url)
            self.ok(req)
            taken_map = self.json(req)
            questions_url = '{0}/assessmentstaken/{1}/questions'.format(self.url,
                                                                        taken_map['id'])
            req = self.app.get(questions_url)
            self.ok(req)
            data = self.json(req)
            if original_order != data['data'][0]['choices']:
                different_order_count += 1

        self.assertTrue(different_order_count > 0)

    def test_inline_choice_interaction_not_shuffled_if_flag_not_set(self):
        unshuffled_item = self.create_unshuffled_fitb_item()
        taken, offered = self.create_taken_for_item(self._bank.ident, Id(unshuffled_item['id']))

        questions_url = '{0}/assessmentstaken/{1}/questions'.format(self.url,
                                                                    unquote(str(taken.ident)))

        req = self.app.get(questions_url)
        self.ok(req)
        data = self.json(req)
        original_order = data['data'][0]['choices']

        same_order_count = 0
        taken_map = taken.object_map
        for i in range(0, 10):
            delete_taken_url = '{0}/assessmentstaken/{1}'.format(self.url,
                                                                 taken_map['id'])
            req = self.app.delete(delete_taken_url)
            self.ok(req)
            data = self.json(req)
            self.assertTrue(data['success'])
            create_taken_url = '{0}/assessmentsoffered/{1}/assessmentstaken'.format(self.url,
                                                                                    unquote(str(offered.ident)))
            req = self.app.post(create_taken_url)
            self.ok(req)
            taken_map = self.json(req)
            questions_url = '{0}/assessmentstaken/{1}/questions'.format(self.url,
                                                                        taken_map['id'])
            req = self.app.get(questions_url)
            self.ok(req)
            data = self.json(req)
            if original_order == data['data'][0]['choices']:
                same_order_count += 1

        # they should all be equal
        self.assertTrue(same_order_count == 10)

    def test_can_add_answer_feedback_on_item_update_for_fitb(self):
        item = self.create_mw_fitb_item()
        wrong_answer_choice_id = '[_3_1_1_1_1_1_1'
        payload = {
            'answers': [{
                'genus': str(WRONG_ANSWER_GENUS),
                'type': ["answer-record-type%3Aqti%40ODL.MIT.EDU",
                         "answer-record-type%3Ainline-choice-answer%40ODL.MIT.EDU"],
                'choiceIds': [wrong_answer_choice_id],
                'region': 'RESPONSE_1',
                'feedback': 'New feedback!!'
            }]
        }
        url = '{0}/items/{1}'.format(self.url,
                                     item['id'])
        req = self.app.put(url,
                           params=json.dumps(payload),
                           headers={'content-type': 'application/json'})
        self.ok(req)

        # now let's make sure it got added correctly
        req = self.app.get(url)
        self.ok(req)
        data = self.json(req)
        self.assertEqual(len(data['answers']), 3)
        self.assertIn('New feedback!!', data['answers'][2]['feedbacks'][0]['text'])
        self.assertEqual(data['answers'][2]['inlineRegions']['RESPONSE_1']['choiceIds'],
                         payload['answers'][0]['choiceIds'])
        self.assertEqual(data['answers'][2]['genusTypeId'],
                         str(WRONG_ANSWER_GENUS))

    def test_can_remove_choice_mc(self):
        mc_item = self.create_mc_multi_select_item()
        url = '{0}/items/{1}'.format(self.url,
                                     mc_item['id'])
        self.assertEqual(len(mc_item['question']['choices']), 5)
        choice_id_to_delete = mc_item['question']['choices'][0]['id']
        payload = {
            'question': {
                'choices': [{
                    'id': choice_id_to_delete,
                    'delete': True
                }]
            }
        }
        req = self.app.put(url,
                           params=json.dumps(payload),
                           headers={'content-type': 'application/json'})
        self.ok(req)

        req = self.app.get(url)
        self.ok(req)
        data = self.json(req)

        self.assertEqual(len(data['question']['choices']), 4)
        current_choice_ids = [c['id'] for c in data['question']['choices']]
        self.assertNotIn(choice_id_to_delete, current_choice_ids)

    def test_can_reorder_choices_mc(self):
        mc_item = self.create_mc_multi_select_item()
        url = '{0}/items/{1}'.format(self.url,
                                     mc_item['id'])
        self.assertEqual(len(mc_item['question']['choices']), 5)
        new_choice_order = mc_item['question']['choices'][0::]

        for index, choice in enumerate(new_choice_order):
            choice['order'] = index

        new_choice_order[0]['order'] = len(new_choice_order) + 1

        payload = {
            'question': {
                'choices': new_choice_order,
                'shuffle': False
            }
        }
        req = self.app.put(url,
                           params=json.dumps(payload),
                           headers={'content-type': 'application/json'})
        self.ok(req)

        req = self.app.get(url)
        self.ok(req)
        data = self.json(req)

        self.assertEqual(len(data['question']['choices']), 5)
        current_choice_ids = [c['id'] for c in data['question']['choices']]
        sorted_desired_choices = sorted(new_choice_order, key=lambda k: k['order'])
        desired_choice_ids = [c['id'] for c in sorted_desired_choices]
        self.assertEqual(current_choice_ids, desired_choice_ids)

    def test_can_reorder_and_add_new_choice_mc(self):
        mc_item = self.create_mc_multi_select_item()
        url = '{0}/items/{1}'.format(self.url,
                                     mc_item['id'])
        self.assertEqual(len(mc_item['question']['choices']), 5)
        new_choice_order = mc_item['question']['choices'][1::]
        new_choice_order.append({'text': 'new choice!'})
        new_choice_order.append(mc_item['question']['choices'][0])

        for index, choice in enumerate(new_choice_order):
            choice['order'] = index

        payload = {
            'question': {
                'choices': new_choice_order,
                'shuffle': False
            }
        }
        req = self.app.put(url,
                           params=json.dumps(payload),
                           headers={'content-type': 'application/json'})
        self.ok(req)

        req = self.app.get(url)
        self.ok(req)
        data = self.json(req)

        self.assertEqual(len(data['question']['choices']), 6)
        current_choice_texts = [c['text'] for c in data['question']['choices']]
        desired_choice_texts = [c['text'] for c in new_choice_order]
        self.assertEqual(current_choice_texts, desired_choice_texts)

    def test_can_reorder_and_delete_choice_mc(self):
        mc_item = self.create_mc_multi_select_item()
        url = '{0}/items/{1}'.format(self.url,
                                     mc_item['id'])
        self.assertEqual(len(mc_item['question']['choices']), 5)
        new_choice_order = mc_item['question']['choices'][1::]
        new_choice_order.append(mc_item['question']['choices'][0])

        new_choice_order[3]['delete'] = True

        for index, choice in enumerate(new_choice_order):
            choice['order'] = index
        payload = {
            'question': {
                'choices': new_choice_order,
                'shuffle': False
            }
        }
        req = self.app.put(url,
                           params=json.dumps(payload),
                           headers={'content-type': 'application/json'})
        self.ok(req)

        req = self.app.get(url)
        self.ok(req)
        data = self.json(req)

        self.assertEqual(len(data['question']['choices']), 4)
        current_choice_texts = [c['text'] for c in data['question']['choices']]
        desired_choice_texts = [c['text'] for c in new_choice_order if 'delete' not in c]
        self.assertEqual(current_choice_texts, desired_choice_texts)

    def test_can_reorder_and_add_and_delete_choice_mc(self):
        mc_item = self.create_mc_multi_select_item()
        url = '{0}/items/{1}'.format(self.url,
                                     mc_item['id'])
        self.assertEqual(len(mc_item['question']['choices']), 5)
        new_choice_order = mc_item['question']['choices'][1::]
        new_choice_order.append({'text': 'new choice!'})
        new_choice_order.append(mc_item['question']['choices'][0])

        new_choice_order[3]['delete'] = True

        for index, choice in enumerate(new_choice_order):
            choice['order'] = index
        payload = {
            'question': {
                'choices': new_choice_order,
                'shuffle': False
            }
        }
        req = self.app.put(url,
                           params=json.dumps(payload),
                           headers={'content-type': 'application/json'})
        self.ok(req)

        req = self.app.get(url)
        self.ok(req)
        data = self.json(req)

        self.assertEqual(len(data['question']['choices']), 5)
        current_choice_texts = [c['text'] for c in data['question']['choices']]
        desired_choice_texts = [c['text'] for c in new_choice_order if 'delete' not in c]
        self.assertEqual(current_choice_texts, desired_choice_texts)

    def test_can_remove_choice_survey(self):
        mc_item = self.create_mc_survey_item()
        url = '{0}/items/{1}'.format(self.url,
                                     mc_item['id'])
        self.assertEqual(len(mc_item['question']['choices']), 3)
        choice_id_to_delete = mc_item['question']['choices'][0]['id']
        payload = {
            'question': {
                'choices': [{
                    'id': choice_id_to_delete,
                    'delete': True
                }]
            }
        }
        req = self.app.put(url,
                           params=json.dumps(payload),
                           headers={'content-type': 'application/json'})
        self.ok(req)

        req = self.app.get(url)
        self.ok(req)
        data = self.json(req)

        self.assertEqual(len(data['question']['choices']), 2)
        current_choice_ids = [c['id'] for c in data['question']['choices']]
        self.assertNotIn(choice_id_to_delete, current_choice_ids)

    def test_can_reorder_choices_survey(self):
        mc_item = self.create_mc_survey_item()
        url = '{0}/items/{1}'.format(self.url,
                                     mc_item['id'])
        self.assertEqual(len(mc_item['question']['choices']), 3)
        new_choice_order = mc_item['question']['choices'][0::]

        for index, choice in enumerate(new_choice_order):
            choice['order'] = index

        new_choice_order[0]['order'] = len(new_choice_order) + 1

        payload = {
            'question': {
                'choices': new_choice_order,
                'shuffle': False
            }
        }
        req = self.app.put(url,
                           params=json.dumps(payload),
                           headers={'content-type': 'application/json'})
        self.ok(req)

        req = self.app.get(url)
        self.ok(req)
        data = self.json(req)

        self.assertEqual(len(data['question']['choices']), 3)
        current_choice_ids = [c['id'] for c in data['question']['choices']]
        sorted_desired_choices = sorted(new_choice_order, key=lambda k: k['order'])
        desired_choice_ids = [c['id'] for c in sorted_desired_choices]
        self.assertEqual(current_choice_ids, desired_choice_ids)

    def test_can_reorder_and_add_new_choices_survey(self):
        mc_item = self.create_mc_survey_item()
        url = '{0}/items/{1}'.format(self.url,
                                     mc_item['id'])
        self.assertEqual(len(mc_item['question']['choices']), 3)
        new_choice_order = mc_item['question']['choices'][1::]
        new_choice_order.append({'text': 'new choice!'})
        new_choice_order.append(mc_item['question']['choices'][0])

        for index, choice in enumerate(new_choice_order):
            choice['order'] = index

        payload = {
            'question': {
                'choices': new_choice_order,
                'shuffle': False
            }
        }
        req = self.app.put(url,
                           params=json.dumps(payload),
                           headers={'content-type': 'application/json'})
        self.ok(req)

        req = self.app.get(url)
        self.ok(req)
        data = self.json(req)

        self.assertEqual(len(data['question']['choices']), 4)
        current_choice_texts = [c['text'] for c in data['question']['choices']]
        desired_choice_texts = [c['text'] for c in new_choice_order]
        self.assertEqual(current_choice_texts, desired_choice_texts)

    def test_can_reorder_and_delete_choices_survey(self):
        mc_item = self.create_mc_survey_item()
        url = '{0}/items/{1}'.format(self.url,
                                     mc_item['id'])
        self.assertEqual(len(mc_item['question']['choices']), 3)
        new_choice_order = mc_item['question']['choices'][1::]
        new_choice_order.append(mc_item['question']['choices'][0])

        new_choice_order[1]['delete'] = True

        for index, choice in enumerate(new_choice_order):
            choice['order'] = index

        payload = {
            'question': {
                'choices': new_choice_order,
                'shuffle': False
            }
        }
        req = self.app.put(url,
                           params=json.dumps(payload),
                           headers={'content-type': 'application/json'})
        self.ok(req)

        req = self.app.get(url)
        self.ok(req)
        data = self.json(req)

        self.assertEqual(len(data['question']['choices']), 2)
        current_choice_texts = [c['text'] for c in data['question']['choices']]
        desired_choice_texts = [c['text'] for c in new_choice_order if 'delete' not in c]
        self.assertEqual(current_choice_texts, desired_choice_texts)

    def test_can_reorder_and_add_and_delete_choices_survey(self):
        mc_item = self.create_mc_survey_item()
        url = '{0}/items/{1}'.format(self.url,
                                     mc_item['id'])
        self.assertEqual(len(mc_item['question']['choices']), 3)
        new_choice_order = mc_item['question']['choices'][1::]
        new_choice_order.append({'text': 'new choice!'})
        new_choice_order.append(mc_item['question']['choices'][0])

        new_choice_order[1]['delete'] = True

        for index, choice in enumerate(new_choice_order):
            choice['order'] = index

        payload = {
            'question': {
                'choices': new_choice_order,
                'shuffle': False
            }
        }
        req = self.app.put(url,
                           params=json.dumps(payload),
                           headers={'content-type': 'application/json'})
        self.ok(req)

        req = self.app.get(url)
        self.ok(req)
        data = self.json(req)

        self.assertEqual(len(data['question']['choices']), 3)
        current_choice_texts = [c['text'] for c in data['question']['choices']]
        desired_choice_texts = [c['text'] for c in new_choice_order if 'delete' not in c]
        self.assertEqual(current_choice_texts, desired_choice_texts)

    def test_can_remove_choice_mw_sentence(self):
        mc_item = self.create_mw_sentence_item()
        url = '{0}/items/{1}'.format(self.url,
                                     mc_item['id'])
        self.assertEqual(len(mc_item['question']['choices']), 7)
        choice_id_to_delete = mc_item['question']['choices'][0]['id']
        payload = {
            'question': {
                'choices': [{
                    'id': choice_id_to_delete,
                    'delete': True
                }]
            }
        }
        req = self.app.put(url,
                           params=json.dumps(payload),
                           headers={'content-type': 'application/json'})
        self.ok(req)

        req = self.app.get(url)
        self.ok(req)
        data = self.json(req)

        self.assertEqual(len(data['question']['choices']), 6)
        current_choice_ids = [c['id'] for c in data['question']['choices']]
        self.assertNotIn(choice_id_to_delete, current_choice_ids)

    def test_can_reorder_choices_mw_sentence(self):
        mc_item = self.create_mw_sentence_item()
        url = '{0}/items/{1}'.format(self.url,
                                     mc_item['id'])
        self.assertEqual(len(mc_item['question']['choices']), 7)
        new_choice_order = mc_item['question']['choices'][0::]

        for index, choice in enumerate(new_choice_order):
            choice['order'] = index

        new_choice_order[0]['order'] = len(new_choice_order) + 1

        payload = {
            'question': {
                'choices': new_choice_order,
                'shuffle': False
            }
        }
        req = self.app.put(url,
                           params=json.dumps(payload),
                           headers={'content-type': 'application/json'})
        self.ok(req)

        req = self.app.get(url)
        self.ok(req)
        data = self.json(req)

        self.assertEqual(len(data['question']['choices']), 7)
        current_choice_ids = [c['id'] for c in data['question']['choices']]
        sorted_desired_choices = sorted(new_choice_order, key=lambda k: k['order'])
        desired_choice_ids = [c['id'] for c in sorted_desired_choices]
        self.assertEqual(current_choice_ids, desired_choice_ids)

    def test_can_reorder_and_add_new_choices_mw_sentence(self):
        mc_item = self.create_mw_sentence_item()
        url = '{0}/items/{1}'.format(self.url,
                                     mc_item['id'])
        self.assertEqual(len(mc_item['question']['choices']), 7)
        new_choice_order = mc_item['question']['choices'][1::]
        new_choice_order.append({'text': 'new choice!'})
        new_choice_order.append(mc_item['question']['choices'][0])

        for index, choice in enumerate(new_choice_order):
            choice['order'] = index

        payload = {
            'question': {
                'choices': new_choice_order,
                'shuffle': False
            }
        }
        req = self.app.put(url,
                           params=json.dumps(payload),
                           headers={'content-type': 'application/json'})
        self.ok(req)

        req = self.app.get(url)
        self.ok(req)
        data = self.json(req)

        self.assertEqual(len(data['question']['choices']), 8)
        current_choice_texts = [c['text'] for c in data['question']['choices']]
        desired_choice_texts = [c['text'] for c in new_choice_order]
        self.assertEqual(current_choice_texts, desired_choice_texts)

    def test_can_reorder_and_delete_choices_mw_sentence(self):
        mc_item = self.create_mw_sentence_item()
        url = '{0}/items/{1}'.format(self.url,
                                     mc_item['id'])
        self.assertEqual(len(mc_item['question']['choices']), 7)
        new_choice_order = mc_item['question']['choices'][1::]
        new_choice_order.append(mc_item['question']['choices'][0])

        new_choice_order[3]['delete'] = True

        for index, choice in enumerate(new_choice_order):
            choice['order'] = index

        payload = {
            'question': {
                'choices': new_choice_order,
                'shuffle': False
            }
        }
        req = self.app.put(url,
                           params=json.dumps(payload),
                           headers={'content-type': 'application/json'})
        self.ok(req)

        req = self.app.get(url)
        self.ok(req)
        data = self.json(req)

        self.assertEqual(len(data['question']['choices']), 6)
        current_choice_texts = [c['text'] for c in data['question']['choices']]
        desired_choice_texts = [c['text'] for c in new_choice_order if 'delete' not in c]
        self.assertEqual(current_choice_texts, desired_choice_texts)

    def test_can_reorder_and_add_and_delete_choices_mw_sentence(self):
        mc_item = self.create_mw_sentence_item()
        url = '{0}/items/{1}'.format(self.url,
                                     mc_item['id'])
        self.assertEqual(len(mc_item['question']['choices']), 7)
        new_choice_order = mc_item['question']['choices'][1::]
        new_choice_order.append({'text': 'new choice!'})
        new_choice_order.append(mc_item['question']['choices'][0])

        new_choice_order[3]['delete'] = True

        for index, choice in enumerate(new_choice_order):
            choice['order'] = index

        payload = {
            'question': {
                'choices': new_choice_order,
                'shuffle': False
            }
        }
        req = self.app.put(url,
                           params=json.dumps(payload),
                           headers={'content-type': 'application/json'})
        self.ok(req)

        req = self.app.get(url)
        self.ok(req)
        data = self.json(req)

        self.assertEqual(len(data['question']['choices']), 7)
        current_choice_texts = [c['text'] for c in data['question']['choices']]
        desired_choice_texts = [c['text'] for c in new_choice_order if 'delete' not in c]
        self.assertEqual(current_choice_texts, desired_choice_texts)

    def test_can_remove_choice_image_sequence(self):
        mc_item = self.create_mw_sentence_item()
        url = '{0}/items/{1}'.format(self.url,
                                     mc_item['id'])
        self.assertEqual(len(mc_item['question']['choices']), 7)
        choice_id_to_delete = mc_item['question']['choices'][0]['id']
        payload = {
            'question': {
                'choices': [{
                    'id': choice_id_to_delete,
                    'delete': True
                }]
            }
        }
        req = self.app.put(url,
                           params=json.dumps(payload),
                           headers={'content-type': 'application/json'})
        self.ok(req)

        req = self.app.get(url)
        self.ok(req)
        data = self.json(req)

        self.assertEqual(len(data['question']['choices']), 6)
        current_choice_ids = [c['id'] for c in data['question']['choices']]
        self.assertNotIn(choice_id_to_delete, current_choice_ids)

    def test_can_reorder_choices_image_sequence(self):
        mc_item = self.create_mw_sentence_item()
        url = '{0}/items/{1}'.format(self.url,
                                     mc_item['id'])
        self.assertEqual(len(mc_item['question']['choices']), 7)
        new_choice_order = mc_item['question']['choices'][0::]

        for index, choice in enumerate(new_choice_order):
            choice['order'] = index

        new_choice_order[0]['order'] = len(new_choice_order) + 1

        payload = {
            'question': {
                'choices': new_choice_order,
                'shuffle': False
            }
        }
        req = self.app.put(url,
                           params=json.dumps(payload),
                           headers={'content-type': 'application/json'})
        self.ok(req)

        req = self.app.get(url)
        self.ok(req)
        data = self.json(req)

        self.assertEqual(len(data['question']['choices']), 7)
        current_choice_ids = [c['id'] for c in data['question']['choices']]
        sorted_desired_choices = sorted(new_choice_order, key=lambda k: k['order'])
        desired_choice_ids = [c['id'] for c in sorted_desired_choices]
        self.assertEqual(current_choice_ids, desired_choice_ids)

    def test_can_reorder_and_add_new_choices_image_sequence(self):
        mc_item = self.create_mw_sentence_item()
        url = '{0}/items/{1}'.format(self.url,
                                     mc_item['id'])
        self.assertEqual(len(mc_item['question']['choices']), 7)
        new_choice_order = mc_item['question']['choices'][1::]
        new_choice_order.append({'text': 'new choice!'})
        new_choice_order.append(mc_item['question']['choices'][0])

        for index, choice in enumerate(new_choice_order):
            choice['order'] = index

        payload = {
            'question': {
                'choices': new_choice_order,
                'shuffle': False
            }
        }
        req = self.app.put(url,
                           params=json.dumps(payload),
                           headers={'content-type': 'application/json'})
        self.ok(req)

        req = self.app.get(url)
        self.ok(req)
        data = self.json(req)

        self.assertEqual(len(data['question']['choices']), 8)
        current_choice_texts = [c['text'] for c in data['question']['choices']]
        desired_choice_texts = [c['text'] for c in new_choice_order]
        self.assertEqual(current_choice_texts, desired_choice_texts)

    def test_can_reorder_and_delete_choices_image_sequence(self):
        mc_item = self.create_mw_sentence_item()
        url = '{0}/items/{1}'.format(self.url,
                                     mc_item['id'])
        self.assertEqual(len(mc_item['question']['choices']), 7)
        new_choice_order = mc_item['question']['choices'][1::]
        new_choice_order.append(mc_item['question']['choices'][0])

        new_choice_order[3]['delete'] = True

        for index, choice in enumerate(new_choice_order):
            choice['order'] = index

        payload = {
            'question': {
                'choices': new_choice_order,
                'shuffle': False
            }
        }
        req = self.app.put(url,
                           params=json.dumps(payload),
                           headers={'content-type': 'application/json'})
        self.ok(req)

        req = self.app.get(url)
        self.ok(req)
        data = self.json(req)

        self.assertEqual(len(data['question']['choices']), 6)
        current_choice_texts = [c['text'] for c in data['question']['choices']]
        desired_choice_texts = [c['text'] for c in new_choice_order if 'delete' not in c]
        self.assertEqual(current_choice_texts, desired_choice_texts)

    def test_can_reorder_and_add_and_delete_choices_image_sequence(self):
        mc_item = self.create_mw_sentence_item()
        url = '{0}/items/{1}'.format(self.url,
                                     mc_item['id'])
        self.assertEqual(len(mc_item['question']['choices']), 7)
        new_choice_order = mc_item['question']['choices'][1::]
        new_choice_order.append({'text': 'new choice!'})
        new_choice_order.append(mc_item['question']['choices'][0])

        new_choice_order[3]['delete'] = True

        for index, choice in enumerate(new_choice_order):
            choice['order'] = index

        payload = {
            'question': {
                'choices': new_choice_order,
                'shuffle': False
            }
        }
        req = self.app.put(url,
                           params=json.dumps(payload),
                           headers={'content-type': 'application/json'})
        self.ok(req)

        req = self.app.get(url)
        self.ok(req)
        data = self.json(req)

        self.assertEqual(len(data['question']['choices']), 7)
        current_choice_texts = [c['text'] for c in data['question']['choices']]
        desired_choice_texts = [c['text'] for c in new_choice_order if 'delete' not in c]
        self.assertEqual(current_choice_texts, desired_choice_texts)

    def test_can_remove_choice_mw_fitb(self):
        mc_item = self.create_mw_fitb_item()
        url = '{0}/items/{1}'.format(self.url,
                                     mc_item['id'])
        self.assertEqual(len(mc_item['question']['choices']), 2)
        region = mc_item['question']['choices'].keys()[0]
        self.assertEqual(len(mc_item['question']['choices'][region]), 4)
        choice_id_to_delete = mc_item['question']['choices'][region][0]['id']
        payload = {
            'question': {
                'inlineRegions': {
                    region: {
                        'choices': [{
                            'id': choice_id_to_delete,
                            'delete': True
                        }]
                    }
                }
            }
        }
        req = self.app.put(url,
                           params=json.dumps(payload),
                           headers={'content-type': 'application/json'})
        self.ok(req)

        req = self.app.get(url)
        self.ok(req)
        data = self.json(req)

        self.assertEqual(len(data['question']['choices'][region]), 3)
        current_choice_ids = [c['id'] for c in data['question']['choices'][region]]
        self.assertNotIn(choice_id_to_delete, current_choice_ids)

    def test_can_reorder_choices_mw_fitb(self):
        mc_item = self.create_mw_fitb_item()
        url = '{0}/items/{1}'.format(self.url,
                                     mc_item['id'])
        self.assertEqual(len(mc_item['question']['choices']), 2)
        region = mc_item['question']['choices'].keys()[0]
        self.assertEqual(len(mc_item['question']['choices'][region]), 4)
        new_choice_order = mc_item['question']['choices'][region][0::]

        for index, choice in enumerate(new_choice_order):
            choice['order'] = index

        new_choice_order[0]['order'] = len(new_choice_order) + 1

        payload = {
            'question': {
                'inlineRegions': {
                    region: {
                        'choices': new_choice_order,
                    }
                },
                'shuffle': False
            }
        }
        req = self.app.put(url,
                           params=json.dumps(payload),
                           headers={'content-type': 'application/json'})
        self.ok(req)

        req = self.app.get(url)
        self.ok(req)
        data = self.json(req)

        self.assertEqual(len(data['question']['choices'][region]), 4)
        current_choice_ids = [c['id'] for c in data['question']['choices'][region]]
        sorted_desired_choices = sorted(new_choice_order, key=lambda k: k['order'])
        desired_choice_ids = [c['id'] for c in sorted_desired_choices]
        self.assertEqual(current_choice_ids, desired_choice_ids)

    def test_can_reorder_and_add_new_choices_mw_fitb(self):
        mc_item = self.create_mw_fitb_item()
        url = '{0}/items/{1}'.format(self.url,
                                     mc_item['id'])
        self.assertEqual(len(mc_item['question']['choices']), 2)
        region = mc_item['question']['choices'].keys()[0]
        self.assertEqual(len(mc_item['question']['choices'][region]), 4)
        new_choice_order = mc_item['question']['choices'][region][1::]
        new_choice_order.append({'text': 'new choice!'})
        new_choice_order.append(mc_item['question']['choices'][region][0])

        for index, choice in enumerate(new_choice_order):
            choice['order'] = index

        payload = {
            'question': {
                'inlineRegions': {
                    region: {
                        'choices': new_choice_order
                    }
                },
                'shuffle': False
            }
        }
        req = self.app.put(url,
                           params=json.dumps(payload),
                           headers={'content-type': 'application/json'})
        self.ok(req)

        req = self.app.get(url)
        self.ok(req)
        data = self.json(req)

        self.assertEqual(len(data['question']['choices'][region]), 5)
        current_choice_texts = [c['text'] for c in data['question']['choices'][region]]
        desired_choice_texts = [c['text'] for c in new_choice_order]
        self.assertEqual(current_choice_texts, desired_choice_texts)

    def test_can_reorder_and_delete_choices_mw_fitb(self):
        mc_item = self.create_mw_fitb_item()
        url = '{0}/items/{1}'.format(self.url,
                                     mc_item['id'])
        self.assertEqual(len(mc_item['question']['choices']), 2)
        region = mc_item['question']['choices'].keys()[0]
        self.assertEqual(len(mc_item['question']['choices'][region]), 4)
        new_choice_order = mc_item['question']['choices'][region][1::]
        new_choice_order.append(mc_item['question']['choices'][region][0])

        new_choice_order[3]['delete'] = True

        for index, choice in enumerate(new_choice_order):
            choice['order'] = index

        payload = {
            'question': {
                'inlineRegions': {
                    region: {
                        'choices': new_choice_order
                    }
                },
                'shuffle': False
            }
        }
        req = self.app.put(url,
                           params=json.dumps(payload),
                           headers={'content-type': 'application/json'})
        self.ok(req)

        req = self.app.get(url)
        self.ok(req)
        data = self.json(req)

        self.assertEqual(len(data['question']['choices'][region]), 3)
        current_choice_texts = [c['text'] for c in data['question']['choices'][region]]
        desired_choice_texts = [c['text'] for c in new_choice_order if 'delete' not in c]
        self.assertEqual(current_choice_texts, desired_choice_texts)

    def test_can_reorder_and_add_and_delete_choices_mw_fitb(self):
        mc_item = self.create_mw_fitb_item()
        url = '{0}/items/{1}'.format(self.url,
                                     mc_item['id'])
        self.assertEqual(len(mc_item['question']['choices']), 2)
        region = mc_item['question']['choices'].keys()[0]
        self.assertEqual(len(mc_item['question']['choices'][region]), 4)
        new_choice_order = mc_item['question']['choices'][region][1::]
        new_choice_order.append({'text': 'new choice!'})
        new_choice_order.append(mc_item['question']['choices'][region][0])

        new_choice_order[2]['delete'] = True

        for index, choice in enumerate(new_choice_order):
            choice['order'] = index

        payload = {
            'question': {
                'inlineRegions': {
                    region: {
                        'choices': new_choice_order
                    }
                },
                'shuffle': False
            }
        }
        req = self.app.put(url,
                           params=json.dumps(payload),
                           headers={'content-type': 'application/json'})
        self.ok(req)

        req = self.app.get(url)
        self.ok(req)
        data = self.json(req)

        self.assertEqual(len(data['question']['choices'][region]), 4)
        current_choice_texts = [c['text'] for c in data['question']['choices'][region]]
        desired_choice_texts = [c['text'] for c in new_choice_order if 'delete' not in c]
        self.assertEqual(current_choice_texts, desired_choice_texts)


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
        asset = self._repo.get_asset(Id(asset['id']))
        contents = asset.get_asset_contents()
        content = contents.next()
        self.assertEqual(content.get_url(), source['src'])
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
        asset = self._repo.get_asset(Id(asset['id']))
        contents = asset.get_asset_contents()
        contents.next()
        content = contents.next()
        self.assertEqual(content.get_url(), track['src'])
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
                video_asset_content = self._repo.get_asset_content(Id(asset_content['id']))
            elif 'vtt' in asset_content['genusTypeId']:
                caption_asset_content = self._repo.get_asset_content(Id(asset_content['id']))

        self.assertEqual(video_asset_content.get_url(),
                         source['src'])
        track = soup.find('track', label='English')
        self.assertEqual(caption_asset_content.get_url(),
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
                'removeLanguageType': data['question']['texts'][0]['languageTypeId'],
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
                'questionString': self._telugu_text,
                'type': 'qti'
            }
        }
        req = self.app.put(url,
                           params=json.dumps(payload),
                           headers=self._telugu_headers())
        self.ok(req)
        data = self.json(req)
        self.assertEqual(len(data['question']['texts']), 3)

        payload = {
            'question': {
                'removeLanguageType': '639-2%3AENG%40ISO',
                'type': 'qti'
            }
        }
        req = self.app.put(url,
                           params=json.dumps(payload),
                           headers=self._telugu_headers())
        self.ok(req)
        data = self.json(req)
        self.assertEqual(len(data['question']['texts']), 2)

        self.assertEqual(data['question']['texts'][1]['text'], self._telugu_text)
        self.assertEqual(data['question']['texts'][1]['languageTypeId'], self._telugu_language_type)
        self.assertEqual(data['question']['texts'][1]['scriptTypeId'], self._telugu_script_type)
        self.assertEqual(data['question']['texts'][0]['text'], self._hindi_text)
        self.assertEqual(data['question']['texts'][0]['languageTypeId'], self._hindi_language_type)
        self.assertEqual(data['question']['texts'][0]['scriptTypeId'], self._hindi_script_type)

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
                'removeLanguageType': item['answers'][0]['feedbacks'][0]['languageTypeId'],
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
                'feedback': self._telugu_text,
                'type': 'qti'
            }, {
                'id': item['answers'][0]['id'],
                'removeLanguageType': '639-2%3AENG%40ISO',
                'type': 'qti'
            }]
        }
        req = self.app.put(url,
                           params=json.dumps(payload),
                           headers=self._telugu_headers())
        self.ok(req)
        data = self.json(req)
        self.assertEqual(len(data['answers'][0]['feedbacks']), 2)
        self.assertEqual(data['answers'][0]['feedbacks'][0]['text'], self._hindi_text)
        self.assertEqual(data['answers'][0]['feedbacks'][0]['languageTypeId'], self._hindi_language_type)
        self.assertEqual(data['answers'][0]['feedbacks'][0]['scriptTypeId'], self._hindi_script_type)
        self.assertEqual(data['answers'][0]['feedbacks'][1]['text'], self._telugu_text)
        self.assertEqual(data['answers'][0]['feedbacks'][1]['languageTypeId'], self._telugu_language_type)
        self.assertEqual(data['answers'][0]['feedbacks'][1]['scriptTypeId'], self._telugu_script_type)

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
                    'removeLanguageType': item['question']['multiLanguageChoices'][0]['texts'][0]['languageTypeId']
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
                    'text': self._telugu_text,
                }, {
                    'id': item['question']['multiLanguageChoices'][0]['id'],
                    'removeLanguageType': '639-2%3AENG%40ISO'
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
        self.assertEqual(data['question']['multiLanguageChoices'][0]['texts'][1]['text'], self._telugu_text)
        self.assertEqual(data['question']['multiLanguageChoices'][0]['texts'][1]['languageTypeId'], self._telugu_language_type)
        self.assertEqual(data['question']['multiLanguageChoices'][0]['texts'][1]['scriptTypeId'], self._telugu_script_type)

        self.assertEqual(data['question']['multiLanguageChoices'][0]['texts'][0]['text'], self._hindi_text)
        self.assertEqual(data['question']['multiLanguageChoices'][0]['texts'][0]['languageTypeId'], self._hindi_language_type)
        self.assertEqual(data['question']['multiLanguageChoices'][0]['texts'][0]['scriptTypeId'], self._hindi_script_type)

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
                            'removeLanguageType': item['question']['multiLanguageChoices'][region][0]['texts'][0]['languageTypeId']
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
                            'text': self._telugu_text
                        }, {
                            'id': desired_choice_id,
                            'removeLanguageType': '639-2%3AENG%40ISO'
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
        self.assertEqual(data['question']['multiLanguageChoices'][region][0]['texts'][1]['text'], self._telugu_text)
        self.assertEqual(data['question']['multiLanguageChoices'][region][0]['texts'][1]['languageTypeId'], self._telugu_language_type)
        self.assertEqual(data['question']['multiLanguageChoices'][region][0]['texts'][1]['scriptTypeId'], self._telugu_script_type)
        self.assertEqual(data['question']['multiLanguageChoices'][region][0]['texts'][0]['text'], self._hindi_text)
        self.assertEqual(data['question']['multiLanguageChoices'][region][0]['texts'][0]['languageTypeId'], self._hindi_language_type)
        self.assertEqual(data['question']['multiLanguageChoices'][region][0]['texts'][0]['scriptTypeId'], self._hindi_script_type)

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
                'updatedFeedback': self._english_text,
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
                'feedback': self._telugu_text,
                'type': 'qti'
            }, {
                'id': item['answers'][0]['id'],
                'removeLanguageType': '639-2%3AENG%40ISO',
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
                'updatedQuestionString': self._english_text,
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
                'updatedQuestionString': self._english_text,
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
                'questionString': self._telugu_text,
                'type': 'qti'
            }
        }
        req = self.app.put(url,
                           params=json.dumps(payload),
                           headers=self._telugu_headers())
        self.ok(req)

        data = self.json(req)
        self.assertEqual(len(data['question']['texts']), 2)

        payload = {
            'question': {
                'removeLanguageType': '639-2%3AENG%40ISO',
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
                'updatedQuestionString': self._english_text,
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
