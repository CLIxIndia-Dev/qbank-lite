# -*- coding: utf-8 -*-

import os
import json

from copy import deepcopy

from paste.fixture import AppError

from dlkit.runtime.primitives import Type
from dlkit.records.registry import ITEM_GENUS_TYPES, QUESTION_GENUS_TYPES,\
    ANSWER_GENUS_TYPES, ASSESSMENT_RECORD_TYPES,\
    ASSESSMENT_OFFERED_RECORD_TYPES, ASSESSMENT_TAKEN_RECORD_TYPES

from testing_utilities import BaseTestCase, get_managers

from utilities import clean_id

from urllib import unquote


PROJECT_PATH = os.path.dirname(os.path.abspath(__file__))
ABS_PATH = os.path.abspath(os.path.join(PROJECT_PATH, os.pardir))

REVIEWABLE_OFFERED = Type(**ASSESSMENT_OFFERED_RECORD_TYPES['review-options'])
REVIEWABLE_TAKEN = Type(**ASSESSMENT_TAKEN_RECORD_TYPES['review-options'])

SIMPLE_SEQUENCE_RECORD = Type(**ASSESSMENT_RECORD_TYPES['simple-child-sequencing'])

DRAG_AND_DROP_ITEM_GENUS_TYPE = Type(**ITEM_GENUS_TYPES['drag-and-drop'])
DRAG_AND_DROP_QUESTION_GENUS_TYPE = Type(**QUESTION_GENUS_TYPES['drag-and-drop'])
WRONG_ANSWER = Type(**ANSWER_GENUS_TYPES['wrong-answer'])
RIGHT_ANSWER = Type(**ANSWER_GENUS_TYPES['right-answer'])

SNAP_DROP_BEHAVIOR = 'drop.behavior%3Asnap%40ODL.MIT.EDU'
DROP_DROP_BEHAVIOR = 'drop.behavior%3Adrop%40ODL.MIT.EDU'
REJECT_DROP_BEHAVIOR = 'drop.behavior%3Areject%40ODL.MIT.EDU'


class BaseDragAndDropTestCase(BaseTestCase):
    @staticmethod
    def _item_payload():
        """payload without the question and answer parts.
        Pull in self._question_payload() and self._answers_payload() if you need those"""
        return {
            'genusTypeId': str(DRAG_AND_DROP_ITEM_GENUS_TYPE),
            'name': 'Test drag and drop item'
        }

    def _question_payload(self):
        payload = {
            'questionString': 'Put the hats on the ball',
            'targets': [{
                'text': '<p><img src="AssetContent:drag_and_drop_input_DPP-Concpt-BlkonRmp-Trgt_png" alt="Ramp" /></p>',
                'name': 'Image of ramp',
                'dropBehaviorType': REJECT_DROP_BEHAVIOR
            }],
            'droppables': [{
                'text': '<p><img src="AssetContent:draggable_green_dot_png" alt="Green dot" /></p>',
                'name': 'Green dot',
                'reuse': 1,
                'dropBehaviorType': DROP_DROP_BEHAVIOR
            }, {
                'text': '<p><img src="AssetContent:draggable_red_dot_png" alt="Red dot" /></p>',
                'name': 'Red dot',
                'reuse': 4,
                'dropBehaviorType': DROP_DROP_BEHAVIOR
            }],
            'zones': [{
                'spatialUnit': {
                    'recordType': 'osid.mapping.SpatialUnit%3Arectangle%40ODL.MIT.EDU',
                    'coordinateValues': [0, 0],
                    'width': 50,
                    'height': 30
                },
                'containerId': 0,
                'dropBehaviorType': SNAP_DROP_BEHAVIOR,
                'name': u'Zone Á',
                'description': 'left of ball',
                'reuse': 0,
                'visible': False
            }, {
                'spatialUnit': {
                    'recordType': 'osid.mapping.SpatialUnit%3Arectangle%40ODL.MIT.EDU',
                    'coordinateValues': [100, 100],
                    'width': 30,
                    'height': 50
                },
                'containerId': 0,
                'dropBehaviorType': DROP_DROP_BEHAVIOR,
                'name': u'Zone बी',
                'description': 'right of ball',
                'reuse': 2,
                'visible': True
            }],
            'fileIds': {},
            'genusTypeId': str(DRAG_AND_DROP_QUESTION_GENUS_TYPE),
            'shuffleDroppables': True,
            'shuffleTargets': False,
            'shuffleZones': True
        }

        media_files = [self._target,
                       self._draggable1,
                       self._draggable2]

        assets = {}
        for media_file in media_files:
            label = self._label(self._filename(media_file))
            assets[label] = self.upload_media_file(media_file)

        for label, asset in assets.iteritems():
            payload['fileIds'][label] = {}
            payload['fileIds'][label]['assetId'] = asset['id']
            payload['fileIds'][label]['assetContentId'] = asset['assetContents'][0]['id']
            payload['fileIds'][label]['assetContentTypeId'] = asset['assetContents'][0]['genusTypeId']

        return payload

    def _answers_payload(self):
        payload = [{
            'feedback': '<p>Good job! <audio type="audio/mp3"><source src="AssetContent:audio_feedback_mp3" /></audio></p>',
            'zoneConditions': [{
                'zoneId': 0,
                'droppableId': 0
            }, {
                'zoneId': 1,
                'droppableId': 1
            }],
            'fileIds': {},
            'genusTypeId': str(RIGHT_ANSWER)
        }, {
            'feedback': '<p>Try again! <audio type="audio/mp3"><source src="AssetContent:audio_feedback_mp3" /></audio></p>',
            'zoneConditions': [{
                'zoneId': 0,
                'droppableId': 1
            }, {
                'zoneId': 1,
                'droppableId': 0
            }],
            'fileIds': {},
            'genusTypeId': str(WRONG_ANSWER)
        }]

        media_files = [self._audio_feedback]

        assets = {}
        for media_file in media_files:
            label = self._label(self._filename(media_file))
            assets[label] = self.upload_media_file(media_file)

        for label, asset in assets.iteritems():
            payload[0]['fileIds'][label] = {}
            payload[0]['fileIds'][label]['assetId'] = asset['id']
            payload[0]['fileIds'][label]['assetContentId'] = asset['assetContents'][0]['id']
            payload[0]['fileIds'][label]['assetContentTypeId'] = asset['assetContents'][0]['genusTypeId']

            payload[1]['fileIds'][label] = {}
            payload[1]['fileIds'][label]['assetId'] = asset['id']
            payload[1]['fileIds'][label]['assetContentId'] = asset['assetContents'][0]['id']
            payload[1]['fileIds'][label]['assetContentTypeId'] = asset['assetContents'][0]['genusTypeId']

        return payload

    def create_assessment_for_item(self, bank_id, item_id):
        if isinstance(bank_id, basestring):
            bank_id = clean_id(bank_id)
        if isinstance(item_id, basestring):
            item_id = clean_id(item_id)

        bank = get_managers()['am'].get_bank(bank_id)
        form = bank.get_assessment_form_for_create([SIMPLE_SEQUENCE_RECORD])
        form.display_name = 'a test assessment'
        form.description = 'for testing with'
        new_assessment = bank.create_assessment(form)

        bank.add_item(new_assessment.ident, item_id)

        return new_assessment

    def create_assessment_offered_for_item(self, bank_id, item_id):
        if isinstance(bank_id, basestring):
            bank_id = clean_id(bank_id)
        if isinstance(item_id, basestring):
            item_id = clean_id(item_id)

        bank = get_managers()['am'].get_bank(bank_id)

        new_assessment = self.create_assessment_for_item(bank_id, item_id)

        form = bank.get_assessment_offered_form_for_create(new_assessment.ident,
                                                           [REVIEWABLE_OFFERED])
        new_offered = bank.create_assessment_offered(form)

        return new_offered

    def create_taken_for_item(self, bank_id, item_id):
        if isinstance(bank_id, basestring):
            bank_id = clean_id(bank_id)
        if isinstance(item_id, basestring):
            item_id = clean_id(item_id)

        bank = get_managers()['am'].get_bank(bank_id)

        new_offered = self.create_assessment_offered_for_item(bank_id, item_id)

        form = bank.get_assessment_taken_form_for_create(new_offered.ident,
                                                         [REVIEWABLE_TAKEN])
        taken = bank.create_assessment_taken(form)
        return taken

    def create_item_without_question_or_answers(self):
        payload = self._item_payload()

        req = self.app.post(self.url,
                            params=json.dumps(payload),
                            headers={'content-type': 'application/json'})
        self.ok(req)
        return self.json(req)

    def create_item_with_question_and_answers(self):
        payload = self._item_payload()
        payload['question'] = self._question_payload()
        payload['answers'] = self._answers_payload()

        req = self.app.post(self.url,
                            params=json.dumps(payload),
                            headers={'content-type': 'application/json'})
        self.ok(req)
        return self.json(req)

    def create_item_with_question_but_no_answers(self):
        payload = self._item_payload()
        payload['question'] = self._question_payload()

        req = self.app.post(self.url,
                            params=json.dumps(payload),
                            headers={'content-type': 'application/json'})
        self.ok(req)
        return self.json(req)

    def setUp(self):
        self._target = open('{0}/tests/files/drag-and-drop/drag_and_drop_input_DPP-Concpt-BlkonRmp-Trgt.png'.format(ABS_PATH), 'rb')
        self._draggable1 = open('{0}/tests/files/drag-and-drop/draggable_green_dot.png'.format(ABS_PATH), 'rb')
        self._draggable2 = open('{0}/tests/files/drag-and-drop/draggable_red_dot.png'.format(ABS_PATH), 'rb')
        self._draggable3 = open('{0}/tests/files/drag-and-drop/draggable_h1i.PNG'.format(ABS_PATH), 'rb')
        self._audio_feedback = open('{0}/tests/files/audio_feedback.mp3'.format(ABS_PATH), 'rb')

        super(BaseDragAndDropTestCase, self).setUp()
        self.url = '/api/v1/assessment/banks/{0}/items'.format(unquote(str(self._bank.ident)))
        self._hi_language_type = '639-2%3AHIN%40ISO'
        self._hi_script_type = '15924%3ADEVA%40ISO'
        self._format_type = 'TextFormats%3APLAIN%40okapia.net'
        self._en_language_type = '639-2%3AENG%40ISO'
        self._en_script_type = '15924%3ALATN%40ISO'

    def tearDown(self):
        super(BaseDragAndDropTestCase, self).tearDown()
        self._target.close()
        self._draggable1.close()
        self._draggable2.close()
        self._draggable3.close()
        self._audio_feedback.close()


class CreateTests(BaseDragAndDropTestCase):
    """Can create drag and drop RESTfully"""
    def test_can_create_item_with_question_and_answers(self):
        """Make sure question genusTypeId is set properly"""
        payload = self._item_payload()
        payload['question'] = self._question_payload()
        payload['answers'] = self._answers_payload()

        req = self.app.post(self.url,
                            params=json.dumps(payload),
                            headers={'content-type': 'application/json'})
        self.ok(req)
        data = self.json(req)
        question = data['question']
        self.assertEqual(data['genusTypeId'], str(DRAG_AND_DROP_ITEM_GENUS_TYPE))
        self.assertEqual(question['genusTypeId'], str(DRAG_AND_DROP_QUESTION_GENUS_TYPE))

        # make sure the question string made it
        self.assertEqual(
            question['text']['text'],
            'Put the hats on the ball'
        )

        # make sure no QTI record types
        self.assertTrue(not any('qti' in r for r in data['recordTypeIds']))
        self.assertTrue(not any('qti' in r for r in data['question']['recordTypeIds']))
        for answer in data['answers']:
            self.assertTrue(not any('qti' in r for r in answer['recordTypeIds']))

        # check the three shuffle flags in the question match the payload
        self.assertEqual(question['shuffleDroppables'],
                         payload['question']['shuffleDroppables'])
        self.assertEqual(question['shuffleTargets'],
                         payload['question']['shuffleTargets'])
        self.assertEqual(question['shuffleZones'],
                         payload['question']['shuffleZones'])

        # make sure the media files all show as URLs
        self.assertIn('fileIds', question)
        for droppable in question['droppables']:
            self.assertIn('/api/v1/repository/repositories', droppable['text'])
            self.assertIn('/stream', droppable['text'])
        for target in question['targets']:
            self.assertIn('/api/v1/repository/repositories', target['text'])
            self.assertIn('/stream', target['text'])
        for answer in data['answers']:
            self.assertIn('/api/v1/repository/repositories', answer['feedback']['text'])
            self.assertIn('/stream', answer['feedback']['text'])
            self.assertIn('fileIds', answer)

        # make sure droppables, targets, and zones appear
        self.assertEqual(len(question['droppables']),
                         len(payload['question']['droppables']))
        self.assertEqual(len(question['targets']),
                         len(payload['question']['targets']))
        self.assertEqual(len(question['zones']),
                         len(payload['question']['zones']))

        # check that the various arguments are saved correctly for the question
        # i.e. visible, reuse, name, etc.
        # use the multiLanguage versions to check, since those aren't shuffled
        # and we can index-match to the payload easier
        for index, droppable in enumerate(question['multiLanguageDroppables']):
            # don't check texts[0]['text'] here because the image src
            self.assertEqual(droppable['names'][0]['text'],
                             payload['question']['droppables'][index]['name'])
            self.assertEqual(droppable['reuse'],
                             payload['question']['droppables'][index]['reuse'])
            self.assertEqual(droppable['dropBehaviorType'],
                             payload['question']['droppables'][index]['dropBehaviorType'])
        for index, target in enumerate(question['multiLanguageTargets']):
            # don't check texts[0]['text'] here because the image src
            self.assertEqual(target['names'][0]['text'],
                             payload['question']['targets'][index]['name'])
            self.assertEqual(target['dropBehaviorType'],
                             payload['question']['targets'][index]['dropBehaviorType'])
        for index, zone in enumerate(question['multiLanguageZones']):
            self.assertEqual(zone['reuse'],
                             payload['question']['zones'][index]['reuse'])
            self.assertEqual(zone['dropBehaviorType'],
                             payload['question']['zones'][index]['dropBehaviorType'])
            self.assertEqual(zone['visible'],
                             payload['question']['zones'][index]['visible'])
            self.assertEqual(zone['spatialUnit']['width'],
                             payload['question']['zones'][index]['spatialUnit']['width'])
            self.assertEqual(zone['spatialUnit']['height'],
                             payload['question']['zones'][index]['spatialUnit']['height'])
            self.assertEqual(zone['spatialUnit']['coordinateValues'],
                             payload['question']['zones'][index]['spatialUnit']['coordinateValues'])
            self.assertEqual(zone['spatialUnit']['recordTypes'][0],
                             payload['question']['zones'][index]['spatialUnit']['recordType'])

        # make sure the multi-language stuff comes out right in the question object_map
        self.assertIn('multiLanguageDroppables', question)
        for droppable in question['multiLanguageDroppables']:
            self.assertNotIn('text', droppable)
            self.assertIn('texts', droppable)
            self.assertNotIn('name', droppable)
            self.assertIn('names', droppable)
        for droppable in question['droppables']:
            self.assertIn('text', droppable)
            self.assertNotIn('texts', droppable)
            self.assertIn('name', droppable)
            self.assertNotIn('names', droppable)
        self.assertIn('multiLanguageTargets', question)
        for target in question['multiLanguageTargets']:
            self.assertNotIn('text', target)
            self.assertIn('texts', target)
            self.assertNotIn('name', target)
            self.assertIn('names', target)
        for target in question['targets']:
            self.assertIn('text', target)
            self.assertNotIn('texts', target)
            self.assertIn('name', target)
            self.assertNotIn('names', target)
        self.assertIn('multiLanguageZones', question)
        for zone in question['multiLanguageZones']:
            self.assertNotIn('name', zone)
            self.assertIn('names', zone)
            self.assertNotIn('description', zone)
            self.assertIn('descriptions', zone)
        for zone in question['zones']:
            self.assertIn('name', zone)
            self.assertNotIn('names', zone)
            self.assertIn('description', zone)
            self.assertNotIn('descriptions', zone)

        # check the answers
        self.assertEqual(len(data['answers']), 2)
        self.assertEqual(data['answers'][0]['genusTypeId'], str(RIGHT_ANSWER))
        self.assertEqual(data['answers'][1]['genusTypeId'], str(WRONG_ANSWER))
        for answer in data['answers']:
            self.assertEqual(len(answer['spatialUnitConditions']), 0)
            self.assertEqual(len(answer['coordinateConditions']), 0)
            self.assertEqual(len(answer['zoneConditions']), 2)

        # check that the indices all got converted to the right IDs for question zones
        # and answer zone conditions
        # Especially important with the shuffling!
        expected_target_id = question['targets'][0]['id']
        for zone in question['zones']:
            self.assertEqual(zone['containerId'], expected_target_id)

        expected_droppable_0_id = question['multiLanguageDroppables'][0]['id']
        expected_droppable_1_id = question['multiLanguageDroppables'][1]['id']

        expected_zone_0_id = question['multiLanguageZones'][0]['id']
        expected_zone_1_id = question['multiLanguageZones'][1]['id']
        for answer in data['answers']:
            if answer['genusTypeId'] == str(RIGHT_ANSWER):
                for zone_condition in answer['zoneConditions']:
                    if zone_condition['droppableId'] == expected_droppable_0_id:
                        self.assertEqual(zone_condition['zoneId'],
                                         expected_zone_0_id)
                    else:
                        self.assertEqual(zone_condition['droppableId'],
                                         expected_droppable_1_id)
                        self.assertEqual(zone_condition['zoneId'],
                                         expected_zone_1_id)
            else:
                for zone_condition in answer['zoneConditions']:
                    if zone_condition['droppableId'] == expected_droppable_1_id:
                        self.assertEqual(zone_condition['zoneId'],
                                         expected_zone_0_id)
                    else:
                        self.assertEqual(zone_condition['droppableId'],
                                         expected_droppable_0_id)
                        self.assertEqual(zone_condition['zoneId'],
                                         expected_zone_1_id)

    def test_can_create_item_without_question_or_answers(self):
        payload = self._item_payload()

        req = self.app.post(self.url,
                            params=json.dumps(payload),
                            headers={'content-type': 'application/json'})
        self.ok(req)
        data = self.json(req)
        self.assertEqual(data['genusTypeId'], str(DRAG_AND_DROP_ITEM_GENUS_TYPE))

    def test_still_creates_question_if_source_tag_not_in_file_ids(self):
        payload = self._item_payload()
        payload['question'] = self._question_payload()

        payload['question']['fileIds'] = {}

        req = self.app.post(self.url,
                            params=json.dumps(payload),
                            headers={'content-type': 'application/json'})
        self.ok(req)
        data = self.json(req)
        question = data['question']

        for droppable in question['droppables']:
            self.assertNotIn('/api/v1/repository/repositories', droppable['text'])
            self.assertNotIn('/stream', droppable['text'])
            self.assertIn('AssetContent:', droppable['text'])
        for target in question['targets']:
            self.assertNotIn('/api/v1/repository/repositories', target['text'])
            self.assertNotIn('/stream', target['text'])
            self.assertIn('AssetContent:', target['text'])

    def test_still_creates_answers_if_source_tag_not_in_file_ids(self):
        payload = self._item_payload()
        payload['question'] = self._question_payload()
        payload['answers'] = self._answers_payload()

        payload['answers'][0]['fileIds'] = {}
        payload['answers'][1]['fileIds'] = {}

        req = self.app.post(self.url,
                            params=json.dumps(payload),
                            headers={'content-type': 'application/json'})
        self.ok(req)
        data = self.json(req)

        for answer in data['answers']:
            self.assertNotIn('/api/v1/repository/repositories', answer['feedback']['text'])
            self.assertNotIn('/stream', answer['feedback']['text'])
            self.assertIn('AssetContent:', answer['feedback']['text'])

    def test_cannot_set_zone_to_negative_target_index(self):
        payload = self._item_payload()
        payload['question'] = self._question_payload()
        payload['question']['zones'][0]['containerId'] = -1

        self.assertRaises(AppError,
                          self.app.post,
                          self.url,
                          params=json.dumps(payload),
                          headers={'content-type': 'application/json'})

    def test_cannot_set_zone_to_non_existent_target_index(self):
        payload = self._item_payload()
        payload['question'] = self._question_payload()
        payload['question']['zones'][0]['containerId'] = 1

        self.assertRaises(AppError,
                          self.app.post,
                          self.url,
                          params=json.dumps(payload),
                          headers={'content-type': 'application/json'})

    def test_cannot_set_answer_droppable_to_negative_index(self):
        payload = self._item_payload()
        payload['question'] = self._question_payload()
        payload['answers'] = self._answers_payload()

        payload['answers'][0]['zoneConditions'][0]['droppableId'] = -1

        self.assertRaises(AppError,
                          self.app.post,
                          self.url,
                          params=json.dumps(payload),
                          headers={'content-type': 'application/json'})

    def test_cannot_set_answer_droppable_to_non_existent_index(self):
        payload = self._item_payload()
        payload['question'] = self._question_payload()
        payload['answers'] = self._answers_payload()

        payload['answers'][0]['zoneConditions'][0]['droppableId'] = 2

        self.assertRaises(AppError,
                          self.app.post,
                          self.url,
                          params=json.dumps(payload),
                          headers={'content-type': 'application/json'})

    def test_cannot_set_answer_zone_to_negative_index(self):
        payload = self._item_payload()
        payload['question'] = self._question_payload()
        payload['answers'] = self._answers_payload()

        payload['answers'][0]['zoneConditions'][0]['zoneId'] = -1

        self.assertRaises(AppError,
                          self.app.post,
                          self.url,
                          params=json.dumps(payload),
                          headers={'content-type': 'application/json'})

    def test_cannot_set_answer_zone_to_non_existent_index(self):
        payload = self._item_payload()
        payload['question'] = self._question_payload()
        payload['answers'] = self._answers_payload()

        payload['answers'][0]['zoneConditions'][0]['zoneId'] = 2

        self.assertRaises(AppError,
                          self.app.post,
                          self.url,
                          params=json.dumps(payload),
                          headers={'content-type': 'application/json'})

    def test_can_create_droppable_with_no_name(self):
        payload = self._item_payload()
        payload['question'] = self._question_payload()
        del payload['question']['droppables'][0]['name']

        req = self.app.post(self.url,
                            params=json.dumps(payload),
                            headers={'content-type': 'application/json'})
        self.ok(req)

    def test_can_create_target_with_no_name(self):
        payload = self._item_payload()
        payload['question'] = self._question_payload()
        del payload['question']['targets'][0]['name']

        req = self.app.post(self.url,
                            params=json.dumps(payload),
                            headers={'content-type': 'application/json'})
        self.ok(req)

    def test_can_create_zone_with_no_name(self):
        payload = self._item_payload()
        payload['question'] = self._question_payload()
        del payload['question']['zones'][0]['name']

        req = self.app.post(self.url,
                            params=json.dumps(payload),
                            headers={'content-type': 'application/json'})
        self.ok(req)


