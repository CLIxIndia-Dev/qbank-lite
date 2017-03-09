# -*- coding: utf-8 -*-

import json
from urllib import unquote

from bs4 import BeautifulSoup
from paste.fixture import AppError

from tests.test_assessment import ABS_PATH, BaseAssessmentTestCase


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
            "name"       : item_name,
            "description": item_desc,
            "question"   : {
                "type"          : question_type,
                "questionString": question_body,
                "choices"       : question_choices
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
            "startTime": {
                "day"  : 1,
                "month": 1,
                "year" : 2015
            },
            "duration": {
                "days": 2
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
            'itemIds': [item_id]
        }
        req = self.app.post(assessment_items_endpoint,
                            params=json.dumps(payload),
                            headers={'content-type': 'application/json'})
        self.ok(req)

        # Now POST to offerings should work
        payload = {
            "startTime": {
                "day"  : 1,
                "month": 1,
                "year" : 2015
            },
            "duration": {
                "days": 2
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
            'id': quote_safe_offering_id
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
            "startTime": {
                "day"  : 1,
                "month": 2,
                "year" : 2015
            }
        }
        expected_payload = new_start_time
        expected_payload.update({
            "duration": {
                "days": 2
            },
            "id": quote_safe_offering_id
        })

        req = self.app.put(assessment_offering_detail_endpoint,
                           params=json.dumps(new_start_time),
                           headers={'content-type': 'application/json'})
        self.ok(req)
        self.verify_offerings(req, 'AssessmentOffered', [expected_payload])

        # PUT with a list of length 1 should also work
        new_duration = [{
            "duration": {
                "days": 5,
                "minutes": 120
            }
        }]
        expected_payload = new_duration
        expected_payload[0].update(new_start_time)
        expected_payload[0].update({
            "id": quote_safe_offering_id
        })
        req = self.app.put(assessment_offering_detail_endpoint,
                           params=json.dumps(new_duration),
                           headers={'content-type': 'application/json'})
        self.ok(req)
        self.verify_offerings(req, 'AssessmentOffered', expected_payload)

        funny_payload = {
            "duration": {
                "hours": 2
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
            "startTime": {
                "day"  : 1,
                "month": 1,
                "year" : 2015
            },
            "duration": {
                "days": 2
            }
        }, {
            "startTime": {
                "day"  : 9,
                "month": 1,
                "year" : 2015
            },
            "duration": {
                "days": 20
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
            'id': offering1_id
        })
        payload[1].update({
            'id': offering2_id
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
                    "sideFaceValue": 2,
                    "topFaceValue": 3
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
            'itemIds': [item_id]
        }
        req = self.app.post(assessment_items_endpoint,
                            params=json.dumps(payload),
                            headers={'content-type': 'application/json'})
        self.ok(req)

        # Use POST to create an offering
        payload = {
            "startTime": {
                "day"  : 1,
                "month": 1,
                "year" : 2015
            },
            "duration": {
                "days": 2
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
                "frontFaceValue": 0,
                "sideFaceValue": 1,
                "topFaceValue": 2
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
                "frontFaceValue": 1,
                "sideFaceValue": 2,
                "topFaceValue": 3
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
            "name": item_name,
            "description": item_desc,
            "genus": item_genus,
            "question": {
                "choices": [
                    'yes',
                    'no',
                    'maybe'
                ],
                "genus": item_genus,
                "promptName": manip_name,
                "type": question_type,
                "questionString": question_string
            },
            "answers": [{
                "genus": item_genus,
                "type": answer_type,
                "choiceId": 1
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
            'itemIds': [item_id]
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
            'itemIds': [item1_id, item2_id]
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
<source src="http://localhost/api/v1/repository/repositories/{0}/assets/{1}/contents/{2}/stream" type="audio/mpeg"/>
</audio>
</p>
<p>
<img alt="This is a drawing of a busy intersection." height="100" src="http://localhost/api/v1/repository/repositories/{0}/assets/{3}/contents/{4}/stream" width="100"/>
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
