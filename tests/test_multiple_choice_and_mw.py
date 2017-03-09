# -*- coding: utf-8 -*-
import json
from copy import deepcopy
from urllib import unquote, quote

from bs4 import BeautifulSoup
from paste.fixture import AppError

import utilities
from dlkit_runtime.primordium import Id, Type
from records.registry import ANSWER_RECORD_TYPES, QUESTION_RECORD_TYPES
from testing_utilities import get_managers
from tests.test_assessment import ABS_PATH, BaseAssessmentTestCase,\
    SIMPLE_SEQUENCE_RECORD, NUMERIC_RESPONSE_ITEM_GENUS_TYPE, \
    NUMERIC_RESPONSE_QUESTION_RECORD_TYPE, NUMERIC_RESPONSE_ANSWER_RECORD_TYPE,\
    EDX_ITEM_RECORD_TYPE, WRONG_ANSWER_GENUS


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
            "name"        : item_name,
            "description" : item_desc,
            "question" : {
                "type"           : question_type,
                "rerandomize"    : "always",
                "questionString" : question_body,
                "choices"        : question_choices
            },
            "answers" : [{
                "type"     : answer_type,
                "choiceId" : answer
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
            "name"            : item_name,
            "description"     : item_desc,
            "question"        : {
                "type"             : question_type,
                "questionString"   : question_body,
                "choices"          : question_choices
            },
            "answers"         : [{
                "type"        : answer_type,
                "choiceId"    : answer
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
            "name"            : item_name,
            "description"     : item_desc,
            "question"        : {
                "type"             : question_type,
                "questionString"   : question_body,
                "choices"          : question_choices
            },
            "answers"         : [{
                "type"        : answer_type,
                "choiceId"    : answer
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
            "name"            : item_name,
            "description"     : item_desc,
            "question"        : {
                "type"             : question_type,
                "questionString"   : question_body,
                "choices"          : question_choices
            },
            "answers"          : [{
                "type"         : answer_type,
                "choiceId"     : answer
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
            "name"            : item_name,
            "description"     : item_desc,
            "question"        : {
                "type"             : question_type,
                "questionString"   : question_body,
                "choices"          : question_choices
            },
            "answers"         : [{
                "type"        : answer_type,
                "choiceId"    : answer
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
            'itemIds': [item_id]
        }
        req = self.app.post(assessment_items_endpoint,
                            params=json.dumps(payload),
                            headers={'content-type': 'application/json'})
        self.ok(req)

        # Use POST to create an offering
        payload = {
            "startTime"   : {
                "day"     : 1,
                "month"   : 1,
                "year"    : 2015
            },
            "duration"    : {
                "days"    : 2
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
            "name"            : item_name,
            "description"     : item_desc,
            "question"        : {
                "type"             : question_type,
                "questionString"   : question_body,
                "choices"          : question_choices
            },
            "answers"         : [{
                "type"        : answer_type,
                "choiceId"    : answer
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
            {'text': 'I hope so.',
             'name': 'yes'},
            {'text': 'I don\'t think I can.',
             'name': 'no'},
            {'text': 'Maybe tomorrow.',
             'name': 'maybe'}
        ]
        question_type = 'question-record-type%3Amulti-choice-edx%40ODL.MIT.EDU'
        answer = 2
        answer_type = 'answer-record-type%3Amulti-choice-edx%40ODL.MIT.EDU'
        payload = {
            "name"            : item_name,
            "description"     : item_desc,
            "question"        : {
                "type"             : question_type,
                "questionString"   : question_body,
                "choices"          : question_choices
            },
            "answers"         : [{
                "type"        : answer_type,
                "choiceId"   : answer
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
                'id': question_id,
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
                'id': answer_id,
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
                        'oldText': text['text'],
                        'newText': str(choice_xml.simpleChoice)
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
                'oldQuestionString': '',
                'newQuestionString': ''
            }
        }

        question_xml = BeautifulSoup(data['question']['texts'][0]['text'], 'xml')
        self.assertIn('height=', data['question']['texts'][0]['text'])
        self.assertIn('width=', data['question']['texts'][0]['text'])

        for img in question_xml.find_all('img'):
            del img['height']
            del img['width']
        payload['question']['newQuestionString'] = str(question_xml.itemBody)
        payload['question']['oldQuestionString'] = data['question']['texts'][0]

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
                'newFeedback': str(answer_xml.modalFeedback),
                'oldFeedback': answer['feedbacks'][0],
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
                'newFeedback': str(answer_xml.modalFeedback),
                'oldFeedback': answer['feedbacks'][0],
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
        self.assertIn('http://localhost', data['feedback'])
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
        self.assertIn('http://localhost', data['feedback'])
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