class UpdateTests(BaseDragAndDropTestCase):
    """Can edit the drag and drop RESTfully"""
    def test_can_add_question_string_in_new_language(self):
        item = self.create_item_with_question_and_answers()

        hindi_question = {
            'text': u'एक भूरा खरगोश',
            'formatTypeId': self._format_type,
            'languageTypeId': self._hi_language_type,
            'scriptTypeId': self._hi_script_type
        }

        url = '{0}/{1}'.format(self.url,
                               item['id'])

        payload = {
            'question': {
                'questionString': hindi_question
            }
        }

        req = self.app.put(url,
                           params=json.dumps(payload),
                           headers={'content-type': 'application/json'})
        self.ok(req)
        data = self.json(req)
        question = data['question']

        self.assertEqual(len(question['texts']), 2)

        self.assertEqual(
            question['texts'][1]['text'],
            hindi_question['text']
        )

        self.assertEqual(
            question['texts'][1]['languageTypeId'],
            hindi_question['languageTypeId']
        )

        self.assertEqual(
            question['texts'][1]['scriptTypeId'],
            hindi_question['scriptTypeId']
        )

        req = self.app.get(url,
                           headers={'x-api-locale': 'hi'})
        self.ok(req)
        data = self.json(req)
        question = data['question']

        self.assertEqual(
            question['text']['text'],
            hindi_question['text']
        )

        self.assertEqual(
            question['text']['languageTypeId'],
            hindi_question['languageTypeId']
        )

        self.assertEqual(
            question['text']['scriptTypeId'],
            hindi_question['scriptTypeId']
        )

    def test_can_edit_question_string(self):
        item = self.create_item_with_question_and_answers()

        new_question = 'does this monkey have a banana?'

        url = '{0}/{1}'.format(self.url,
                               item['id'])

        payload = {
            'question': {
                'questionString': new_question
            }
        }

        req = self.app.put(url,
                           params=json.dumps(payload),
                           headers={'content-type': 'application/json'})
        self.ok(req)
        data = self.json(req)
        question = data['question']

        self.assertEqual(len(question['texts']), 1)

        self.assertEqual(
            question['text']['text'],
            new_question
        )

    def test_can_remove_question_string_language(self):
        item = self.create_item_with_question_and_answers()

        hindi_question = {
            'text': u'एक भूरा खरगोश',
            'formatTypeId': self._format_type,
            'languageTypeId': self._hi_language_type,
            'scriptTypeId': self._hi_script_type
        }

        url = '{0}/{1}'.format(self.url,
                               item['id'])

        payload = {
            'question': {
                'questionString': hindi_question
            }
        }

        req = self.app.put(url,
                           params=json.dumps(payload),
                           headers={'content-type': 'application/json'})
        self.ok(req)
        data = self.json(req)
        question = data['question']

        self.assertEqual(len(question['texts']), 2)

        payload = {
            'question': {
                'removeLanguageType': self._en_language_type
            }
        }

        req = self.app.put(url,
                           params=json.dumps(payload),
                           headers={'content-type': 'application/json'})
        self.ok(req)
        data = self.json(req)
        question = data['question']

        self.assertEqual(len(question['texts']), 1)

        self.assertEqual(
            question['text']['text'],
            hindi_question['text']
        )

    def test_can_add_question_to_existing_item(self):
        item = self.create_item_without_question_or_answers()

        url = '{0}/{1}'.format(self.url,
                               item['id'])
        payload = {
            'question': self._question_payload()
        }

        req = self.app.put(url,
                           params=json.dumps(payload),
                           headers={'content-type': 'application/json'})
        self.ok(req)
        data = self.json(req)
        question = data['question']

        self.assertEqual(question['genusTypeId'], str(DRAG_AND_DROP_QUESTION_GENUS_TYPE))

        # make sure no QTI record types
        self.assertTrue(not any('qti' in r for r in data['recordTypeIds']))
        self.assertTrue(not any('qti' in r for r in data['question']['recordTypeIds']))

        # check the three shuffle flags in the question match the payload
        self.assertEqual(question['shuffleDroppables'],
                         payload['question']['shuffleDroppables'])
        self.assertEqual(question['shuffleTargets'],
                         payload['question']['shuffleTargets'])
        self.assertEqual(question['shuffleZones'],
                         payload['question']['shuffleZones'])

        # make sure the media files all show as URLs
        self.assertIn('fileIds', question)
        for droppable in question['droppables']:
            self.assertIn('/api/v1/repository/repositories', droppable['text'])
            self.assertIn('/stream', droppable['text'])
        for target in question['targets']:
            self.assertIn('/api/v1/repository/repositories', target['text'])
            self.assertIn('/stream', target['text'])

        # make sure droppables, targets, and zones appear
        self.assertEqual(len(question['droppables']),
                         len(payload['question']['droppables']))
        self.assertEqual(len(question['targets']),
                         len(payload['question']['targets']))
        self.assertEqual(len(question['zones']),
                         len(payload['question']['zones']))

        # check that the various arguments are saved correctly for the question
        # i.e. visible, reuse, name, etc.
        # use the multiLanguage versions to check, since those aren't shuffled
        # and we can index-match to the payload easier
        for index, droppable in enumerate(question['multiLanguageDroppables']):
            self.assertEqual(droppable['names'][0]['text'],
                             payload['question']['droppables'][index]['name'])
            self.assertEqual(droppable['reuse'],
                             payload['question']['droppables'][index]['reuse'])
            self.assertEqual(droppable['dropBehaviorType'],
                             payload['question']['droppables'][index]['dropBehaviorType'])
        for index, target in enumerate(question['multiLanguageTargets']):
            self.assertEqual(target['names'][0]['text'],
                             payload['question']['targets'][index]['name'])
            self.assertEqual(target['dropBehaviorType'],
                             payload['question']['targets'][index]['dropBehaviorType'])
        for index, zone in enumerate(question['multiLanguageZones']):
            self.assertEqual(zone['reuse'],
                             payload['question']['zones'][index]['reuse'])
            self.assertEqual(zone['dropBehaviorType'],
                             payload['question']['zones'][index]['dropBehaviorType'])
            self.assertEqual(zone['visible'],
                             payload['question']['zones'][index]['visible'])
            self.assertEqual(zone['spatialUnit']['width'],
                             payload['question']['zones'][index]['spatialUnit']['width'])
            self.assertEqual(zone['spatialUnit']['height'],
                             payload['question']['zones'][index]['spatialUnit']['height'])
            self.assertEqual(zone['spatialUnit']['coordinateValues'],
                             payload['question']['zones'][index]['spatialUnit']['coordinateValues'])
            self.assertEqual(zone['spatialUnit']['recordTypes'][0],
                             payload['question']['zones'][index]['spatialUnit']['recordType'])

        # make sure the multi-language stuff comes out right in the question object_map
        self.assertIn('multiLanguageDroppables', question)
        for droppable in question['multiLanguageDroppables']:
            self.assertNotIn('text', droppable)
            self.assertIn('texts', droppable)
            self.assertNotIn('name', droppable)
            self.assertIn('names', droppable)
        for droppable in question['droppables']:
            self.assertIn('text', droppable)
            self.assertNotIn('texts', droppable)
            self.assertIn('name', droppable)
            self.assertNotIn('names', droppable)
        self.assertIn('multiLanguageTargets', question)
        for target in question['multiLanguageTargets']:
            self.assertNotIn('text', target)
            self.assertIn('texts', target)
            self.assertNotIn('name', target)
            self.assertIn('names', target)
        for target in question['targets']:
            self.assertIn('text', target)
            self.assertNotIn('texts', target)
            self.assertIn('name', target)
            self.assertNotIn('names', target)
        self.assertIn('multiLanguageZones', question)
        for zone in question['multiLanguageZones']:
            self.assertNotIn('name', zone)
            self.assertIn('names', zone)
            self.assertNotIn('description', zone)
            self.assertIn('descriptions', zone)
        for zone in question['zones']:
            self.assertIn('name', zone)
            self.assertNotIn('names', zone)
            self.assertIn('description', zone)
            self.assertNotIn('descriptions', zone)

        # check that the indices all got converted to the right IDs for question zones
        # and answer zone conditions
        # Especially important with the shuffling!
        expected_target_id = question['targets'][0]['id']
        for zone in question['zones']:
            self.assertEqual(zone['containerId'], expected_target_id)

    def test_can_add_answers_to_existing_item(self):
        item = self.create_item_without_question_or_answers()

        url = '{0}/{1}'.format(self.url,
                               item['id'])
        payload = {
            'answers': self._answers_payload()
        }

        req = self.app.put(url,
                           params=json.dumps(payload),
                           headers={'content-type': 'application/json'})
        self.ok(req)
        data = self.json(req)

        for answer in data['answers']:
            self.assertTrue(not any('qti' in r for r in answer['recordTypeIds']))

        # make sure the media files all show as URLs
        for answer in data['answers']:
            self.assertIn('/api/v1/repository/repositories', answer['feedback']['text'])
            self.assertIn('/stream', answer['feedback']['text'])
            self.assertIn('fileIds', answer)

        # check the answers
        self.assertEqual(len(data['answers']), 2)
        self.assertEqual(data['answers'][0]['genusTypeId'], str(RIGHT_ANSWER))
        self.assertEqual(data['answers'][1]['genusTypeId'], str(WRONG_ANSWER))
        for answer in data['answers']:
            self.assertEqual(len(answer['spatialUnitConditions']), 0)
            self.assertEqual(len(answer['coordinateConditions']), 0)
            self.assertEqual(len(answer['zoneConditions']), 2)

        # For the indices, in this case since no question exists,
        # we should expect no conversion.
        expected_droppable_0_id = 0
        expected_droppable_1_id = 1

        expected_zone_0_id = 0
        expected_zone_1_id = 1
        for answer in data['answers']:
            if answer['genusTypeId'] == str(RIGHT_ANSWER):
                for zone_condition in answer['zoneConditions']:
                    if zone_condition['droppableId'] == expected_droppable_0_id:
                        self.assertEqual(zone_condition['zoneId'],
                                         expected_zone_0_id)
                    else:
                        self.assertEqual(zone_condition['droppableId'],
                                         expected_droppable_1_id)
                        self.assertEqual(zone_condition['zoneId'],
                                         expected_zone_1_id)
            else:
                for zone_condition in answer['zoneConditions']:
                    if zone_condition['droppableId'] == expected_droppable_1_id:
                        self.assertEqual(zone_condition['zoneId'],
                                         expected_zone_0_id)
                    else:
                        self.assertEqual(zone_condition['droppableId'],
                                         expected_droppable_0_id)
                        self.assertEqual(zone_condition['zoneId'],
                                         expected_zone_1_id)

    def test_can_update_zone_name_with_new_language(self):
        item = self.create_item_with_question_and_answers()
        hindi_name = u'एक भूरा खरगोश'
        zone_0_id = item['question']['multiLanguageZones'][0]['id']
        payload = {
            'question': {
                'zones': [{
                    'id': zone_0_id,
                    'name': {
                        'text': hindi_name,
                        'formatTypeId': self._format_type,
                        'languageTypeId': self._hi_language_type,
                        'scriptTypeId': self._hi_script_type
                    }
                }]
            }
        }
        url = '{0}/{1}'.format(self.url, item['id'])
        req = self.app.put(url,
                           params=json.dumps(payload),
                           headers={'content-type': 'application/json'})
        self.ok(req)
        data = self.json(req)
        self.assertEqual(len(data['question']['multiLanguageZones']), 2)  # make sure this didn't increment
        self.assertEqual(len(data['question']['multiLanguageZones'][0]['names']), 2)
        self.assertTrue(any(n['text'] == hindi_name for n in data['question']['multiLanguageZones'][0]['names']))

        req = self.app.get(url)
        # zone text should be in English
        self.ok(req)
        data = self.json(req)
        zone = [z for z in data['question']['zones'] if z['id'] == zone_0_id][0]
        self.assertIn('Zone', zone['name'])

        req = self.app.get(url,
                           headers={'x-api-locale': 'hi'})
        # zone text should be in Hindi
        self.ok(req)
        data = self.json(req)
        zone = [z for z in data['question']['zones'] if z['id'] == zone_0_id][0]
        self.assertEqual(hindi_name, zone['name'])

    def test_can_update_zone_description_with_new_language(self):
        item = self.create_item_with_question_and_answers()
        hindi_description = u'एक भूरा खरगोश'
        zone_0_id = item['question']['multiLanguageZones'][0]['id']
        payload = {
            'question': {
                'zones': [{
                    'id': zone_0_id,
                    'description': {
                        'text': hindi_description,
                        'formatTypeId': self._format_type,
                        'languageTypeId': self._hi_language_type,
                        'scriptTypeId': self._hi_script_type
                    }
                }]
            }
        }
        url = '{0}/{1}'.format(self.url, item['id'])
        req = self.app.put(url,
                           params=json.dumps(payload),
                           headers={'content-type': 'application/json'})
        self.ok(req)
        data = self.json(req)
        self.assertEqual(len(data['question']['multiLanguageZones']), 2)  # make sure this didn't increment
        self.assertEqual(len(data['question']['multiLanguageZones'][0]['descriptions']), 2)
        self.assertTrue(any(d['text'] == hindi_description for d in data['question']['multiLanguageZones'][0]['descriptions']))

        req = self.app.get(url)
        # zone text should be in English
        self.ok(req)
        data = self.json(req)
        zone = [z for z in data['question']['zones'] if z['id'] == zone_0_id][0]
        self.assertIn('left', zone['description'])

        req = self.app.get(url,
                           headers={'x-api-locale': 'hi'})
        # zone text should be in Hindi
        self.ok(req)
        data = self.json(req)
        zone = [z for z in data['question']['zones'] if z['id'] == zone_0_id][0]
        self.assertEqual(hindi_description, zone['description'])

    def test_can_remove_zone_name_language(self):
        item = self.create_item_with_question_and_answers()
        hindi_name = u'एक भूरा खरगोश'
        zone_0_id = item['question']['multiLanguageZones'][0]['id']
        payload = {
            'question': {
                'zones': [{
                    'id': zone_0_id,
                    'name': {
                        'text': hindi_name,
                        'formatTypeId': self._format_type,
                        'languageTypeId': self._hi_language_type,
                        'scriptTypeId': self._hi_script_type
                    }
                }]
            }
        }
        url = '{0}/{1}'.format(self.url, item['id'])
        req = self.app.put(url,
                           params=json.dumps(payload),
                           headers={'content-type': 'application/json'})
        self.ok(req)

        payload = {
            'question': {
                'zones': [{
                    'id': zone_0_id,
                    'removeLanguageType': self._en_language_type,
                    'removeFromField': 'name'
                }]
            }
        }
        req = self.app.put(url,
                           params=json.dumps(payload),
                           headers={'content-type': 'application/json'})
        self.ok(req)
        data = self.json(req)

        self.assertEqual(len(data['question']['multiLanguageZones']), 2)  # make sure this didn't increment
        self.assertEqual(len(data['question']['multiLanguageZones'][0]['names']), 1)
        self.assertEqual(data['question']['multiLanguageZones'][0]['names'][0]['text'],
                         hindi_name)

        req = self.app.get(url)
        # zone text should be in Hindi because that's the only available language
        self.ok(req)
        data = self.json(req)
        zone = [z for z in data['question']['zones'] if z['id'] == zone_0_id][0]
        self.assertEqual(hindi_name, zone['name'])

    def test_can_remove_zone_description_language(self):
        item = self.create_item_with_question_and_answers()
        hindi_description = u'एक भूरा खरगोश'
        zone_0_id = item['question']['multiLanguageZones'][0]['id']
        payload = {
            'question': {
                'zones': [{
                    'id': zone_0_id,
                    'description': {
                        'text': hindi_description,
                        'formatTypeId': self._format_type,
                        'languageTypeId': self._hi_language_type,
                        'scriptTypeId': self._hi_script_type
                    }
                }]
            }
        }
        url = '{0}/{1}'.format(self.url, item['id'])
        req = self.app.put(url,
                           params=json.dumps(payload),
                           headers={'content-type': 'application/json'})
        self.ok(req)

        payload = {
            'question': {
                'zones': [{
                    'id': zone_0_id,
                    'removeLanguageType': self._en_language_type,
                    'removeFromField': 'description'
                }]
            }
        }
        req = self.app.put(url,
                           params=json.dumps(payload),
                           headers={'content-type': 'application/json'})
        self.ok(req)
        data = self.json(req)

        self.assertEqual(len(data['question']['multiLanguageZones']), 2)  # make sure this didn't increment
        self.assertEqual(len(data['question']['multiLanguageZones'][0]['descriptions']), 1)
        self.assertEqual(data['question']['multiLanguageZones'][0]['descriptions'][0]['text'],
                         hindi_description)

        req = self.app.get(url)
        # zone text should be in Hindi because that's the only available language
        self.ok(req)
        data = self.json(req)
        zone = [z for z in data['question']['zones'] if z['id'] == zone_0_id][0]
        self.assertEqual(hindi_description, zone['description'])

    def test_no_field_when_removing_language_for_zone_has_no_effect(self):
        item = self.create_item_with_question_and_answers()
        hindi_description = u'एक भूरा खरगोश'
        hindi_name = hindi_description
        zone_0_id = item['question']['multiLanguageZones'][0]['id']
        payload = {
            'question': {
                'zones': [{
                    'id': zone_0_id,
                    'name': {
                        'text': hindi_name,
                        'formatTypeId': self._format_type,
                        'languageTypeId': self._hi_language_type,
                        'scriptTypeId': self._hi_script_type
                    },
                    'description': {
                        'text': hindi_description,
                        'formatTypeId': self._format_type,
                        'languageTypeId': self._hi_language_type,
                        'scriptTypeId': self._hi_script_type
                    }
                }]
            }
        }
        url = '{0}/{1}'.format(self.url, item['id'])
        req = self.app.put(url,
                           params=json.dumps(payload),
                           headers={'content-type': 'application/json'})
        self.ok(req)

        payload = {
            'question': {
                'zones': [{
                    'id': zone_0_id,
                    'removeLanguageType': self._en_language_type
                }]
            }
        }
        req = self.app.put(url,
                           params=json.dumps(payload),
                           headers={'content-type': 'application/json'})
        self.ok(req)
        data = self.json(req)

        self.assertEqual(len(data['question']['multiLanguageZones']), 2)  # make sure this didn't increment
        self.assertEqual(len(data['question']['multiLanguageZones'][0]['descriptions']), 2)
        self.assertEqual(len(data['question']['multiLanguageZones'][0]['names']), 2)

        req = self.app.get(url)
        # zone text should be in English
        self.ok(req)
        data = self.json(req)
        zone = [z for z in data['question']['zones'] if z['id'] == zone_0_id][0]
        self.assertIn('left', zone['description'])
        self.assertIn('Zone', zone['name'])

        req = self.app.get(url,
                           headers={'x-api-locale': 'hi'})
        # zone text should be in Hindi
        self.ok(req)
        data = self.json(req)
        zone = [z for z in data['question']['zones'] if z['id'] == zone_0_id][0]
        self.assertEqual(hindi_description, zone['description'])
        self.assertEqual(hindi_description, zone['name'])

    def test_can_add_new_zone(self):
        item = self.create_item_with_question_and_answers()
        target_id = item['question']['targets'][0]['id']
        self.assertEqual(len(item['question']['multiLanguageZones']), 2)
        payload = {
            'question': {
                'zones': [{
                    'name': 'Zone 3',
                    'description': 'Foo zone',
                    'visible': False,
                    'reuse': 1,
                    'dropBehaviorType': SNAP_DROP_BEHAVIOR,
                    'spatialUnit': {
                        'recordType': 'osid.mapping.SpatialUnit%3Arectangle%40ODL.MIT.EDU',
                        'coordinateValues': [100, 100],
                        'width': 25,
                        'height': 25
                    },
                    'containerId': target_id
                }]
            }
        }
        url = '{0}/{1}'.format(self.url, item['id'])
        req = self.app.put(url,
                           params=json.dumps(payload),
                           headers={'content-type': 'application/json'})
        self.ok(req)
        data = self.json(req)
        self.assertEqual(len(data['question']['multiLanguageZones']), 3)
        new_zone = data['question']['multiLanguageZones'][2]
        self.assertEqual(new_zone['names'][0]['text'],
                         payload['question']['zones'][0]['name'])
        self.assertEqual(new_zone['descriptions'][0]['text'],
                         payload['question']['zones'][0]['description'])
        self.assertEqual(new_zone['visible'],
                         payload['question']['zones'][0]['visible'])
        self.assertEqual(new_zone['reuse'],
                         payload['question']['zones'][0]['reuse'])
        self.assertEqual(new_zone['dropBehaviorType'],
                         payload['question']['zones'][0]['dropBehaviorType'])
        self.assertEqual(new_zone['containerId'],
                         payload['question']['zones'][0]['containerId'])
        self.assertEqual(new_zone['spatialUnit']['coordinateValues'],
                         payload['question']['zones'][0]['spatialUnit']['coordinateValues'])
        self.assertEqual(new_zone['spatialUnit']['height'],
                         payload['question']['zones'][0]['spatialUnit']['height'])
        self.assertEqual(new_zone['spatialUnit']['width'],
                         payload['question']['zones'][0]['spatialUnit']['width'])

    def test_can_clear_zone_names(self):
        item = self.create_item_with_question_and_answers()
        zone_0_id = item['question']['multiLanguageZones'][0]['id']
        self.assertEqual(len(item['question']['multiLanguageZones'][0]['names']), 1)
        payload = {
            'question': {
                'clearZoneNames': [zone_0_id]
            }
        }
        url = '{0}/{1}'.format(self.url, item['id'])
        req = self.app.put(url,
                           params=json.dumps(payload),
                           headers={'content-type': 'application/json'})
        self.ok(req)
        data = self.json(req)
        self.assertEqual(len(data['question']['multiLanguageZones'][0]['names']), 0)
        self.assertEqual(data['question']['zones'][0]['name'], '')

    def test_can_clear_zone_descriptions(self):
        item = self.create_item_with_question_and_answers()
        zone_0_id = item['question']['multiLanguageZones'][0]['id']
        self.assertEqual(len(item['question']['multiLanguageZones'][0]['descriptions']), 1)
        payload = {
            'question': {
                'clearZoneDescriptions': [zone_0_id]
            }
        }
        url = '{0}/{1}'.format(self.url, item['id'])
        req = self.app.put(url,
                           params=json.dumps(payload),
                           headers={'content-type': 'application/json'})
        self.ok(req)
        data = self.json(req)
        self.assertEqual(len(data['question']['multiLanguageZones'][0]['descriptions']), 0)
        self.assertEqual(data['question']['zones'][0]['description'], '')

    def test_can_change_zone_visibility(self):
        item = self.create_item_with_question_and_answers()
        zone_0_id = item['question']['multiLanguageZones'][0]['id']
        new_visibility = not item['question']['multiLanguageZones'][0]['visible']
        payload = {
            'question': {
                'zones': [{
                    'id': zone_0_id,
                    'visible': new_visibility
                }]
            }
        }
        url = '{0}/{1}'.format(self.url, item['id'])
        req = self.app.put(url,
                           params=json.dumps(payload),
                           headers={'content-type': 'application/json'})
        self.ok(req)
        data = self.json(req)
        zone = [z for z in data['question']['zones'] if z['id'] == zone_0_id][0]
        self.assertEqual(zone['visible'], new_visibility)

    def test_can_change_zone_reuse(self):
        item = self.create_item_with_question_and_answers()
        zone_0_id = item['question']['multiLanguageZones'][0]['id']
        new_reuse = item['question']['multiLanguageZones'][0]['reuse'] + 2
        payload = {
            'question': {
                'zones': [{
                    'id': zone_0_id,
                    'reuse': new_reuse
                }]
            }
        }
        url = '{0}/{1}'.format(self.url, item['id'])
        req = self.app.put(url,
                           params=json.dumps(payload),
                           headers={'content-type': 'application/json'})
        self.ok(req)
        data = self.json(req)
        zone = [z for z in data['question']['zones'] if z['id'] == zone_0_id][0]
        self.assertEqual(zone['reuse'], new_reuse)

    def test_zone_reuse_cannot_be_negative(self):
        item = self.create_item_with_question_and_answers()
        zone_0_id = item['question']['multiLanguageZones'][0]['id']
        original_reuse = item['question']['multiLanguageZones'][0]['reuse']
        payload = {
            'question': {
                'zones': [{
                    'id': zone_0_id,
                    'reuse': -1
                }]
            }
        }
        url = '{0}/{1}'.format(self.url, item['id'])

        self.assertRaises(AppError,
                          self.app.put,
                          url,
                          json.dumps(payload),
                          {'content-type': 'application/json'})

        req = self.app.get(url)
        self.ok(req)
        data = self.json(req)
        zone = [z for z in data['question']['zones'] if z['id'] == zone_0_id][0]
        self.assertEqual(zone['reuse'], original_reuse)

    def test_zone_reuse_must_be_integer(self):
        item = self.create_item_with_question_and_answers()
        zone_0_id = item['question']['multiLanguageZones'][0]['id']
        original_reuse = item['question']['multiLanguageZones'][0]['reuse']
        payload = {
            'question': {
                'zones': [{
                    'id': zone_0_id,
                    'reuse': 'foo'
                }]
            }
        }
        url = '{0}/{1}'.format(self.url, item['id'])

        self.assertRaises(AppError,
                          self.app.put,
                          url,
                          json.dumps(payload),
                          {'content-type': 'application/json'})

        req = self.app.get(url)
        self.ok(req)
        data = self.json(req)
        zone = [z for z in data['question']['zones'] if z['id'] == zone_0_id][0]
        self.assertEqual(zone['reuse'], original_reuse)

    def test_can_change_zone_drop_behavior(self):
        item = self.create_item_with_question_and_answers()
        zone_0_id = item['question']['multiLanguageZones'][0]['id']
        new_drop_behavior = 'drop.behavior%3Abounce%40ODL.MIT.EDU'
        payload = {
            'question': {
                'zones': [{
                    'id': zone_0_id,
                    'dropBehaviorType': new_drop_behavior
                }]
            }
        }
        url = '{0}/{1}'.format(self.url, item['id'])
        req = self.app.put(url,
                           params=json.dumps(payload),
                           headers={'content-type': 'application/json'})
        self.ok(req)
        data = self.json(req)
        zone = [z for z in data['question']['zones'] if z['id'] == zone_0_id][0]
        self.assertEqual(zone['dropBehaviorType'], new_drop_behavior)

    def test_can_change_zone_spatial_unit(self):
        item = self.create_item_with_question_and_answers()
        zone_0_id = item['question']['multiLanguageZones'][0]['id']
        new_spatial_unit = {
            'recordType': 'osid.mapping.SpatialUnit%3Arectangle%40ODL.MIT.EDU',
            'coordinateValues': [-40, -40],
            'width': 10,
            'height': 10
        }
        payload = {
            'question': {
                'zones': [{
                    'id': zone_0_id,
                    'spatialUnit': new_spatial_unit
                }]
            }
        }
        url = '{0}/{1}'.format(self.url, item['id'])
        req = self.app.put(url,
                           params=json.dumps(payload),
                           headers={'content-type': 'application/json'})
        self.ok(req)
        data = self.json(req)
        zone = [z for z in data['question']['zones'] if z['id'] == zone_0_id][0]
        self.assertEqual(zone['spatialUnit']['coordinateValues'],
                         new_spatial_unit['coordinateValues'])
        self.assertEqual(zone['spatialUnit']['height'],
                         new_spatial_unit['height'])
        self.assertEqual(zone['spatialUnit']['width'],
                         new_spatial_unit['width'])

    def test_can_change_zone_container(self):
        item = self.create_item_with_question_and_answers()
        zone_0_id = item['question']['multiLanguageZones'][0]['id']
        new_container_id = '58ca8f8f8a80a74957609d15'
        payload = {
            'question': {
                'zones': [{
                    'id': zone_0_id,
                    'containerId': new_container_id
                }]
            }
        }
        url = '{0}/{1}'.format(self.url, item['id'])
        req = self.app.put(url,
                           params=json.dumps(payload),
                           headers={'content-type': 'application/json'})
        self.ok(req)
        data = self.json(req)
        zone = [z for z in data['question']['zones'] if z['id'] == zone_0_id][0]
        self.assertEqual(zone['containerId'], new_container_id)

    def test_can_delete_zone(self):
        item = self.create_item_with_question_and_answers()
        zone_0_id = item['question']['multiLanguageZones'][0]['id']
        payload = {
            'question': {
                'zones': [{
                    'id': zone_0_id,
                    'delete': True
                }]
            }
        }
        url = '{0}/{1}'.format(self.url, item['id'])
        req = self.app.put(url,
                           params=json.dumps(payload),
                           headers={'content-type': 'application/json'})
        self.ok(req)
        data = self.json(req)
        self.assertEqual(len(data['question']['zones']), 1)
        self.assertNotEqual(data['question']['zones'][0]['id'],
                            zone_0_id)

    def test_deleting_zone_requires_delete_flag_to_be_true(self):
        item = self.create_item_with_question_and_answers()
        zone_0_id = item['question']['multiLanguageZones'][0]['id']
        payload = {
            'question': {
                'zones': [{
                    'id': zone_0_id,
                    'delete': False
                }]
            }
        }
        url = '{0}/{1}'.format(self.url, item['id'])
        req = self.app.put(url,
                           params=json.dumps(payload),
                           headers={'content-type': 'application/json'})
        self.ok(req)
        data = self.json(req)
        self.assertEqual(len(data['question']['zones']), 2)
        self.assertEqual(data['question']['multiLanguageZones'][0]['id'],
                         zone_0_id)

    def test_can_delete_all_zones(self):
        item = self.create_item_with_question_and_answers()
        payload = {
            'question': {
                'clearZones': True
            }
        }
        url = '{0}/{1}'.format(self.url, item['id'])
        req = self.app.put(url,
                           params=json.dumps(payload),
                           headers={'content-type': 'application/json'})
        self.ok(req)
        data = self.json(req)
        self.assertEqual(len(data['question']['zones']), 0)
        self.assertEqual(len(data['question']['multiLanguageZones']), 0)

    def test_deleting_all_zones_requires_flag_to_be_true(self):
        item = self.create_item_with_question_and_answers()
        payload = {
            'question': {
                'clearZones': False
            }
        }
        url = '{0}/{1}'.format(self.url, item['id'])
        req = self.app.put(url,
                           params=json.dumps(payload),
                           headers={'content-type': 'application/json'})
        self.ok(req)
        data = self.json(req)
        self.assertEqual(len(data['question']['zones']), 2)
        self.assertEqual(len(data['question']['multiLanguageZones']), 2)

    def test_can_update_target_text_with_new_language(self):
        item = self.create_item_with_question_and_answers()
        hindi_text = u'ढलान'
        target_0_id = item['question']['multiLanguageTargets'][0]['id']
        payload = {
            'question': {
                'targets': [{
                    'id': target_0_id,
                    'text': {
                        'text': u'<p><img src="AssetContent:drag_and_drop_input_DPP-Concpt-BlkonRmp-Trgt_png" alt="{0}" /></p>'.format(hindi_text),
                        'formatTypeId': self._format_type,
                        'languageTypeId': self._hi_language_type,
                        'scriptTypeId': self._hi_script_type
                    }
                }]
            }
        }
        url = '{0}/{1}'.format(self.url, item['id'])
        req = self.app.put(url,
                           params=json.dumps(payload),
                           headers={'content-type': 'application/json'})
        self.ok(req)
        data = self.json(req)
        self.assertEqual(len(data['question']['multiLanguageTargets']), 1)  # make sure this didn't increment
        self.assertEqual(len(data['question']['multiLanguageTargets'][0]['texts']), 2)
        self.assertTrue(any(hindi_text in t['text'] for t in data['question']['multiLanguageTargets'][0]['texts']))

        req = self.app.get(url)
        # target text should be in English
        self.ok(req)
        data = self.json(req)
        target = [t for t in data['question']['targets'] if t['id'] == target_0_id][0]
        self.assertIn('Ramp', target['text'])
        self.assertNotIn(hindi_text, target['text'])

        req = self.app.get(url,
                           headers={'x-api-locale': 'hi'})
        # target text should be in Hindi
        self.ok(req)
        data = self.json(req)
        target = [t for t in data['question']['targets'] if t['id'] == target_0_id][0]
        self.assertNotIn('Ramp', target['text'])
        self.assertIn(hindi_text, target['text'])

    def test_can_update_target_name_with_new_language(self):
        item = self.create_item_with_question_and_answers()
        hindi_text = u'ढलान'
        target_0_id = item['question']['multiLanguageTargets'][0]['id']
        payload = {
            'question': {
                'targets': [{
                    'id': target_0_id,
                    'name': {
                        'text': hindi_text,
                        'formatTypeId': self._format_type,
                        'languageTypeId': self._hi_language_type,
                        'scriptTypeId': self._hi_script_type
                    }
                }]
            }
        }
        url = '{0}/{1}'.format(self.url, item['id'])
        req = self.app.put(url,
                           params=json.dumps(payload),
                           headers={'content-type': 'application/json'})
        self.ok(req)
        data = self.json(req)
        self.assertEqual(len(data['question']['multiLanguageTargets']), 1)  # make sure this didn't increment
        self.assertEqual(len(data['question']['multiLanguageTargets'][0]['names']), 2)
        self.assertTrue(any(hindi_text == n['text'] for n in data['question']['multiLanguageTargets'][0]['names']))

        req = self.app.get(url)
        # target text should be in English
        self.ok(req)
        data = self.json(req)
        target = [t for t in data['question']['targets'] if t['id'] == target_0_id][0]
        self.assertEqual('Image of ramp', target['name'])
        self.assertNotEqual(hindi_text, target['name'])

        req = self.app.get(url,
                           headers={'x-api-locale': 'hi'})
        # target text should be in Hindi
        self.ok(req)
        data = self.json(req)
        target = [t for t in data['question']['targets'] if t['id'] == target_0_id][0]
        self.assertNotEqual('Image of ramp', target['name'])
        self.assertEqual(hindi_text, target['name'])

    def test_can_remove_target_text_language(self):
        item = self.create_item_with_question_and_answers()
        hindi_text = u'ढलान'
        target_0_id = item['question']['multiLanguageTargets'][0]['id']
        payload = {
            'question': {
                'targets': [{
                    'id': target_0_id,
                    'text': {
                        'text': u'<p><img src="AssetContent:drag_and_drop_input_DPP-Concpt-BlkonRmp-Trgt_png" alt="{0}" /></p>'.format(hindi_text),
                        'formatTypeId': self._format_type,
                        'languageTypeId': self._hi_language_type,
                        'scriptTypeId': self._hi_script_type
                    }
                }]
            }
        }
        url = '{0}/{1}'.format(self.url, item['id'])
        req = self.app.put(url,
                           params=json.dumps(payload),
                           headers={'content-type': 'application/json'})
        self.ok(req)

        payload = {
            'question': {
                'targets': [{
                    'id': target_0_id,
                    'removeLanguageType': self._en_language_type,
                    'removeFromField': 'text'
                }]
            }
        }
        req = self.app.put(url,
                           params=json.dumps(payload),
                           headers={'content-type': 'application/json'})
        self.ok(req)
        data = self.json(req)

        self.assertEqual(len(data['question']['multiLanguageTargets']), 1)  # make sure this didn't increment
        self.assertEqual(len(data['question']['multiLanguageTargets'][0]['texts']), 1)
        self.assertIn(hindi_text,
                      data['question']['multiLanguageTargets'][0]['texts'][0]['text'])

        req = self.app.get(url)
        # zone text should be in Hindi because that's the only available language
        self.ok(req)
        data = self.json(req)
        target = [t for t in data['question']['targets'] if t['id'] == target_0_id][0]
        self.assertNotIn('Ramp', target['text'])
        self.assertIn(hindi_text, target['text'])

    def test_can_remove_target_name_language(self):
        item = self.create_item_with_question_and_answers()
        hindi_text = u'ढलान'
        target_0_id = item['question']['multiLanguageTargets'][0]['id']
        payload = {
            'question': {
                'targets': [{
                    'id': target_0_id,
                    'name': {
                        'text': hindi_text,
                        'formatTypeId': self._format_type,
                        'languageTypeId': self._hi_language_type,
                        'scriptTypeId': self._hi_script_type
                    }
                }]
            }
        }
        url = '{0}/{1}'.format(self.url, item['id'])
        req = self.app.put(url,
                           params=json.dumps(payload),
                           headers={'content-type': 'application/json'})
        self.ok(req)

        payload = {
            'question': {
                'targets': [{
                    'id': target_0_id,
                    'removeLanguageType': self._en_language_type,
                    'removeFromField': 'name'
                }]
            }
        }
        req = self.app.put(url,
                           params=json.dumps(payload),
                           headers={'content-type': 'application/json'})
        self.ok(req)
        data = self.json(req)

        self.assertEqual(len(data['question']['multiLanguageTargets']), 1)  # make sure this didn't increment
        self.assertEqual(len(data['question']['multiLanguageTargets'][0]['names']), 1)
        self.assertEqual(hindi_text,
                         data['question']['multiLanguageTargets'][0]['names'][0]['text'])

        req = self.app.get(url)
        # zone text should be in Hindi because that's the only available language
        self.ok(req)
        data = self.json(req)
        target = [t for t in data['question']['targets'] if t['id'] == target_0_id][0]
        self.assertEqual(hindi_text, target['name'])

    def test_can_add_new_target(self):
        item = self.create_item_with_question_and_answers()
        self.assertEqual(len(item['question']['multiLanguageTargets']), 1)
        payload = {
            'question': {
                'targets': [{
                    'text': '<p><img src="AssetContent:drag_and_drop_input_DPP-Concpt-BlkonRmp-Trgt_png" alt="Ski slope" /></p>',
                    'name': 'Image of ski slope',
                    'dropBehaviorType': DROP_DROP_BEHAVIOR
                }]
            }
        }
        url = '{0}/{1}'.format(self.url, item['id'])
        req = self.app.put(url,
                           params=json.dumps(payload),
                           headers={'content-type': 'application/json'})
        self.ok(req)
        data = self.json(req)
        self.assertEqual(len(data['question']['multiLanguageTargets']), 2)
        new_target = data['question']['multiLanguageTargets'][1]
        self.assertIn('Ski slope', new_target['texts'][0]['text'])
        self.assertEqual(new_target['names'][0]['text'],
                         payload['question']['targets'][0]['name'])
        self.assertEqual(new_target['dropBehaviorType'],
                         payload['question']['targets'][0]['dropBehaviorType'])

    def test_can_clear_target_texts(self):
        item = self.create_item_with_question_and_answers()
        self.assertEqual(len(item['question']['multiLanguageTargets'][0]['texts']), 1)
        target_0_id = item['question']['multiLanguageTargets'][0]['id']
        payload = {
            'question': {
                'clearTargetTexts': [target_0_id]
            }
        }
        url = '{0}/{1}'.format(self.url, item['id'])
        req = self.app.put(url,
                           params=json.dumps(payload),
                           headers={'content-type': 'application/json'})
        self.ok(req)
        data = self.json(req)
        self.assertEqual(len(data['question']['multiLanguageTargets'][0]['texts']), 0)
        self.assertEqual(data['question']['targets'][0]['text'], '')

    def test_can_clear_target_names(self):
        item = self.create_item_with_question_and_answers()
        self.assertEqual(len(item['question']['multiLanguageTargets'][0]['names']), 1)
        target_0_id = item['question']['multiLanguageTargets'][0]['id']
        payload = {
            'question': {
                'clearTargetNames': [target_0_id]
            }
        }
        url = '{0}/{1}'.format(self.url, item['id'])
        req = self.app.put(url,
                           params=json.dumps(payload),
                           headers={'content-type': 'application/json'})
        self.ok(req)
        data = self.json(req)
        self.assertEqual(len(data['question']['multiLanguageTargets'][0]['names']), 0)
        self.assertEqual(data['question']['targets'][0]['name'], '')

    def test_can_change_target_name(self):
        item = self.create_item_with_question_and_answers()
        target_0_id = item['question']['multiLanguageTargets'][0]['id']
        new_name = 'Image of cheese wedge'
        payload = {
            'question': {
                'targets': [{
                    'id': target_0_id,
                    'name': new_name
                }]
            }
        }
        url = '{0}/{1}'.format(self.url, item['id'])
        req = self.app.put(url,
                           params=json.dumps(payload),
                           headers={'content-type': 'application/json'})
        self.ok(req)
        data = self.json(req)
        target = [t for t in data['question']['targets'] if t['id'] == target_0_id][0]
        self.assertEqual(target['name'], new_name)

    def test_can_change_target_drop_behavior(self):
        item = self.create_item_with_question_and_answers()
        target_0_id = item['question']['multiLanguageTargets'][0]['id']
        new_drop_behavior = 'drop.behavior%3Abounce%40ODL.MIT.EDU'
        payload = {
            'question': {
                'targets': [{
                    'id': target_0_id,
                    'dropBehaviorType': new_drop_behavior
                }]
            }
        }
        url = '{0}/{1}'.format(self.url, item['id'])
        req = self.app.put(url,
                           params=json.dumps(payload),
                           headers={'content-type': 'application/json'})
        self.ok(req)
        data = self.json(req)
        target = [t for t in data['question']['targets'] if t['id'] == target_0_id][0]
        self.assertEqual(target['dropBehaviorType'], new_drop_behavior)

    def test_can_delete_target(self):
        item = self.create_item_with_question_and_answers()
        target_0_id = item['question']['multiLanguageTargets'][0]['id']
        payload = {
            'question': {
                'targets': [{
                    'id': target_0_id,
                    'delete': True
                }]
            }
        }
        url = '{0}/{1}'.format(self.url, item['id'])
        req = self.app.put(url,
                           params=json.dumps(payload),
                           headers={'content-type': 'application/json'})
        self.ok(req)
        data = self.json(req)
        self.assertEqual(len(data['question']['targets']), 0)

    def test_deleting_target_requires_delete_flag_to_be_true(self):
        item = self.create_item_with_question_and_answers()
        target_0_id = item['question']['multiLanguageTargets'][0]['id']
        payload = {
            'question': {
                'targets': [{
                    'id': target_0_id,
                    'delete': False
                }]
            }
        }
        url = '{0}/{1}'.format(self.url, item['id'])
        req = self.app.put(url,
                           params=json.dumps(payload),
                           headers={'content-type': 'application/json'})
        self.ok(req)
        data = self.json(req)
        self.assertEqual(len(data['question']['targets']), 1)
        self.assertEqual(data['question']['targets'][0]['id'], target_0_id)

    def test_can_delete_all_targets(self):
        item = self.create_item_with_question_and_answers()
        payload = {
            'question': {
                'clearTargets': True
            }
        }
        url = '{0}/{1}'.format(self.url, item['id'])
        req = self.app.put(url,
                           params=json.dumps(payload),
                           headers={'content-type': 'application/json'})
        self.ok(req)
        data = self.json(req)
        self.assertEqual(len(data['question']['targets']), 0)
        self.assertEqual(len(data['question']['multiLanguageTargets']), 0)

    def test_deleting_all_targets_requires_flag_to_be_true(self):
        item = self.create_item_with_question_and_answers()
        payload = {
            'question': {
                'clearTargets': False
            }
        }
        url = '{0}/{1}'.format(self.url, item['id'])
        req = self.app.put(url,
                           params=json.dumps(payload),
                           headers={'content-type': 'application/json'})
        self.ok(req)
        data = self.json(req)
        self.assertEqual(len(data['question']['targets']), 1)
        self.assertEqual(len(data['question']['multiLanguageTargets']), 1)

    def test_can_update_droppable_text_with_new_language(self):
        item = self.create_item_with_question_and_answers()
        hindi_text = u'हरा बिंदु'
        droppable_0_id = item['question']['multiLanguageDroppables'][0]['id']
        payload = {
            'question': {
                'droppables': [{
                    'id': droppable_0_id,
                    'text': {
                        'text': u'<p><img src="AssetContent:draggable_green_dot_png" alt="{0}" /></p>'.format(hindi_text),
                        'formatTypeId': self._format_type,
                        'languageTypeId': self._hi_language_type,
                        'scriptTypeId': self._hi_script_type
                    }
                }]
            }
        }
        url = '{0}/{1}'.format(self.url, item['id'])
        req = self.app.put(url,
                           params=json.dumps(payload),
                           headers={'content-type': 'application/json'})
        self.ok(req)
        data = self.json(req)
        self.assertEqual(len(data['question']['multiLanguageDroppables']), 2)  # make sure this didn't increment
        self.assertEqual(len(data['question']['multiLanguageDroppables'][0]['texts']), 2)
        self.assertTrue(any(hindi_text in t['text'] for t in data['question']['multiLanguageDroppables'][0]['texts']))

        req = self.app.get(url)
        # target text should be in English
        self.ok(req)
        data = self.json(req)
        droppable = [d for d in data['question']['droppables'] if d['id'] == droppable_0_id][0]
        self.assertIn('Green dot', droppable['text'])
        self.assertNotIn(hindi_text, droppable['text'])

        req = self.app.get(url,
                           headers={'x-api-locale': 'hi'})
        # target text should be in Hindi
        self.ok(req)
        data = self.json(req)
        droppable = [d for d in data['question']['droppables'] if d['id'] == droppable_0_id][0]
        self.assertNotIn('Green dot', droppable['text'])
        self.assertIn(hindi_text, droppable['text'])

    def test_can_update_droppable_name_with_new_language(self):
        item = self.create_item_with_question_and_answers()
        hindi_text = u'हरा बिंदु'
        droppable_0_id = item['question']['multiLanguageDroppables'][0]['id']
        payload = {
            'question': {
                'droppables': [{
                    'id': droppable_0_id,
                    'name': {
                        'text': hindi_text,
                        'formatTypeId': self._format_type,
                        'languageTypeId': self._hi_language_type,
                        'scriptTypeId': self._hi_script_type
                    }
                }]
            }
        }
        url = '{0}/{1}'.format(self.url, item['id'])
        req = self.app.put(url,
                           params=json.dumps(payload),
                           headers={'content-type': 'application/json'})
        self.ok(req)
        data = self.json(req)
        self.assertEqual(len(data['question']['multiLanguageDroppables']), 2)  # make sure this didn't increment
        self.assertEqual(len(data['question']['multiLanguageDroppables'][0]['names']), 2)
        self.assertTrue(any(hindi_text == n['text'] for n in data['question']['multiLanguageDroppables'][0]['names']))

        req = self.app.get(url)
        # target text should be in English
        self.ok(req)
        data = self.json(req)
        droppable = [d for d in data['question']['droppables'] if d['id'] == droppable_0_id][0]
        self.assertEqual('Green dot', droppable['name'])
        self.assertNotEqual(hindi_text, droppable['name'])

        req = self.app.get(url,
                           headers={'x-api-locale': 'hi'})
        # target text should be in Hindi
        self.ok(req)
        data = self.json(req)
        droppable = [d for d in data['question']['droppables'] if d['id'] == droppable_0_id][0]
        self.assertNotEqual('Green dot', droppable['name'])
        self.assertEqual(hindi_text, droppable['name'])

    def test_can_remove_droppable_text_language(self):
        item = self.create_item_with_question_and_answers()
        hindi_text = u'हरा बिंदु'
        droppable_0_id = item['question']['multiLanguageDroppables'][0]['id']
        payload = {
            'question': {
                'droppables': [{
                    'id': droppable_0_id,
                    'text': {
                        'text': u'<p><img src="AssetContent:draggable_green_dot_png" alt="{0}" /></p>'.format(hindi_text),
                        'formatTypeId': self._format_type,
                        'languageTypeId': self._hi_language_type,
                        'scriptTypeId': self._hi_script_type
                    }
                }]
            }
        }
        url = '{0}/{1}'.format(self.url, item['id'])
        req = self.app.put(url,
                           params=json.dumps(payload),
                           headers={'content-type': 'application/json'})
        self.ok(req)

        payload = {
            'question': {
                'droppables': [{
                    'id': droppable_0_id,
                    'removeLanguageType': self._en_language_type,
                    'removeFromField': 'text'
                }]
            }
        }
        req = self.app.put(url,
                           params=json.dumps(payload),
                           headers={'content-type': 'application/json'})
        self.ok(req)
        data = self.json(req)

        self.assertEqual(len(data['question']['multiLanguageDroppables']), 2)  # make sure this didn't increment
        self.assertEqual(len(data['question']['multiLanguageDroppables'][0]['texts']), 1)
        self.assertIn(hindi_text,
                      data['question']['multiLanguageDroppables'][0]['texts'][0]['text'])

        req = self.app.get(url)
        # zone text should be in Hindi because that's the only available language
        self.ok(req)
        data = self.json(req)
        droppable = [d for d in data['question']['droppables'] if d['id'] == droppable_0_id][0]
        self.assertNotIn('Green dot', droppable['text'])
        self.assertIn(hindi_text, droppable['text'])

    def test_can_remove_droppable_name_language(self):
        item = self.create_item_with_question_and_answers()
        hindi_text = u'हरा बिंदु'
        droppable_0_id = item['question']['multiLanguageDroppables'][0]['id']
        payload = {
            'question': {
                'droppables': [{
                    'id': droppable_0_id,
                    'name': {
                        'text': hindi_text,
                        'formatTypeId': self._format_type,
                        'languageTypeId': self._hi_language_type,
                        'scriptTypeId': self._hi_script_type
                    }
                }]
            }
        }
        url = '{0}/{1}'.format(self.url, item['id'])
        req = self.app.put(url,
                           params=json.dumps(payload),
                           headers={'content-type': 'application/json'})
        self.ok(req)

        payload = {
            'question': {
                'droppables': [{
                    'id': droppable_0_id,
                    'removeLanguageType': self._en_language_type,
                    'removeFromField': 'name'
                }]
            }
        }
        req = self.app.put(url,
                           params=json.dumps(payload),
                           headers={'content-type': 'application/json'})
        self.ok(req)
        data = self.json(req)

        self.assertEqual(len(data['question']['multiLanguageDroppables']), 2)  # make sure this didn't increment
        self.assertEqual(len(data['question']['multiLanguageDroppables'][0]['names']), 1)
        self.assertEqual(hindi_text,
                         data['question']['multiLanguageDroppables'][0]['names'][0]['text'])

        req = self.app.get(url)
        # zone text should be in Hindi because that's the only available language
        self.ok(req)
        data = self.json(req)
        droppable = [d for d in data['question']['droppables'] if d['id'] == droppable_0_id][0]
        self.assertEqual(hindi_text, droppable['name'])

    def test_can_add_new_droppable(self):
        item = self.create_item_with_question_and_answers()
        self.assertEqual(len(item['question']['multiLanguageDroppables']), 2)
        payload = {
            'question': {
                'droppables': [{
                    'text': '<p><img src="AssetContent:draggable_red_dot_png" alt="Watermelon" /></p>',
                    'name': 'Image of watermelon',
                    'dropBehaviorType': DROP_DROP_BEHAVIOR
                }]
            }
        }
        url = '{0}/{1}'.format(self.url, item['id'])
        req = self.app.put(url,
                           params=json.dumps(payload),
                           headers={'content-type': 'application/json'})
        self.ok(req)
        data = self.json(req)
        self.assertEqual(len(data['question']['multiLanguageDroppables']), 3)
        new_droppable = data['question']['multiLanguageDroppables'][2]
        self.assertIn('Watermelon', new_droppable['texts'][0]['text'])
        self.assertEqual(new_droppable['names'][0]['text'],
                         payload['question']['droppables'][0]['name'])
        self.assertEqual(new_droppable['dropBehaviorType'],
                         payload['question']['droppables'][0]['dropBehaviorType'])

    def test_can_clear_droppable_texts(self):
        item = self.create_item_with_question_and_answers()
        self.assertEqual(len(item['question']['multiLanguageDroppables'][0]['texts']), 1)
        droppable_0_id = item['question']['multiLanguageDroppables'][0]['id']
        payload = {
            'question': {
                'clearDroppableTexts': [droppable_0_id]
            }
        }
        url = '{0}/{1}'.format(self.url, item['id'])
        req = self.app.put(url,
                           params=json.dumps(payload),
                           headers={'content-type': 'application/json'})
        self.ok(req)
        data = self.json(req)
        self.assertEqual(len(data['question']['multiLanguageDroppables'][0]['texts']), 0)
        self.assertEqual(data['question']['droppables'][0]['text'], '')

    def test_can_clear_droppable_names(self):
        item = self.create_item_with_question_and_answers()
        self.assertEqual(len(item['question']['multiLanguageDroppables'][0]['names']), 1)
        droppable_0_id = item['question']['multiLanguageDroppables'][0]['id']
        payload = {
            'question': {
                'clearDroppableNames': [droppable_0_id]
            }
        }
        url = '{0}/{1}'.format(self.url, item['id'])
        req = self.app.put(url,
                           params=json.dumps(payload),
                           headers={'content-type': 'application/json'})
        self.ok(req)
        data = self.json(req)
        self.assertEqual(len(data['question']['multiLanguageDroppables'][0]['names']), 0)
        self.assertEqual(data['question']['droppables'][0]['name'], '')

    def test_can_change_droppable_reuse(self):
        item = self.create_item_with_question_and_answers()
        droppable_0_id = item['question']['multiLanguageDroppables'][0]['id']
        new_reuse = item['question']['multiLanguageDroppables'][0]['reuse'] + 2
        payload = {
            'question': {
                'droppables': [{
                    'id': droppable_0_id,
                    'reuse': new_reuse
                }]
            }
        }
        url = '{0}/{1}'.format(self.url, item['id'])
        req = self.app.put(url,
                           params=json.dumps(payload),
                           headers={'content-type': 'application/json'})
        self.ok(req)
        data = self.json(req)
        droppable = [d for d in data['question']['droppables'] if d['id'] == droppable_0_id][0]
        self.assertEqual(droppable['reuse'], new_reuse)

    def test_droppable_reuse_cannot_be_negative(self):
        item = self.create_item_with_question_and_answers()
        droppable_0_id = item['question']['multiLanguageDroppables'][0]['id']
        original_reuse = item['question']['multiLanguageDroppables'][0]['reuse']
        payload = {
            'question': {
                'droppables': [{
                    'id': droppable_0_id,
                    'reuse': -1
                }]
            }
        }
        url = '{0}/{1}'.format(self.url, item['id'])

        self.assertRaises(AppError,
                          self.app.put,
                          url,
                          json.dumps(payload),
                          {'content-type': 'application/json'})

        req = self.app.get(url)
        self.ok(req)
        data = self.json(req)
        droppable = [d for d in data['question']['droppables'] if d['id'] == droppable_0_id][0]
        self.assertEqual(droppable['reuse'], original_reuse)

    def test_droppable_reuse_must_be_integer(self):
        item = self.create_item_with_question_and_answers()
        droppable_0_id = item['question']['multiLanguageDroppables'][0]['id']
        original_reuse = item['question']['multiLanguageDroppables'][0]['reuse']
        payload = {
            'question': {
                'droppables': [{
                    'id': droppable_0_id,
                    'reuse': 'foo'
                }]
            }
        }
        url = '{0}/{1}'.format(self.url, item['id'])

        self.assertRaises(AppError,
                          self.app.put,
                          url,
                          json.dumps(payload),
                          {'content-type': 'application/json'})

        req = self.app.get(url)
        self.ok(req)
        data = self.json(req)
        droppable = [d for d in data['question']['droppables'] if d['id'] == droppable_0_id][0]
        self.assertEqual(droppable['reuse'], original_reuse)

    def test_can_delete_droppable(self):
        item = self.create_item_with_question_and_answers()
        droppable_0_id = item['question']['multiLanguageDroppables'][0]['id']
        payload = {
            'question': {
                'droppables': [{
                    'id': droppable_0_id,
                    'delete': True
                }]
            }
        }
        url = '{0}/{1}'.format(self.url, item['id'])
        req = self.app.put(url,
                           params=json.dumps(payload),
                           headers={'content-type': 'application/json'})
        self.ok(req)
        data = self.json(req)
        self.assertEqual(len(data['question']['droppables']), 1)
        self.assertNotEqual(data['question']['droppables'][0]['id'],
                            droppable_0_id)

    def test_deleting_droppable_requires_delete_flag_to_be_true(self):
        item = self.create_item_with_question_and_answers()
        droppable_0_id = item['question']['multiLanguageDroppables'][0]['id']
        payload = {
            'question': {
                'droppables': [{
                    'id': droppable_0_id,
                    'delete': False
                }]
            }
        }
        url = '{0}/{1}'.format(self.url, item['id'])
        req = self.app.put(url,
                           params=json.dumps(payload),
                           headers={'content-type': 'application/json'})
        self.ok(req)
        data = self.json(req)
        self.assertEqual(len(data['question']['droppables']), 2)
        self.assertEqual(data['question']['droppables'][0]['id'], droppable_0_id)

    def test_can_delete_all_droppables(self):
        item = self.create_item_with_question_and_answers()
        payload = {
            'question': {
                'clearDroppables': True
            }
        }
        url = '{0}/{1}'.format(self.url, item['id'])
        req = self.app.put(url,
                           params=json.dumps(payload),
                           headers={'content-type': 'application/json'})
        self.ok(req)
        data = self.json(req)
        self.assertEqual(len(data['question']['droppables']), 0)
        self.assertEqual(len(data['question']['multiLanguageDroppables']), 0)

    def test_deleting_all_droppables_requires_flag_to_be_true(self):
        item = self.create_item_with_question_and_answers()
        payload = {
            'question': {
                'clearDroppables': False
            }
        }
        url = '{0}/{1}'.format(self.url, item['id'])
        req = self.app.put(url,
                           params=json.dumps(payload),
                           headers={'content-type': 'application/json'})
        self.ok(req)
        data = self.json(req)
        self.assertEqual(len(data['question']['droppables']), 2)
        self.assertEqual(len(data['question']['multiLanguageDroppables']), 2)

    def test_can_add_new_file_to_question(self):
        item = self.create_item_with_question_and_answers()

        payload = {
            'question': {
                'fileIds': {}
            }
        }

        media_files = [self._draggable3]

        assets = {}
        for media_file in media_files:
            label = self._label(self._filename(media_file))
            assets[label] = self.upload_media_file(media_file)

        for label, asset in assets.iteritems():
            payload['question']['fileIds'][label] = {}
            payload['question']['fileIds'][label]['assetId'] = asset['id']
            payload['question']['fileIds'][label]['assetContentId'] = asset['assetContents'][0]['id']
            payload['question']['fileIds'][label]['assetContentTypeId'] = asset['assetContents'][0]['genusTypeId']

        url = '{0}/{1}'.format(self.url,
                               item['id'])

        req = self.app.put(url,
                           params=json.dumps(payload),
                           headers={'content-type': 'application/json'})
        self.ok(req)
        data = self.json(req)

        self.assertIn('draggable_h1i_PNG', data['question']['fileIds'])

    def test_can_toggle_shuffle_droppables(self):
        item = self.create_item_with_question_and_answers()
        original_shuffle_droppables = item['question']['shuffleDroppables']

        payload = {
            'question': {
                'shuffleDroppables': not original_shuffle_droppables
            }
        }

        url = '{0}/{1}'.format(self.url,
                               item['id'])

        req = self.app.put(url,
                           params=json.dumps(payload),
                           headers={'content-type': 'application/json'})
        self.ok(req)
        data = self.json(req)

        self.assertNotEqual(data['question']['shuffleDroppables'],
                            original_shuffle_droppables)

        payload = {
            'question': {
                'shuffleDroppables': original_shuffle_droppables
            }
        }

        req = self.app.put(url,
                           params=json.dumps(payload),
                           headers={'content-type': 'application/json'})
        self.ok(req)
        data = self.json(req)

        self.assertEqual(data['question']['shuffleDroppables'],
                         original_shuffle_droppables)

    def test_can_toggle_shuffle_targets(self):
        item = self.create_item_with_question_and_answers()
        original_shuffle_targets = item['question']['shuffleTargets']

        payload = {
            'question': {
                'shuffleTargets': not original_shuffle_targets
            }
        }

        url = '{0}/{1}'.format(self.url,
                               item['id'])

        req = self.app.put(url,
                           params=json.dumps(payload),
                           headers={'content-type': 'application/json'})
        self.ok(req)
        data = self.json(req)

        self.assertNotEqual(data['question']['shuffleTargets'],
                            original_shuffle_targets)

        payload = {
            'question': {
                'shuffleTargets': original_shuffle_targets
            }
        }

        req = self.app.put(url,
                           params=json.dumps(payload),
                           headers={'content-type': 'application/json'})
        self.ok(req)
        data = self.json(req)

        self.assertEqual(data['question']['shuffleTargets'],
                         original_shuffle_targets)

    def test_can_toggle_shuffle_zones(self):
        item = self.create_item_with_question_and_answers()
        original_shuffle_zones = item['question']['shuffleZones']

        payload = {
            'question': {
                'shuffleZones': not original_shuffle_zones
            }
        }

        url = '{0}/{1}'.format(self.url,
                               item['id'])

        req = self.app.put(url,
                           params=json.dumps(payload),
                           headers={'content-type': 'application/json'})
        self.ok(req)
        data = self.json(req)

        self.assertNotEqual(data['question']['shuffleZones'],
                            original_shuffle_zones)

        payload = {
            'question': {
                'shuffleZones': original_shuffle_zones
            }
        }

        req = self.app.put(url,
                           params=json.dumps(payload),
                           headers={'content-type': 'application/json'})
        self.ok(req)
        data = self.json(req)

        self.assertEqual(data['question']['shuffleZones'],
                         original_shuffle_zones)

    def test_can_set_target_order(self):
        item = self.create_item_with_question_and_answers()
        payload = {
            'question': {
                'targets': [{
                    'text': '<p><img src="AssetContent:drag_and_drop_input_DPP-Concpt-BlkonRmp-Trgt_png" alt="Ski slope" /></p>',
                    'name': 'Image of ski slope',
                    'dropBehaviorType': DROP_DROP_BEHAVIOR
                }]
            }
        }
        url = '{0}/{1}'.format(self.url, item['id'])
        req = self.app.put(url,
                           params=json.dumps(payload),
                           headers={'content-type': 'application/json'})
        self.ok(req)
        data = self.json(req)

        original_targets_order = [t for t in data['question']['targets']]

        reversed_order = []
        # this extended slice returns the list in reverse order
        for index, target in enumerate(original_targets_order[::-1]):
            target['order'] = index
            reversed_order.append(target)

        payload = {
            'question': {
                'targets': reversed_order
            }
        }

        req = self.app.put(url,
                           params=json.dumps(payload),
                           headers={'content-type': 'application/json'})
        self.ok(req)
        data = self.json(req)

        original_target_ids_order = [t['id'] for t in original_targets_order]
        updated_target_ids_order = [t['id'] for t in data['question']['multiLanguageTargets']]

        # check same length
        self.assertEqual(len(updated_target_ids_order),
                         len(original_target_ids_order))

        # check same elements
        self.assertEqual(set(updated_target_ids_order),
                         set(original_target_ids_order))

        # but check order not equal
        self.assertNotEqual(original_target_ids_order,
                            updated_target_ids_order)

    def test_can_set_target_order_with_duplicate_ids(self):
        item = self.create_item_with_question_and_answers()
        payload = {
            'question': {
                'targets': [{
                    'text': '<p><img src="AssetContent:drag_and_drop_input_DPP-Concpt-BlkonRmp-Trgt_png" alt="Ski slope" /></p>',
                    'name': 'Image of ski slope',
                    'dropBehaviorType': DROP_DROP_BEHAVIOR
                }]
            }
        }
        url = '{0}/{1}'.format(self.url, item['id'])
        req = self.app.put(url,
                           params=json.dumps(payload),
                           headers={'content-type': 'application/json'})
        self.ok(req)
        data = self.json(req)

        original_targets_order = [t for t in data['question']['targets']]

        reversed_order = []
        # this extended slice returns the list in reverse order
        for index, target in enumerate(original_targets_order[::-1]):
            target['order'] = index
            reversed_order.append(target)

        reversed_order.append(deepcopy(reversed_order[0]))
        reversed_order[-1]['order'] = len(reversed_order)

        payload = {
            'question': {
                'targets': reversed_order
            }
        }

        req = self.app.put(url,
                           params=json.dumps(payload),
                           headers={'content-type': 'application/json'})
        self.ok(req)
        data = self.json(req)

        original_target_ids_order = [t['id'] for t in original_targets_order]
        updated_target_ids_order = [t['id'] for t in data['question']['multiLanguageTargets']]

        # check same length
        self.assertEqual(len(updated_target_ids_order),
                         len(original_target_ids_order))

        # check same elements
        self.assertEqual(set(updated_target_ids_order),
                         set(original_target_ids_order))

        # but check order not equal
        self.assertNotEqual(original_target_ids_order,
                            updated_target_ids_order)

    def test_can_set_droppable_order(self):
        item = self.create_item_with_question_and_answers()
        original_droppables_order = [d for d in item['question']['droppables']]

        reversed_order = []
        # this extended slice returns the list in reverse order
        for index, droppable in enumerate(original_droppables_order[::-1]):
            droppable['order'] = index
            reversed_order.append(droppable)

        payload = {
            'question': {
                'droppables': reversed_order
            }
        }
        url = '{0}/{1}'.format(self.url, item['id'])
        req = self.app.put(url,
                           params=json.dumps(payload),
                           headers={'content-type': 'application/json'})
        self.ok(req)
        data = self.json(req)

        original_droppable_ids_order = [d['id'] for d in original_droppables_order]
        updated_droppable_ids_order = [d['id'] for d in data['question']['multiLanguageDroppables']]

        # check same length
        self.assertEqual(len(updated_droppable_ids_order),
                         len(original_droppable_ids_order))

        # check same elements
        self.assertEqual(set(updated_droppable_ids_order),
                         set(original_droppable_ids_order))

        # but check order not equal
        self.assertNotEqual(original_droppable_ids_order,
                            updated_droppable_ids_order)

    def test_can_set_droppable_order_with_duplicate_ids(self):
        item = self.create_item_with_question_and_answers()
        original_droppables_order = [d for d in item['question']['droppables']]

        reversed_order = []
        # this extended slice returns the list in reverse order
        for index, droppable in enumerate(original_droppables_order[::-1]):
            droppable['order'] = index
            reversed_order.append(droppable)

        reversed_order.append(deepcopy(reversed_order[0]))
        reversed_order[-1]['order'] = len(reversed_order)

        payload = {
            'question': {
                'droppables': reversed_order
            }
        }
        url = '{0}/{1}'.format(self.url, item['id'])
        req = self.app.put(url,
                           params=json.dumps(payload),
                           headers={'content-type': 'application/json'})
        self.ok(req)
        data = self.json(req)

        original_droppable_ids_order = [d['id'] for d in original_droppables_order]
        updated_droppable_ids_order = [d['id'] for d in data['question']['multiLanguageDroppables']]

        # check same length
        self.assertEqual(len(updated_droppable_ids_order),
                         len(original_droppable_ids_order))

        # check same elements
        self.assertEqual(set(updated_droppable_ids_order),
                         set(original_droppable_ids_order))

        # but check order not equal
        self.assertNotEqual(original_droppable_ids_order,
                            updated_droppable_ids_order)

    def test_can_set_zone_order(self):
        item = self.create_item_with_question_and_answers()
        original_zones_order = [d for d in item['question']['zones']]

        reversed_order = []
        # this extended slice returns the list in reverse order
        for index, zone in enumerate(original_zones_order[::-1]):
            zone['order'] = index
            reversed_order.append(zone)

        payload = {
            'question': {
                'zones': reversed_order
            }
        }
        url = '{0}/{1}'.format(self.url, item['id'])
        req = self.app.put(url,
                           params=json.dumps(payload),
                           headers={'content-type': 'application/json'})
        self.ok(req)
        data = self.json(req)

        original_zone_ids_order = [d['id'] for d in original_zones_order]
        updated_zone_ids_order = [d['id'] for d in data['question']['multiLanguageZones']]

        # check same length
        self.assertEqual(len(updated_zone_ids_order),
                         len(original_zone_ids_order))

        # check same elements
        self.assertEqual(set(updated_zone_ids_order),
                         set(original_zone_ids_order))

        # but check order not equal
        self.assertNotEqual(original_zone_ids_order,
                            updated_zone_ids_order)

    def test_can_set_zone_order_with_duplicate_ids(self):
        item = self.create_item_with_question_and_answers()
        original_zones_order = [d for d in item['question']['zones']]

        reversed_order = []
        # this extended slice returns the list in reverse order
        for index, zone in enumerate(original_zones_order[::-1]):
            zone['order'] = index
            reversed_order.append(zone)

        reversed_order.append(deepcopy(reversed_order[0]))
        reversed_order[-1]['order'] = len(reversed_order)

        payload = {
            'question': {
                'zones': reversed_order
            }
        }
        url = '{0}/{1}'.format(self.url, item['id'])
        req = self.app.put(url,
                           params=json.dumps(payload),
                           headers={'content-type': 'application/json'})
        self.ok(req)
        data = self.json(req)

        original_zone_ids_order = [d['id'] for d in original_zones_order]
        updated_zone_ids_order = [d['id'] for d in data['question']['multiLanguageZones']]

        # check same length
        self.assertEqual(len(updated_zone_ids_order),
                         len(original_zone_ids_order))

        # check same elements
        self.assertEqual(set(updated_zone_ids_order),
                         set(original_zone_ids_order))

        # but check order not equal
        self.assertNotEqual(original_zone_ids_order,
                            updated_zone_ids_order)

    def test_can_replace_answer_zone_conditions(self):
        item = self.create_item_with_question_and_answers()
        answer_id = item['answers'][0]['id']
        zone_0_id = item['question']['multiLanguageZones'][0]['id']
        droppable_1_id = item['question']['multiLanguageDroppables'][1]['id']

        self.assertEqual(len(item['answers'][0]['zoneConditions']), 2)

        payload = {
            'answers': [{
                'id': answer_id,
                'zoneConditions': [{
                    'zoneId': zone_0_id,
                    'droppableId': droppable_1_id
                }]
            }]
        }

        url = '{0}/{1}'.format(self.url, item['id'])
        req = self.app.put(url,
                           params=json.dumps(payload),
                           headers={'content-type': 'application/json'})
        self.ok(req)
        data = self.json(req)
        self.assertEqual(len(data['answers'][0]['zoneConditions']), 1)
        self.assertEqual(data['answers'][0]['zoneConditions'][0]['zoneId'],
                         zone_0_id)
        self.assertEqual(data['answers'][0]['zoneConditions'][0]['droppableId'],
                         droppable_1_id)

    def test_can_clear_answer_zone_conditions(self):
        item = self.create_item_with_question_and_answers()
        answer_id = item['answers'][0]['id']

        self.assertEqual(len(item['answers'][0]['zoneConditions']), 2)

        payload = {
            'answers': [{
                'id': answer_id,
                'clearZoneConditions': True
            }]
        }

        url = '{0}/{1}'.format(self.url, item['id'])
        req = self.app.put(url,
                           params=json.dumps(payload),
                           headers={'content-type': 'application/json'})
        self.ok(req)
        data = self.json(req)
        self.assertEqual(len(data['answers'][0]['zoneConditions']), 0)

    def test_clearing_answer_zone_conditions_requires_flag_to_be_true(self):
        item = self.create_item_with_question_and_answers()
        answer_id = item['answers'][0]['id']

        self.assertEqual(len(item['answers'][0]['zoneConditions']), 2)

        payload = {
            'answers': [{
                'id': answer_id,
                'clearZoneConditions': False
            }]
        }

        url = '{0}/{1}'.format(self.url, item['id'])
        req = self.app.put(url,
                           params=json.dumps(payload),
                           headers={'content-type': 'application/json'})
        self.ok(req)
        data = self.json(req)

        self.assertEqual(len(data['answers'][0]['zoneConditions']), 2)

    def test_can_replace_answer_spatial_unit_conditions(self):
        item = self.create_item_with_question_and_answers()
        answer_id = item['answers'][0]['id']
        target_0_id = item['question']['multiLanguageTargets'][0]['id']
        droppable_1_id = item['question']['multiLanguageDroppables'][1]['id']

        self.assertEqual(len(item['answers'][0]['spatialUnitConditions']), 0)

        payload = {
            'answers': [{
                'id': answer_id,
                'spatialUnitConditions': [{
                    'containerId': target_0_id,
                    'droppableId': droppable_1_id,
                    'spatialUnit': {
                        'recordType': 'osid.mapping.SpatialUnit%3Arectangle%40ODL.MIT.EDU',
                        'coordinateValues': [0, 0],
                        'width': 50,
                        'height': 30
                    }
                }]
            }]
        }

        url = '{0}/{1}'.format(self.url, item['id'])
        req = self.app.put(url,
                           params=json.dumps(payload),
                           headers={'content-type': 'application/json'})
        self.ok(req)
        data = self.json(req)
        self.assertEqual(len(data['answers'][0]['spatialUnitConditions']), 1)
        self.assertEqual(data['answers'][0]['spatialUnitConditions'][0]['containerId'],
                         target_0_id)
        self.assertEqual(data['answers'][0]['spatialUnitConditions'][0]['droppableId'],
                         droppable_1_id)
        self.assertEqual(data['answers'][0]['spatialUnitConditions'][0]['spatialUnit']['coordinateValues'],
                         payload['answers'][0]['spatialUnitConditions'][0]['spatialUnit']['coordinateValues'])
        self.assertEqual(data['answers'][0]['spatialUnitConditions'][0]['spatialUnit']['height'],
                         payload['answers'][0]['spatialUnitConditions'][0]['spatialUnit']['height'])
        self.assertEqual(data['answers'][0]['spatialUnitConditions'][0]['spatialUnit']['width'],
                         payload['answers'][0]['spatialUnitConditions'][0]['spatialUnit']['width'])

    def test_can_clear_answer_spatial_unit_conditions(self):
        item = self.create_item_with_question_and_answers()
        answer_id = item['answers'][0]['id']
        target_0_id = item['question']['multiLanguageTargets'][0]['id']
        droppable_1_id = item['question']['multiLanguageDroppables'][1]['id']

        self.assertEqual(len(item['answers'][0]['spatialUnitConditions']), 0)

        payload = {
            'answers': [{
                'id': answer_id,
                'spatialUnitConditions': [{
                    'containerId': target_0_id,
                    'droppableId': droppable_1_id,
                    'spatialUnit': {
                        'recordType': 'osid.mapping.SpatialUnit%3Arectangle%40ODL.MIT.EDU',
                        'coordinateValues': [0, 0],
                        'width': 50,
                        'height': 30
                    }
                }]
            }]
        }

        url = '{0}/{1}'.format(self.url, item['id'])
        req = self.app.put(url,
                           params=json.dumps(payload),
                           headers={'content-type': 'application/json'})
        self.ok(req)
        data = self.json(req)
        self.assertEqual(len(data['answers'][0]['spatialUnitConditions']), 1)

        payload = {
            'answers': [{
                'id': answer_id,
                'clearSpatialUnitConditions': True
            }]
        }

        req = self.app.put(url,
                           params=json.dumps(payload),
                           headers={'content-type': 'application/json'})
        self.ok(req)
        data = self.json(req)
        self.assertEqual(len(data['answers'][0]['spatialUnitConditions']), 0)

    def test_clearing_answer_spatial_unit_conditions_requires_flag_to_be_true(self):
        item = self.create_item_with_question_and_answers()
        answer_id = item['answers'][0]['id']
        target_0_id = item['question']['multiLanguageTargets'][0]['id']
        droppable_1_id = item['question']['multiLanguageDroppables'][1]['id']

        self.assertEqual(len(item['answers'][0]['spatialUnitConditions']), 0)

        payload = {
            'answers': [{
                'id': answer_id,
                'spatialUnitConditions': [{
                    'containerId': target_0_id,
                    'droppableId': droppable_1_id,
                    'spatialUnit': {
                        'recordType': 'osid.mapping.SpatialUnit%3Arectangle%40ODL.MIT.EDU',
                        'coordinateValues': [0, 0],
                        'width': 50,
                        'height': 30
                    }
                }]
            }]
        }

        url = '{0}/{1}'.format(self.url, item['id'])
        req = self.app.put(url,
                           params=json.dumps(payload),
                           headers={'content-type': 'application/json'})
        self.ok(req)
        data = self.json(req)
        self.assertEqual(len(data['answers'][0]['spatialUnitConditions']), 1)

        payload = {
            'answers': [{
                'id': answer_id,
                'clearSpatialUnitConditions': False
            }]
        }

        req = self.app.put(url,
                           params=json.dumps(payload),
                           headers={'content-type': 'application/json'})
        self.ok(req)
        data = self.json(req)
        self.assertEqual(len(data['answers'][0]['spatialUnitConditions']), 1)

    def test_can_replace_answer_coordinate_conditions(self):
        item = self.create_item_with_question_and_answers()
        answer_id = item['answers'][0]['id']
        target_0_id = item['question']['multiLanguageTargets'][0]['id']
        droppable_1_id = item['question']['multiLanguageDroppables'][1]['id']

        self.assertEqual(len(item['answers'][0]['coordinateConditions']), 0)

        payload = {
            'answers': [{
                'id': answer_id,
                'coordinateConditions': [{
                    'containerId': target_0_id,
                    'droppableId': droppable_1_id,
                    'coordinateValues': [0, 0]
                }]
            }]
        }

        url = '{0}/{1}'.format(self.url, item['id'])
        req = self.app.put(url,
                           params=json.dumps(payload),
                           headers={'content-type': 'application/json'})
        self.ok(req)
        data = self.json(req)
        self.assertEqual(len(data['answers'][0]['coordinateConditions']), 1)
        self.assertEqual(data['answers'][0]['coordinateConditions'][0]['containerId'],
                         target_0_id)
        self.assertEqual(data['answers'][0]['coordinateConditions'][0]['droppableId'],
                         droppable_1_id)
        self.assertEqual(data['answers'][0]['coordinateConditions'][0]['coordinate'],
                         payload['answers'][0]['coordinateConditions'][0]['coordinateValues'])

    def test_can_clear_answer_coordinate_conditions(self):
        item = self.create_item_with_question_and_answers()
        answer_id = item['answers'][0]['id']
        target_0_id = item['question']['multiLanguageTargets'][0]['id']
        droppable_1_id = item['question']['multiLanguageDroppables'][1]['id']

        self.assertEqual(len(item['answers'][0]['coordinateConditions']), 0)

        payload = {
            'answers': [{
                'id': answer_id,
                'coordinateConditions': [{
                    'containerId': target_0_id,
                    'droppableId': droppable_1_id,
                    'coordinateValues': [0, 0]
                }]
            }]
        }

        url = '{0}/{1}'.format(self.url, item['id'])
        req = self.app.put(url,
                           params=json.dumps(payload),
                           headers={'content-type': 'application/json'})
        self.ok(req)
        data = self.json(req)
        self.assertEqual(len(data['answers'][0]['coordinateConditions']), 1)

        payload = {
            'answers': [{
                'id': answer_id,
                'clearCoordinateConditions': True
            }]
        }

        req = self.app.put(url,
                           params=json.dumps(payload),
                           headers={'content-type': 'application/json'})
        self.ok(req)
        data = self.json(req)
        self.assertEqual(len(data['answers'][0]['coordinateConditions']), 0)

    def test_clearing_answer_coordinate_conditions_requires_flag_to_be_true(self):
        item = self.create_item_with_question_and_answers()
        answer_id = item['answers'][0]['id']
        target_0_id = item['question']['multiLanguageTargets'][0]['id']
        droppable_1_id = item['question']['multiLanguageDroppables'][1]['id']

        self.assertEqual(len(item['answers'][0]['coordinateConditions']), 0)

        payload = {
            'answers': [{
                'id': answer_id,
                'coordinateConditions': [{
                    'containerId': target_0_id,
                    'droppableId': droppable_1_id,
                    'coordinateValues': [0, 0]
                }]
            }]
        }

        url = '{0}/{1}'.format(self.url, item['id'])
        req = self.app.put(url,
                           params=json.dumps(payload),
                           headers={'content-type': 'application/json'})
        self.ok(req)
        data = self.json(req)
        self.assertEqual(len(data['answers'][0]['coordinateConditions']), 1)

        payload = {
            'answers': [{
                'id': answer_id,
                'clearCoordinateConditions': False
            }]
        }

        req = self.app.put(url,
                           params=json.dumps(payload),
                           headers={'content-type': 'application/json'})
        self.ok(req)
        data = self.json(req)
        self.assertEqual(len(data['answers'][0]['coordinateConditions']), 1)


class DeleteTests(BaseDragAndDropTestCase):
    """Can delete item / answer RESTfully"""
    def test_can_delete_drag_and_drop_item(self):
        item = self.create_item_with_question_and_answers()
        url = '{0}/{1}'.format(self.url,
                               item['id'])
        req = self.app.delete(url)
        self.ok(req)

        self.assertRaises(AppError,
                          self.app.get,
                          url)

    def test_can_remove_answer(self):
        item = self.create_item_with_question_and_answers()
        answer_id = item['answers'][0]['id']
        self.assertEqual(len(item['answers']), 2)
        url = '{0}/{1}'.format(self.url,
                               item['id'])

        payload = {
            'answers': [{
                'id': answer_id,
                'delete': True
            }]
        }
        req = self.app.put(url,
                           params=json.dumps(payload),
                           headers={'content-type': 'application/json'})
        self.ok(req)
        data = self.json(req)

        self.assertEqual(len(data['answers']), 1)
        self.assertNotEqual(data['answers'][0]['id'], answer_id)

    def test_removing_answer_requires_delete_flag_to_be_true(self):
        item = self.create_item_with_question_and_answers()
        answer_id = item['answers'][0]['id']
        self.assertEqual(len(item['answers']), 2)
        url = '{0}/{1}'.format(self.url,
                               item['id'])

        payload = {
            'answers': [{
                'id': answer_id,
                'delete': False
            }]
        }
        req = self.app.put(url,
                           params=json.dumps(payload),
                           headers={'content-type': 'application/json'})
        self.ok(req)
        data = self.json(req)

        self.assertEqual(len(data['answers']), 2)
        self.assertTrue(any(a['id'] == answer_id for a in data['answers']))


class AuthoringGetTests(BaseDragAndDropTestCase):
    def test_can_get_item_with_no_question_or_answers_from_item_list(self):
        item = self.create_item_without_question_or_answers()

        req = self.app.get(self.url)
        self.ok(req)
        data = self.json(req)
        self.assertEqual(len(data), 1)
        self.assertEqual(data[0]['id'],
                         item['id'])

        self.assertEqual(data[0]['genusTypeId'], str(DRAG_AND_DROP_ITEM_GENUS_TYPE))

        req = self.app.get('{0}?qti'.format(self.url))
        self.ok(req)
        data = self.json(req)
        self.assertEqual(len(data), 1)
        self.assertEqual(data[0]['id'],
                         item['id'])

        self.assertEqual(data[0]['genusTypeId'], str(DRAG_AND_DROP_ITEM_GENUS_TYPE))

    def test_can_get_item_with_no_question_or_answers_from_assessment_items_list(self):
        item = self.create_item_without_question_or_answers()

        assessment = self.create_assessment_for_item(self._bank.ident, item['id'])
        assessment_items_url = '/api/v1/assessment/banks/{0}/assessments/{1}/items'.format(str(self._bank.ident),
                                                                                           str(assessment.ident))

        req = self.app.get(assessment_items_url)
        self.ok(req)
        data = self.json(req)
        self.assertEqual(len(data), 1)
        self.assertEqual(data[0]['id'],
                         item['id'])

        self.assertEqual(data[0]['genusTypeId'], str(DRAG_AND_DROP_ITEM_GENUS_TYPE))

        assessment_items_url = '/api/v1/assessment/banks/{0}/assessments/{1}/items?qti'.format(str(self._bank.ident),
                                                                                               str(assessment.ident))

        req = self.app.get(assessment_items_url)
        self.ok(req)
        data = self.json(req)
        self.assertEqual(len(data), 1)
        self.assertEqual(data[0]['id'],
                         item['id'])

        self.assertEqual(data[0]['genusTypeId'], str(DRAG_AND_DROP_ITEM_GENUS_TYPE))

    def test_can_get_item_with_no_question_or_answers_from_item_details(self):
        item = self.create_item_without_question_or_answers()

        url = '{0}/{1}'.format(self.url, item['id'])

        req = self.app.get(url)
        self.ok(req)
        data = self.json(req)
        self.assertEqual(data['id'],
                         item['id'])

        self.assertEqual(data['genusTypeId'], str(DRAG_AND_DROP_ITEM_GENUS_TYPE))

    def test_can_get_item_with_question_but_no_answers_from_item_list(self):
        item = self.create_item_with_question_but_no_answers()

        req = self.app.get(self.url)
        self.ok(req)
        data = self.json(req)
        self.assertEqual(len(data), 1)
        self.assertEqual(data[0]['id'],
                         item['id'])

        self.assertEqual(data[0]['genusTypeId'], str(DRAG_AND_DROP_ITEM_GENUS_TYPE))
        self.assertEqual(data[0]['question']['genusTypeId'], str(DRAG_AND_DROP_QUESTION_GENUS_TYPE))

        req = self.app.get('{0}?qti'.format(self.url))
        self.ok(req)
        data = self.json(req)
        self.assertEqual(len(data), 1)
        self.assertEqual(data[0]['id'],
                         item['id'])

        self.assertEqual(data[0]['genusTypeId'], str(DRAG_AND_DROP_ITEM_GENUS_TYPE))
        self.assertEqual(data[0]['question']['genusTypeId'], str(DRAG_AND_DROP_QUESTION_GENUS_TYPE))

    def test_can_get_item_with_question_but_no_answers_from_assessment_items_list(self):
        item = self.create_item_with_question_but_no_answers()

        assessment = self.create_assessment_for_item(self._bank.ident, item['id'])
        assessment_items_url = '/api/v1/assessment/banks/{0}/assessments/{1}/items'.format(str(self._bank.ident),
                                                                                           str(assessment.ident))

        req = self.app.get(assessment_items_url)
        self.ok(req)
        data = self.json(req)
        self.assertEqual(len(data), 1)
        self.assertEqual(data[0]['id'],
                         item['id'])

        self.assertEqual(data[0]['genusTypeId'], str(DRAG_AND_DROP_ITEM_GENUS_TYPE))
        self.assertEqual(data[0]['question']['genusTypeId'], str(DRAG_AND_DROP_QUESTION_GENUS_TYPE))

        assessment_items_url = '/api/v1/assessment/banks/{0}/assessments/{1}/items?qti'.format(str(self._bank.ident),
                                                                                               str(assessment.ident))

        req = self.app.get(assessment_items_url)
        self.ok(req)
        data = self.json(req)
        self.assertEqual(len(data), 1)
        self.assertEqual(data[0]['id'],
                         item['id'])

        self.assertEqual(data[0]['genusTypeId'], str(DRAG_AND_DROP_ITEM_GENUS_TYPE))
        self.assertEqual(data[0]['question']['genusTypeId'], str(DRAG_AND_DROP_QUESTION_GENUS_TYPE))

    def test_can_get_item_with_question_but_no_answers_from_item_details(self):
        item = self.create_item_with_question_but_no_answers()

        url = '{0}/{1}'.format(self.url, item['id'])

        req = self.app.get(url)
        self.ok(req)
        data = self.json(req)
        self.assertEqual(data['id'],
                         item['id'])

        self.assertEqual(data['genusTypeId'], str(DRAG_AND_DROP_ITEM_GENUS_TYPE))
        self.assertEqual(data['question']['genusTypeId'], str(DRAG_AND_DROP_QUESTION_GENUS_TYPE))

    def test_can_get_item_with_question_and_answers_from_item_list(self):
        item = self.create_item_with_question_and_answers()

        req = self.app.get(self.url)
        self.ok(req)
        data = self.json(req)
        self.assertEqual(len(data), 1)
        self.assertEqual(data[0]['id'],
                         item['id'])

        self.assertEqual(data[0]['genusTypeId'], str(DRAG_AND_DROP_ITEM_GENUS_TYPE))
        self.assertEqual(data[0]['question']['genusTypeId'], str(DRAG_AND_DROP_QUESTION_GENUS_TYPE))

        req = self.app.get('{0}?qti'.format(self.url))
        self.ok(req)
        data = self.json(req)
        self.assertEqual(len(data), 1)
        self.assertEqual(data[0]['id'],
                         item['id'])

        self.assertEqual(data[0]['genusTypeId'], str(DRAG_AND_DROP_ITEM_GENUS_TYPE))
        self.assertEqual(data[0]['question']['genusTypeId'], str(DRAG_AND_DROP_QUESTION_GENUS_TYPE))

    def test_can_get_item_with_question_and_answers_from_assessment_items_list(self):
        item = self.create_item_with_question_and_answers()

        assessment = self.create_assessment_for_item(self._bank.ident, item['id'])
        assessment_items_url = '/api/v1/assessment/banks/{0}/assessments/{1}/items'.format(str(self._bank.ident),
                                                                                           str(assessment.ident))

        req = self.app.get(assessment_items_url)
        self.ok(req)
        data = self.json(req)
        self.assertEqual(len(data), 1)
        self.assertEqual(data[0]['id'],
                         item['id'])

        self.assertEqual(data[0]['genusTypeId'], str(DRAG_AND_DROP_ITEM_GENUS_TYPE))
        self.assertEqual(data[0]['question']['genusTypeId'], str(DRAG_AND_DROP_QUESTION_GENUS_TYPE))

        assessment_items_url = '/api/v1/assessment/banks/{0}/assessments/{1}/items?qti'.format(str(self._bank.ident),
                                                                                               str(assessment.ident))

        req = self.app.get(assessment_items_url)
        self.ok(req)
        data = self.json(req)
        self.assertEqual(len(data), 1)
        self.assertEqual(data[0]['id'],
                         item['id'])

        self.assertEqual(data[0]['genusTypeId'], str(DRAG_AND_DROP_ITEM_GENUS_TYPE))
        self.assertEqual(data[0]['question']['genusTypeId'], str(DRAG_AND_DROP_QUESTION_GENUS_TYPE))

    def test_can_get_item_with_question_and_answers_from_item_details(self):
        item = self.create_item_with_question_and_answers()

        url = '{0}/{1}'.format(self.url, item['id'])

        req = self.app.get(url)
        self.ok(req)
        data = self.json(req)
        self.assertEqual(data['id'],
                         item['id'])

        self.assertEqual(data['genusTypeId'], str(DRAG_AND_DROP_ITEM_GENUS_TYPE))
        self.assertEqual(data['question']['genusTypeId'], str(DRAG_AND_DROP_QUESTION_GENUS_TYPE))

    def test_shuffled_droppables_do_not_shuffle_for_authoring(self):
        def check_droppables_not_shuffled(_url):
            num_different = 0

            for i in range(0, 15):
                req2 = self.app.get(_url)
                self.ok(req2)
                data2 = self.json(req2)
                if isinstance(data2, list):
                    data2 = [d for d in data2 if d['id'] == data['id']][0]
                droppable_ids_order_2 = [d['id'] for d in data2['question']['droppables']]

                if original_droppable_ids_order != droppable_ids_order_2:
                    num_different += 1
            self.assertTrue(num_different == 0)

        def check_droppables_are_shuffled(_url):
            num_different = 0

            for i in range(0, 15):
                req2 = self.app.get(_url)
                self.ok(req2)
                data2 = self.json(req2)
                if isinstance(data2, list):
                    data2 = [d for d in data2 if d['id'] == data['id']][0]
                droppable_ids_order_2 = [d['id'] for d in data2['question']['droppables']]

                if original_droppable_ids_order != droppable_ids_order_2:
                    num_different += 1
            self.assertTrue(num_different > 0)

        payload = self._item_payload()
        payload['question'] = self._question_payload()
        payload['answers'] = self._answers_payload()

        req = self.app.post(self.url,
                            params=json.dumps(payload),
                            headers={'content-type': 'application/json'})
        self.ok(req)
        data = self.json(req)
        self.assertTrue(data['question']['shuffleDroppables'])
        original_droppable_ids_order = [d['id'] for d in data['question']['multiLanguageDroppables']]

        check_droppables_are_shuffled('{0}'.format(self.url))
        check_droppables_not_shuffled('{0}?unshuffled'.format(self.url))

        item_url = '{0}/{1}'.format(self.url,
                                    data['id'])

        check_droppables_not_shuffled(item_url)

        assessment = self.create_assessment_for_item(self._bank.ident, data['id'])
        assessment_items_url = '/api/v1/assessment/banks/{0}/assessments/{1}/items'.format(str(self._bank.ident),
                                                                                           str(assessment.ident))

        check_droppables_not_shuffled(assessment_items_url)

    def test_shuffled_targets_do_not_shuffle_for_authoring(self):
        def check_targets_not_shuffled(_url):
            num_different = 0

            for i in range(0, 15):
                req2 = self.app.get(_url)
                self.ok(req2)
                data2 = self.json(req2)
                if isinstance(data2, list):
                    data2 = [d for d in data2 if d['id'] == data['id']][0]
                target_ids_order_2 = [t['id'] for t in data2['question']['targets']]

                if original_target_ids_order != target_ids_order_2:
                    num_different += 1
            self.assertTrue(num_different == 0)

        def check_targets_are_shuffled(_url):
            num_different = 0

            for i in range(0, 15):
                req2 = self.app.get(_url)
                self.ok(req2)
                data2 = self.json(req2)
                if isinstance(data2, list):
                    data2 = [d for d in data2 if d['id'] == data['id']][0]
                target_ids_order_2 = [t['id'] for t in data2['question']['targets']]

                if original_target_ids_order != target_ids_order_2:
                    num_different += 1
            self.assertTrue(num_different > 0)

        payload = self._item_payload()
        payload['question'] = self._question_payload()
        payload['question']['shuffleTargets'] = True

        # let's make two targets for this test to see if they don't shuffle
        payload['question']['targets'].append(payload['question']['targets'][0])

        payload['answers'] = self._answers_payload()

        req = self.app.post(self.url,
                            params=json.dumps(payload),
                            headers={'content-type': 'application/json'})
        self.ok(req)
        data = self.json(req)
        self.assertTrue(data['question']['shuffleTargets'])
        original_target_ids_order = [t['id'] for t in data['question']['multiLanguageTargets']]

        self.assertEqual(len(original_target_ids_order), 2)

        check_targets_are_shuffled('{0}'.format(self.url))
        check_targets_not_shuffled('{0}?unshuffled'.format(self.url))

        item_url = '{0}/{1}'.format(self.url,
                                    data['id'])

        check_targets_not_shuffled(item_url)

        assessment = self.create_assessment_for_item(self._bank.ident, data['id'])
        assessment_items_url = '/api/v1/assessment/banks/{0}/assessments/{1}/items'.format(str(self._bank.ident),
                                                                                           str(assessment.ident))

        check_targets_not_shuffled(assessment_items_url)

    def test_shuffled_zones_do_not_shuffle_for_authoring(self):
        def check_zones_not_shuffled(_url):
            num_different = 0

            for i in range(0, 15):
                req2 = self.app.get(_url)
                self.ok(req2)
                data2 = self.json(req2)
                if isinstance(data2, list):
                    data2 = [d for d in data2 if d['id'] == data['id']][0]
                zone_ids_order_2 = [z['id'] for z in data2['question']['zones']]

                if original_zone_ids_order != zone_ids_order_2:
                    num_different += 1
            self.assertTrue(num_different == 0)

        def check_zones_are_shuffled(_url):
            num_different = 0

            for i in range(0, 15):
                req2 = self.app.get(_url)
                self.ok(req2)
                data2 = self.json(req2)
                if isinstance(data2, list):
                    data2 = [d for d in data2 if d['id'] == data['id']][0]
                zone_ids_order_2 = [z['id'] for z in data2['question']['zones']]

                if original_zone_ids_order != zone_ids_order_2:
                    num_different += 1
            self.assertTrue(num_different > 0)

        payload = self._item_payload()
        payload['question'] = self._question_payload()
        payload['answers'] = self._answers_payload()

        req = self.app.post(self.url,
                            params=json.dumps(payload),
                            headers={'content-type': 'application/json'})
        self.ok(req)
        data = self.json(req)
        self.assertTrue(data['question']['shuffleZones'])
        original_zone_ids_order = [t['id'] for t in data['question']['multiLanguageZones']]

        self.assertEqual(len(original_zone_ids_order), 2)

        check_zones_are_shuffled('{0}'.format(self.url))
        check_zones_not_shuffled('{0}?unshuffled'.format(self.url))

        item_url = '{0}/{1}'.format(self.url,
                                    data['id'])

        check_zones_not_shuffled(item_url)

        assessment = self.create_assessment_for_item(self._bank.ident, data['id'])
        assessment_items_url = '/api/v1/assessment/banks/{0}/assessments/{1}/items'.format(str(self._bank.ident),
                                                                                           str(assessment.ident))

        check_zones_not_shuffled(assessment_items_url)


class SingleTargetTakingTests(BaseDragAndDropTestCase):
    """Can submit right / wrong answers to a drag-and-drop question"""
    def test_shuffled_droppables_do_shuffle_when_taking(self):
        def check_droppables_are_shuffled(_offered):
            num_different = 0

            for i in range(0, 15):
                create_taken_url = '/api/v1/assessment/banks/{0}/assessmentsoffered/{1}/assessmentstaken'.format(str(self._bank.ident),
                                                                                                                 str(_offered.ident))
                req = self.app.post(create_taken_url)
                self.ok(req)
                taken = self.json(req)

                taken_questions_url = '/api/v1/assessment/banks/{0}/assessmentstaken/{1}/questions'.format(str(self._bank.ident),
                                                                                                           taken['id'])
                req2 = self.app.get(taken_questions_url)
                self.ok(req2)
                data2 = self.json(req2)['data']
                if isinstance(data2, list):
                    data2 = data2[0]  # only one question in this assessment...id's won't match
                droppable_ids_order_2 = [d['id'] for d in data2['droppables']]

                if original_droppable_ids_order != droppable_ids_order_2:
                    num_different += 1

                # now delete the taken
                delete_taken_url = '/api/v1/assessment/banks/{0}/assessmentstaken/{1}'.format(str(self._bank.ident),
                                                                                              taken['id'])
                req = self.app.delete(delete_taken_url)
                self.ok(req)

            self.assertTrue(num_different > 0)

        item = self.create_item_with_question_and_answers()
        self.assertTrue(item['question']['shuffleDroppables'])
        original_droppable_ids_order = [d['id'] for d in item['question']['multiLanguageDroppables']]

        offered = self.create_assessment_offered_for_item(self._bank.ident, item['id'])

        check_droppables_are_shuffled(offered)

    # Deprecate this -- if SingleTarget, nothing to shuffle!
    # def test_shuffled_targets_do_shuffle_when_taking(self):
    #     self.fail('finish writing the test')

    def test_shuffled_zones_do_shuffle_when_taking(self):
        def check_zones_are_shuffled(_offered):
            num_different = 0

            for i in range(0, 15):
                create_taken_url = '/api/v1/assessment/banks/{0}/assessmentsoffered/{1}/assessmentstaken'.format(str(self._bank.ident),
                                                                                                                 str(_offered.ident))
                req = self.app.post(create_taken_url)
                self.ok(req)
                taken = self.json(req)

                taken_questions_url = '/api/v1/assessment/banks/{0}/assessmentstaken/{1}/questions'.format(str(self._bank.ident),
                                                                                                           taken['id'])
                req2 = self.app.get(taken_questions_url)
                self.ok(req2)
                data2 = self.json(req2)['data']
                if isinstance(data2, list):
                    data2 = data2[0]  # only one question in this assessment...id's won't match
                zone_ids_order_2 = [d['id'] for d in data2['zones']]

                if original_zone_ids_order != zone_ids_order_2:
                    num_different += 1

                # now delete the taken
                delete_taken_url = '/api/v1/assessment/banks/{0}/assessmentstaken/{1}'.format(str(self._bank.ident),
                                                                                              taken['id'])
                req = self.app.delete(delete_taken_url)
                self.ok(req)

            self.assertTrue(num_different > 0)

        item = self.create_item_with_question_and_answers()
        self.assertTrue(item['question']['shuffleZones'])
        original_zone_ids_order = [z['id'] for z in item['question']['multiLanguageZones']]

        offered = self.create_assessment_offered_for_item(self._bank.ident, item['id'])

        check_zones_are_shuffled(offered)

    def test_shuffle_droppables_false_do_not_shuffle_when_taking(self):
        def check_droppables_not_shuffled(_offered):
            num_different = 0

            for i in range(0, 15):
                create_taken_url = '/api/v1/assessment/banks/{0}/assessmentsoffered/{1}/assessmentstaken'.format(str(self._bank.ident),
                                                                                                                 str(_offered.ident))
                req = self.app.post(create_taken_url)
                self.ok(req)
                taken = self.json(req)

                taken_questions_url = '/api/v1/assessment/banks/{0}/assessmentstaken/{1}/questions'.format(str(self._bank.ident),
                                                                                                           taken['id'])
                req2 = self.app.get(taken_questions_url)
                self.ok(req2)
                data2 = self.json(req2)['data']
                if isinstance(data2, list):
                    data2 = data2[0]  # only one question in this assessment...id's won't match
                droppable_ids_order_2 = [d['id'] for d in data2['droppables']]

                if original_droppable_ids_order != droppable_ids_order_2:
                    num_different += 1

                # now delete the taken
                delete_taken_url = '/api/v1/assessment/banks/{0}/assessmentstaken/{1}'.format(str(self._bank.ident),
                                                                                              taken['id'])
                req = self.app.delete(delete_taken_url)
                self.ok(req)

            self.assertTrue(num_different == 0)

        item = self.create_item_with_question_and_answers()

        payload = {
            'question': {
                'shuffleDroppables': False
            }
        }

        url = '{0}/{1}'.format(self.url,
                               item['id'])

        req = self.app.put(url,
                           params=json.dumps(payload),
                           headers={'content-type': 'application/json'})
        self.ok(req)
        item = self.json(req)

        self.assertFalse(item['question']['shuffleDroppables'])
        original_droppable_ids_order = [d['id'] for d in item['question']['multiLanguageDroppables']]

        offered = self.create_assessment_offered_for_item(self._bank.ident, item['id'])

        check_droppables_not_shuffled(offered)

    # Deprecate this -- if SingleTarget, nothing to shuffle!
    # def test_shuffle_targets_false_do_not_shuffle_when_taking(self):
    #     self.fail('finish writing the test')

    def test_shuffle_zones_false_do_not_shuffle_when_taking(self):
        def check_zones_not_shuffled(_offered):
            num_different = 0

            for i in range(0, 15):
                create_taken_url = '/api/v1/assessment/banks/{0}/assessmentsoffered/{1}/assessmentstaken'.format(str(self._bank.ident),
                                                                                                                 str(_offered.ident))
                req = self.app.post(create_taken_url)
                self.ok(req)
                taken = self.json(req)

                taken_questions_url = '/api/v1/assessment/banks/{0}/assessmentstaken/{1}/questions'.format(str(self._bank.ident),
                                                                                                           taken['id'])
                req2 = self.app.get(taken_questions_url)
                self.ok(req2)
                data2 = self.json(req2)['data']
                if isinstance(data2, list):
                    data2 = data2[0]  # only one question in this assessment...id's won't match
                zone_ids_order_2 = [d['id'] for d in data2['zones']]

                if original_zone_ids_order != zone_ids_order_2:
                    num_different += 1

                # now delete the taken
                delete_taken_url = '/api/v1/assessment/banks/{0}/assessmentstaken/{1}'.format(str(self._bank.ident),
                                                                                              taken['id'])
                req = self.app.delete(delete_taken_url)
                self.ok(req)

            self.assertTrue(num_different == 0)

        item = self.create_item_with_question_and_answers()

        payload = {
            'question': {
                'shuffleZones': False
            }
        }

        url = '{0}/{1}'.format(self.url,
                               item['id'])

        req = self.app.put(url,
                           params=json.dumps(payload),
                           headers={'content-type': 'application/json'})
        self.ok(req)
        item = self.json(req)

        self.assertFalse(item['question']['shuffleZones'])
        original_zone_ids_order = [z['id'] for z in item['question']['multiLanguageZones']]

        offered = self.create_assessment_offered_for_item(self._bank.ident, item['id'])

        check_zones_not_shuffled(offered)

    def test_can_submit_wrong_answer_with_no_match(self):
        item = self.create_item_with_question_and_answers()
        droppable_0_id = item['question']['multiLanguageDroppables'][0]['id']
        target_0_id = item['question']['multiLanguageTargets'][0]['id']

        taken = self.create_taken_for_item(self._bank.ident, item['id'])

        url = '/api/v1/assessment/banks/{0}/assessmentstaken/{1}/questions'.format(str(self._bank.ident),
                                                                                   str(taken.ident))
        req = self.app.get(url)
        self.ok(req)
        data = self.json(req)['data'][0]

        submit_url = '{0}/{1}/submit'.format(url, data['id'])
        payload = {
            'coordinateConditions': [{
                'droppableId': droppable_0_id,
                'containerId': target_0_id,
                'coordinateValues': [200, 200]
            }]
        }

        req = self.app.post(submit_url,
                            params=json.dumps(payload),
                            headers={'content-type': 'application/json'})
        self.ok(req)
        data = self.json(req)
        self.assertFalse(data['correct'])
        self.assertEqual('No feedback available.', data['feedback'])

    def test_can_submit_wrong_answer_and_get_generic_incorrect_feedback(self):
        item = self.create_item_with_question_and_answers()
        droppable_0_id = item['question']['multiLanguageDroppables'][0]['id']
        target_0_id = item['question']['multiLanguageTargets'][0]['id']

        url = '{0}/{1}'.format(self.url, item['id'])
        payload = {
            'answers': [{
                'genusTypeId': str(WRONG_ANSWER),
                'feedback': '<p>Try again! <audio type="audio/mp3"><source src="AssetContent:audio_feedback_mp3" /></audio></p>',
                'fileIds': {}
            }]
        }

        media_files = [self._audio_feedback]

        assets = {}
        for media_file in media_files:
            label = self._label(self._filename(media_file))
            assets[label] = self.upload_media_file(media_file)

        for label, asset in assets.iteritems():
            payload['answers'][0]['fileIds'][label] = {}
            payload['answers'][0]['fileIds'][label]['assetId'] = asset['id']
            payload['answers'][0]['fileIds'][label]['assetContentId'] = asset['assetContents'][0]['id']
            payload['answers'][0]['fileIds'][label]['assetContentTypeId'] = asset['assetContents'][0]['genusTypeId']

        req = self.app.put(url,
                           params=json.dumps(payload),
                           headers={'content-type': 'application/json'})
        self.ok(req)

        taken = self.create_taken_for_item(self._bank.ident, item['id'])

        url = '/api/v1/assessment/banks/{0}/assessmentstaken/{1}/questions'.format(str(self._bank.ident),
                                                                                   str(taken.ident))
        req = self.app.get(url)
        self.ok(req)
        data = self.json(req)['data'][0]

        submit_url = '{0}/{1}/submit'.format(url, data['id'])
        payload = {
            'coordinateConditions': [{
                'droppableId': droppable_0_id,
                'containerId': target_0_id,
                'coordinateValues': [200, 200]
            }]
        }

        req = self.app.post(submit_url,
                            params=json.dumps(payload),
                            headers={'content-type': 'application/json'})
        self.ok(req)
        data = self.json(req)
        self.assertFalse(data['correct'])
        self.assertIn('Try again!', data['feedback'])
        self.assertIn('/api/v1/repository/repositories', data['feedback'])
        self.assertIn('/stream', data['feedback'])
        self.assertIn('<modalFeedback', data['feedback'])
        self.assertIn('<p>', data['feedback'])
        self.assertNotIn('&lt;', data['feedback'])
        self.assertNotIn('&gt;', data['feedback'])

    def test_can_submit_wrong_answer_with_answer_match(self):
        item = self.create_item_with_question_and_answers()
        droppable_0_id = item['question']['multiLanguageDroppables'][0]['id']
        droppable_1_id = item['question']['multiLanguageDroppables'][1]['id']
        target_0_id = item['question']['multiLanguageTargets'][0]['id']

        taken = self.create_taken_for_item(self._bank.ident, item['id'])

        url = '/api/v1/assessment/banks/{0}/assessmentstaken/{1}/questions'.format(str(self._bank.ident),
                                                                                   str(taken.ident))
        req = self.app.get(url)
        self.ok(req)
        data = self.json(req)['data'][0]

        submit_url = '{0}/{1}/submit'.format(url, data['id'])
        payload = {
            'coordinateConditions': [{
                'droppableId': droppable_0_id,
                'containerId': target_0_id,
                'coordinateValues': [115, 125]
            }, {
                'droppableId': droppable_1_id,
                'containerId': target_0_id,
                'coordinateValues': [25, 15]
            }]
        }

        req = self.app.post(submit_url,
                            params=json.dumps(payload),
                            headers={'content-type': 'application/json'})
        self.ok(req)
        data = self.json(req)
        self.assertFalse(data['correct'])
        self.assertIn('Try again!', data['feedback'])
        self.assertIn('/api/v1/repository/repositories', data['feedback'])
        self.assertIn('/stream', data['feedback'])
        self.assertIn('<modalFeedback', data['feedback'])
        self.assertIn('<p>', data['feedback'])
        self.assertNotIn('&lt;', data['feedback'])
        self.assertNotIn('&gt;', data['feedback'])

    def test_can_submit_right_answer(self):
        item = self.create_item_with_question_and_answers()
        droppable_0_id = item['question']['multiLanguageDroppables'][0]['id']
        droppable_1_id = item['question']['multiLanguageDroppables'][1]['id']
        target_0_id = item['question']['multiLanguageTargets'][0]['id']

        taken = self.create_taken_for_item(self._bank.ident, item['id'])

        url = '/api/v1/assessment/banks/{0}/assessmentstaken/{1}/questions'.format(str(self._bank.ident),
                                                                                   str(taken.ident))
        req = self.app.get(url)
        self.ok(req)
        data = self.json(req)['data'][0]

        submit_url = '{0}/{1}/submit'.format(url, data['id'])
        payload = {
            'coordinateConditions': [{
                'droppableId': droppable_0_id,
                'containerId': target_0_id,
                'coordinateValues': [25.25, 14.9]
            }, {
                'droppableId': droppable_1_id,
                'containerId': target_0_id,
                'coordinateValues': [115, 125]
            }]
        }

        req = self.app.post(submit_url,
                            params=json.dumps(payload),
                            headers={'content-type': 'application/json'})
        self.ok(req)
        data = self.json(req)
        self.assertTrue(data['correct'])
        self.assertIn('Good job!', data['feedback'])
        self.assertIn('/api/v1/repository/repositories', data['feedback'])
        self.assertIn('/stream', data['feedback'])
        self.assertIn('<modalFeedback', data['feedback'])
        self.assertIn('<p>', data['feedback'])
        self.assertNotIn('&lt;', data['feedback'])
        self.assertNotIn('&gt;', data['feedback'])

    def test_submitting_coordinate_off_of_the_target_is_incorrect(self):
        item = self.create_item_with_question_and_answers()
        droppable_0_id = item['question']['multiLanguageDroppables'][0]['id']
        droppable_1_id = item['question']['multiLanguageDroppables'][1]['id']
        target_0_id = item['question']['multiLanguageTargets'][0]['id']

        taken = self.create_taken_for_item(self._bank.ident, item['id'])

        url = '/api/v1/assessment/banks/{0}/assessmentstaken/{1}/questions'.format(str(self._bank.ident),
                                                                                   str(taken.ident))
        req = self.app.get(url)
        self.ok(req)
        data = self.json(req)['data'][0]

        submit_url = '{0}/{1}/submit'.format(url, data['id'])
        payload = {
            'coordinateConditions': [{
                'droppableId': droppable_0_id,
                'containerId': target_0_id,
                'coordinateValues': [51.1, 31.2]
            }, {
                'droppableId': droppable_1_id,
                'containerId': target_0_id,
                'coordinateValues': [10000.25, 10000.75]
            }]
        }

        req = self.app.post(submit_url,
                            params=json.dumps(payload),
                            headers={'content-type': 'application/json'})
        self.ok(req)
        data = self.json(req)
        self.assertFalse(data['correct'])

    def test_submitting_negative_coordinates_is_incorrect(self):
        item = self.create_item_with_question_and_answers()
        droppable_0_id = item['question']['multiLanguageDroppables'][0]['id']
        droppable_1_id = item['question']['multiLanguageDroppables'][1]['id']
        target_0_id = item['question']['multiLanguageTargets'][0]['id']

        taken = self.create_taken_for_item(self._bank.ident, item['id'])

        url = '/api/v1/assessment/banks/{0}/assessmentstaken/{1}/questions'.format(str(self._bank.ident),
                                                                                   str(taken.ident))
        req = self.app.get(url)
        self.ok(req)
        data = self.json(req)['data'][0]

        submit_url = '{0}/{1}/submit'.format(url, data['id'])
        payload = {
            'coordinateConditions': [{
                'droppableId': droppable_0_id,
                'containerId': target_0_id,
                'coordinateValues': [-1, -1]
            }, {
                'droppableId': droppable_1_id,
                'containerId': target_0_id,
                'coordinateValues': [-1, -10000]
            }]
        }

        req = self.app.post(submit_url,
                            params=json.dumps(payload),
                            headers={'content-type': 'application/json'})
        self.ok(req)
        data = self.json(req)
        self.assertFalse(data['correct'])

    def test_submitting_coordinate_on_the_zone_boundary_is_correct(self):
        item = self.create_item_with_question_and_answers()
        droppable_0_id = item['question']['multiLanguageDroppables'][0]['id']
        droppable_1_id = item['question']['multiLanguageDroppables'][1]['id']
        target_0_id = item['question']['multiLanguageTargets'][0]['id']

        taken = self.create_taken_for_item(self._bank.ident, item['id'])

        url = '/api/v1/assessment/banks/{0}/assessmentstaken/{1}/questions'.format(str(self._bank.ident),
                                                                                   str(taken.ident))
        req = self.app.get(url)
        self.ok(req)
        data = self.json(req)['data'][0]

        submit_url = '{0}/{1}/submit'.format(url, data['id'])
        payload = {
            'coordinateConditions': [{
                'droppableId': droppable_0_id,
                'containerId': target_0_id,
                'coordinateValues': [50, 30]
            }, {
                'droppableId': droppable_1_id,
                'containerId': target_0_id,
                'coordinateValues': [100, 100]
            }]
        }

        req = self.app.post(submit_url,
                            params=json.dumps(payload),
                            headers={'content-type': 'application/json'})
        self.ok(req)
        data = self.json(req)
        self.assertTrue(data['correct'])

    def test_cannot_submit_non_numeric_coordinates(self):
        item = self.create_item_with_question_and_answers()
        droppable_0_id = item['question']['multiLanguageDroppables'][0]['id']
        droppable_1_id = item['question']['multiLanguageDroppables'][1]['id']
        target_0_id = item['question']['multiLanguageTargets'][0]['id']

        taken = self.create_taken_for_item(self._bank.ident, item['id'])

        url = '/api/v1/assessment/banks/{0}/assessmentstaken/{1}/questions'.format(str(self._bank.ident),
                                                                                   str(taken.ident))
        req = self.app.get(url)
        self.ok(req)
        data = self.json(req)['data'][0]

        submit_url = '{0}/{1}/submit'.format(url, data['id'])
        payload = {
            'coordinateConditions': [{
                'droppableId': droppable_0_id,
                'containerId': target_0_id,
                'coordinateValues': ['50', '0']
            }, {
                'droppableId': droppable_1_id,
                'containerId': target_0_id,
                'coordinateValues': ['101', '129']
            }]
        }

        self.assertRaises(AppError,
                          self.app.post,
                          submit_url,
                          json.dumps(payload),
                          {'content-type': 'application/json'})

    def test_text_comes_back_in_desired_language(self):
        """ Check that zones, targets, and droppables all return the right language
        """
        item = self.create_item_with_question_and_answers()
        hindi_text = u'हरा बिंदु'
        droppable_0_id = item['question']['multiLanguageDroppables'][0]['id']
        target_0_id = item['question']['multiLanguageTargets'][0]['id']
        zone_0_id = item['question']['multiLanguageZones'][0]['id']

        payload = {
            'question': {
                'droppables': [{
                    'id': droppable_0_id,
                    'text': {
                        'text': u'<p><img src="AssetContent:draggable_green_dot_png" alt="{0}" /></p>'.format(hindi_text),
                        'formatTypeId': self._format_type,
                        'languageTypeId': self._hi_language_type,
                        'scriptTypeId': self._hi_script_type
                    }  # ignore the other droppable for now, to make sure it comes back English
                }],
                'targets': [{
                    'id': target_0_id,
                    'text': {
                        'text': u'<p><img src="AssetContent:drag_and_drop_input_DPP-Concpt-BlkonRmp-Trgt_png" alt="{0}" /></p>'.format(hindi_text),
                        'formatTypeId': self._format_type,
                        'languageTypeId': self._hi_language_type,
                        'scriptTypeId': self._hi_script_type
                    }
                }],
                'zones': [{
                    'id': zone_0_id,
                    'description': {
                        'text': hindi_text,
                        'formatTypeId': self._format_type,
                        'languageTypeId': self._hi_language_type,
                        'scriptTypeId': self._hi_script_type
                    }  # leave name out to check that it comes back as English
                }]
            }
        }
        url = '{0}/{1}'.format(self.url, item['id'])
        req = self.app.put(url,
                           params=json.dumps(payload),
                           headers={'content-type': 'application/json'})
        self.ok(req)

        taken = self.create_taken_for_item(self._bank.ident, item['id'])

        url = '/api/v1/assessment/banks/{0}/assessmentstaken/{1}/questions'.format(str(self._bank.ident),
                                                                                   str(taken.ident))
        req = self.app.get(url)

        self.ok(req)
        data = self.json(req)['data'][0]
        question_id = data['id']
        droppable_0 = [d for d in data['droppables'] if d['id'] == droppable_0_id][0]
        droppable_1 = [d for d in data['droppables'] if d['id'] != droppable_0_id][0]

        self.assertIn('Green', droppable_0['text'])
        self.assertNotIn(hindi_text, droppable_0['text'])
        self.assertIn('Red', droppable_1['text'])

        target = data['targets'][0]

        self.assertIn('Ramp', target['text'])
        self.assertNotIn(hindi_text, target['text'])

        zone_0 = [z for z in data['zones'] if z['id'] == zone_0_id][0]
        zone_1 = [z for z in data['zones'] if z['id'] != zone_0_id][0]

        self.assertIn('Zone', zone_0['name'])
        self.assertIn('left', zone_0['description'])
        self.assertNotIn(hindi_text, zone_0['description'])
        self.assertIn('Zone', zone_1['name'])
        self.assertIn('right', zone_1['description'])

        req = self.app.get(url,
                           headers={'x-api-locale': 'hi'})

        self.ok(req)
        data = self.json(req)['data'][0]
        self.assertEqual(question_id, data['id'])
        droppable_0 = [d for d in data['droppables'] if d['id'] == droppable_0_id][0]
        droppable_1 = [d for d in data['droppables'] if d['id'] != droppable_0_id][0]

        self.assertNotIn('Green', droppable_0['text'])
        self.assertIn(hindi_text, droppable_0['text'])
        self.assertIn('Red', droppable_1['text'])

        target = data['targets'][0]

        self.assertNotIn('Ramp', target['text'])
        self.assertIn(hindi_text, target['text'])

        zone_0 = [z for z in data['zones'] if z['id'] == zone_0_id][0]
        zone_1 = [z for z in data['zones'] if z['id'] != zone_0_id][0]

        self.assertIn('Zone', zone_0['name'])
        self.assertNotIn('left', zone_0['description'])
        self.assertIn(hindi_text, zone_0['description'])
        self.assertIn('Zone', zone_1['name'])
        self.assertIn('right', zone_1['description'])

    def test_image_urls_come_back_in_targets(self):
        item = self.create_item_with_question_and_answers()
        taken = self.create_taken_for_item(self._bank.ident, item['id'])

        url = '/api/v1/assessment/banks/{0}/assessmentstaken/{1}/questions'.format(str(self._bank.ident),
                                                                                   str(taken.ident))
        req = self.app.get(url)
        self.ok(req)
        data = self.json(req)['data'][0]
        self.assertIn('/api/v1/repository/repositories', data['targets'][0]['text'])
        self.assertIn('/stream', data['targets'][0]['text'])

    def test_image_urls_come_back_in_droppables(self):
        item = self.create_item_with_question_and_answers()
        taken = self.create_taken_for_item(self._bank.ident, item['id'])

        url = '/api/v1/assessment/banks/{0}/assessmentstaken/{1}/questions'.format(str(self._bank.ident),
                                                                                   str(taken.ident))
        req = self.app.get(url)
        self.ok(req)
        data = self.json(req)['data'][0]
        for droppable in data['droppables']:
            self.assertIn('/api/v1/repository/repositories', droppable['text'])
            self.assertIn('/stream', droppable['text'])

    def test_can_get_question_when_using_qti_flag(self):
        item = self.create_item_with_question_and_answers()
        droppable_0_id = item['question']['multiLanguageDroppables'][0]['id']
        target_0_id = item['question']['multiLanguageTargets'][0]['id']

        taken = self.create_taken_for_item(self._bank.ident, item['id'])

        url = '/api/v1/assessment/banks/{0}/assessmentstaken/{1}/questions?qti'.format(str(self._bank.ident),
                                                                                       str(taken.ident))
        req = self.app.get(url)
        self.ok(req)
        data = self.json(req)['data'][0]
        url = '/api/v1/assessment/banks/{0}/assessmentstaken/{1}/questions'.format(str(self._bank.ident),
                                                                                   str(taken.ident))

        submit_url = '{0}/{1}/submit'.format(url, data['id'])
        payload = {
            'coordinateConditions': [{
                'droppableId': droppable_0_id,
                'containerId': target_0_id,
                'coordinateValues': [200, 200]
            }]
        }

        req = self.app.post(submit_url,
                            params=json.dumps(payload),
                            headers={'content-type': 'application/json'})
        self.ok(req)
        data = self.json(req)
        self.assertFalse(data['correct'])
        self.assertEqual('No feedback available.', data['feedback'])
