# -*- coding: utf-8 -*-
import json
from bs4 import BeautifulSoup, Tag

from urllib import unquote, quote

from .test_assessment import BaseAssessmentTestCase, _stringify, ABS_PATH,\
    SIMPLE_SEQUENCE_RECORD,\
    QTI_ITEM_RECORD,\
    MULTI_LANGUAGE_ITEM_RECORD,\
    QTI_QUESTION_RECORD,\
    MULTI_LANGUAGE_QUESTION_RECORD,\
    QTI_ANSWER_RECORD,\
    MULTI_LANGUAGE_FEEDBACK_ANSWER_RECORD,\
    FILES_ANSWER_RECORD,\
    RIGHT_ANSWER_GENUS,\
    WRONG_ANSWER_GENUS,\
    QTI_QUESTION_UPLOAD_INTERACTION_AUDIO_GENUS,\
    QTI_QUESTION_UPLOAD_INTERACTION_GENERIC_GENUS,\
    QTI_ITEM_UPLOAD_INTERACTION_AUDIO_GENUS,\
    QTI_ITEM_UPLOAD_INTERACTION_GENERIC_GENUS,\
    QTI_ITEM_CHOICE_INTERACTION_GENUS,\
    QTI_ITEM_CHOICE_INTERACTION_MULTI_GENUS,\
    QTI_ITEM_CHOICE_INTERACTION_MULTI_SELECT_SURVEY_GENUS,\
    QTI_ITEM_CHOICE_INTERACTION_SURVEY_GENUS,\
    QTI_ITEM_INLINE_CHOICE_INTERACTION_GENUS,\
    QTI_ITEM_EXTENDED_TEXT_INTERACTION_GENUS,\
    QTI_ITEM_NUMERIC_RESPONSE_INTERACTION_GENUS,\
    QTI_ITEM_ORDER_INTERACTION_MW_SANDBOX_GENUS,\
    QTI_ITEM_ORDER_INTERACTION_MW_SENTENCE_GENUS,\
    QTI_ITEM_ORDER_INTERACTION_OBJECT_MANIPULATION_GENUS,\
    QTI_QUESTION_CHOICE_INTERACTION_GENUS,\
    QTI_QUESTION_CHOICE_INTERACTION_MULTI_GENUS,\
    QTI_QUESTION_CHOICE_INTERACTION_MULTI_SELECT_SURVEY_GENUS,\
    QTI_QUESTION_CHOICE_INTERACTION_SURVEY_GENUS,\
    QTI_QUESTION_EXTENDED_TEXT_INTERACTION_GENUS,\
    QTI_QUESTION_INLINE_CHOICE_INTERACTION_GENUS,\
    QTI_QUESTION_NUMERIC_RESPONSE_INTERACTION_GENUS,\
    QTI_QUESTION_ORDER_INTERACTION_MW_SANDBOX_GENUS,\
    QTI_QUESTION_ORDER_INTERACTION_MW_SENTENCE_GENUS,\
    QTI_QUESTION_ORDER_INTERACTION_OBJECT_MANIPULATION_GENUS

from testing_utilities import get_managers, get_valid_contents

import utilities


class QTIEndpointTests(BaseAssessmentTestCase):
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

    @staticmethod
    def _label(text):
        return text.replace('.', '_')

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
        form = bank.get_item_form_for_create([QTI_ITEM_RECORD,
                                              MULTI_LANGUAGE_ITEM_RECORD])
        form.display_name = 'a test item!'
        form.description = 'for testing with'
        form.load_from_qti_item(self._test_xml)
        new_item = bank.create_item(form)

        form = bank.get_question_form_for_create(item_id=new_item.ident,
                                                 question_record_types=[QTI_QUESTION_RECORD,
                                                                        MULTI_LANGUAGE_QUESTION_RECORD])
        form.load_from_qti_item(self._test_xml)
        bank.create_question(form)

        form = bank.get_answer_form_for_create(item_id=new_item.ident,
                                               answer_record_types=[QTI_ANSWER_RECORD,
                                                                    MULTI_LANGUAGE_FEEDBACK_ANSWER_RECORD,
                                                                    FILES_ANSWER_RECORD])
        form.load_from_qti_item(self._test_xml)
        bank.create_answer(form)

        return bank.get_item(new_item.ident)

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
        super(QTIEndpointTests, self).setUp()

        self._test_file = open('{0}/tests/files/sample_qti_choice_interaction.xml'.format(ABS_PATH), 'r')
        self._test_xml = BeautifulSoup(self._test_file.read(), 'xml').prettify()

        self._test_file2 = open('{0}/tests/files/qti_file_with_images.zip'.format(ABS_PATH), 'r')
        self._audio_recording_test_file = open('{0}/tests/files/Social_Introductions_Role_Play.zip'.format(ABS_PATH), 'r')
        self._mc_feedback_test_file = open('{0}/tests/files/ee_u1l01a04q03_en.zip'.format(ABS_PATH), 'r')
        self._mw_sentence_test_file = open('{0}/tests/files/mw_sentence_with_audio_file.zip'.format(ABS_PATH), 'r')
        self._mw_sentence_missing_audio_test_file = open('{0}/tests/files/mw_sentence_missing_audio_file.zip'.format(ABS_PATH), 'r')
        self._xml_after_audio_test_file = open('{0}/tests/files/qti_file_for_testing_xml_output.zip'.format(ABS_PATH), 'r')
        self._mw_sandbox_test_file = open('{0}/tests/files/mw_sandbox.zip'.format(ABS_PATH), 'r')
        self._mc_multi_select_test_file = open('{0}/tests/files/mc_multi_select_test_file.zip'.format(ABS_PATH), 'r')
        self._short_answer_test_file = open('{0}/tests/files/short_answer_test_file.zip'.format(ABS_PATH), 'r')
        self._mw_fill_in_the_blank_test_file = open('{0}/tests/files/mw_fill_in_the_blank_test_file.zip'.format(ABS_PATH), 'r')
        self._generic_upload_test_file = open('{0}/tests/files/generic_upload_test_file.zip'.format(ABS_PATH), 'r')
        self._drag_and_drop_test_file = open('{0}/tests/files/drag_and_drop_test_file.zip'.format(ABS_PATH), 'r')
        self._simple_numeric_response_test_file = open('{0}/tests/files/new_numeric_response_format_test_file.zip'.format(ABS_PATH), 'r')
        # self._simple_numeric_response_test_file = open('{0}/tests/files/numeric_response_test_file.zip'.format(ABS_PATH), 'r')
        self._floating_point_numeric_input_test_file = open('{0}/tests/files/new_floating_point_numeric_response_test_file.zip'.format(ABS_PATH), 'r')
        # self._floating_point_numeric_input_test_file = open('{0}/tests/files/floating_point_numeric_input_test_file.zip'.format(ABS_PATH), 'r')
        self._video_test_file = open('{0}/tests/files/video_test_file.zip'.format(ABS_PATH), 'r')
        self._audio_everywhere_test_file = open('{0}/tests/files/audio_everywhere_test_file.zip'.format(ABS_PATH), 'r')
        self._audio_in_choices_test_file = open('{0}/tests/files/audio_choices_only_test_file.zip'.format(ABS_PATH), 'r')
        self._mw_fitb_2_test_file = open('{0}/tests/files/mw_fill_in_the_blank_example_2.zip'.format(ABS_PATH), 'r')
        self._image_in_feedback_test_file = open('{0}/tests/files/image_feedback_test_file.zip'.format(ABS_PATH), 'r')
        self._telugu_test_file = open('{0}/tests/files/telugu_question_test_file.zip'.format(ABS_PATH), 'r')
        self._survey_question_test_file = open('{0}/tests/files/survey_question_test_file.zip'.format(ABS_PATH), 'r')
        self._multi_select_survey_question_test_file = open('{0}/tests/files/survey_question_multi_select_test_file.zip'.format(ABS_PATH), 'r')
        self._unicode_feedback_test_file = open('{0}/tests/files/ee_u1l05a04q01_en.zip'.format(ABS_PATH), 'r')
        self._fitb_with_punctuation_test_file = open('{0}/tests/files/eb_u01l03a06q03_en.zip'.format(ABS_PATH), 'r')
        self._square_image = open('{0}/tests/files/square.png'.format(ABS_PATH), 'r')
        self._diamond_image = open('{0}/tests/files/diamond.png'.format(ABS_PATH), 'r')
        self._rectangle_image = open('{0}/tests/files/rectangle.png'.format(ABS_PATH), 'r')
        self._parallelogram_image = open('{0}/tests/files/parallelogram.png'.format(ABS_PATH), 'r')
        self._green_dot_image = open('{0}/tests/files/green_dot.png'.format(ABS_PATH), 'r')
        self._h1i_image = open('{0}/tests/files/h1i.png'.format(ABS_PATH), 'r')
        self._audio_test_file = open('{0}/tests/files/audioTestFile_.mp3'.format(ABS_PATH), 'r')
        self._intersection_image = open('{0}/tests/files/intersection.png'.format(ABS_PATH), 'r')
        self._mw_sentence_audio_file = open('{0}/tests/files/ee_u1l01a01r05_.mp3'.format(ABS_PATH), 'r')
        self._mw_sandbox_audio_file = open('{0}/tests/files/ee_u1l01a01r04_.mp3'.format(ABS_PATH), 'r')
        self._shapes_image = open('{0}/tests/files/shapes.png'.format(ABS_PATH), 'r')
        self._picture1 = open('{0}/tests/files/Picture1.png'.format(ABS_PATH), 'r')
        self._picture2 = open('{0}/tests/files/Picture2.png'.format(ABS_PATH), 'r')
        self._picture3 = open('{0}/tests/files/Picture3.png'.format(ABS_PATH), 'r')
        self._picture4 = open('{0}/tests/files/Picture4.png'.format(ABS_PATH), 'r')

        self._item = self.create_item(self._bank.ident)
        self._taken, self._offered, self._assessment = self.create_taken_for_item(self._bank.ident, self._item.ident)

        self.url += '/banks/' + unquote(str(self._bank.ident))

    def tearDown(self):
        super(QTIEndpointTests, self).tearDown()

        self._test_file.close()
        self._test_file2.close()
        self._audio_recording_test_file.close()
        self._mc_feedback_test_file.close()
        self._mw_sentence_test_file.close()
        self._mw_sentence_missing_audio_test_file.close()
        self._xml_after_audio_test_file.close()
        self._mw_sandbox_test_file.close()
        self._mc_multi_select_test_file.close()
        self._short_answer_test_file.close()
        self._mw_fill_in_the_blank_test_file.close()
        self._generic_upload_test_file.close()
        self._drag_and_drop_test_file.close()
        self._simple_numeric_response_test_file.close()
        self._floating_point_numeric_input_test_file.close()
        self._video_test_file.close()
        self._audio_everywhere_test_file.close()
        self._audio_in_choices_test_file.close()
        self._mw_fitb_2_test_file.close()
        self._image_in_feedback_test_file.close()
        self._telugu_test_file.close()
        self._survey_question_test_file.close()
        self._multi_select_survey_question_test_file.close()
        self._unicode_feedback_test_file.close()
        self._fitb_with_punctuation_test_file.close()
        self._square_image.close()
        self._diamond_image.close()
        self._rectangle_image.close()
        self._parallelogram_image.close()
        self._green_dot_image.close()
        self._h1i_image.close()
        self._audio_test_file.close()
        self._intersection_image.close()
        self._mw_sentence_audio_file.close()
        self._mw_sandbox_audio_file.close()
        self._shapes_image.close()
        self._picture1.close()
        self._picture2.close()
        self._picture3.close()
        self._picture4.close()

    def upload_media_file(self, file_handle):
        url = '/api/v1/repository/repositories/{0}/assets'.format(unquote(str(self._bank.ident)))
        file_handle.seek(0)
        req = self.app.post(url,
                            upload_files=[('inputFile',
                                           self._filename(file_handle),
                                           file_handle.read())])
        self.ok(req)
        data = self.json(req)
        return data

    def test_can_get_item_qti_with_answers(self):
        url = '{0}/items/{1}/qti'.format(self.url,
                                         unquote(str(self._item.ident)))
        req = self.app.get(url)
        qti_xml = BeautifulSoup(req.body, 'lxml-xml')
        item = qti_xml.assessmentItem
        self.assertTrue(item.itemBody.choiceInteraction)
        self.assertTrue(item.responseDeclaration)
        self.assertTrue(item.responseProcessing)

    def test_can_upload_qti_choice_interaction_file(self):
        url = '{0}/items'.format(self.url)
        self._test_file2.seek(0)
        req = self.app.post(url,
                            upload_files=[('qtiFile', 'testFile', self._test_file2.read())])
        self.ok(req)
        item = self.json(req)

        self.assertEqual(
            item['genusTypeId'],
            str(QTI_ITEM_CHOICE_INTERACTION_GENUS)
        )

        self.assertEqual(
            item['question']['genusTypeId'],
            str(QTI_QUESTION_CHOICE_INTERACTION_GENUS)
        )

        self.assertEqual(
            item['answers'][0]['genusTypeId'],
            str(RIGHT_ANSWER_GENUS)
        )

        self.assertNotEqual(
            item['id'],
            str(self._item.ident)
        )

        # now verify the QTI XML matches the JSON format
        url = '{0}/{1}/qti'.format(url, unquote(item['id']))
        req = self.app.get(url)
        self.ok(req)
        qti_xml = BeautifulSoup(req.body, 'lxml-xml').assessmentItem
        item_body = qti_xml.itemBody

        choice_interaction = item_body.choiceInteraction.extract()

        image_1_asset_label = 'medium8701311014467393642draggable_green_dot_png'
        image_2_asset_label = 'medium3854799028001516110draggable_h1i_PNG'
        image_1_asset_id = item['question']['fileIds'][image_1_asset_label]['assetId']
        image_1_asset_content_id = item['question']['fileIds'][image_1_asset_label]['assetContentId']

        image_2_asset_id = item['question']['fileIds'][image_2_asset_label]['assetId']
        image_2_asset_content_id = item['question']['fileIds'][image_2_asset_label]['assetContentId']

        expected_string = """<itemBody>
<p>
   Which of the following is a circle?
  </p>

</itemBody>"""

        self.assertEqual(
            str(item_body),
            expected_string
        )

        self.assertEqual(
            str(item_body),
            expected_string
        )

        self.assertEqual(
            len(choice_interaction.find_all('simpleChoice')),
            3
        )
        self.assertEqual(
            choice_interaction['maxChoices'],
            "1"
        )
        self.assertEqual(
            choice_interaction['responseIdentifier'],
            'RESPONSE_1'
        )
        self.assertEqual(
            choice_interaction['shuffle'],
            'true'
        )

        repository_id = str(self._bank.ident).replace('assessment.Bank', 'repository.Repository')

        expected_choices = {
            "idc561552b-ed48-46c3-b20d-873150dfd4a2": """<simpleChoice identifier="idc561552b-ed48-46c3-b20d-873150dfd4a2">
<p>
<img alt="image 1" height="20" src="/api/v1/repository/repositories/{0}/assets/{1}/contents/{2}/stream" width="20"/>
</p>
</simpleChoice>""".format(repository_id,
                          image_1_asset_id,
                          image_1_asset_content_id),
            "ida86a26e0-a563-4e48-801a-ba9d171c24f7": """<simpleChoice identifier="ida86a26e0-a563-4e48-801a-ba9d171c24f7">
<p>
     |__|
    </p>
</simpleChoice>""",
            "id32b596f4-d970-4d1e-a667-3ca762c002c5": """<simpleChoice identifier="id32b596f4-d970-4d1e-a667-3ca762c002c5">
<p>
<img alt="image 2" height="24" src="/api/v1/repository/repositories/{0}/assets/{1}/contents/{2}/stream" width="26"/>
</p>
</simpleChoice>""".format(repository_id,
                          image_2_asset_id,
                          image_2_asset_content_id)
        }

        for choice in choice_interaction.find_all('simpleChoice'):
            choice_id = choice['identifier']
            self.assertEqual(
                str(choice),
                expected_choices[choice_id]
            )

    def test_xml_preserved(self):
        url = '{0}/items'.format(self.url)
        self._xml_after_audio_test_file.seek(0)
        req = self.app.post(url,
                            upload_files=[('qtiFile', 'testFile', self._xml_after_audio_test_file.read())])
        self.ok(req)
        item = self.json(req)

        self.assertEqual(
            item['genusTypeId'],
            str(QTI_ITEM_CHOICE_INTERACTION_GENUS)
        )

        self.assertEqual(
            item['question']['genusTypeId'],
            str(QTI_QUESTION_CHOICE_INTERACTION_GENUS)
        )

        self.assertEqual(
            item['answers'][0]['genusTypeId'],
            str(RIGHT_ANSWER_GENUS)
        )

        self.assertNotEqual(
            item['id'],
            str(self._item.ident)
        )

        # now verify the QTI XML matches the JSON format
        url = '{0}/{1}/qti'.format(url, unquote(item['id']))
        req = self.app.get(url)
        self.ok(req)
        qti_xml = BeautifulSoup(req.body, 'lxml-xml').assessmentItem
        item_body = qti_xml.itemBody
        item_body.choiceInteraction.extract()
        string_children = get_valid_contents(item_body)
        expected = BeautifulSoup(item['question']['texts'][0]['text'], 'lxml-xml').itemBody
        expected_children = get_valid_contents(expected)
        self.assertEqual(len(string_children), len(expected_children))
        for index, child in enumerate(string_children):
            if isinstance(child, Tag):
                child_contents = get_valid_contents(child)
                expected_child_contents = get_valid_contents(expected_children[index])
                for grandchild_index, grandchild in enumerate(child_contents):
                    if isinstance(grandchild, Tag):
                        for key, val in grandchild.attrs.iteritems():
                            if key not in ['data', 'src']:
                                if key == "class":
                                    self.assertIn(val,
                                                  expected_child_contents[grandchild_index].attrs[key])
                                else:
                                    self.assertEqual(val,
                                                     expected_child_contents[grandchild_index].attrs[key])
                    else:
                        self.assertEqual(grandchild.string.strip(),
                                         expected_child_contents[grandchild_index].string.strip())
            else:
                self.assertEqual(child.string.strip(), expected_children[index].string.strip())

    def test_can_upload_qti_upload_interaction_file(self):
        url = '{0}/items'.format(self.url)
        self._audio_recording_test_file.seek(0)
        req = self.app.post(url,
                            upload_files=[('qtiFile', 'testFile', self._audio_recording_test_file.read())])
        self.ok(req)
        item = self.json(req)

        self.assertEqual(
            item['genusTypeId'],
            str(QTI_ITEM_UPLOAD_INTERACTION_AUDIO_GENUS)
        )

        self.assertEqual(
            item['question']['genusTypeId'],
            str(QTI_QUESTION_UPLOAD_INTERACTION_AUDIO_GENUS)
        )

        self.assertEqual(
            item['answers'][0]['genusTypeId'],
            str(RIGHT_ANSWER_GENUS)
        )

        self.assertEqual(
            item['answers'][0]['feedbacks'][0]['text'],
            '<modalFeedback  identifier="Feedback" outcomeIdentifier="FEEDBACKMODAL" showHide="show">\n<p></p>\n</modalFeedback>'
        )

        self.assertNotEqual(
            item['id'],
            str(self._item.ident)
        )

        item_qti_url = '{0}/{1}/qti'.format(url, item['id'])
        req = self.app.get(item_qti_url)
        self.ok(req)
        qti_xml = BeautifulSoup(req.body, 'lxml-xml').assessmentItem
        item_body = qti_xml.itemBody

        audio_asset_label = 'audioTestFile__mp3'
        audio_asset_id = item['question']['fileIds'][audio_asset_label]['assetId']
        audio_asset_content_id = item['question']['fileIds'][audio_asset_label]['assetContentId']

        expected_string = """<itemBody>
<p>
<audio autoplay="autoplay" controls="controls" style="width: 125px">
<source src="/api/v1/repository/repositories/{0}/assets/{1}/contents/{2}/stream" type="audio/mpeg"/>
</audio>
</p>
<p>
<strong>
    Introducting a new student
   </strong>
</p>
<p>
   It's the first day of school after the summer vacations. A new student has joined the class
  </p>
<p>
   Student 1 talks to the new student to make him/her feel comfortable.
  </p>
<p>
   Student 2 talks about herself or himself and asks a few questions about the new school
  </p>
<uploadInteraction responseIdentifier="RESPONSE_1"/>
</itemBody>""".format(str(self._bank.ident).replace('assessment.Bank', 'repository.Repository'),
                      audio_asset_id,
                      audio_asset_content_id)

        self.assertEqual(
            str(item_body),
            expected_string
        )

    def test_can_upload_generic_qti_upload_interaction_file(self):
        url = '{0}/items'.format(self.url)
        self._generic_upload_test_file.seek(0)
        req = self.app.post(url,
                            upload_files=[('qtiFile', 'testFile', self._generic_upload_test_file.read())])
        self.ok(req)
        item = self.json(req)

        self.assertEqual(
            item['genusTypeId'],
            str(QTI_ITEM_UPLOAD_INTERACTION_GENERIC_GENUS)
        )

        self.assertEqual(
            item['question']['genusTypeId'],
            str(QTI_QUESTION_UPLOAD_INTERACTION_GENERIC_GENUS)
        )

        self.assertEqual(
            item['answers'][0]['genusTypeId'],
            str(RIGHT_ANSWER_GENUS)
        )

        self.assertEqual(
            item['answers'][0]['feedbacks'][0]['text'],
            '<modalFeedback identifier="Feedback464983843" outcomeIdentifier="FEEDBACKMODAL" showHide="show"><p><strong><span id="docs-internal-guid-46f83555-04c5-8000-2639-b910cd8704bf">Upload successful!</span><br/></strong></p></modalFeedback>'
        )

        self.assertNotEqual(
            item['id'],
            str(self._item.ident)
        )

        item_qti_url = '{0}/{1}/qti'.format(url, item['id'])
        req = self.app.get(item_qti_url)
        self.ok(req)
        qti_xml = BeautifulSoup(req.body, 'lxml-xml').assessmentItem
        item_body = qti_xml.itemBody

        expected_string = """<itemBody>
<p>
<strong>
<span id="docs-internal-guid-46f83555-04c5-4e80-4138-8ed0f8d56345">
     Construct a rhombus of side 200 using Turtle Blocks. Save the shape you draw, and upload it here.
    </span>
<br/>
</strong>
</p>
<uploadInteraction responseIdentifier="RESPONSE_1"/>
</itemBody>"""

        self.assertEqual(
            str(item_body),
            expected_string
        )

    def test_can_upload_qti_order_interaction_file(self):
        url = '{0}/items'.format(self.url)
        self._mw_sentence_test_file.seek(0)
        req = self.app.post(url,
                            upload_files=[('qtiFile', 'testFile', self._mw_sentence_test_file.read())])
        self.ok(req)
        item = self.json(req)

        self.assertEqual(
            item['genusTypeId'],
            str(QTI_ITEM_ORDER_INTERACTION_MW_SENTENCE_GENUS)
        )

        self.assertEqual(
            item['question']['genusTypeId'],
            str(QTI_QUESTION_ORDER_INTERACTION_MW_SENTENCE_GENUS)
        )

        self.assertEqual(
            item['answers'][0]['genusTypeId'],
            str(RIGHT_ANSWER_GENUS)
        )
        self.assertEqual(
            len(item['answers'][0]['choiceIds']),
            7
        )
        self.assertIn('feedbacks', item['answers'][0])
        self.assertTrue(len(item['answers'][0]['feedbacks']) == 1)

        self.assertEqual(
            item['answers'][1]['genusTypeId'],
            str(WRONG_ANSWER_GENUS)
        )

        self.assertEqual(
            len(item['answers'][1]['choiceIds']),
            1
        )
        self.assertIsNone(item['answers'][1]['choiceIds'][0])
        self.assertIn('feedbacks', item['answers'][1])
        self.assertTrue(len(item['answers'][1]['feedbacks']) == 1)

        self.assertEqual(
            len(item['question']['choices']),
            7
        )

        for choice in item['question']['multiLanguageChoices']:
            self.assertTrue(len(choice['texts']) == 1)
            for text in choice['texts']:
                self.assertIn('<p class="', text['text'])
                if any(n in text['text'] for n in ['the bags', 'the bus', 'the bridge', 'Raju', 'the seat']):
                    self.assertIn('"noun"', text['text'])
                elif any(p in text['text'] for p in ['on']):
                    self.assertIn('"prep"', text['text'])
                elif 'left' in text['text']:
                    self.assertIn('"verb"', text['text'])
                elif 'under' in text['text']:
                    self.assertIn('"adverb"', text['text'])
        for choice in item['question']['choices']:
            self.assertIn('<p class="', choice['text'])
            if any(n in choice['text'] for n in ['the bags', 'the bus', 'the bridge', 'Raju', 'the seat']):
                self.assertIn('"noun"', choice['text'])
            elif any(p in choice['text'] for p in ['on']):
                self.assertIn('"prep"', choice['text'])
            elif 'left' in choice['text']:
                self.assertIn('"verb"', choice['text'])
            elif 'under' in choice['text']:
                self.assertIn('"adverb"', choice['text'])

        self.assertNotEqual(
            item['id'],
            str(self._item.ident)
        )

        item_details_url = '{0}?qti'.format(url)
        req = self.app.get(item_details_url)
        self.ok(req)
        data = self.json(req)
        item = [i for i in data if i['id'] == item['id']][0]
        self.assertIn('qti', item)
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

    def test_can_upload_question_with_image_in_feedback(self):
        url = '{0}/items'.format(self.url)
        self._image_in_feedback_test_file.seek(0)
        req = self.app.post(url,
                            upload_files=[('qtiFile',
                                           self._filename(self._image_in_feedback_test_file),
                                           self._image_in_feedback_test_file.read())])
        self.ok(req)
        item = self.json(req)

        self.assertEqual(
            item['genusTypeId'],
            str(QTI_ITEM_CHOICE_INTERACTION_GENUS)
        )

        self.assertEqual(
            item['question']['genusTypeId'],
            str(QTI_QUESTION_CHOICE_INTERACTION_GENUS)
        )

        self.assertEqual(
            len(item['answers']),
            3
        )
        self.assertEqual(
            item['answers'][0]['genusTypeId'],
            str(RIGHT_ANSWER_GENUS)
        )
        self.assertEqual(
            len(item['answers'][0]['choiceIds']),
            1
        )
        self.assertIn('fileIds', item['answers'][0])
        self.assertEqual(len(item['answers'][0]['fileIds'].keys()), 1)
        self.assertIn('feedbacks', item['answers'][0])
        self.assertTrue(len(item['answers'][0]['feedbacks']) == 1)

        image_asset_label = 'medium849946232588888784replacement_image_png'

        asset_id = item['answers'][0]['fileIds'][image_asset_label]['assetId']
        asset_content_id = item['answers'][0]['fileIds'][image_asset_label]['assetContentId']

        expected_string = """<modalFeedback identifier="Feedback864753096" outcomeIdentifier="FEEDBACKMODAL" showHide="show"><p>You did it!</p><p><img alt="CLIx" height="182" src="/api/v1/repository/repositories/{0}/assets/{1}/contents/{2}/stream" width="614"/></p></modalFeedback>""".format(str(self._bank.ident).replace('assessment.Bank', 'repository.Repository'),
                                                                                                                                                                                                                                                                                                    asset_id,
                                                                                                                                                                                                                                                                                                    asset_content_id)

        self.assertEqual(
            item['answers'][0]['feedbacks'][0]['text'],
            expected_string
        )

        for index in [1, 2]:
            self.assertEqual(
                item['answers'][index]['genusTypeId'],
                str(WRONG_ANSWER_GENUS)
            )
            self.assertEqual(
                len(item['answers'][index]['choiceIds']),
                1
            )
            self.assertIn('fileIds', item['answers'][index])
            self.assertEqual(len(item['answers'][index]['fileIds'].keys()), 1)
            self.assertIn('feedbacks', item['answers'][index])
            self.assertTrue(len(item['answers'][index]['feedbacks']) == 1)

            image_asset_label = 'medium534315617922181373draggable_red_dot_png'

            asset_id = item['answers'][index]['fileIds'][image_asset_label]['assetId']
            asset_content_id = item['answers'][index]['fileIds'][image_asset_label]['assetContentId']

            expected_string = """<modalFeedback identifier="Feedback1588452919" outcomeIdentifier="FEEDBACKMODAL" showHide="show"><p>Sorry, bad choice</p><p><img alt="oops" height="20" src="/api/v1/repository/repositories/{0}/assets/{1}/contents/{2}/stream" width="20"/></p></modalFeedback>""".format(str(self._bank.ident).replace('assessment.Bank', 'repository.Repository'),
                                                                                                                                                                                                                                                                                                             asset_id,
                                                                                                                                                                                                                                                                                                             asset_content_id)

            self.assertEqual(
                item['answers'][index]['feedbacks'][0]['text'],
                expected_string
            )

    def test_audio_file_in_question_gets_saved(self):
        url = '{0}/items'.format(self.url)
        self._audio_recording_test_file.seek(0)
        req = self.app.post(url,
                            upload_files=[('qtiFile', 'testFile2', self._audio_recording_test_file.read())])
        self.ok(req)
        item = self.json(req)

        url = '{0}/{1}/qti'.format(url,
                                   item['id'])
        req = self.app.get(url)
        self.ok(req)
        qti = BeautifulSoup(req.body, 'lxml-xml').assessmentItem
        expected_string_start = '/api/v1/repository/repositories/'
        self.assertIn(expected_string_start,
                      qti.itemBody.contents[1].source['src'])

    def test_audio_elements_get_autoplay_false_flag(self):
        url = '{0}/items'.format(self.url)
        self._audio_everywhere_test_file.seek(0)
        req = self.app.post(url,
                            upload_files=[('qtiFile', 'testQTI.zip', self._audio_everywhere_test_file.read())])
        self.ok(req)
        item = self.json(req)

        url = '{0}/{1}/qti'.format(url,
                                   item['id'])
        req = self.app.get(url)
        self.ok(req)
        qti = BeautifulSoup(req.body, 'lxml-xml').assessmentItem
        first_tag = True
        for object_ in qti.find_all('object'):
            if first_tag:
                self.assertEqual(
                    len(object_.contents),
                    0
                )
                first_tag = False
            else:
                self.assertEqual(
                    len(object_.contents),
                    3)
                self.assertEqual(
                    object_.contents[0],
                    u'\n'
                )
                self.assertEqual(
                    str(object_.contents[1]),
                    '<param name="autoplay" value="false"/>'
                )
                self.assertEqual(
                    object_.contents[2],
                    u'\n'
                )

    def test_audio_in_choices_always_get_autoplay_false_flag(self):
        url = '{0}/items'.format(self.url)
        self._audio_in_choices_test_file.seek(0)
        req = self.app.post(url,
                            upload_files=[('qtiFile', 'testQTI.zip', self._audio_in_choices_test_file.read())])
        self.ok(req)
        item = self.json(req)

        url = '{0}/{1}/qti'.format(url,
                                   item['id'])
        req = self.app.get(url)
        self.ok(req)
        qti = BeautifulSoup(req.body, 'lxml-xml').assessmentItem
        for object_ in qti.find_all('object'):
            self.assertEqual(
                len(object_.contents),
                3)
            self.assertEqual(
                object_.contents[0],
                u'\n'
            )
            self.assertEqual(
                str(object_.contents[1]),
                '<param name="autoplay" value="false"/>'
            )
            self.assertEqual(
                object_.contents[2],
                u'\n'
            )

    def test_with_taken_can_get_question_qti_without_answers(self):
        url = '{0}/assessmentstaken/{1}/questions?qti'.format(self.url,
                                                              unquote(str(self._taken.ident)))
        req = self.app.get(url)
        self.ok(req)

        data = self.json(req)['data'][0]

        self.assertEqual(
            data['genusTypeId'],
            str(QTI_QUESTION_CHOICE_INTERACTION_GENUS)
        )

        self.assertNotIn('question', data)
        self.assertNotIn('answers', data)

        qti = BeautifulSoup(data['qti'], 'lxml-xml').assessmentItem
        self.assertTrue(qti.itemBody.choiceInteraction)
        self.assertFalse(qti.responseDeclaration)
        self.assertFalse(qti.responseProcessing)

    def test_with_taken_can_get_individual_question_qti(self):
        questions_url = '{0}/assessmentstaken/{1}/questions'.format(self.url,
                                                                    unquote(str(self._taken.ident)))

        req = self.app.get(questions_url)
        self.ok(req)
        data = self.json(req)

        question_id = data['data'][0]['id']

        url = '{0}/assessmentstaken/{1}/questions/{2}/qti'.format(self.url,
                                                                  unquote(str(self._taken.ident)),
                                                                  question_id)
        req = self.app.get(url)
        self.ok(req)

        qti = BeautifulSoup(req.body, 'lxml-xml')

        self.assertTrue(qti.itemBody.choiceInteraction)
        self.assertFalse(qti.responseDeclaration)
        self.assertFalse(qti.responseProcessing)

    def test_with_all_items_can_include_qti_flag(self):
        url = '{0}/items?qti'.format(self.url)
        req = self.app.get(url)
        data = self.json(req)
        qti_xml = BeautifulSoup(data[0]['qti'], 'lxml-xml')
        item = qti_xml.assessmentItem
        self.assertTrue(item.itemBody.choiceInteraction)
        self.assertTrue(item.responseDeclaration)
        self.assertTrue(item.responseProcessing)

    def test_media_images_get_uploaded_and_assigned(self):
        url = '{0}/items'.format(self.url)
        self._test_file.seek(0)
        req = self.app.post(url,
                            upload_files=[('qtiFile', 'testFile2', self._test_file2.read())])
        self.ok(req)
        item = self.json(req)

        self.assertEqual(
            item['genusTypeId'],
            str(QTI_ITEM_CHOICE_INTERACTION_GENUS)
        )

        self.assertEqual(
            item['question']['genusTypeId'],
            str(QTI_QUESTION_CHOICE_INTERACTION_GENUS)
        )

        self.assertEqual(
            item['answers'][0]['genusTypeId'],
            str(RIGHT_ANSWER_GENUS)
        )

        self.assertNotEqual(
            item['id'],
            str(self._item.ident)
        )

        self.assertIn('fileIds', item['question'])
        self.assertEqual(
            len(item['question']['fileIds']),
            2
        )
        file_1 = item['question']['fileIds'].keys()[0]
        self.assertIn('assetContentId',
                      item['question']['fileIds'][file_1])

    def test_media_file_names_are_replaced_with_url_on_qti_get(self):
        url = '{0}/items'.format(self.url)
        self._test_file.seek(0)
        req = self.app.post(url,
                            upload_files=[('qtiFile', 'testFile2', self._test_file2.read())])
        self.ok(req)
        item = self.json(req)

        url = '{0}/{1}/qti'.format(url,
                                   item['id'])
        req = self.app.get(url)
        self.ok(req)
        qti = BeautifulSoup(req.body, 'lxml-xml').assessmentItem
        expected_string_start = '/api/v1/repository/repositories/'
        for choice in qti.itemBody.choiceInteraction.find_all('simpleChoice'):
            if choice.find('img'):
                self.assertIn(expected_string_start,
                              choice.img['src'])

    def test_can_get_qti_items_in_assessment(self):
        url = '{0}/assessments/{1}/items?qti'.format(self.url,
                                                     unquote(str(self._assessment.ident)))
        req = self.app.get(url)
        data = self.json(req)[0]

        self.assertIn('qti', data)
        qti_xml = BeautifulSoup(data['qti'], 'lxml-xml')

        item = qti_xml.assessmentItem
        self.assertTrue(item.itemBody.choiceInteraction)
        self.assertTrue(item.responseDeclaration)
        self.assertTrue(item.responseProcessing)

    def test_uploading_same_qti_item_id_sets_provenance(self):
        url = '{0}/items'.format(self.url)
        self._test_file2.seek(0)
        req = self.app.post(url,
                            upload_files=[('qtiFile', 'testFile', self._test_file2.read())])
        self.ok(req)
        item = self.json(req)

        self._test_file2.seek(0)
        req = self.app.post(url,
                            upload_files=[('qtiFile', 'testFile', self._test_file2.read())])
        self.ok(req)
        item2 = self.json(req)

        self.assertNotEqual(item['id'], item2['id'])
        self.assertEqual(item['provenanceId'], '')
        self.assertEqual(item2['provenanceId'], item['id'])

    def test_uploading_same_qti_item_id_archives_old_item(self):
        url = '{0}/items'.format(self.url)
        self._test_file2.seek(0)
        req = self.app.post(url,
                            upload_files=[('qtiFile', 'testFile', self._test_file2.read())])
        self.ok(req)
        item = self.json(req)
        original_item_id = item['id']

        banks_url = '/api/v1/assessment/banks'
        req = self.app.get(banks_url)
        self.ok(req)
        banks = self.json(req)
        self.assertEqual(len(banks), 1)

        self._test_file2.seek(0)
        req = self.app.post(url,
                            upload_files=[('qtiFile', 'testFile', self._test_file2.read())])
        self.ok(req)
        item2 = self.json(req)

        self.assertNotEqual(item['id'], item2['id'])

        req = self.app.get(url)
        self.ok(req)
        items = self.json(req)

        self.assertEqual(len(items), 2)  # because there is another question from the setup
        item_ids = [i['id'] for i in items]
        self.assertIn(item2['id'], item_ids)

        req = self.app.get(banks_url)
        self.ok(req)
        banks = self.json(req)
        self.assertEqual(len(banks), 2)
        archive_bank = [b for b in banks if 'archive' in b['genusTypeId']][0]

        url = '/api/v1/assessment/banks/{0}/items'.format(archive_bank['id'])
        req = self.app.get(url)
        self.ok(req)
        items = self.json(req)
        self.assertEqual(len(items), 1)
        self.assertEqual(
            items[0]['id'],
            original_item_id
        )

    def test_archiving_only_creates_one_archive_bank(self):
        url = '{0}/items'.format(self.url)
        self._test_file2.seek(0)
        req = self.app.post(url,
                            upload_files=[('qtiFile', 'testFile', self._test_file2.read())])
        self.ok(req)
        item = self.json(req)
        original_item_id = item['id']

        banks_url = '/api/v1/assessment/banks'
        req = self.app.get(banks_url)
        self.ok(req)
        banks = self.json(req)
        self.assertEqual(len(banks), 1)

        self._test_file2.seek(0)
        req = self.app.post(url,
                            upload_files=[('qtiFile', 'testFile', self._test_file2.read())])
        self.ok(req)
        item2 = self.json(req)

        self.assertNotEqual(item['id'], item2['id'])

        req = self.app.get(url)
        self.ok(req)
        items = self.json(req)

        self.assertEqual(len(items), 2)  # because there is another question from the setup
        item_ids = [i['id'] for i in items]
        self.assertIn(item2['id'], item_ids)

        req = self.app.get(banks_url)
        self.ok(req)
        banks = self.json(req)
        self.assertEqual(len(banks), 2)
        archive_bank = [b for b in banks if 'archive' in b['genusTypeId']][0]

        archive_bank_items_url = '/api/v1/assessment/banks/{0}/items'.format(archive_bank['id'])
        req = self.app.get(archive_bank_items_url)
        self.ok(req)
        items = self.json(req)
        self.assertEqual(len(items), 1)
        self.assertEqual(
            items[0]['id'],
            original_item_id
        )

        self._test_file2.seek(0)
        req = self.app.post(url,
                            upload_files=[('qtiFile', 'testFile', self._test_file2.read())])
        self.ok(req)
        item3 = self.json(req)

        req = self.app.get(banks_url)
        self.ok(req)
        banks = self.json(req)
        self.assertEqual(len(banks), 2)

        req = self.app.get(archive_bank_items_url)
        self.ok(req)
        items = self.json(req)
        self.assertEqual(len(items), 2)
        item_ids = [i['id'] for i in items]
        self.assertIn(original_item_id, item_ids)
        self.assertIn(item2['id'], item_ids)

        req = self.app.get(url)
        self.ok(req)
        items = self.json(req)

        self.assertEqual(len(items), 2)  # because there is another question from the setup
        item_ids = [i['id'] for i in items]
        self.assertIn(item3['id'], item_ids)

    def test_feedback_gets_set_on_qti_mc_upload(self):
        url = '{0}/items'.format(self.url)
        self._mc_feedback_test_file.seek(0)
        req = self.app.post(url,
                            upload_files=[('qtiFile', 'testFile', self._mc_feedback_test_file.read())])
        self.ok(req)
        item = self.json(req)

        self.assertEqual(
            item['genusTypeId'],
            str(QTI_ITEM_CHOICE_INTERACTION_GENUS)
        )

        self.assertEqual(
            item['question']['genusTypeId'],
            str(QTI_QUESTION_CHOICE_INTERACTION_GENUS)
        )

        self.assertEqual(len(item['answers']), 4)

        self.assertEqual(
            item['answers'][0]['genusTypeId'],
            str(RIGHT_ANSWER_GENUS)
        )

        for i in range(1, 4):
            self.assertEqual(
                item['answers'][i]['genusTypeId'],
                str(WRONG_ANSWER_GENUS)
            )
        expected_matches = {
            "id8f5eed97-9e0d-4df5-a4c5-2a11bc6ae985": u"<p>Well done!<br/>Zo is hurt. But his wound is not serious - just some light scratches.\xa0</p>",
            "id5bde4781-dcb6-4d1e-8954-8d81f21efe3f": "<p>Listen again and answer.</p>",
            "id8e65e4e1-e891-4c30-a35c-5cc43df18710": "<p>Is Zo in a lot of pain? Does he need to see a doctor immediately?</p>",
            "ida1986000-f320-4346-b289-7310974afd1a": "<p>Zo has hurt himself.</p>"
        }

        for answer in item['answers']:
            answer_choice = answer['choiceIds'][0]
            self.assertIn(expected_matches[answer_choice],
                          answer['feedbacks'][0]['text'])

        self.assertNotEqual(
            item['id'],
            str(self._item.ident)
        )

    def test_item_name_removes_language_code(self):
        url = '{0}/items'.format(self.url)
        self._mc_feedback_test_file.seek(0)
        req = self.app.post(url,
                            upload_files=[('qtiFile',
                                           self._filename(self._mc_feedback_test_file),
                                           self._mc_feedback_test_file.read())])
        self.ok(req)
        item = self.json(req)

        self.assertEqual(
            item['displayName']['text'],
            'ee_u1l01a04q03'
        )

    def test_missing_media_element_just_gets_filtered_out(self):
        url = '{0}/items'.format(self.url)
        self._mw_sentence_missing_audio_test_file.seek(0)
        req = self.app.post(url,
                            upload_files=[('qtiFile', 'testFile', self._mw_sentence_missing_audio_test_file.read())])
        self.ok(req)
        item = self.json(req)

        self.assertEqual(
            item['genusTypeId'],
            str(QTI_ITEM_ORDER_INTERACTION_MW_SENTENCE_GENUS)
        )

        self.assertEqual(
            item['question']['genusTypeId'],
            str(QTI_QUESTION_ORDER_INTERACTION_MW_SENTENCE_GENUS)
        )

        self.assertEqual(
            item['answers'][0]['genusTypeId'],
            str(RIGHT_ANSWER_GENUS)
        )
        self.assertEqual(
            len(item['answers'][0]['choiceIds']),
            7
        )
        self.assertIn('feedbacks', item['answers'][0])
        self.assertTrue(len(item['answers'][0]['feedbacks']) == 1)

        self.assertEqual(
            item['answers'][1]['genusTypeId'],
            str(WRONG_ANSWER_GENUS)
        )
        self.assertEqual(
            len(item['answers'][1]['choiceIds']),
            1
        )
        self.assertIsNone(item['answers'][1]['choiceIds'][0])
        self.assertIn('feedbacks', item['answers'][1])
        self.assertTrue(len(item['answers'][1]['feedbacks']) == 1)

        self.assertEqual(
            len(item['question']['choices']),
            7
        )

        for choice in item['question']['multiLanguageChoices']:
            self.assertTrue(len(choice['texts']) == 1)
            for text in choice['texts']:
                self.assertIn('<p class="', text['text'])
                if any(n in text['text'] for n in ['the bags', 'the bus', 'the bridge', 'Raju', 'the seat']):
                    self.assertIn('"noun"', text['text'])
                elif any(p in text['text'] for p in ['on']):
                    self.assertIn('"prep"', text['text'])
                elif 'left' in text['text']:
                    self.assertIn('"verb"', text['text'])
                elif 'under' in text['text']:
                    self.assertIn('"adverb"', text['text'])
        for choice in item['question']['choices']:
            self.assertIn('<p class="', choice['text'])
            if any(n in choice['text'] for n in ['the bags', 'the bus', 'the bridge', 'Raju', 'the seat']):
                self.assertIn('"noun"', choice['text'])
            elif any(p in choice['text'] for p in ['on']):
                self.assertIn('"prep"', choice['text'])
            elif 'left' in choice['text']:
                self.assertIn('"verb"', choice['text'])
            elif 'under' in choice['text']:
                self.assertIn('"adverb"', choice['text'])

        self.assertNotEqual(
            item['id'],
            str(self._item.ident)
        )

        self.assertIn('%2Fmedia%2Fee_u1l01a01r04_.mp3', item['question']['texts'][0]['text'])

    def test_learning_objectives_are_parsed_and_saved(self):
        url = '{0}/items'.format(self.url)
        self._mw_sandbox_test_file.seek(0)
        req = self.app.post(url,
                            upload_files=[('qtiFile', 'testFile', self._mw_sandbox_test_file.read())])
        self.ok(req)
        item = self.json(req)
        self.assertEqual(
            item['learningObjectiveIds'],
            ['learning.Objective%3AGrade 9.B2%40CLIX.TISS.EDU']
        )

    def test_can_upload_mw_sandbox_qti_file(self):
        url = '{0}/items'.format(self.url)
        self._mw_sandbox_test_file.seek(0)
        req = self.app.post(url,
                            upload_files=[('qtiFile', 'testFile', self._mw_sandbox_test_file.read())])
        self.ok(req)
        item = self.json(req)

        self.assertEqual(
            item['genusTypeId'],
            str(QTI_ITEM_ORDER_INTERACTION_MW_SANDBOX_GENUS)
        )

        self.assertEqual(
            item['question']['genusTypeId'],
            str(QTI_QUESTION_ORDER_INTERACTION_MW_SANDBOX_GENUS)
        )

        self.assertEqual(
            item['answers'][0]['genusTypeId'],
            str(RIGHT_ANSWER_GENUS)
        )
        # deprecated -- there should be no answer choices; is a file submission if anything
        # self.assertEqual(
        #     len(item['answers'][0]['choiceIds']),
        #     13
        # )
        self.assertEqual(
            len(item['question']['choices']),
            13
        )

        for choice in item['question']['multiLanguageChoices']:
            self.assertTrue(len(choice['texts']) == 1)
            for text in choice['texts']:
                self.assertIn('<p class="', text['text'])
                if any(n == text['text'] for n in ['the bags', 'the bus',
                                                   'the bridge', "Raju's",
                                                   'the seat', 'the airport',
                                                   'the city', 'the bicycle']):
                    self.assertIn('"noun"', text['text'])
                elif any(p == text['text'] for p in ['on']):
                    self.assertIn('"prep"', text['text'])
                elif any(v == text['text'] for v in ['are', 'left', 'dropped']):
                    self.assertIn('"verb"', text['text'])
                elif any(av == text['text'] for av in ['under', 'on top of']):
                    self.assertIn('"adverb"', text['text'])
        for choice in item['question']['choices']:
            self.assertIn('<p class="', choice['text'])
            if any(n == choice['text'] for n in ['the bags', 'the bus',
                                                 'the bridge', "Raju's",
                                                 'the seat', 'the airport',
                                                 'the city', 'the bicycle']):
                self.assertIn('"noun"', choice['text'])
            elif any(p == choice['text'] for p in ['on']):
                self.assertIn('"prep"', choice['text'])
            elif any(v == choice['text'] for v in ['are', 'left', 'dropped']):
                self.assertIn('"verb"', choice['text'])
            elif any(av == choice['text'] for av in ['under', 'on top of']):
                self.assertIn('"adverb"', choice['text'])

        self.assertNotEqual(
            item['id'],
            str(self._item.ident)
        )

        item_details_url = '{0}?qti'.format(url)
        req = self.app.get(item_details_url)
        self.ok(req)
        data = self.json(req)
        item = [i for i in data if i['id'] == item['id']][0]
        self.assertIn('qti', item)
        item_qti = BeautifulSoup(item['qti'], 'lxml-xml').assessmentItem
        expected_values = ['id14a6824a-79f2-4c00-ac6a-b41cbb64db45',
                           'id969e920d-6d22-4d06-b4ac-40a821e350c6',
                           'id820fae90-3794-40d1-bee0-daa36da223b3',
                           'id2d13b6d7-87e9-4022-a4b6-dcdbba5c8b60',
                           'idf1583dac-fb7a-4365-aa0d-f64e5ab61029',
                           'idd8449f3e-820f-46f8-9529-7e019fceaaa6',
                           'iddd689e9d-0cd0-478d-9d37-2856f866a757',
                           'id1c0298a6-90ed-4bc9-987a-7fd0165c0fcf',
                           'id41288bb9-e76e-4313-bf57-2101edfe3a76',
                           'id4435ccd8-df65-45e7-8d82-6c077473d8d4',
                           'idfffc63c0-f227-4ac4-ad0a-2f0b92b28fd1',
                           'id472afb75-4aa9-4daa-a163-075798ee57ab',
                           'id8c68713f-8e39-446b-a6c8-df25dfb8118e']
        for index, value in enumerate(item_qti.responseDeclaration.correctResponse.find_all('value')):
            self.assertEqual(value.string.strip(), expected_values[index])

        item_body = item_qti.itemBody

        order_interaction = item_body.orderInteraction.extract()

        audio_asset_label = 'ee_u1l01a01r04__mp3'
        asset_id = item['question']['fileIds'][audio_asset_label]['assetId']
        asset_content_id = item['question']['fileIds'][audio_asset_label]['assetContentId']

        expected_string = """<itemBody>
<p>
   Movable Word Sandbox:
  </p>
<p>
<audio autoplay="autoplay" controls="controls" style="width: 125px">
<source src="/api/v1/repository/repositories/{0}/assets/{1}/contents/{2}/stream" type="audio/mpeg"/>
</audio>
</p>

</itemBody>""".format(str(self._bank.ident).replace('assessment.Bank', 'repository.Repository'),
                      asset_id,
                      asset_content_id)

        self.assertEqual(
            str(item_body),
            expected_string
        )

        self.assertEqual(
            len(order_interaction.find_all('simpleChoice')),
            13
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
            "id14a6824a-79f2-4c00-ac6a-b41cbb64db45": """<simpleChoice identifier="id14a6824a-79f2-4c00-ac6a-b41cbb64db45">
<p class="noun">
     the bus
    </p>
</simpleChoice>""",
            "id969e920d-6d22-4d06-b4ac-40a821e350c6": """<simpleChoice identifier="id969e920d-6d22-4d06-b4ac-40a821e350c6">
<p class="noun">
     the airport
    </p>
</simpleChoice>""",
            "id820fae90-3794-40d1-bee0-daa36da223b3": """<simpleChoice identifier="id820fae90-3794-40d1-bee0-daa36da223b3">
<p class="noun">
     the bags
    </p>
</simpleChoice>""",
            "id2d13b6d7-87e9-4022-a4b6-dcdbba5c8b60": """<simpleChoice identifier="id2d13b6d7-87e9-4022-a4b6-dcdbba5c8b60">
<p class="verb">
     are
    </p>
</simpleChoice>""",
            "idf1583dac-fb7a-4365-aa0d-f64e5ab61029": """<simpleChoice identifier="idf1583dac-fb7a-4365-aa0d-f64e5ab61029">
<p class="adverb">
     under
    </p>
</simpleChoice>""",
            "idd8449f3e-820f-46f8-9529-7e019fceaaa6": """<simpleChoice identifier="idd8449f3e-820f-46f8-9529-7e019fceaaa6">
<p class="prep">
     on
    </p>
</simpleChoice>""",
            "iddd689e9d-0cd0-478d-9d37-2856f866a757": """<simpleChoice identifier="iddd689e9d-0cd0-478d-9d37-2856f866a757">
<p class="adverb">
     on top of
    </p>
</simpleChoice>""",
            "id1c0298a6-90ed-4bc9-987a-7fd0165c0fcf": """<simpleChoice identifier="id1c0298a6-90ed-4bc9-987a-7fd0165c0fcf">
<p class="noun">
     Raju's
    </p>
</simpleChoice>""",
            "id41288bb9-e76e-4313-bf57-2101edfe3a76": """<simpleChoice identifier="id41288bb9-e76e-4313-bf57-2101edfe3a76">
<p class="verb">
     left
    </p>
</simpleChoice>""",
            "id4435ccd8-df65-45e7-8d82-6c077473d8d4": """<simpleChoice identifier="id4435ccd8-df65-45e7-8d82-6c077473d8d4">
<p class="noun">
     the seat
    </p>
</simpleChoice>""",
            "idfffc63c0-f227-4ac4-ad0a-2f0b92b28fd1": """<simpleChoice identifier="idfffc63c0-f227-4ac4-ad0a-2f0b92b28fd1">
<p class="noun">
     the city
    </p>
</simpleChoice>""",
            "id472afb75-4aa9-4daa-a163-075798ee57ab": """<simpleChoice identifier="id472afb75-4aa9-4daa-a163-075798ee57ab">
<p class="noun">
     the bicycle
    </p>
</simpleChoice>""",
            "id8c68713f-8e39-446b-a6c8-df25dfb8118e": """<simpleChoice identifier="id8c68713f-8e39-446b-a6c8-df25dfb8118e">
<p class="verb">
     dropped
    </p>
</simpleChoice>"""
        }

        for choice in order_interaction.find_all('simpleChoice'):
            choice_id = choice['identifier']
            self.assertEqual(
                str(choice),
                expected_choices[choice_id]
            )

    def test_can_upload_mc_multi_select(self):
        url = '{0}/items'.format(self.url)
        self._mc_multi_select_test_file.seek(0)
        req = self.app.post(url,
                            upload_files=[('qtiFile', 'testFile', self._mc_multi_select_test_file.read())])
        self.ok(req)
        item = self.json(req)

        self.assertEqual(
            item['genusTypeId'],
            str(QTI_ITEM_CHOICE_INTERACTION_MULTI_GENUS)
        )

        self.assertEqual(
            item['question']['genusTypeId'],
            str(QTI_QUESTION_CHOICE_INTERACTION_MULTI_GENUS)
        )

        self.assertEqual(
            item['answers'][0]['genusTypeId'],
            str(RIGHT_ANSWER_GENUS)
        )

        self.assertEqual(
            len(item['answers'][0]['choiceIds']),
            3
        )

        self.assertEqual(
            len(item['answers']),
            2
        )

        self.assertNotEqual(
            item['id'],
            str(self._item.ident)
        )

        # now verify the QTI XML matches the JSON format
        url = '{0}/{1}/qti'.format(url, unquote(item['id']))
        req = self.app.get(url)
        self.ok(req)
        qti_xml = BeautifulSoup(req.body, 'lxml-xml').assessmentItem
        item_body = qti_xml.itemBody

        diamond_label = 'medium5027634271179083907square_png'
        rectangle_label = 'medium2852808971416763161rectangle_png'
        parallel_label = 'medium5011234143907175882parallel_png'
        regular_square_label = 'medium3312330729255923592regularsquare_png'

        diamond_asset_id = item['question']['fileIds'][diamond_label]['assetId']
        diamond_asset_content_id = item['question']['fileIds'][diamond_label]['assetContentId']
        rectangle_asset_id = item['question']['fileIds'][rectangle_label]['assetId']
        rectangle_asset_content_id = item['question']['fileIds'][rectangle_label]['assetContentId']
        parallel_asset_id = item['question']['fileIds'][parallel_label]['assetId']
        parallel_asset_content_id = item['question']['fileIds'][parallel_label]['assetContentId']
        regular_square_asset_id = item['question']['fileIds'][regular_square_label]['assetId']
        regular_square_asset_content_id = item['question']['fileIds'][regular_square_label]['assetContentId']

        expected_string = """<itemBody>
<p dir="ltr" id="docs-internal-guid-46f83555-04c7-ceb0-1838-715e13031a60">
   In the diagram below,
  </p>
<p>
<strong>
</strong>
</p>
<p dir="ltr">
   A is the set of rectangles, and
  </p>
<p dir="ltr">
   B is the set of rhombuses
  </p>
<p dir="ltr">
</p>
<p dir="ltr">
<img alt="venn1" height="202" src="https://lh5.googleusercontent.com/a7NFx8J7jcDSr37Nen6ReW2doooJXZDm6GD1HQTfImkrzah94M_jkYoMapeYoRilKSSOz0gxVOUto0n5R4GWI4UWSnmzoTxH0VMQqRgzYMKWjJCG6OQgp8VPB4ghBAAeHlgI4ze7" width="288"/>
</p>
<p dir="ltr">
</p>
<p>
<strong>
    Which all shape(s) can be contained in the gray shaded area?
    <br/>
</strong>
</p>
<choiceInteraction maxChoices="0" responseIdentifier="RESPONSE_1" shuffle="false">
<simpleChoice identifier="idb5345daa-a5c2-4924-a92b-e326886b5d1d">
<p>
<img alt="parallelagram" height="147" src="/api/v1/repository/repositories/{0}/assets/{1}/contents/{2}/stream" width="186"/>
</p>
</simpleChoice>
<simpleChoice identifier="id47e56db8-ee16-4111-9bcc-b8ac9716bcd4">
<p>
<img alt="square" height="141" src="/api/v1/repository/repositories/{0}/assets/{3}/contents/{4}/stream" width="144"/>
</p>
</simpleChoice>
<simpleChoice identifier="id01913fba-e66d-4a01-9625-94102847faac">
<p>
<img alt="rectangle" height="118" src="/api/v1/repository/repositories/{0}/assets/{5}/contents/{6}/stream" width="201"/>
</p>
</simpleChoice>
<simpleChoice identifier="id4f525d00-e24c-4ac3-a104-848a2cd686c0">
<p>
<img alt="diamond shape" height="146" src="/api/v1/repository/repositories/{0}/assets/{7}/contents/{8}/stream" width="148"/>
</p>
</simpleChoice>
<simpleChoice identifier="id18c8cc80-68d1-4c1f-b9f0-cb345bad2862">
<p>
<strong>
<span id="docs-internal-guid-46f83555-04cb-9334-80dc-c56402044c02">
       None of these
      </span>
<br/>
</strong>
</p>
</simpleChoice>
</choiceInteraction>
</itemBody>""".format(str(self._bank.ident).replace('assessment.Bank', 'repository.Repository'),
                      parallel_asset_id,
                      parallel_asset_content_id,
                      regular_square_asset_id,
                      regular_square_asset_content_id,
                      rectangle_asset_id,
                      rectangle_asset_content_id,
                      diamond_asset_id,
                      diamond_asset_content_id)

        self.assertEqual(
            str(item_body),
            expected_string
        )

    def test_can_upload_short_answer(self):
        url = '{0}/items'.format(self.url)
        self._short_answer_test_file.seek(0)
        req = self.app.post(url,
                            upload_files=[('qtiFile', 'testFile', self._short_answer_test_file.read())])
        self.ok(req)
        item = self.json(req)

        self.assertEqual(
            item['genusTypeId'],
            str(QTI_ITEM_EXTENDED_TEXT_INTERACTION_GENUS)
        )

        self.assertEqual(
            item['question']['genusTypeId'],
            str(QTI_QUESTION_EXTENDED_TEXT_INTERACTION_GENUS)
        )

        self.assertEqual(
            len(item['answers']),
            1
        )

        self.assertEqual(
            item['answers'][0]['genusTypeId'],
            str(RIGHT_ANSWER_GENUS)
        )

        self.assertIn('<p></p>', item['answers'][0]['feedbacks'][0]['text'])

        self.assertNotEqual(
            item['id'],
            str(self._item.ident)
        )

        self.assertEqual(item['question']['maxStrings'], 300)
        self.assertEqual(item['question']['expectedLength'], 100)
        self.assertEqual(item['question']['expectedLines'], 5)

        # now verify the QTI XML matches the JSON format
        url = '{0}/{1}/qti'.format(url, unquote(item['id']))
        req = self.app.get(url)
        self.ok(req)
        qti_xml = BeautifulSoup(req.body, 'lxml-xml').assessmentItem
        item_body = qti_xml.itemBody
        asset_label = item['question']['fileIds'].keys()[0]
        asset_id = item['question']['fileIds'][asset_label]['assetId']
        asset_content_id = item['question']['fileIds'][asset_label]['assetContentId']

        expected_string = """<itemBody>
<p>
<strong>
<span id="docs-internal-guid-46f83555-04bd-94f0-a53d-94c5c97ab6e6">
     Which of the following figure(s) is/are parallelogram(s)? Give a reason for your choice.
    </span>
<br/>
</strong>
</p>
<p>
<strong>
<img alt="A set of four shapes." height="204" src="/api/v1/repository/repositories/{0}/assets/{1}/contents/{2}/stream" width="703"/>
</strong>
</p>
<extendedTextInteraction expectedLength="100" expectedLines="5" maxStrings="300" responseIdentifier="RESPONSE_1"/>
</itemBody>""".format(str(self._bank.ident).replace('assessment.Bank', 'repository.Repository'),
                      asset_id,
                      asset_content_id)
        self.assertEqual(
            str(item_body),
            expected_string
        )

    def test_can_upload_mw_fill_in_the_blank(self):
        url = '{0}/items'.format(self.url)
        self._mw_fill_in_the_blank_test_file.seek(0)
        req = self.app.post(url,
                            upload_files=[('qtiFile', 'testFile', self._mw_fill_in_the_blank_test_file.read())])
        self.ok(req)
        item = self.json(req)

        self.assertEqual(
            item['genusTypeId'],
            str(QTI_ITEM_INLINE_CHOICE_INTERACTION_GENUS)
        )

        self.assertEqual(
            item['question']['genusTypeId'],
            str(QTI_QUESTION_INLINE_CHOICE_INTERACTION_GENUS)
        )

        self.assertIn('RESPONSE_1', item['question']['choices'])
        self.assertIn('RESPONSE_2', item['question']['choices'])

        response_1_choice_ids = [c['id'] for c in item['question']['choices']['RESPONSE_1']]
        response_2_choice_ids = [c['id'] for c in item['question']['choices']['RESPONSE_2']]

        self.assertIn('[_1_1_1_1_1_1_1', response_1_choice_ids)
        self.assertIn('[_1_1_1_1_1_1', response_2_choice_ids)

        self.assertEqual(
            len(item['answers']),
            2
        )

        self.assertEqual(
            item['answers'][0]['genusTypeId'],
            str(RIGHT_ANSWER_GENUS)
        )
        self.assertIn('RESPONSE_1', item['answers'][0]['inlineRegions'])
        self.assertIn('RESPONSE_2', item['answers'][0]['inlineRegions'])

        self.assertEqual(
            item['answers'][0]['inlineRegions']['RESPONSE_1']['choiceIds'],
            ['[_1_1_1_1_1_1_1']
        )
        self.assertEqual(
            item['answers'][0]['inlineRegions']['RESPONSE_2']['choiceIds'],
            ['[_1_1_1_1_1_1']
        )

        self.assertIn('Yes, you are correct.', item['answers'][0]['feedbacks'][0]['text'])

        self.assertEqual(
            item['answers'][1]['genusTypeId'],
            str(WRONG_ANSWER_GENUS)
        )

        self.assertIn('No, please listen to the story again.', item['answers'][1]['feedbacks'][0]['text'])

        self.assertNotEqual(
            item['id'],
            str(self._item.ident)
        )

        # now verify the QTI XML matches the JSON format
        url = '{0}/{1}/qti'.format(url, unquote(item['id']))
        req = self.app.get(url)
        self.ok(req)
        qti_xml = BeautifulSoup(req.body, 'lxml-xml').assessmentItem
        item_body = qti_xml.itemBody

        inline_choice_interaction_1 = item_body.inlineChoiceInteraction.extract()
        inline_choice_interaction_2 = item_body.inlineChoiceInteraction.extract()

        audio_asset_label = 'ee_u1l01a01r04__mp3'
        image_asset_label = 'medium2741930469600907330bus_png'
        audio_asset_id = item['question']['fileIds'][audio_asset_label]['assetId']
        audio_asset_content_id = item['question']['fileIds'][audio_asset_label]['assetContentId']

        image_asset_id = item['question']['fileIds'][image_asset_label]['assetId']
        image_asset_content_id = item['question']['fileIds'][image_asset_label]['assetContentId']

        expected_string = """<itemBody>
<p>
<p>
<p class="noun">
     Raju's
    </p>
<p class="noun">
     bags
    </p>
<p class="verb">
     are
    </p>
</p>

<p>
<p class="noun">
     the bus
    </p>
<p class="prep">
     in the
    </p>
</p>

   .
  </p>
<p>
<audio autoplay="autoplay" controls="controls" style="width: 125px">
<source src="/api/v1/repository/repositories/{0}/assets/{1}/contents/{2}/stream" type="audio/mpeg"/>
</audio>
</p>
<p>
<img alt="This is a picture of a bus." height="100" src="/api/v1/repository/repositories/{0}/assets/{3}/contents/{4}/stream" width="100"/>
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
            len(inline_choice_interaction_1.find_all('inlineChoice')),
            4
        )
        self.assertEqual(
            inline_choice_interaction_1['responseIdentifier'],
            'RESPONSE_1'
        )
        self.assertEqual(
            inline_choice_interaction_1['shuffle'],
            'true'
        )

        expected_choices_region_1 = {
            "[_1_1_1_1_1_1_1": """<inlineChoice identifier="[_1_1_1_1_1_1_1">
<p class="prep">
      on
     </p>
</inlineChoice>""",
            "[_1_1_1_1_1_1_1_1": """<inlineChoice identifier="[_1_1_1_1_1_1_1_1">
<p class="under">
      under
     </p>
</inlineChoice>""",
            "[_2_1_1_1_1_1_1_1": """<inlineChoice identifier="[_2_1_1_1_1_1_1_1">
<p class="verb">
      lost
     </p>
</inlineChoice>""",
            "[_3_1_1_1_1_1_1_1": """<inlineChoice identifier="[_3_1_1_1_1_1_1_1">
<p class="prep">
      on top of
     </p>
</inlineChoice>"""
        }

        for choice in inline_choice_interaction_1.find_all('inlineChoice'):
            choice_id = choice['identifier']
            self.assertEqual(
                str(choice),
                expected_choices_region_1[choice_id]
            )

        self.assertEqual(
            len(inline_choice_interaction_2.find_all('inlineChoice')),
            4
        )
        self.assertEqual(
            inline_choice_interaction_2['responseIdentifier'],
            'RESPONSE_2'
        )
        self.assertEqual(
            inline_choice_interaction_2['shuffle'],
            'true'
        )

        expected_choices_region_2 = {
            "[_1_1_1_1_1_1": """<inlineChoice identifier="[_1_1_1_1_1_1">
<p class="noun">
      city
     </p>
</inlineChoice>""",
            "[_1_1_1_1_1_1_1": """<inlineChoice identifier="[_1_1_1_1_1_1_1">
<p class="noun">
      town
     </p>
</inlineChoice>""",
            "[_2_1_1_1_1_1_1": """<inlineChoice identifier="[_2_1_1_1_1_1_1">
<p class="noun">
      station
     </p>
</inlineChoice>""",
            "[_3_1_1_1_1_1_1": """<inlineChoice identifier="[_3_1_1_1_1_1_1">
<p class="noun">
      airport
     </p>
</inlineChoice>"""
        }

        for choice in inline_choice_interaction_2.find_all('inlineChoice'):
            choice_id = choice['identifier']
            self.assertEqual(
                str(choice),
                expected_choices_region_2[choice_id]
            )

    def test_can_upload_mw_fill_in_the_blank_2(self):
        """mostly to test that the words post-<inlineChoiceInteraction> are wrapped properly"""
        url = '{0}/items'.format(self.url)
        self._mw_fitb_2_test_file.seek(0)
        req = self.app.post(url,
                            upload_files=[('qtiFile', 'testFile', self._mw_fitb_2_test_file.read())])
        self.ok(req)
        item = self.json(req)

        self.assertEqual(
            item['genusTypeId'],
            str(QTI_ITEM_INLINE_CHOICE_INTERACTION_GENUS)
        )

        self.assertEqual(
            item['question']['genusTypeId'],
            str(QTI_QUESTION_INLINE_CHOICE_INTERACTION_GENUS)
        )

        self.assertIn('RESPONSE_1', item['question']['choices'])

        response_1_choice_ids = [c['id'] for c in item['question']['choices']['RESPONSE_1']]

        self.assertIn('[_1_1_1', response_1_choice_ids)

        self.assertEqual(
            len(item['answers']),
            2
        )

        self.assertEqual(
            item['answers'][0]['genusTypeId'],
            str(RIGHT_ANSWER_GENUS)
        )
        self.assertIn('RESPONSE_1', item['answers'][0]['inlineRegions'])

        self.assertEqual(
            item['answers'][0]['inlineRegions']['RESPONSE_1']['choiceIds'],
            ['[_1_1_1']
        )
        self.assertIn('Yes, you are correct.', item['answers'][0]['feedbacks'][0]['text'])

        self.assertEqual(
            item['answers'][1]['genusTypeId'],
            str(WRONG_ANSWER_GENUS)
        )

        self.assertIn('Please listem to the story and try again.', item['answers'][1]['feedbacks'][0]['text'])

        self.assertNotEqual(
            item['id'],
            str(self._item.ident)
        )

        # now verify the QTI XML matches the JSON format
        url = '{0}/{1}/qti'.format(url, unquote(item['id']))
        req = self.app.get(url)
        self.ok(req)
        qti_xml = BeautifulSoup(req.body, 'lxml-xml').assessmentItem
        item_body = qti_xml.itemBody

        inline_choice_interaction = item_body.inlineChoiceInteraction.extract()

        expected_string = """<itemBody>
<p>
<p>
<p class="noun">
     Raju's
    </p>
</p>

<p>
<p class="verb">
     are
    </p>
<p class="prep">
     on
    </p>
<p class="noun">
     the bus.
    </p>
</p>
</p>
</itemBody>"""

        self.assertEqual(
            str(item_body),
            expected_string
        )

        self.assertEqual(
            len(inline_choice_interaction.find_all('inlineChoice')),
            5
        )
        self.assertEqual(
            inline_choice_interaction['responseIdentifier'],
            'RESPONSE_1'
        )
        self.assertEqual(
            inline_choice_interaction['shuffle'],
            'true'
        )

        expected_choices = {
            "[_1_1": """<inlineChoice identifier="[_1_1">
<p class="noun">
      gifts
     </p>
</inlineChoice>""",
            "[_1_1_1": """<inlineChoice identifier="[_1_1_1">
<p class="noun">
      bags
     </p>
</inlineChoice>""",
            "[_2_1_1": """<inlineChoice identifier="[_2_1_1">
<p class="noun">
      bicycles
     </p>
</inlineChoice>""",
            "[_3_1_1": """<inlineChoice identifier="[_3_1_1">
<p class="noun">
      lunches
     </p>
</inlineChoice>""",
            "[_4_1_1": """<inlineChoice identifier="[_4_1_1">
<p class="noun">
      flowers
     </p>
</inlineChoice>"""
        }

        for choice in inline_choice_interaction.find_all('simpleChoice'):
            choice_id = choice['identifier']
            self.assertEqual(
                str(choice),
                expected_choices[choice_id]
            )

    def test_can_upload_mw_fill_in_the_blank_with_ending_punctuation(self):
        """mostly to test that any ending puncutation . ? ! is included in the output"""
        url = '{0}/items'.format(self.url)
        self._fitb_with_punctuation_test_file.seek(0)
        req = self.app.post(url,
                            upload_files=[('qtiFile',
                                           self._filename(self._fitb_with_punctuation_test_file),
                                           self._fitb_with_punctuation_test_file.read())])
        self.ok(req)
        item = self.json(req)

        self.assertEqual(
            item['genusTypeId'],
            str(QTI_ITEM_INLINE_CHOICE_INTERACTION_GENUS)
        )

        self.assertEqual(
            item['question']['genusTypeId'],
            str(QTI_QUESTION_INLINE_CHOICE_INTERACTION_GENUS)
        )

        self.assertIn('RESPONSE_1', item['question']['choices'])

        response_1_choice_ids = [c['id'] for c in item['question']['choices']['RESPONSE_1']]

        self.assertIn('[_1_1', response_1_choice_ids)

        self.assertEqual(
            len(item['answers']),
            2
        )

        self.assertEqual(
            item['answers'][0]['genusTypeId'],
            str(RIGHT_ANSWER_GENUS)
        )
        self.assertIn('RESPONSE_1', item['answers'][0]['inlineRegions'])

        self.assertEqual(
            item['answers'][0]['inlineRegions']['RESPONSE_1']['choiceIds'],
            ['[_1_1']
        )
        self.assertIn('You are right! Please try the next question.', item['answers'][0]['feedbacks'][0]['text'])

        self.assertEqual(
            item['answers'][1]['genusTypeId'],
            str(WRONG_ANSWER_GENUS)
        )

        self.assertIn('Please try again.', item['answers'][1]['feedbacks'][0]['text'])

        self.assertNotEqual(
            item['id'],
            str(self._item.ident)
        )

        # now verify the QTI XML matches the JSON format
        url = '{0}/{1}/qti'.format(url, unquote(item['id']))
        req = self.app.get(url)
        self.ok(req)
        qti_xml = BeautifulSoup(req.body, 'lxml-xml').assessmentItem
        item_body = qti_xml.itemBody

        inline_choice_interaction = item_body.inlineChoiceInteraction.extract()

        expected_string = """<itemBody>
<p>
<span data-sheets-userformat=\"{\" data-sheets-value=\"{\">
<p>
<p class="other">
      Putting things away
     </p>
<p class="preposition">
      in
     </p>
<p class="other">
      the
     </p>
<p class="adjective">
      proper
     </p>
<p class="noun">
      place
     </p>
<p class="verb">
      makes
     </p>
<p class="noun">
      it
     </p>
</p>

<p>
<p class="other">
      to
     </p>
<p class="verb">
      find
     </p>
<p class="noun">
      them
     </p>
<p class="adverb">
      later
     </p>
     .
    </p>
</span>
</p>
</itemBody>"""

        self.assertEqual(
            str(item_body),
            expected_string
        )

        self.assertEqual(
            len(inline_choice_interaction.find_all('inlineChoice')),
            4
        )
        self.assertEqual(
            inline_choice_interaction['responseIdentifier'],
            'RESPONSE_1'
        )
        self.assertEqual(
            inline_choice_interaction['shuffle'],
            'false'
        )

        expected_choices = {
            "[_1_1": """<inlineChoice identifier="[_1_1">
<p class="adjective">
      easy
     </p>
</inlineChoice>""",
            "[_1_1_1": """<inlineChoice identifier="[_1_1_1">
<p class="adjective">
      neat
     </p>
</inlineChoice>""",
            "[_2_1_1": """<inlineChoice identifier="[_2_1_1">
<p class="adjective">
      fast
     </p>
</inlineChoice>""",
            "[_3_1_1": """<inlineChoice identifier="[_3_1_1">
<p class="adjective">
      good
     </p>
</inlineChoice>"""
        }

        for choice in inline_choice_interaction.find_all('simpleChoice'):
            choice_id = choice['identifier']
            self.assertEqual(
                str(choice),
                expected_choices[choice_id]
            )

    def test_description_saved_if_provided(self):
        url = '{0}/items'.format(self.url)
        self._generic_upload_test_file.seek(0)
        req = self.app.post(url,
                            upload_files=[('qtiFile', 'testFile', self._generic_upload_test_file.read())])
        self.ok(req)
        item = self.json(req)

        self.assertEqual(
            item['description']['text'],
            'Understanding shape properties through construction in LOGO'
        )

    def test_can_provide_both_description_and_type_in_description_field(self):
        url = '{0}/items'.format(self.url)
        self._drag_and_drop_test_file.seek(0)
        req = self.app.post(url,
                            upload_files=[('qtiFile', 'testFile', self._drag_and_drop_test_file.read())])
        self.ok(req)
        item = self.json(req)
        self.assertEqual(
            item['description']['text'],
            'This is an example of a drag and drop story sequence question from the English team.'
        )
        self.assertEqual(
            item['genusTypeId'],
            str(QTI_ITEM_ORDER_INTERACTION_OBJECT_MANIPULATION_GENUS)
        )

    def test_can_upload_drag_and_drop_qti_file(self):
        url = '{0}/items'.format(self.url)
        self._drag_and_drop_test_file.seek(0)
        req = self.app.post(url,
                            upload_files=[('qtiFile', 'testFile', self._drag_and_drop_test_file.read())])
        self.ok(req)
        item = self.json(req)

        self.assertEqual(
            item['genusTypeId'],
            str(QTI_ITEM_ORDER_INTERACTION_OBJECT_MANIPULATION_GENUS)
        )

        self.assertEqual(
            item['question']['genusTypeId'],
            str(QTI_QUESTION_ORDER_INTERACTION_OBJECT_MANIPULATION_GENUS)
        )

        self.assertEqual(
            item['answers'][0]['genusTypeId'],
            str(RIGHT_ANSWER_GENUS)
        )
        self.assertEqual(
            len(item['answers'][0]['choiceIds']),
            4
        )
        self.assertEqual(
            len(item['question']['choices']),
            4
        )

        self.assertNotEqual(
            item['id'],
            str(self._item.ident)
        )

        url = '{0}/{1}/qti'.format(url, unquote(item['id']))
        req = self.app.get(url)
        self.ok(req)
        item_qti = BeautifulSoup(req.body, 'lxml-xml').assessmentItem
        expected_values = ['id127df214-2a19-44da-894a-853948313dae',
                           'iddcbf40ab-782e-4d4f-9020-6b8414699a72',
                           'idb4f6cd03-cf58-4391-9ca2-44b7bded3d4b',
                           'ide576c9cc-d20e-4ba3-8881-716100b796a0']
        for index, value in enumerate(item_qti.responseDeclaration.correctResponse.find_all('value')):
            self.assertEqual(value.string.strip(), expected_values[index])

        item_body = item_qti.itemBody

        order_interaction = item_body.orderInteraction.extract()

        repository_id = str(self._bank.ident).replace('assessment.Bank', 'repository.Repository')
        audio_asset_label = 'audioTestFile__mp3'
        image_1_asset_label = 'medium6529396219987445959Picture1_png'
        image_2_asset_label = 'medium5957728225939996885Picture2_png'
        image_3_asset_label = 'medium4379732137514528329Picture3_png'
        image_4_asset_label = 'medium3189220463551707716Picture4_png'
        audio_asset_id = item['question']['fileIds'][audio_asset_label]['assetId']
        audio_asset_content_id = item['question']['fileIds'][audio_asset_label]['assetContentId']
        image_1_asset_id = item['question']['fileIds'][image_1_asset_label]['assetId']
        image_1_asset_content_id = item['question']['fileIds'][image_1_asset_label]['assetContentId']
        image_2_asset_id = item['question']['fileIds'][image_2_asset_label]['assetId']
        image_2_asset_content_id = item['question']['fileIds'][image_2_asset_label]['assetContentId']
        image_3_asset_id = item['question']['fileIds'][image_3_asset_label]['assetId']
        image_3_asset_content_id = item['question']['fileIds'][image_3_asset_label]['assetContentId']
        image_4_asset_id = item['question']['fileIds'][image_4_asset_label]['assetId']
        image_4_asset_content_id = item['question']['fileIds'][image_4_asset_label]['assetContentId']

        expected_string = """<itemBody>
<p>
   Listen to each audio clip and put the pictures of the story in order.
  </p>
<p>
<audio autoplay="autoplay" controls="controls" style="width: 125px">
<source src="/api/v1/repository/repositories/{0}/assets/{1}/contents/{2}/stream" type="audio/mpeg"/>
</audio>
</p>

</itemBody>""".format(repository_id,
                      audio_asset_id,
                      audio_asset_content_id)

        self.assertEqual(
            str(item_body),
            expected_string
        )

        self.assertEqual(
            len(order_interaction.find_all('simpleChoice')),
            4
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
            "idb4f6cd03-cf58-4391-9ca2-44b7bded3d4b": """<simpleChoice identifier="idb4f6cd03-cf58-4391-9ca2-44b7bded3d4b">
<p>
<img alt="Picture 1" height="100" src="/api/v1/repository/repositories/{0}/assets/{1}/contents/{2}/stream" width="100"/>
</p>
</simpleChoice>""".format(repository_id,
                          image_1_asset_id,
                          image_1_asset_content_id),
            "id127df214-2a19-44da-894a-853948313dae": """<simpleChoice identifier="id127df214-2a19-44da-894a-853948313dae">
<p>
<img alt="Picture 2" height="100" src="/api/v1/repository/repositories/{0}/assets/{1}/contents/{2}/stream" width="100"/>
</p>
</simpleChoice>""".format(repository_id,
                          image_2_asset_id,
                          image_2_asset_content_id),
            "iddcbf40ab-782e-4d4f-9020-6b8414699a72": """<simpleChoice identifier="iddcbf40ab-782e-4d4f-9020-6b8414699a72">
<p>
<img alt="Picture 3" height="100" src="/api/v1/repository/repositories/{0}/assets/{1}/contents/{2}/stream" width="100"/>
</p>
</simpleChoice>""".format(repository_id,
                          image_3_asset_id,
                          image_3_asset_content_id),
            "ide576c9cc-d20e-4ba3-8881-716100b796a0": """<simpleChoice identifier="ide576c9cc-d20e-4ba3-8881-716100b796a0">
<p>
<img alt="Picture 4" height="100" src="/api/v1/repository/repositories/{0}/assets/{1}/contents/{2}/stream" width="100"/>
</p>
</simpleChoice>""".format(repository_id,
                          image_4_asset_id,
                          image_4_asset_content_id)
        }

        for choice in order_interaction.find_all('simpleChoice'):
            choice_id = choice['identifier']
            self.assertEqual(
                str(choice),
                expected_choices[choice_id]
            )

    def test_can_upload_simple_numeric_response_qti_file(self):
        url = '{0}/items'.format(self.url)
        self._simple_numeric_response_test_file.seek(0)
        req = self.app.post(url,
                            upload_files=[('qtiFile', 'testFile', self._simple_numeric_response_test_file.read())])
        self.ok(req)
        item = self.json(req)

        self.assertEqual(
            item['genusTypeId'],
            str(QTI_ITEM_NUMERIC_RESPONSE_INTERACTION_GENUS)
        )

        self.assertEqual(
            item['question']['genusTypeId'],
            str(QTI_QUESTION_NUMERIC_RESPONSE_INTERACTION_GENUS)
        )
        self.assertIn('var1', item['question']['variables'])
        self.assertIn('var2', item['question']['variables'])

        self.assertEqual(
            item['question']['variables']['var1']['min_value'],
            1
        )
        self.assertEqual(
            item['question']['variables']['var1']['max_value'],
            10
        )
        self.assertEqual(
            item['question']['variables']['var1']['type'],
            'integer'
        )
        self.assertEqual(
            item['question']['variables']['var1']['step'],
            1
        )
        self.assertEqual(
            item['question']['variables']['var2']['min_value'],
            1
        )
        self.assertEqual(
            item['question']['variables']['var2']['max_value'],
            10
        )
        self.assertEqual(
            item['question']['variables']['var2']['type'],
            'integer'
        )
        self.assertEqual(
            item['question']['variables']['var2']['step'],
            1
        )

        self.assertEqual(
            item['answers'][0]['genusTypeId'],
            str(RIGHT_ANSWER_GENUS)
        )
        self.assertIn('<p></p>', item['answers'][0]['feedbacks'][0]['text'])
        self.assertIn('<p></p>', item['answers'][1]['feedbacks'][0]['text'])

        self.assertNotEqual(
            item['id'],
            str(self._item.ident)
        )

        url = '{0}/{1}/qti'.format(url, unquote(item['id']))
        req = self.app.get(url)
        self.ok(req)
        item_qti = BeautifulSoup(req.body, 'lxml-xml').assessmentItem
        item_body = item_qti.itemBody

        expected_string = """<itemBody>
<p>
   Please solve: {var1} + {var2} =
   <textEntryInteraction responseIdentifier="RESPONSE_1"/>
</p>
</itemBody>"""

        self.assertNotEqual(
            str(item_body),
            expected_string
        )

        # make sure some random integers are inserted that meet the requirements
        numeric_choice_wrapper = None
        interaction = item_body.textEntryInteraction
        for parent in interaction.parents:
            if parent.name == 'p':
                numeric_choice_wrapper = parent
                break

        numeric_choice_line_str = _stringify(numeric_choice_wrapper)
        expression = numeric_choice_line_str[3:numeric_choice_line_str.index('=')].strip()  # skip the opening <p> tag

        var1 = int(expression[0:expression.index('+')].strip())
        var2 = int(expression[expression.index('+') + 1::].strip())

        self.assertTrue(1 <= var1 <= 10)
        self.assertTrue(1 <= var2 <= 10)

        # make sure the questionId is "magical"
        self.assertNotEqual(
            item['id'],
            item['question']['id']
        )
        self.assertNotIn('?', item['question']['id'])
        self.assertEqual(
            item['question']['id'].split('%40')[-1],
            'qti-numeric-response'
        )
        self.assertIn('var1', item['question']['id'].split('%3A')[-1].split('%40')[0])
        self.assertIn('var2', item['question']['id'].split('%3A')[-1].split('%40')[0])

    def test_can_upload_floating_point_numeric_response_qti_file(self):
        url = '{0}/items'.format(self.url)
        self._floating_point_numeric_input_test_file.seek(0)
        req = self.app.post(url,
                            upload_files=[('qtiFile', 'testFile', self._floating_point_numeric_input_test_file.read())])
        self.ok(req)
        item = self.json(req)

        self.assertEqual(
            item['genusTypeId'],
            str(QTI_ITEM_NUMERIC_RESPONSE_INTERACTION_GENUS)
        )

        self.assertEqual(
            item['question']['genusTypeId'],
            str(QTI_QUESTION_NUMERIC_RESPONSE_INTERACTION_GENUS)
        )

        self.assertIn('var1', item['question']['variables'])
        self.assertIn('var2', item['question']['variables'])

        self.assertEqual(
            item['question']['variables']['var1']['min_value'],
            1.0
        )
        self.assertEqual(
            item['question']['variables']['var1']['max_value'],
            10.0
        )
        self.assertEqual(
            item['question']['variables']['var1']['type'],
            'float'
        )
        self.assertEqual(
            item['question']['variables']['var1']['format'],
            '%.4f'
        )
        self.assertEqual(
            item['question']['variables']['var2']['min_value'],
            1
        )
        self.assertEqual(
            item['question']['variables']['var2']['max_value'],
            10
        )
        self.assertEqual(
            item['question']['variables']['var2']['type'],
            'integer'
        )
        self.assertEqual(
            item['question']['variables']['var2']['step'],
            1
        )

        self.assertEqual(
            item['answers'][0]['genusTypeId'],
            str(RIGHT_ANSWER_GENUS)
        )
        self.assertIn('<p></p>', item['answers'][0]['feedbacks'][0]['text'])
        self.assertIn('<p></p>', item['answers'][1]['feedbacks'][0]['text'])

        self.assertNotEqual(
            item['id'],
            str(self._item.ident)
        )

        url = '{0}/{1}/qti'.format(url, unquote(item['id']))
        req = self.app.get(url)
        self.ok(req)
        item_qti = BeautifulSoup(req.body, 'lxml-xml').assessmentItem
        item_body = item_qti.itemBody

        expected_string = """<itemBody>
<p>
   Please solve:
   <printedVariable format="%.4f" identifier="var1"/>
   +
   <printedVariable identifier="var2"/>
   =
   <textEntryInteraction responseIdentifier="RESPONSE"/>
</p>
</itemBody>"""

        self.assertNotEqual(
            str(item_body),
            expected_string
        )

        # make sure some random numbers are inserted that meet the requirements
        expression = self._grab_expression(str(item_body))
        var1 = float(expression[0:expression.index('+')].strip())
        var2 = int(expression[expression.index('+') + 1::].strip())

        self.assertTrue(1.0 <= var1 <= 10.0)
        self.assertTrue(1 <= var2 <= 10)

        # make sure the questionId is "magical"
        self.assertNotEqual(
            item['id'],
            item['question']['id']
        )
        self.assertNotIn('?', item['question']['id'])
        self.assertEqual(
            item['question']['id'].split('%40')[-1],
            'qti-numeric-response'
        )
        self.assertIn('var1', item['question']['id'].split('%3A')[-1].split('%40')[0])
        self.assertIn('var2', item['question']['id'].split('%3A')[-1].split('%40')[0])

    def test_can_upload_non_english_qti_file(self):
        url = '{0}/items'.format(self.url)
        self._telugu_test_file.seek(0)
        req = self.app.post(url,
                            upload_files=[('qtiFile',
                                           self._filename(self._telugu_test_file),
                                           self._telugu_test_file.read())])
        self.ok(req)
        item = self.json(req)

        self.assertEqual(
            item['genusTypeId'],
            str(QTI_ITEM_CHOICE_INTERACTION_GENUS)
        )

        self.assertEqual(
            item['question']['genusTypeId'],
            str(QTI_QUESTION_CHOICE_INTERACTION_GENUS)
        )

        self.assertIn(u'మీ గ్రూప్ తో కలిసి', item['learningObjectiveIds'][0])
        self.assertIn(u'అదేపనినిత్రిభుజంతోచేయడానికిప్రయత్నించండి',
                      item['answers'][0]['feedbacks'][0]['text'])
        self.assertIn(u'ఒక నక్షత్ర ఆకారం',
                      item['answers'][1]['feedbacks'][0]['text'])
        self.assertIn(u'అగ్గిపుల్లల(ఉపయోగించబడిన) ఒక సెట్మరియుసైకిల్',
                      item['question']['texts'][0]['text'])

    def test_can_upload_unicode_in_feedback_in_qti_file(self):
        url = '{0}/items'.format(self.url)
        self._unicode_feedback_test_file.seek(0)
        req = self.app.post(url,
                            upload_files=[('qtiFile',
                                           self._filename(self._unicode_feedback_test_file),
                                           self._unicode_feedback_test_file.read())])
        self.ok(req)
        item = self.json(req)

        self.assertEqual(
            item['genusTypeId'],
            str(QTI_ITEM_CHOICE_INTERACTION_GENUS)
        )

        self.assertEqual(
            item['question']['genusTypeId'],
            str(QTI_QUESTION_CHOICE_INTERACTION_GENUS)
        )

        self.assertIn(u'Very good! That is correct!',
                      item['answers'][0]['feedbacks'][0]['text'])
        self.assertIn(u'Recall the audio. Were Kanasu, Zo and Sahir playing?',
                      item['answers'][1]['feedbacks'][0]['text'])
        self.assertIn(u'This is our fifth round of this playground. I\u2019m sitting ',
                      item['answers'][1]['feedbacks'][0]['text'])
        self.assertIn(u'Doesn\'t Kanasu say she is bored of walking',
                      item['answers'][2]['feedbacks'][0]['text'])
        self.assertIn(u'This is our fifth round of this playground. I\u2019m sitting ',
                      item['answers'][2]['feedbacks'][0]['text'])
        self.assertIn(u'Are Kanasu, Zo and Sahir planning to leave?',
                      item['answers'][3]['feedbacks'][0]['text'])
        self.assertIn(u'This is our fifth round of this playground. I\u2019m sitting ',
                      item['answers'][3]['feedbacks'][0]['text'])

    def test_can_upload_survey_question_qti_file(self):
        url = '{0}/items'.format(self.url)
        self._survey_question_test_file.seek(0)
        req = self.app.post(url,
                            upload_files=[('qtiFile',
                                           self._filename(self._survey_question_test_file),
                                           self._survey_question_test_file.read())])
        self.ok(req)
        item = self.json(req)

        self.assertEqual(
            item['genusTypeId'],
            str(QTI_ITEM_CHOICE_INTERACTION_SURVEY_GENUS)
        )

        self.assertEqual(
            item['question']['genusTypeId'],
            str(QTI_QUESTION_CHOICE_INTERACTION_SURVEY_GENUS)
        )
        self.assertEqual(
            len(item['question']['choices']),
            3
        )
        choice_ids = [c['id'] for c in item['question']['choices']]

        self.assertEqual(
            len(item['answers']),
            3
        )
        for answer in item['answers']:
            self.assertEqual(
                answer['genusTypeId'],
                str(RIGHT_ANSWER_GENUS)
            )
            self.assertIn('Thank you for your participation.', answer['feedbacks'][0]['text'])
            self.assertIn(answer['choiceIds'][0], choice_ids)

        self.assertNotEqual(
            item['id'],
            str(self._item.ident)
        )

        url = '{0}/{1}/qti'.format(url, unquote(item['id']))
        req = self.app.get(url)
        self.ok(req)
        item_qti = BeautifulSoup(req.body, 'lxml-xml').assessmentItem
        item_body = item_qti.itemBody

        choice_interaction = item_body.choiceInteraction.extract()

        expected_string = """<itemBody>
<p>
   Did you eat breakfast today?
  </p>

</itemBody>"""

        self.assertEqual(
            str(item_body),
            expected_string
        )

        self.assertEqual(
            len(choice_interaction.find_all('simpleChoice')),
            3
        )
        self.assertEqual(
            choice_interaction['maxChoices'],
            "1"
        )
        self.assertEqual(
            choice_interaction['responseIdentifier'],
            'RESPONSE_1'
        )
        self.assertEqual(
            choice_interaction['shuffle'],
            'true'
        )

        expected_choices = {
            "id5f1fc52a-a04e-4fa1-b855-51da24967a31": """<simpleChoice identifier="id5f1fc52a-a04e-4fa1-b855-51da24967a31">
<p>
     Yes
    </p>
</simpleChoice>""",
            "id31392307-c87e-476b-8f92-b0f12ed66300": """<simpleChoice identifier="id31392307-c87e-476b-8f92-b0f12ed66300">
<p>
     No
    </p>
</simpleChoice>""",
            "id8188b5cd-89b0-4140-b12a-aed5426bd81b": """<simpleChoice identifier="id8188b5cd-89b0-4140-b12a-aed5426bd81b">
<p>
     I don\'t remember
    </p>
</simpleChoice>"""
        }

        for choice in choice_interaction.find_all('simpleChoice'):
            choice_id = choice['identifier']
            self.assertEqual(
                str(choice),
                expected_choices[choice_id]
            )

    def test_can_upload_multi_select_survey_question_qti_file(self):
        url = '{0}/items'.format(self.url)
        self._multi_select_survey_question_test_file.seek(0)
        req = self.app.post(url,
                            upload_files=[('qtiFile',
                                           self._filename(self._multi_select_survey_question_test_file),
                                           self._multi_select_survey_question_test_file.read())])
        self.ok(req)
        item = self.json(req)

        self.assertEqual(
            item['genusTypeId'],
            str(QTI_ITEM_CHOICE_INTERACTION_MULTI_SELECT_SURVEY_GENUS)
        )

        self.assertEqual(
            item['question']['genusTypeId'],
            str(QTI_QUESTION_CHOICE_INTERACTION_MULTI_SELECT_SURVEY_GENUS)
        )
        self.assertEqual(
            len(item['question']['choices']),
            3
        )
        choice_ids = [c['id'] for c in item['question']['choices']]

        self.assertEqual(
            len(item['answers']),
            3
        )
        for answer in item['answers']:
            self.assertEqual(
                answer['genusTypeId'],
                str(RIGHT_ANSWER_GENUS)
            )
            self.assertIn('Thank you for your participation.', answer['feedbacks'][0]['text'])
            self.assertIn(answer['choiceIds'][0], choice_ids)

        self.assertNotEqual(
            item['id'],
            str(self._item.ident)
        )

        url = '{0}/{1}/qti'.format(url, unquote(item['id']))
        req = self.app.get(url)
        self.ok(req)
        item_qti = BeautifulSoup(req.body, 'lxml-xml').assessmentItem
        item_body = item_qti.itemBody

        choice_interaction = item_body.choiceInteraction.extract()

        expected_string = """<itemBody>
<p>
   Did you eat breakfast today?
  </p>

</itemBody>"""

        self.assertEqual(
            str(item_body),
            expected_string
        )

        self.assertEqual(
            len(choice_interaction.find_all('simpleChoice')),
            3
        )
        self.assertEqual(
            choice_interaction['maxChoices'],
            "0"
        )
        self.assertEqual(
            choice_interaction['responseIdentifier'],
            'RESPONSE_1'
        )
        self.assertEqual(
            choice_interaction['shuffle'],
            'true'
        )

        expected_choices = {
            "id5f1fc52a-a04e-4fa1-b855-51da24967a31": """<simpleChoice identifier="id5f1fc52a-a04e-4fa1-b855-51da24967a31">
<p>
     Yes
    </p>
</simpleChoice>""",
            "id31392307-c87e-476b-8f92-b0f12ed66300": """<simpleChoice identifier="id31392307-c87e-476b-8f92-b0f12ed66300">
<p>
     No
    </p>
</simpleChoice>""",
            "id8188b5cd-89b0-4140-b12a-aed5426bd81b": """<simpleChoice identifier="id8188b5cd-89b0-4140-b12a-aed5426bd81b">
<p>
     I don\'t remember
    </p>
</simpleChoice>"""
        }

        for choice in choice_interaction.find_all('simpleChoice'):
            choice_id = choice['identifier']
            self.assertEqual(
                str(choice),
                expected_choices[choice_id]
            )

    def test_video_tags_appear_in_qti(self):
        url = '{0}/items'.format(self.url)
        self._video_test_file.seek(0)
        req = self.app.post(url,
                            upload_files=[('qtiFile', 'testFile.zip', self._video_test_file.read())])
        self.ok(req)
        item = self.json(req)

        self.assertEqual(
            item['genusTypeId'],
            str(QTI_ITEM_CHOICE_INTERACTION_GENUS)
        )

        self.assertEqual(
            item['question']['genusTypeId'],
            str(QTI_QUESTION_CHOICE_INTERACTION_GENUS)
        )

        url = '{0}/{1}/qti'.format(url, unquote(item['id']))
        req = self.app.get(url)
        self.ok(req)
        item_qti = BeautifulSoup(req.body, 'lxml-xml').assessmentItem
        item_body = item_qti.itemBody
        item_body.choiceInteraction.extract()

        expected_string = """<itemBody>
<p>
<span style="font-size: 12.8px;">
    [type]{video}
   </span>
</p>
<p>
<span style="font-size: 12.8px;">
    Was Raju\'s father on the bus?
   </span>
</p>

</itemBody>"""

        self.assertEqual(
            str(item_body),
            expected_string
        )

    def test_can_get_wrong_answers_in_items_list(self):
        media_files = [self._green_dot_image,
                       self._h1i_image,
                       self._audio_test_file,
                       self._diamond_image]

        assets = {}
        for media_file in media_files:
            label = self._label(self._filename(media_file))
            assets[label] = self.upload_media_file(media_file)

        url = '{0}/items'.format(self.url)

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
  <img src="AssetContent:green_dot_png" alt="image 1" width="20" height="20" />
</p>
</simpleChoice>"""
                }, {
                    "id": "ida86a26e0-a563-4e48-801a-ba9d171c24f7",
                    "text": """<simpleChoice identifier="ida86a26e0-a563-4e48-801a-ba9d171c24f7">
<p>|__|</p>
</simpleChoice>"""
                }, {
                    "id": "id32b596f4-d970-4d1e-a667-3ca762c002c5",
                    "text": """<simpleChoice identifier="id32b596f4-d970-4d1e-a667-3ca762c002c5">
<p>
  <img src="AssetContent:h1i_png" alt="image 2" width="26" height="24" />
</p>
</simpleChoice>"""
                }],
                "genusTypeId": str(QTI_QUESTION_CHOICE_INTERACTION_GENUS),
                "shuffle": True,
                "fileIds": {}
            },
            "answers": [{
                "genusTypeId": str(RIGHT_ANSWER_GENUS),
                "choiceIds": ["idc561552b-ed48-46c3-b20d-873150dfd4a2"],
                "feedback": """<modalFeedback  identifier="Feedback933928139" outcomeIdentifier="FEEDBACKMODAL" showHide="show">
  <p id="docs-internal-guid-46f83555-04cc-a70f-2574-1b5c79fe206e" dir="ltr">You are correct! A square has the properties of both a rectangle, and a rhombus. Hence, it can also occupy the shaded region.</p>
</modalFeedback>""",
                "fileIds": {}
            }, {
                "genusTypeId": str(WRONG_ANSWER_GENUS),
                "feedback": """<modalFeedback  identifier="Feedback506508014" outcomeIdentifier="FEEDBACKMODAL" showHide="show">
  <p>
    <strong>
      <span id="docs-internal-guid-46f83555-04cc-d077-5f2e-58f80bf813e2">Please try again!</span>
      <br />
    </strong>
  </p>
</modalFeedback>""",
                'fileIds': {}
            }]
        }

        for label, asset in assets.iteritems():
            target = payload['question']
            if "audio" in label:
                target = payload['answers'][0]
            if "diamond" in label:
                target = payload['answers'][1]
            target['fileIds'][label] = {}
            target['fileIds'][label]['assetId'] = asset['id']
            target['fileIds'][label]['assetContentId'] = asset['assetContents'][0]['id']
            target['fileIds'][label]['assetContentTypeId'] = asset['assetContents'][0]['genusTypeId']

        req = self.app.post(url,
                            params=json.dumps(payload),
                            headers={'content-type': 'application/json'})
        self.ok(req)
        item = self.json(req)

        items_list_url = '{0}?wronganswers'.format(url)
        req = self.app.get(items_list_url)
        data = self.json(req)
        item_with_wrong_answers = [i for i in data if i['id'] == item['id']][0]

        self.assertEqual(len(item_with_wrong_answers['answers']),
                         len(item['answers']))

        self.assertTrue(any(answer['genusTypeId'] == str(WRONG_ANSWER_GENUS) for
                            answer in item_with_wrong_answers['answers']))

        req = self.app.get(url)
        data = self.json(req)
        item_with_no_wrong_answers = [i for i in data if i['id'] == item['id']][0]

        self.assertEqual(len(item_with_no_wrong_answers['answers']),
                         1)

        self.assertFalse(any(answer['genusTypeId'] == str(WRONG_ANSWER_GENUS) for
                             answer in item_with_no_wrong_answers['answers']))

    def test_can_create_multi_choice_single_answer_question_via_rest(self):
        media_files = [self._green_dot_image,
                       self._h1i_image,
                       self._audio_test_file,
                       self._diamond_image]

        assets = {}
        for media_file in media_files:
            label = self._label(self._filename(media_file))
            assets[label] = self.upload_media_file(media_file)

        url = '{0}/items'.format(self.url)

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
  <img src="AssetContent:green_dot_png" alt="image 1" width="20" height="20" />
</p>
</simpleChoice>"""
                }, {
                    "id": "ida86a26e0-a563-4e48-801a-ba9d171c24f7",
                    "text": """<simpleChoice identifier="ida86a26e0-a563-4e48-801a-ba9d171c24f7">
<p>|__|</p>
</simpleChoice>"""
                }, {
                    "id": "id32b596f4-d970-4d1e-a667-3ca762c002c5",
                    "text": """<simpleChoice identifier="id32b596f4-d970-4d1e-a667-3ca762c002c5">
<p>
  <img src="AssetContent:h1i_png" alt="image 2" width="26" height="24" />
</p>
</simpleChoice>"""
                }],
                "genusTypeId": str(QTI_QUESTION_CHOICE_INTERACTION_GENUS),
                "shuffle": True,
                "fileIds": {}
            },
            "answers": [{
                "genusTypeId": str(RIGHT_ANSWER_GENUS),
                "choiceIds": ["idc561552b-ed48-46c3-b20d-873150dfd4a2"],
                "feedback": """<modalFeedback  identifier="Feedback933928139" outcomeIdentifier="FEEDBACKMODAL" showHide="show">
  <p id="docs-internal-guid-46f83555-04cc-a70f-2574-1b5c79fe206e" dir="ltr">You are correct! A square has the properties of both a rectangle, and a rhombus. Hence, it can also occupy the shaded region.</p>
</modalFeedback>""",
                "fileIds": {}
            }, {
                "genusTypeId": str(WRONG_ANSWER_GENUS),
                "feedback": """<modalFeedback  identifier="Feedback506508014" outcomeIdentifier="FEEDBACKMODAL" showHide="show">
  <p>
    <strong>
      <span id="docs-internal-guid-46f83555-04cc-d077-5f2e-58f80bf813e2">Please try again!</span>
      <br />
    </strong>
  </p>
</modalFeedback>""",
                'fileIds': {}
            }]
        }

        for label, asset in assets.iteritems():
            target = payload['question']
            if "audio" in label:
                target = payload['answers'][0]
            if "diamond" in label:
                target = payload['answers'][1]
            target['fileIds'][label] = {}
            target['fileIds'][label]['assetId'] = asset['id']
            target['fileIds'][label]['assetContentId'] = asset['assetContents'][0]['id']
            target['fileIds'][label]['assetContentTypeId'] = asset['assetContents'][0]['genusTypeId']

        req = self.app.post(url,
                            params=json.dumps(payload),
                            headers={'content-type': 'application/json'})
        self.ok(req)
        item = self.json(req)

        self.assertEqual(
            item['genusTypeId'],
            str(QTI_ITEM_CHOICE_INTERACTION_GENUS)
        )

        self.assertEqual(
            item['question']['genusTypeId'],
            str(QTI_QUESTION_CHOICE_INTERACTION_GENUS)
        )

        self.assertEqual(
            item['answers'][0]['genusTypeId'],
            str(RIGHT_ANSWER_GENUS)
        )

        self.assertNotEqual(
            item['id'],
            str(self._item.ident)
        )

        self.assertIn('fileIds', item['answers'][0])
        self.assertEqual(
            len(item['answers'][0]['fileIds'].keys()),
            1
        )
        audio_label = 'audioTestFile__mp3'
        self.assertEqual(
            item['answers'][0]['fileIds'][audio_label]['assetId'],
            assets[audio_label]['id']
        )
        self.assertEqual(
            item['answers'][0]['fileIds'][audio_label]['assetContentTypeId'],
            assets[audio_label]['assetContents'][0]['genusTypeId']
        )
        self.assertEqual(
            item['answers'][0]['fileIds'][audio_label]['assetContentId'],
            assets[audio_label]['assetContents'][0]['id']
        )

        # verify wrong answer file ids also saved
        url = '{0}/{1}'.format(url, unquote(item['id']))
        req = self.app.get(url)
        self.ok(req)
        data = self.json(req)
        self.assertEqual(len(data['answers']), 2)
        self.assertEqual(data['answers'][1]['genusTypeId'],
                         str(WRONG_ANSWER_GENUS))
        self.assertIn('fileIds', data['answers'][1])
        self.assertEqual(
            len(data['answers'][1]['fileIds'].keys()),
            1
        )
        diamond_label = 'diamond_png'
        self.assertEqual(
            data['answers'][1]['fileIds'][diamond_label]['assetId'],
            assets[diamond_label]['id']
        )
        self.assertEqual(
            data['answers'][1]['fileIds'][diamond_label]['assetContentTypeId'],
            assets[diamond_label]['assetContents'][0]['genusTypeId']
        )
        self.assertEqual(
            data['answers'][1]['fileIds'][diamond_label]['assetContentId'],
            assets[diamond_label]['assetContents'][0]['id']
        )

        # now verify the QTI XML matches the JSON format
        url = '{0}/{1}/qti'.format(url, unquote(item['id']))
        req = self.app.get(url)
        self.ok(req)
        qti_xml = BeautifulSoup(req.body, 'lxml-xml').assessmentItem
        item_body = qti_xml.itemBody

        choice_interaction = item_body.choiceInteraction.extract()

        image_1_asset_label = 'green_dot_png'
        image_2_asset_label = 'h1i_png'
        image_1_asset_id = item['question']['fileIds'][image_1_asset_label]['assetId']
        image_1_asset_content_id = item['question']['fileIds'][image_1_asset_label]['assetContentId']

        image_2_asset_id = item['question']['fileIds'][image_2_asset_label]['assetId']
        image_2_asset_content_id = item['question']['fileIds'][image_2_asset_label]['assetContentId']

        expected_string = """<itemBody>
<p>
   Which of the following is a circle?
  </p>

</itemBody>"""

        self.assertEqual(
            str(item_body),
            expected_string
        )

        self.assertEqual(
            str(item_body),
            expected_string
        )

        self.assertEqual(
            len(choice_interaction.find_all('simpleChoice')),
            3
        )
        self.assertEqual(
            choice_interaction['maxChoices'],
            "1"
        )
        self.assertEqual(
            choice_interaction['responseIdentifier'],
            'RESPONSE_1'
        )
        self.assertEqual(
            choice_interaction['shuffle'],
            'true'
        )

        repository_id = str(self._bank.ident).replace('assessment.Bank', 'repository.Repository')

        expected_choices = {
            "idc561552b-ed48-46c3-b20d-873150dfd4a2": """<simpleChoice identifier="idc561552b-ed48-46c3-b20d-873150dfd4a2">
<p>
<img alt="image 1" height="20" src="/api/v1/repository/repositories/{0}/assets/{1}/contents/{2}/stream" width="20"/>
</p>
</simpleChoice>""".format(repository_id,
                          image_1_asset_id,
                          image_1_asset_content_id),
            "ida86a26e0-a563-4e48-801a-ba9d171c24f7": """<simpleChoice identifier="ida86a26e0-a563-4e48-801a-ba9d171c24f7">
<p>
     |__|
    </p>
</simpleChoice>""",
            "id32b596f4-d970-4d1e-a667-3ca762c002c5": """<simpleChoice identifier="id32b596f4-d970-4d1e-a667-3ca762c002c5">
<p>
<img alt="image 2" height="24" src="/api/v1/repository/repositories/{0}/assets/{1}/contents/{2}/stream" width="26"/>
</p>
</simpleChoice>""".format(repository_id,
                          image_2_asset_id,
                          image_2_asset_content_id)
        }

        for choice in choice_interaction.find_all('simpleChoice'):
            choice_id = choice['identifier']
            self.assertEqual(
                str(choice),
                expected_choices[choice_id]
            )

    def test_can_add_multi_choice_single_answer_question_to_existing_item_via_rest(self):
        media_files = [self._green_dot_image,
                       self._h1i_image,
                       self._audio_test_file,
                       self._diamond_image]

        assets = {}
        for media_file in media_files:
            label = self._label(self._filename(media_file))
            assets[label] = self.upload_media_file(media_file)

        url = '{0}/items'.format(self.url)

        payload = {
            "genusTypeId": str(QTI_ITEM_CHOICE_INTERACTION_GENUS),
            "name": "Question 1",
            "description": "For testing"
        }

        req = self.app.post(url,
                            params=json.dumps(payload),
                            headers={'content-type': 'application/json'})
        self.ok(req)
        item = self.json(req)

        payload = {
            "question": {
                "questionString": """<itemBody >
<p>Which of the following is a circle?</p>
</itemBody>""",
                "choices": [{
                    "id": "idc561552b-ed48-46c3-b20d-873150dfd4a2",
                    "text": """<simpleChoice identifier="idc561552b-ed48-46c3-b20d-873150dfd4a2">
<p>
  <img src="AssetContent:green_dot_png" alt="image 1" width="20" height="20" />
</p>
</simpleChoice>"""
                }, {
                    "id": "ida86a26e0-a563-4e48-801a-ba9d171c24f7",
                    "text": """<simpleChoice identifier="ida86a26e0-a563-4e48-801a-ba9d171c24f7">
<p>|__|</p>
</simpleChoice>"""
                }, {
                    "id": "id32b596f4-d970-4d1e-a667-3ca762c002c5",
                    "text": """<simpleChoice identifier="id32b596f4-d970-4d1e-a667-3ca762c002c5">
<p>
  <img src="AssetContent:h1i_png" alt="image 2" width="26" height="24" />
</p>
</simpleChoice>"""
                }],
                "genusTypeId": str(QTI_QUESTION_CHOICE_INTERACTION_GENUS),
                "shuffle": True,
                "fileIds": {}
            },
            "answers": [{
                "genusTypeId": str(RIGHT_ANSWER_GENUS),
                "choiceIds": ["idc561552b-ed48-46c3-b20d-873150dfd4a2"],
                "feedback": """<modalFeedback  identifier="Feedback933928139" outcomeIdentifier="FEEDBACKMODAL" showHide="show">
  <p id="docs-internal-guid-46f83555-04cc-a70f-2574-1b5c79fe206e" dir="ltr">You are correct! A square has the properties of both a rectangle, and a rhombus. Hence, it can also occupy the shaded region.</p>
</modalFeedback>""",
                "fileIds": {}
            }, {
                "genusTypeId": str(WRONG_ANSWER_GENUS),
                "feedback": """<modalFeedback  identifier="Feedback506508014" outcomeIdentifier="FEEDBACKMODAL" showHide="show">
  <p>
    <strong>
      <span id="docs-internal-guid-46f83555-04cc-d077-5f2e-58f80bf813e2">Please try again!</span>
      <br />
    </strong>
  </p>
</modalFeedback>""",
                'fileIds': {}
            }]
        }

        for label, asset in assets.iteritems():
            target = payload['question']
            if "audio" in label:
                target = payload['answers'][0]
            if "diamond" in label:
                target = payload['answers'][1]
            target['fileIds'][label] = {}
            target['fileIds'][label]['assetId'] = asset['id']
            target['fileIds'][label]['assetContentId'] = asset['assetContents'][0]['id']
            target['fileIds'][label]['assetContentTypeId'] = asset['assetContents'][0]['genusTypeId']

        url = '{0}/items/{1}'.format(self.url, item['id'])

        req = self.app.put(url,
                           params=json.dumps(payload),
                           headers={'content-type': 'application/json'})
        self.ok(req)
        item = self.json(req)

        self.assertEqual(
            item['genusTypeId'],
            str(QTI_ITEM_CHOICE_INTERACTION_GENUS)
        )

        self.assertEqual(
            item['question']['genusTypeId'],
            str(QTI_QUESTION_CHOICE_INTERACTION_GENUS)
        )

        self.assertEqual(
            item['answers'][0]['genusTypeId'],
            str(RIGHT_ANSWER_GENUS)
        )

        self.assertNotEqual(
            item['id'],
            str(self._item.ident)
        )

        self.assertIn('fileIds', item['answers'][0])
        self.assertEqual(
            len(item['answers'][0]['fileIds'].keys()),
            1
        )
        audio_label = 'audioTestFile__mp3'
        self.assertEqual(
            item['answers'][0]['fileIds'][audio_label]['assetId'],
            assets[audio_label]['id']
        )
        self.assertEqual(
            item['answers'][0]['fileIds'][audio_label]['assetContentTypeId'],
            assets[audio_label]['assetContents'][0]['genusTypeId']
        )
        self.assertEqual(
            item['answers'][0]['fileIds'][audio_label]['assetContentId'],
            assets[audio_label]['assetContents'][0]['id']
        )

        # verify wrong answer file ids also saved
        req = self.app.get(url)
        self.ok(req)
        data = self.json(req)
        self.assertEqual(len(data['answers']), 2)
        self.assertEqual(data['answers'][1]['genusTypeId'],
                         str(WRONG_ANSWER_GENUS))
        self.assertIn('fileIds', data['answers'][1])
        self.assertEqual(
            len(data['answers'][1]['fileIds'].keys()),
            1
        )
        diamond_label = 'diamond_png'
        self.assertEqual(
            data['answers'][1]['fileIds'][diamond_label]['assetId'],
            assets[diamond_label]['id']
        )
        self.assertEqual(
            data['answers'][1]['fileIds'][diamond_label]['assetContentTypeId'],
            assets[diamond_label]['assetContents'][0]['genusTypeId']
        )
        self.assertEqual(
            data['answers'][1]['fileIds'][diamond_label]['assetContentId'],
            assets[diamond_label]['assetContents'][0]['id']
        )

        # now verify the QTI XML matches the JSON format
        url = '{0}/{1}/qti'.format(url, unquote(item['id']))
        req = self.app.get(url)
        self.ok(req)
        qti_xml = BeautifulSoup(req.body, 'lxml-xml').assessmentItem
        item_body = qti_xml.itemBody

        choice_interaction = item_body.choiceInteraction.extract()

        image_1_asset_label = 'green_dot_png'
        image_2_asset_label = 'h1i_png'
        image_1_asset_id = item['question']['fileIds'][image_1_asset_label]['assetId']
        image_1_asset_content_id = item['question']['fileIds'][image_1_asset_label]['assetContentId']

        image_2_asset_id = item['question']['fileIds'][image_2_asset_label]['assetId']
        image_2_asset_content_id = item['question']['fileIds'][image_2_asset_label]['assetContentId']

        expected_string = """<itemBody>
<p>
   Which of the following is a circle?
  </p>

</itemBody>"""

        self.assertEqual(
            str(item_body),
            expected_string
        )

        self.assertEqual(
            str(item_body),
            expected_string
        )

        self.assertEqual(
            len(choice_interaction.find_all('simpleChoice')),
            3
        )
        self.assertEqual(
            choice_interaction['maxChoices'],
            "1"
        )
        self.assertEqual(
            choice_interaction['responseIdentifier'],
            'RESPONSE_1'
        )
        self.assertEqual(
            choice_interaction['shuffle'],
            'true'
        )

        repository_id = str(self._bank.ident).replace('assessment.Bank', 'repository.Repository')

        expected_choices = {
            "idc561552b-ed48-46c3-b20d-873150dfd4a2": """<simpleChoice identifier="idc561552b-ed48-46c3-b20d-873150dfd4a2">
<p>
<img alt="image 1" height="20" src="/api/v1/repository/repositories/{0}/assets/{1}/contents/{2}/stream" width="20"/>
</p>
</simpleChoice>""".format(repository_id,
                          image_1_asset_id,
                          image_1_asset_content_id),
            "ida86a26e0-a563-4e48-801a-ba9d171c24f7": """<simpleChoice identifier="ida86a26e0-a563-4e48-801a-ba9d171c24f7">
<p>
     |__|
    </p>
</simpleChoice>""",
            "id32b596f4-d970-4d1e-a667-3ca762c002c5": """<simpleChoice identifier="id32b596f4-d970-4d1e-a667-3ca762c002c5">
<p>
<img alt="image 2" height="24" src="/api/v1/repository/repositories/{0}/assets/{1}/contents/{2}/stream" width="26"/>
</p>
</simpleChoice>""".format(repository_id,
                          image_2_asset_id,
                          image_2_asset_content_id)
        }

        for choice in choice_interaction.find_all('simpleChoice'):
            choice_id = choice['identifier']
            self.assertEqual(
                str(choice),
                expected_choices[choice_id]
            )

    def test_getting_qti_for_multi_choice_single_answer_with_no_question_returns_empty_string(self):
        media_files = [self._green_dot_image,
                       self._h1i_image,
                       self._audio_test_file,
                       self._diamond_image]

        assets = {}
        for media_file in media_files:
            label = self._label(self._filename(media_file))
            assets[label] = self.upload_media_file(media_file)

        url = '{0}/items'.format(self.url)

        payload = {
            "genusTypeId": str(QTI_ITEM_CHOICE_INTERACTION_GENUS),
            "name": "Question 1",
            "description": "For testing"
        }

        req = self.app.post(url,
                            params=json.dumps(payload),
                            headers={'content-type': 'application/json'})
        self.ok(req)
        item = self.json(req)

        # now verify the QTI XML is empty string
        url = '{0}/{1}/qti'.format(url, unquote(item['id']))
        req = self.app.get(url)
        self.ok(req)
        self.assertEqual(req.body, '')

    def test_updating_multi_choice_single_answer_choices_clears_existing_choices(self):
        media_files = [self._green_dot_image,
                       self._h1i_image,
                       self._audio_test_file,
                       self._diamond_image]

        assets = {}
        for media_file in media_files:
            label = self._label(self._filename(media_file))
            assets[label] = self.upload_media_file(media_file)

        url = '{0}/items'.format(self.url)

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
  <img src="AssetContent:green_dot_png" alt="image 1" width="20" height="20" />
</p>
</simpleChoice>"""
                }, {
                    "id": "ida86a26e0-a563-4e48-801a-ba9d171c24f7",
                    "text": """<simpleChoice identifier="ida86a26e0-a563-4e48-801a-ba9d171c24f7">
<p>|__|</p>
</simpleChoice>"""
                }, {
                    "id": "id32b596f4-d970-4d1e-a667-3ca762c002c5",
                    "text": """<simpleChoice identifier="id32b596f4-d970-4d1e-a667-3ca762c002c5">
<p>
  <img src="AssetContent:h1i_png" alt="image 2" width="26" height="24" />
</p>
</simpleChoice>"""
                }],
                "genusTypeId": str(QTI_QUESTION_CHOICE_INTERACTION_GENUS),
                "shuffle": True,
                "fileIds": {}
            },
            "answers": [{
                "genusTypeId": str(RIGHT_ANSWER_GENUS),
                "choiceIds": ["idc561552b-ed48-46c3-b20d-873150dfd4a2"],
                "feedback": """<modalFeedback  identifier="Feedback933928139" outcomeIdentifier="FEEDBACKMODAL" showHide="show">
  <p id="docs-internal-guid-46f83555-04cc-a70f-2574-1b5c79fe206e" dir="ltr">You are correct! A square has the properties of both a rectangle, and a rhombus. Hence, it can also occupy the shaded region.</p>
</modalFeedback>""",
                "fileIds": {}
            }, {
                "genusTypeId": str(WRONG_ANSWER_GENUS),
                "feedback": """<modalFeedback  identifier="Feedback506508014" outcomeIdentifier="FEEDBACKMODAL" showHide="show">
  <p>
    <strong>
      <span id="docs-internal-guid-46f83555-04cc-d077-5f2e-58f80bf813e2">Please try again!</span>
      <br />
    </strong>
  </p>
</modalFeedback>""",
                'fileIds': {}
            }]
        }

        for label, asset in assets.iteritems():
            target = payload['question']
            if "audio" in label:
                target = payload['answers'][0]
            if "diamond" in label:
                target = payload['answers'][1]
            target['fileIds'][label] = {}
            target['fileIds'][label]['assetId'] = asset['id']
            target['fileIds'][label]['assetContentId'] = asset['assetContents'][0]['id']
            target['fileIds'][label]['assetContentTypeId'] = asset['assetContents'][0]['genusTypeId']

        req = self.app.post(url,
                            params=json.dumps(payload),
                            headers={'content-type': 'application/json'})
        self.ok(req)
        item = self.json(req)

        right_answer = [a for a in item['answers'] if a['genusTypeId'] == str(RIGHT_ANSWER_GENUS)][0]
        previous_right_answer_choice = right_answer['choiceIds'][0]
        new_right_answer_choice = 'ida86a26e0-a563-4e48-801a-ba9d171c24f7'

        self.assertNotEqual(previous_right_answer_choice,
                            new_right_answer_choice)

        url = '{0}/{1}'.format(url, item['id'])
        payload = {
            'answers': [{
                'id': right_answer['id'],
                'choiceIds': [new_right_answer_choice]
            }]
        }
        req = self.app.put(url,
                           params=json.dumps(payload),
                           headers={'content-type': 'application/json'})
        self.ok(req)
        data = self.json(req)
        self.assertEqual(data['id'], item['id'])
        self.assertEqual(data['answers'][0]['id'], right_answer['id'])
        self.assertEqual(data['answers'][0]['genusTypeId'], str(RIGHT_ANSWER_GENUS))
        self.assertNotIn(previous_right_answer_choice, data['answers'][0]['choiceIds'])
        self.assertIn(new_right_answer_choice, data['answers'][0]['choiceIds'])
        self.assertEqual(len(data['answers'][0]['choiceIds']), 1)

    def test_item_body_and_simple_choice_tags_provided_multiple_choice(self):
        media_files = [self._green_dot_image,
                       self._h1i_image]

        assets = {}
        for media_file in media_files:
            label = self._label(self._filename(media_file))
            assets[label] = self.upload_media_file(media_file)

        url = '{0}/items'.format(self.url)

        payload = {
            "genusTypeId": str(QTI_ITEM_CHOICE_INTERACTION_GENUS),
            "name": "Question 1",
            "description": "For testing",
            "question": {
                "questionString": """<p>Which of the following is a circle?</p>""",
                "choices": [{
                    "id": "idc561552b-ed48-46c3-b20d-873150dfd4a2",
                    "text": """<p>
  <img src="AssetContent:green_dot_png" alt="image 1" width="20" height="20" />
</p>"""
                }, {
                    "id": "ida86a26e0-a563-4e48-801a-ba9d171c24f7",
                    "text": """<p>|__|</p>"""
                }, {
                    "id": "id32b596f4-d970-4d1e-a667-3ca762c002c5",
                    "text": """<p>
  <img src="AssetContent:h1i_png" alt="image 2" width="26" height="24" />
</p>"""
                }],
                "genusTypeId": str(QTI_QUESTION_CHOICE_INTERACTION_GENUS),
                "shuffle": True,
                "fileIds": {}
            },
            "answers": [{
                "genusTypeId": str(RIGHT_ANSWER_GENUS),
                "choiceIds": ["idc561552b-ed48-46c3-b20d-873150dfd4a2"],
                "feedback": """<modalFeedback  identifier="Feedback933928139" outcomeIdentifier="FEEDBACKMODAL" showHide="show">
  <p id="docs-internal-guid-46f83555-04cc-a70f-2574-1b5c79fe206e" dir="ltr">You are correct! A square has the properties of both a rectangle, and a rhombus. Hence, it can also occupy the shaded region.</p>
</modalFeedback>"""
            }, {
                "genusTypeId": str(WRONG_ANSWER_GENUS),
                "feedback": """<modalFeedback  identifier="Feedback506508014" outcomeIdentifier="FEEDBACKMODAL" showHide="show">
  <p>
    <strong>
      <span id="docs-internal-guid-46f83555-04cc-d077-5f2e-58f80bf813e2">Please try again!</span>
      <br />
    </strong>
  </p>
</modalFeedback>"""
            }]
        }

        for label, asset in assets.iteritems():
            payload['question']['fileIds'][label] = {}
            payload['question']['fileIds'][label]['assetId'] = asset['id']
            payload['question']['fileIds'][label]['assetContentId'] = asset['assetContents'][0]['id']
            payload['question']['fileIds'][label]['assetContentTypeId'] = asset['assetContents'][0]['genusTypeId']

        req = self.app.post(url,
                            params=json.dumps(payload),
                            headers={'content-type': 'application/json'})
        self.ok(req)
        item = self.json(req)

        self.assertEqual(
            item['genusTypeId'],
            str(QTI_ITEM_CHOICE_INTERACTION_GENUS)
        )

        self.assertEqual(
            item['question']['genusTypeId'],
            str(QTI_QUESTION_CHOICE_INTERACTION_GENUS)
        )

        self.assertEqual(
            item['answers'][0]['genusTypeId'],
            str(RIGHT_ANSWER_GENUS)
        )

        self.assertNotEqual(
            item['id'],
            str(self._item.ident)
        )

        # now verify the QTI XML matches the JSON format
        url = '{0}/{1}/qti'.format(url, unquote(item['id']))
        req = self.app.get(url)
        self.ok(req)
        qti_xml = BeautifulSoup(req.body, 'lxml-xml').assessmentItem
        item_body = qti_xml.itemBody

        choice_interaction = item_body.choiceInteraction.extract()

        image_1_asset_label = 'green_dot_png'
        image_2_asset_label = 'h1i_png'
        image_1_asset_id = item['question']['fileIds'][image_1_asset_label]['assetId']
        image_1_asset_content_id = item['question']['fileIds'][image_1_asset_label]['assetContentId']

        image_2_asset_id = item['question']['fileIds'][image_2_asset_label]['assetId']
        image_2_asset_content_id = item['question']['fileIds'][image_2_asset_label]['assetContentId']

        expected_string = """<itemBody>
<p>
   Which of the following is a circle?
  </p>

</itemBody>"""

        self.assertEqual(
            str(item_body),
            expected_string
        )

        self.assertEqual(
            str(item_body),
            expected_string
        )

        self.assertEqual(
            len(choice_interaction.find_all('simpleChoice')),
            3
        )
        self.assertEqual(
            choice_interaction['maxChoices'],
            "1"
        )
        self.assertEqual(
            choice_interaction['responseIdentifier'],
            'RESPONSE_1'
        )
        self.assertEqual(
            choice_interaction['shuffle'],
            'true'
        )

        repository_id = str(self._bank.ident).replace('assessment.Bank', 'repository.Repository')

        expected_choices = {
            "idc561552b-ed48-46c3-b20d-873150dfd4a2": """<simpleChoice identifier="idc561552b-ed48-46c3-b20d-873150dfd4a2">
<p>
<img alt="image 1" height="20" src="/api/v1/repository/repositories/{0}/assets/{1}/contents/{2}/stream" width="20"/>
</p>
</simpleChoice>""".format(repository_id,
                          image_1_asset_id,
                          image_1_asset_content_id),
            "ida86a26e0-a563-4e48-801a-ba9d171c24f7": """<simpleChoice identifier="ida86a26e0-a563-4e48-801a-ba9d171c24f7">
<p>
     |__|
    </p>
</simpleChoice>""",
            "id32b596f4-d970-4d1e-a667-3ca762c002c5": """<simpleChoice identifier="id32b596f4-d970-4d1e-a667-3ca762c002c5">
<p>
<img alt="image 2" height="24" src="/api/v1/repository/repositories/{0}/assets/{1}/contents/{2}/stream" width="26"/>
</p>
</simpleChoice>""".format(repository_id,
                          image_2_asset_id,
                          image_2_asset_content_id)
        }

        for choice in choice_interaction.find_all('simpleChoice'):
            choice_id = choice['identifier']
            self.assertEqual(
                str(choice),
                expected_choices[choice_id]
            )

    def test_can_create_multi_choice_multi_answer_question_via_rest(self):
        media_files = [self._square_image,
                       self._diamond_image,
                       self._parallelogram_image,
                       self._rectangle_image]

        assets = {}
        for media_file in media_files:
            label = self._label(self._filename(media_file))
            assets[label] = self.upload_media_file(media_file)

        url = '{0}/items'.format(self.url)

        payload = {
            "genusTypeId": str(QTI_ITEM_CHOICE_INTERACTION_MULTI_GENUS),
            "name": "Question 1",
            "description": "For testing",
            "question": {
                "questionString": """<itemBody >
<p id="docs-internal-guid-46f83555-04c7-ceb0-1838-715e13031a60" dir="ltr">In the diagram below,</p>
<p>
  <strong>
  </strong>
</p>
<p dir="ltr">A is the set of rectangles, and</p>
<p dir="ltr">B is the set of rhombuses</p>
<p dir="ltr">
</p>
<p dir="ltr">
  <img src="https://lh5.googleusercontent.com/a7NFx8J7jcDSr37Nen6ReW2doooJXZDm6GD1HQTfImkrzah94M_jkYoMapeYoRilKSSOz0gxVOUto0n5R4GWI4UWSnmzoTxH0VMQqRgzYMKWjJCG6OQgp8VPB4ghBAAeHlgI4ze7" alt="venn1" width="288" height="202" />
</p>
<p dir="ltr">
</p>
<p>
  <strong>Which all shape(s) can be contained in the gray shaded area?<br />
</strong>
</p>
</itemBody>""",
                "choices": [{
                    "id": "idb5345daa-a5c2-4924-a92b-e326886b5d1d",
                    "text": """<simpleChoice identifier="idb5345daa-a5c2-4924-a92b-e326886b5d1d">
<p>
<img src="AssetContent:parallelogram_png" alt="parallelagram" width="186" height="147" />
</p>
</simpleChoice>"""
                }, {
                    "id": "id31392307-c87e-476b-8f92-b0f12ed66300",
                    "text": """<simpleChoice identifier="id31392307-c87e-476b-8f92-b0f12ed66300">
<p>
<img src="AssetContent:square_png" alt="square" width="144" height="141" />
</p>
</simpleChoice>"""
                }, {
                    "id": "id01913fba-e66d-4a01-9625-94102847faac",
                    "text": """<simpleChoice identifier="id01913fba-e66d-4a01-9625-94102847faac">
<p>
<img src="AssetContent:rectangle_png" alt="rectangle" width="201" height="118" />
</p>
</simpleChoice>"""
                }, {
                    "id": "id4f525d00-e24c-4ac3-a104-848a2cd686c0",
                    "text": """<simpleChoice identifier="id4f525d00-e24c-4ac3-a104-848a2cd686c0">
<p>
<img src="AssetContent:diamond_png" alt="diamond shape" width="148" height="146" />
</p>
</simpleChoice>"""
                }, {
                    "id": "id18c8cc80-68d1-4c1f-b9f0-cb345bad2862",
                    "text": """<simpleChoice identifier="id18c8cc80-68d1-4c1f-b9f0-cb345bad2862">
<p>
<strong>
  <span id="docs-internal-guid-46f83555-04cb-9334-80dc-c56402044c02">None of these </span>
  <br />
</strong>
</p>
</simpleChoice>"""
                }],
                "genusTypeId": str(QTI_QUESTION_CHOICE_INTERACTION_MULTI_GENUS),
                "shuffle": False,
                "fileIds": {}
            },
            "answers": [{
                "genusTypeId": str(RIGHT_ANSWER_GENUS),
                "choiceIds": ["idb5345daa-a5c2-4924-a92b-e326886b5d1d",
                              "id47e56db8-ee16-4111-9bcc-b8ac9716bcd4",
                              "id4f525d00-e24c-4ac3-a104-848a2cd686c0"],
                "feedback": """<modalFeedback  identifier="Feedback933928139" outcomeIdentifier="FEEDBACKMODAL" showHide="show">
  <p id="docs-internal-guid-46f83555-04cc-a70f-2574-1b5c79fe206e" dir="ltr">You are correct! A square has the properties of both a rectangle, and a rhombus. Hence, it can also occupy the shaded region.</p>
</modalFeedback>"""
            }, {
                "genusTypeId": str(WRONG_ANSWER_GENUS),
                "feedback": """<modalFeedback  identifier="Feedback506508014" outcomeIdentifier="FEEDBACKMODAL" showHide="show">
  <p>
    <strong>
      <span id="docs-internal-guid-46f83555-04cc-d077-5f2e-58f80bf813e2">Please try again!</span>
      <br />
    </strong>
  </p>
</modalFeedback>"""
            }]
        }

        for label, asset in assets.iteritems():
            payload['question']['fileIds'][label] = {}
            payload['question']['fileIds'][label]['assetId'] = asset['id']
            payload['question']['fileIds'][label]['assetContentId'] = asset['assetContents'][0]['id']
            payload['question']['fileIds'][label]['assetContentTypeId'] = asset['assetContents'][0]['genusTypeId']

        req = self.app.post(url,
                            params=json.dumps(payload),
                            headers={'content-type': 'application/json'})
        self.ok(req)
        item = self.json(req)

        self.assertEqual(
            item['genusTypeId'],
            str(QTI_ITEM_CHOICE_INTERACTION_MULTI_GENUS)
        )

        self.assertEqual(
            item['question']['genusTypeId'],
            str(QTI_QUESTION_CHOICE_INTERACTION_MULTI_GENUS)
        )

        self.assertEqual(
            item['answers'][0]['genusTypeId'],
            str(RIGHT_ANSWER_GENUS)
        )

        self.assertEqual(
            len(item['answers'][0]['choiceIds']),
            3
        )

        self.assertEqual(
            len(item['answers']),
            2
        )

        self.assertNotEqual(
            item['id'],
            str(self._item.ident)
        )

        # now verify the QTI XML matches the JSON format
        url = '{0}/{1}/qti'.format(url, unquote(item['id']))
        req = self.app.get(url)
        self.ok(req)
        qti_xml = BeautifulSoup(req.body, 'lxml-xml').assessmentItem
        item_body = qti_xml.itemBody

        diamond_label = 'diamond_png'
        rectangle_label = 'rectangle_png'
        parallel_label = 'parallelogram_png'
        regular_square_label = 'square_png'

        diamond_asset_id = item['question']['fileIds'][diamond_label]['assetId']
        diamond_asset_content_id = item['question']['fileIds'][diamond_label]['assetContentId']
        rectangle_asset_id = item['question']['fileIds'][rectangle_label]['assetId']
        rectangle_asset_content_id = item['question']['fileIds'][rectangle_label]['assetContentId']
        parallel_asset_id = item['question']['fileIds'][parallel_label]['assetId']
        parallel_asset_content_id = item['question']['fileIds'][parallel_label]['assetContentId']
        regular_square_asset_id = item['question']['fileIds'][regular_square_label]['assetId']
        regular_square_asset_content_id = item['question']['fileIds'][regular_square_label]['assetContentId']

        expected_string = """<itemBody>
<p dir="ltr" id="docs-internal-guid-46f83555-04c7-ceb0-1838-715e13031a60">
   In the diagram below,
  </p>
<p>
<strong>
</strong>
</p>
<p dir="ltr">
   A is the set of rectangles, and
  </p>
<p dir="ltr">
   B is the set of rhombuses
  </p>
<p dir="ltr">
</p>
<p dir="ltr">
<img alt="venn1" height="202" src="https://lh5.googleusercontent.com/a7NFx8J7jcDSr37Nen6ReW2doooJXZDm6GD1HQTfImkrzah94M_jkYoMapeYoRilKSSOz0gxVOUto0n5R4GWI4UWSnmzoTxH0VMQqRgzYMKWjJCG6OQgp8VPB4ghBAAeHlgI4ze7" width="288"/>
</p>
<p dir="ltr">
</p>
<p>
<strong>
    Which all shape(s) can be contained in the gray shaded area?
    <br/>
</strong>
</p>
<choiceInteraction maxChoices="0" responseIdentifier="RESPONSE_1" shuffle="false">
<simpleChoice identifier="idb5345daa-a5c2-4924-a92b-e326886b5d1d">
<p>
<img alt="parallelagram" height="147" src="/api/v1/repository/repositories/{0}/assets/{1}/contents/{2}/stream" width="186"/>
</p>
</simpleChoice>
<simpleChoice identifier="id31392307-c87e-476b-8f92-b0f12ed66300">
<p>
<img alt="square" height="141" src="/api/v1/repository/repositories/{0}/assets/{3}/contents/{4}/stream" width="144"/>
</p>
</simpleChoice>
<simpleChoice identifier="id01913fba-e66d-4a01-9625-94102847faac">
<p>
<img alt="rectangle" height="118" src="/api/v1/repository/repositories/{0}/assets/{5}/contents/{6}/stream" width="201"/>
</p>
</simpleChoice>
<simpleChoice identifier="id4f525d00-e24c-4ac3-a104-848a2cd686c0">
<p>
<img alt="diamond shape" height="146" src="/api/v1/repository/repositories/{0}/assets/{7}/contents/{8}/stream" width="148"/>
</p>
</simpleChoice>
<simpleChoice identifier="id18c8cc80-68d1-4c1f-b9f0-cb345bad2862">
<p>
<strong>
<span id="docs-internal-guid-46f83555-04cb-9334-80dc-c56402044c02">
       None of these
      </span>
<br/>
</strong>
</p>
</simpleChoice>
</choiceInteraction>
</itemBody>""".format(str(self._bank.ident).replace('assessment.Bank', 'repository.Repository'),
                      parallel_asset_id,
                      parallel_asset_content_id,
                      regular_square_asset_id,
                      regular_square_asset_content_id,
                      rectangle_asset_id,
                      rectangle_asset_content_id,
                      diamond_asset_id,
                      diamond_asset_content_id)

        self.assertEqual(
            str(item_body),
            expected_string
        )

    def test_can_add_question_to_existing_multi_choice_multi_answer_item_via_rest(self):
        url = '{0}/items'.format(self.url)

        payload = {
            "genusTypeId": str(QTI_ITEM_CHOICE_INTERACTION_MULTI_GENUS),
            "name": "Question 1",
            "description": "For testing"
        }

        req = self.app.post(url,
                            params=json.dumps(payload),
                            headers={'content-type': 'application/json'})
        self.ok(req)
        item = self.json(req)

        media_files = [self._square_image,
                       self._diamond_image,
                       self._parallelogram_image,
                       self._rectangle_image]

        assets = {}
        for media_file in media_files:
            label = self._label(self._filename(media_file))
            assets[label] = self.upload_media_file(media_file)

        url = '{0}/items/{1}'.format(self.url, item['id'])

        payload = {
            "question": {
                "questionString": """<itemBody >
<p id="docs-internal-guid-46f83555-04c7-ceb0-1838-715e13031a60" dir="ltr">In the diagram below,</p>
<p>
  <strong>
  </strong>
</p>
<p dir="ltr">A is the set of rectangles, and</p>
<p dir="ltr">B is the set of rhombuses</p>
<p dir="ltr">
</p>
<p dir="ltr">
  <img src="https://lh5.googleusercontent.com/a7NFx8J7jcDSr37Nen6ReW2doooJXZDm6GD1HQTfImkrzah94M_jkYoMapeYoRilKSSOz0gxVOUto0n5R4GWI4UWSnmzoTxH0VMQqRgzYMKWjJCG6OQgp8VPB4ghBAAeHlgI4ze7" alt="venn1" width="288" height="202" />
</p>
<p dir="ltr">
</p>
<p>
  <strong>Which all shape(s) can be contained in the gray shaded area?<br />
</strong>
</p>
</itemBody>""",
                "choices": [{
                    "id": "idb5345daa-a5c2-4924-a92b-e326886b5d1d",
                    "text": """<simpleChoice identifier="idb5345daa-a5c2-4924-a92b-e326886b5d1d">
<p>
<img src="AssetContent:parallelogram_png" alt="parallelagram" width="186" height="147" />
</p>
</simpleChoice>"""
                }, {
                    "id": "id31392307-c87e-476b-8f92-b0f12ed66300",
                    "text": """<simpleChoice identifier="id31392307-c87e-476b-8f92-b0f12ed66300">
<p>
<img src="AssetContent:square_png" alt="square" width="144" height="141" />
</p>
</simpleChoice>"""
                }, {
                    "id": "id01913fba-e66d-4a01-9625-94102847faac",
                    "text": """<simpleChoice identifier="id01913fba-e66d-4a01-9625-94102847faac">
<p>
<img src="AssetContent:rectangle_png" alt="rectangle" width="201" height="118" />
</p>
</simpleChoice>"""
                }, {
                    "id": "id4f525d00-e24c-4ac3-a104-848a2cd686c0",
                    "text": """<simpleChoice identifier="id4f525d00-e24c-4ac3-a104-848a2cd686c0">
<p>
<img src="AssetContent:diamond_png" alt="diamond shape" width="148" height="146" />
</p>
</simpleChoice>"""
                }, {
                    "id": "id18c8cc80-68d1-4c1f-b9f0-cb345bad2862",
                    "text": """<simpleChoice identifier="id18c8cc80-68d1-4c1f-b9f0-cb345bad2862">
<p>
<strong>
  <span id="docs-internal-guid-46f83555-04cb-9334-80dc-c56402044c02">None of these </span>
  <br />
</strong>
</p>
</simpleChoice>"""
                }],
                "genusTypeId": str(QTI_QUESTION_CHOICE_INTERACTION_MULTI_GENUS),
                "shuffle": False,
                "fileIds": {}
            },
            "answers": [{
                "genusTypeId": str(RIGHT_ANSWER_GENUS),
                "choiceIds": ["idb5345daa-a5c2-4924-a92b-e326886b5d1d",
                              "id47e56db8-ee16-4111-9bcc-b8ac9716bcd4",
                              "id4f525d00-e24c-4ac3-a104-848a2cd686c0"],
                "feedback": """<modalFeedback  identifier="Feedback933928139" outcomeIdentifier="FEEDBACKMODAL" showHide="show">
  <p id="docs-internal-guid-46f83555-04cc-a70f-2574-1b5c79fe206e" dir="ltr">You are correct! A square has the properties of both a rectangle, and a rhombus. Hence, it can also occupy the shaded region.</p>
</modalFeedback>"""
            }, {
                "genusTypeId": str(WRONG_ANSWER_GENUS),
                "feedback": """<modalFeedback  identifier="Feedback506508014" outcomeIdentifier="FEEDBACKMODAL" showHide="show">
  <p>
    <strong>
      <span id="docs-internal-guid-46f83555-04cc-d077-5f2e-58f80bf813e2">Please try again!</span>
      <br />
    </strong>
  </p>
</modalFeedback>"""
            }]
        }

        for label, asset in assets.iteritems():
            payload['question']['fileIds'][label] = {}
            payload['question']['fileIds'][label]['assetId'] = asset['id']
            payload['question']['fileIds'][label]['assetContentId'] = asset['assetContents'][0]['id']
            payload['question']['fileIds'][label]['assetContentTypeId'] = asset['assetContents'][0]['genusTypeId']

        req = self.app.put(url,
                           params=json.dumps(payload),
                           headers={'content-type': 'application/json'})
        self.ok(req)
        item = self.json(req)

        self.assertEqual(
            item['genusTypeId'],
            str(QTI_ITEM_CHOICE_INTERACTION_MULTI_GENUS)
        )

        self.assertEqual(
            item['question']['genusTypeId'],
            str(QTI_QUESTION_CHOICE_INTERACTION_MULTI_GENUS)
        )

        self.assertEqual(
            item['answers'][0]['genusTypeId'],
            str(RIGHT_ANSWER_GENUS)
        )

        self.assertEqual(
            len(item['answers'][0]['choiceIds']),
            3
        )

        self.assertEqual(
            len(item['answers']),
            2
        )

        self.assertNotEqual(
            item['id'],
            str(self._item.ident)
        )

        # now verify the QTI XML matches the JSON format
        url = '{0}/{1}/qti'.format(url, unquote(item['id']))
        req = self.app.get(url)
        self.ok(req)
        qti_xml = BeautifulSoup(req.body, 'lxml-xml').assessmentItem
        item_body = qti_xml.itemBody

        diamond_label = 'diamond_png'
        rectangle_label = 'rectangle_png'
        parallel_label = 'parallelogram_png'
        regular_square_label = 'square_png'

        diamond_asset_id = item['question']['fileIds'][diamond_label]['assetId']
        diamond_asset_content_id = item['question']['fileIds'][diamond_label]['assetContentId']
        rectangle_asset_id = item['question']['fileIds'][rectangle_label]['assetId']
        rectangle_asset_content_id = item['question']['fileIds'][rectangle_label]['assetContentId']
        parallel_asset_id = item['question']['fileIds'][parallel_label]['assetId']
        parallel_asset_content_id = item['question']['fileIds'][parallel_label]['assetContentId']
        regular_square_asset_id = item['question']['fileIds'][regular_square_label]['assetId']
        regular_square_asset_content_id = item['question']['fileIds'][regular_square_label]['assetContentId']

        expected_string = """<itemBody>
<p dir="ltr" id="docs-internal-guid-46f83555-04c7-ceb0-1838-715e13031a60">
   In the diagram below,
  </p>
<p>
<strong>
</strong>
</p>
<p dir="ltr">
   A is the set of rectangles, and
  </p>
<p dir="ltr">
   B is the set of rhombuses
  </p>
<p dir="ltr">
</p>
<p dir="ltr">
<img alt="venn1" height="202" src="https://lh5.googleusercontent.com/a7NFx8J7jcDSr37Nen6ReW2doooJXZDm6GD1HQTfImkrzah94M_jkYoMapeYoRilKSSOz0gxVOUto0n5R4GWI4UWSnmzoTxH0VMQqRgzYMKWjJCG6OQgp8VPB4ghBAAeHlgI4ze7" width="288"/>
</p>
<p dir="ltr">
</p>
<p>
<strong>
    Which all shape(s) can be contained in the gray shaded area?
    <br/>
</strong>
</p>
<choiceInteraction maxChoices="0" responseIdentifier="RESPONSE_1" shuffle="false">
<simpleChoice identifier="idb5345daa-a5c2-4924-a92b-e326886b5d1d">
<p>
<img alt="parallelagram" height="147" src="/api/v1/repository/repositories/{0}/assets/{1}/contents/{2}/stream" width="186"/>
</p>
</simpleChoice>
<simpleChoice identifier="id31392307-c87e-476b-8f92-b0f12ed66300">
<p>
<img alt="square" height="141" src="/api/v1/repository/repositories/{0}/assets/{3}/contents/{4}/stream" width="144"/>
</p>
</simpleChoice>
<simpleChoice identifier="id01913fba-e66d-4a01-9625-94102847faac">
<p>
<img alt="rectangle" height="118" src="/api/v1/repository/repositories/{0}/assets/{5}/contents/{6}/stream" width="201"/>
</p>
</simpleChoice>
<simpleChoice identifier="id4f525d00-e24c-4ac3-a104-848a2cd686c0">
<p>
<img alt="diamond shape" height="146" src="/api/v1/repository/repositories/{0}/assets/{7}/contents/{8}/stream" width="148"/>
</p>
</simpleChoice>
<simpleChoice identifier="id18c8cc80-68d1-4c1f-b9f0-cb345bad2862">
<p>
<strong>
<span id="docs-internal-guid-46f83555-04cb-9334-80dc-c56402044c02">
       None of these
      </span>
<br/>
</strong>
</p>
</simpleChoice>
</choiceInteraction>
</itemBody>""".format(str(self._bank.ident).replace('assessment.Bank', 'repository.Repository'),
                      parallel_asset_id,
                      parallel_asset_content_id,
                      regular_square_asset_id,
                      regular_square_asset_content_id,
                      rectangle_asset_id,
                      rectangle_asset_content_id,
                      diamond_asset_id,
                      diamond_asset_content_id)

        self.assertEqual(
            str(item_body),
            expected_string
        )

        expected_json_string = """<itemBody >
<p id="docs-internal-guid-46f83555-04c7-ceb0-1838-715e13031a60" dir="ltr">In the diagram below,</p>
<p>
  <strong>
  </strong>
</p>
<p dir="ltr">A is the set of rectangles, and</p>
<p dir="ltr">B is the set of rhombuses</p>
<p dir="ltr">
</p>
<p dir="ltr">
  <img src="https://lh5.googleusercontent.com/a7NFx8J7jcDSr37Nen6ReW2doooJXZDm6GD1HQTfImkrzah94M_jkYoMapeYoRilKSSOz0gxVOUto0n5R4GWI4UWSnmzoTxH0VMQqRgzYMKWjJCG6OQgp8VPB4ghBAAeHlgI4ze7" alt="venn1" width="288" height="202" />
</p>
<p dir="ltr">
</p>
<p>
  <strong>Which all shape(s) can be contained in the gray shaded area?<br />
</strong>
</p>
</itemBody>""".format(str(self._bank.ident).replace('assessment.Bank', 'repository.Repository'))
        self.assertEqual(
            item['question']['text']['text'],
            expected_json_string
        )

    def test_can_get_multi_choice_multi_answer_item_with_no_choices(self):
        url = '{0}/items'.format(self.url)

        payload = {
            "genusTypeId": str(QTI_ITEM_CHOICE_INTERACTION_MULTI_GENUS),
            "name": "Question 1",
            "description": "For testing",
            "question": {
                "questionString": """<itemBody >
<p id="docs-internal-guid-46f83555-04c7-ceb0-1838-715e13031a60" dir="ltr">In the diagram below,</p>
<p>
  <strong>
  </strong>
</p>
<p dir="ltr">A is the set of rectangles, and</p>
<p dir="ltr">B is the set of rhombuses</p>
<p dir="ltr">
</p>
<p dir="ltr">
  <img src="https://lh5.googleusercontent.com/a7NFx8J7jcDSr37Nen6ReW2doooJXZDm6GD1HQTfImkrzah94M_jkYoMapeYoRilKSSOz0gxVOUto0n5R4GWI4UWSnmzoTxH0VMQqRgzYMKWjJCG6OQgp8VPB4ghBAAeHlgI4ze7" alt="venn1" width="288" height="202" />
</p>
<p dir="ltr">
</p>
<p>
  <strong>Which all shape(s) can be contained in the gray shaded area?<br />
</strong>
</p>
</itemBody>"""}
        }

        req = self.app.post(url,
                            params=json.dumps(payload),
                            headers={'content-type': 'application/json'})
        self.ok(req)
        item = self.json(req)

        url = '{0}/items/{1}'.format(self.url, item['id'])

        req = self.app.get(url)
        self.ok(req)
        data = self.json(req)
        self.assertEqual(data['question']['choices'], [])

    def test_can_get_multi_choice_multi_answer_item_qti_with_no_answer(self):
        url = '{0}/items'.format(self.url)

        payload = {
            "genusTypeId": str(QTI_ITEM_CHOICE_INTERACTION_MULTI_GENUS),
            "name": "Question 1",
            "description": "For testing",
            "question": {
                "questionString": """<itemBody >
<p id="docs-internal-guid-46f83555-04c7-ceb0-1838-715e13031a60" dir="ltr">In the diagram below,</p>
<p>
  <strong>
  </strong>
</p>
<p dir="ltr">A is the set of rectangles, and</p>
<p dir="ltr">B is the set of rhombuses</p>
<p dir="ltr">
</p>
<p dir="ltr">
  <img src="https://lh5.googleusercontent.com/a7NFx8J7jcDSr37Nen6ReW2doooJXZDm6GD1HQTfImkrzah94M_jkYoMapeYoRilKSSOz0gxVOUto0n5R4GWI4UWSnmzoTxH0VMQqRgzYMKWjJCG6OQgp8VPB4ghBAAeHlgI4ze7" alt="venn1" width="288" height="202" />
</p>
<p dir="ltr">
</p>
<p>
  <strong>Which all shape(s) can be contained in the gray shaded area?<br />
</strong>
</p>
</itemBody>"""}
        }

        req = self.app.post(url,
                            params=json.dumps(payload),
                            headers={'content-type': 'application/json'})
        self.ok(req)
        item = self.json(req)

        url = '{0}/items/{1}/qti'.format(self.url, item['id'])

        req = self.app.get(url)
        self.ok(req)
        qti = BeautifulSoup(req.body, 'xml')
        self.assertIsNone(qti.responseDeclaration)

    def test_getting_qti_for_multi_choice_multi_answer_with_no_question_returns_empty_string(self):
        url = '{0}/items'.format(self.url)

        payload = {
            "genusTypeId": str(QTI_ITEM_CHOICE_INTERACTION_MULTI_GENUS),
            "name": "Question 1",
            "description": "For testing"
        }

        req = self.app.post(url,
                            params=json.dumps(payload),
                            headers={'content-type': 'application/json'})
        self.ok(req)
        item = self.json(req)

        # now verify the QTI XML is empty string
        url = '{0}/{1}/qti'.format(url, unquote(item['id']))
        req = self.app.get(url)
        self.ok(req)
        self.assertEqual(req.body, '')

    def test_updating_multi_choice_multi_answer_answer_clears_existing_choices(self):
        url = '{0}/items'.format(self.url)

        media_files = [self._square_image,
                       self._diamond_image,
                       self._parallelogram_image,
                       self._rectangle_image]

        assets = {}
        for media_file in media_files:
            label = self._label(self._filename(media_file))
            assets[label] = self.upload_media_file(media_file)

        payload = {
            "genusTypeId": str(QTI_ITEM_CHOICE_INTERACTION_MULTI_GENUS),
            "name": "Question 1",
            "description": "For testing",
            "question": {
                "questionString": """<itemBody >
<p id="docs-internal-guid-46f83555-04c7-ceb0-1838-715e13031a60" dir="ltr">In the diagram below,</p>
<p>
  <strong>
  </strong>
</p>
<p dir="ltr">A is the set of rectangles, and</p>
<p dir="ltr">B is the set of rhombuses</p>
<p dir="ltr">
</p>
<p dir="ltr">
  <img src="https://lh5.googleusercontent.com/a7NFx8J7jcDSr37Nen6ReW2doooJXZDm6GD1HQTfImkrzah94M_jkYoMapeYoRilKSSOz0gxVOUto0n5R4GWI4UWSnmzoTxH0VMQqRgzYMKWjJCG6OQgp8VPB4ghBAAeHlgI4ze7" alt="venn1" width="288" height="202" />
</p>
<p dir="ltr">
</p>
<p>
  <strong>Which all shape(s) can be contained in the gray shaded area?<br />
</strong>
</p>
</itemBody>""",
                "choices": [{
                    "id": "idb5345daa-a5c2-4924-a92b-e326886b5d1d",
                    "text": """<simpleChoice identifier="idb5345daa-a5c2-4924-a92b-e326886b5d1d">
<p>
<img src="AssetContent:parallelogram_png" alt="parallelagram" width="186" height="147" />
</p>
</simpleChoice>"""
                }, {
                    "id": "id31392307-c87e-476b-8f92-b0f12ed66300",
                    "text": """<simpleChoice identifier="id31392307-c87e-476b-8f92-b0f12ed66300">
<p>
<img src="AssetContent:square_png" alt="square" width="144" height="141" />
</p>
</simpleChoice>"""
                }, {
                    "id": "id01913fba-e66d-4a01-9625-94102847faac",
                    "text": """<simpleChoice identifier="id01913fba-e66d-4a01-9625-94102847faac">
<p>
<img src="AssetContent:rectangle_png" alt="rectangle" width="201" height="118" />
</p>
</simpleChoice>"""
                }, {
                    "id": "id4f525d00-e24c-4ac3-a104-848a2cd686c0",
                    "text": """<simpleChoice identifier="id4f525d00-e24c-4ac3-a104-848a2cd686c0">
<p>
<img src="AssetContent:diamond_png" alt="diamond shape" width="148" height="146" />
</p>
</simpleChoice>"""
                }, {
                    "id": "id18c8cc80-68d1-4c1f-b9f0-cb345bad2862",
                    "text": """<simpleChoice identifier="id18c8cc80-68d1-4c1f-b9f0-cb345bad2862">
<p>
<strong>
  <span id="docs-internal-guid-46f83555-04cb-9334-80dc-c56402044c02">None of these </span>
  <br />
</strong>
</p>
</simpleChoice>"""
                }],
                "genusTypeId": str(QTI_QUESTION_CHOICE_INTERACTION_MULTI_GENUS),
                "shuffle": False,
                "fileIds": {}
            },
            "answers": [{
                "genusTypeId": str(RIGHT_ANSWER_GENUS),
                "choiceIds": ["idb5345daa-a5c2-4924-a92b-e326886b5d1d",
                              "id47e56db8-ee16-4111-9bcc-b8ac9716bcd4",
                              "id4f525d00-e24c-4ac3-a104-848a2cd686c0"],
                "feedback": """<modalFeedback  identifier="Feedback933928139" outcomeIdentifier="FEEDBACKMODAL" showHide="show">
  <p id="docs-internal-guid-46f83555-04cc-a70f-2574-1b5c79fe206e" dir="ltr">You are correct! A square has the properties of both a rectangle, and a rhombus. Hence, it can also occupy the shaded region.</p>
</modalFeedback>"""
            }, {
                "genusTypeId": str(WRONG_ANSWER_GENUS),
                "feedback": """<modalFeedback  identifier="Feedback506508014" outcomeIdentifier="FEEDBACKMODAL" showHide="show">
  <p>
    <strong>
      <span id="docs-internal-guid-46f83555-04cc-d077-5f2e-58f80bf813e2">Please try again!</span>
      <br />
    </strong>
  </p>
</modalFeedback>"""
            }]
        }

        for label, asset in assets.iteritems():
            payload['question']['fileIds'][label] = {}
            payload['question']['fileIds'][label]['assetId'] = asset['id']
            payload['question']['fileIds'][label]['assetContentId'] = asset['assetContents'][0]['id']
            payload['question']['fileIds'][label]['assetContentTypeId'] = asset['assetContents'][0]['genusTypeId']

        req = self.app.post(url,
                            params=json.dumps(payload),
                            headers={'content-type': 'application/json'})
        self.ok(req)
        item = self.json(req)

        right_answer = [a for a in item['answers'] if a['genusTypeId'] == str(RIGHT_ANSWER_GENUS)][0]
        previous_right_answer_choices = right_answer['choiceIds']
        new_right_answer_choices = ["idb5345daa-a5c2-4924-a92b-e326886b5d1d",
                                    "id47e56db8-ee16-4111-9bcc-b8ac9716bcd4"]

        self.assertNotEqual(previous_right_answer_choices,
                            new_right_answer_choices)

        url = '{0}/{1}'.format(url, item['id'])
        payload = {
            'answers': [{
                'id': right_answer['id'],
                'choiceIds': new_right_answer_choices
            }]
        }
        req = self.app.put(url,
                           params=json.dumps(payload),
                           headers={'content-type': 'application/json'})
        self.ok(req)
        data = self.json(req)
        self.assertEqual(data['id'], item['id'])
        self.assertEqual(data['answers'][0]['id'], right_answer['id'])
        self.assertEqual(data['answers'][0]['genusTypeId'], str(RIGHT_ANSWER_GENUS))
        self.assertNotEqual(previous_right_answer_choices, data['answers'][0]['choiceIds'])
        self.assertEqual(new_right_answer_choices, data['answers'][0]['choiceIds'])

    def test_can_create_reflection_single_answer_question_via_rest(self):
        url = '{0}/items'.format(self.url)
        payload = {
            "genusTypeId": str(QTI_ITEM_CHOICE_INTERACTION_SURVEY_GENUS),
            "name": "Question 1",
            "description": "For testing",
            "question": {
                "questionString": """<itemBody >
<p>Did you eat breakfast today?</p>
</itemBody>""",
                "choices": [{
                    "id": "id5f1fc52a-a04e-4fa1-b855-51da24967a31",
                    "text": """<simpleChoice identifier="id5f1fc52a-a04e-4fa1-b855-51da24967a31">
<p>Yes</p>
</simpleChoice>"""
                }, {
                    "id": "id31392307-c87e-476b-8f92-b0f12ed66300",
                    "text": """<simpleChoice identifier="id31392307-c87e-476b-8f92-b0f12ed66300">
<p>No</p>
</simpleChoice>"""
                }, {
                    "id": "id8188b5cd-89b0-4140-b12a-aed5426bd81b",
                    "text": """<simpleChoice identifier="id8188b5cd-89b0-4140-b12a-aed5426bd81b">
<p>I don't remember</p>
</simpleChoice>"""
                }],
                "genusTypeId": str(QTI_QUESTION_CHOICE_INTERACTION_SURVEY_GENUS),
                "shuffle": True
            },
            "answers": [{
                "genusTypeId": str(RIGHT_ANSWER_GENUS),
                "choiceIds": ["id5f1fc52a-a04e-4fa1-b855-51da24967a31"],
                "feedback": """<modalFeedback  identifier="Feedback1359458626" outcomeIdentifier="FEEDBACKMODAL" showHide="show">
<p>Thank you for your participation.</p>
</modalFeedback>"""
            }, {
                "genusTypeId": str(RIGHT_ANSWER_GENUS),
                "choiceIds": ["id31392307-c87e-476b-8f92-b0f12ed66300"],
                "feedback": """<modalFeedback  identifier="Feedback1359458626" outcomeIdentifier="FEEDBACKMODAL" showHide="show">
<p>Thank you for your participation.</p>
</modalFeedback>"""
            }, {
                "genusTypeId": str(RIGHT_ANSWER_GENUS),
                "choiceIds": ["id8188b5cd-89b0-4140-b12a-aed5426bd81b"],
                "feedback": """<modalFeedback  identifier="Feedback1359458626" outcomeIdentifier="FEEDBACKMODAL" showHide="show">
<p>Thank you for your participation.</p>
</modalFeedback>"""
            }]
        }
        req = self.app.post(url,
                            params=json.dumps(payload),
                            headers={'content-type': 'application/json'})
        self.ok(req)
        item = self.json(req)

        self.assertEqual(
            item['genusTypeId'],
            str(QTI_ITEM_CHOICE_INTERACTION_SURVEY_GENUS)
        )

        self.assertEqual(
            item['question']['genusTypeId'],
            str(QTI_QUESTION_CHOICE_INTERACTION_SURVEY_GENUS)
        )
        self.assertEqual(
            len(item['question']['choices']),
            3
        )
        choice_ids = [c['id'] for c in item['question']['choices']]

        self.assertEqual(
            len(item['answers']),
            3
        )
        for answer in item['answers']:
            self.assertEqual(
                answer['genusTypeId'],
                str(RIGHT_ANSWER_GENUS)
            )
            self.assertIn('Thank you for your participation.', answer['feedbacks'][0]['text'])
            self.assertIn(answer['choiceIds'][0], choice_ids)

        self.assertNotEqual(
            item['id'],
            str(self._item.ident)
        )

        url = '{0}/{1}/qti'.format(url, unquote(item['id']))
        req = self.app.get(url)
        self.ok(req)
        item_qti = BeautifulSoup(req.body, 'lxml-xml').assessmentItem
        item_body = item_qti.itemBody

        choice_interaction = item_body.choiceInteraction.extract()

        expected_string = """<itemBody>
<p>
   Did you eat breakfast today?
  </p>

</itemBody>"""

        self.assertEqual(
            str(item_body),
            expected_string
        )

        self.assertEqual(
            len(choice_interaction.find_all('simpleChoice')),
            3
        )
        self.assertEqual(
            choice_interaction['maxChoices'],
            "1"
        )
        self.assertEqual(
            choice_interaction['responseIdentifier'],
            'RESPONSE_1'
        )
        self.assertEqual(
            choice_interaction['shuffle'],
            'true'
        )

        expected_choices = {
            "id5f1fc52a-a04e-4fa1-b855-51da24967a31": """<simpleChoice identifier="id5f1fc52a-a04e-4fa1-b855-51da24967a31">
<p>
     Yes
    </p>
</simpleChoice>""",
            "id31392307-c87e-476b-8f92-b0f12ed66300": """<simpleChoice identifier="id31392307-c87e-476b-8f92-b0f12ed66300">
<p>
     No
    </p>
</simpleChoice>""",
            "id8188b5cd-89b0-4140-b12a-aed5426bd81b": """<simpleChoice identifier="id8188b5cd-89b0-4140-b12a-aed5426bd81b">
<p>
     I don\'t remember
    </p>
</simpleChoice>"""
        }

        for choice in choice_interaction.find_all('simpleChoice'):
            choice_id = choice['identifier']
            self.assertEqual(
                str(choice),
                expected_choices[choice_id]
            )

    def test_can_add_question_to_existing_reflection_single_answer_item_via_rest(self):
        url = '{0}/items'.format(self.url)
        payload = {
            "genusTypeId": str(QTI_ITEM_CHOICE_INTERACTION_SURVEY_GENUS),
            "name": "Question 1",
            "description": "For testing"
        }
        req = self.app.post(url,
                            params=json.dumps(payload),
                            headers={'content-type': 'application/json'})
        self.ok(req)
        item = self.json(req)

        url = '{0}/items/{1}'.format(self.url, item['id'])
        payload = {
            "question": {
                "questionString": """<itemBody >
<p>Did you eat breakfast today?</p>
</itemBody>""",
                "choices": [{
                    "id": "id5f1fc52a-a04e-4fa1-b855-51da24967a31",
                    "text": """<simpleChoice identifier="id5f1fc52a-a04e-4fa1-b855-51da24967a31">
<p>Yes</p>
</simpleChoice>"""
                }, {
                    "id": "id31392307-c87e-476b-8f92-b0f12ed66300",
                    "text": """<simpleChoice identifier="id31392307-c87e-476b-8f92-b0f12ed66300">
<p>No</p>
</simpleChoice>"""
                }, {
                    "id": "id8188b5cd-89b0-4140-b12a-aed5426bd81b",
                    "text": """<simpleChoice identifier="id8188b5cd-89b0-4140-b12a-aed5426bd81b">
<p>I don't remember</p>
</simpleChoice>"""
                }],
                "genusTypeId": str(QTI_QUESTION_CHOICE_INTERACTION_SURVEY_GENUS),
                "shuffle": True
            },
            "answers": [{
                "genusTypeId": str(RIGHT_ANSWER_GENUS),
                "choiceIds": ["id5f1fc52a-a04e-4fa1-b855-51da24967a31"],
                "feedback": """<modalFeedback  identifier="Feedback1359458626" outcomeIdentifier="FEEDBACKMODAL" showHide="show">
<p>Thank you for your participation.</p>
</modalFeedback>"""
            }, {
                "genusTypeId": str(RIGHT_ANSWER_GENUS),
                "choiceIds": ["id31392307-c87e-476b-8f92-b0f12ed66300"],
                "feedback": """<modalFeedback  identifier="Feedback1359458626" outcomeIdentifier="FEEDBACKMODAL" showHide="show">
<p>Thank you for your participation.</p>
</modalFeedback>"""
            }, {
                "genusTypeId": str(RIGHT_ANSWER_GENUS),
                "choiceIds": ["id8188b5cd-89b0-4140-b12a-aed5426bd81b"],
                "feedback": """<modalFeedback  identifier="Feedback1359458626" outcomeIdentifier="FEEDBACKMODAL" showHide="show">
<p>Thank you for your participation.</p>
</modalFeedback>"""
            }]
        }
        req = self.app.put(url,
                           params=json.dumps(payload),
                           headers={'content-type': 'application/json'})
        self.ok(req)
        item = self.json(req)

        self.assertEqual(
            item['genusTypeId'],
            str(QTI_ITEM_CHOICE_INTERACTION_SURVEY_GENUS)
        )

        self.assertEqual(
            item['question']['genusTypeId'],
            str(QTI_QUESTION_CHOICE_INTERACTION_SURVEY_GENUS)
        )
        self.assertEqual(
            len(item['question']['choices']),
            3
        )
        choice_ids = [c['id'] for c in item['question']['choices']]

        self.assertEqual(
            len(item['answers']),
            3
        )
        for answer in item['answers']:
            self.assertEqual(
                answer['genusTypeId'],
                str(RIGHT_ANSWER_GENUS)
            )
            self.assertIn('Thank you for your participation.', answer['feedbacks'][0]['text'])
            self.assertIn(answer['choiceIds'][0], choice_ids)

        self.assertNotEqual(
            item['id'],
            str(self._item.ident)
        )

        url = '{0}/{1}/qti'.format(url, unquote(item['id']))
        req = self.app.get(url)
        self.ok(req)
        item_qti = BeautifulSoup(req.body, 'lxml-xml').assessmentItem
        item_body = item_qti.itemBody

        choice_interaction = item_body.choiceInteraction.extract()

        expected_string = """<itemBody>
<p>
   Did you eat breakfast today?
  </p>

</itemBody>"""

        self.assertEqual(
            str(item_body),
            expected_string
        )

        self.assertEqual(
            len(choice_interaction.find_all('simpleChoice')),
            3
        )
        self.assertEqual(
            choice_interaction['maxChoices'],
            "1"
        )
        self.assertEqual(
            choice_interaction['responseIdentifier'],
            'RESPONSE_1'
        )
        self.assertEqual(
            choice_interaction['shuffle'],
            'true'
        )

        expected_choices = {
            "id5f1fc52a-a04e-4fa1-b855-51da24967a31": """<simpleChoice identifier="id5f1fc52a-a04e-4fa1-b855-51da24967a31">
<p>
     Yes
    </p>
</simpleChoice>""",
            "id31392307-c87e-476b-8f92-b0f12ed66300": """<simpleChoice identifier="id31392307-c87e-476b-8f92-b0f12ed66300">
<p>
     No
    </p>
</simpleChoice>""",
            "id8188b5cd-89b0-4140-b12a-aed5426bd81b": """<simpleChoice identifier="id8188b5cd-89b0-4140-b12a-aed5426bd81b">
<p>
     I don\'t remember
    </p>
</simpleChoice>"""
        }

        for choice in choice_interaction.find_all('simpleChoice'):
            choice_id = choice['identifier']
            self.assertEqual(
                str(choice),
                expected_choices[choice_id]
            )

    def test_can_get_reflection_single_answer_item_with_no_choices(self):
        url = '{0}/items'.format(self.url)
        payload = {
            "genusTypeId": str(QTI_ITEM_CHOICE_INTERACTION_SURVEY_GENUS),
            "name": "Question 1",
            "description": "For testing",

            "question": {
                "questionString": """<itemBody >
<p>Did you eat breakfast today?</p>
</itemBody>"""}
        }
        req = self.app.post(url,
                            params=json.dumps(payload),
                            headers={'content-type': 'application/json'})
        self.ok(req)
        item = self.json(req)

        url = '{0}/items/{1}'.format(self.url, item['id'])
        req = self.app.get(url)
        self.ok(req)
        data = self.json(req)
        self.assertEqual(data['question']['choices'], [])

    def test_can_get_reflection_single_answer_item_qti_with_no_answers(self):
        url = '{0}/items'.format(self.url)
        payload = {
            "genusTypeId": str(QTI_ITEM_CHOICE_INTERACTION_SURVEY_GENUS),
            "name": "Question 1",
            "description": "For testing",

            "question": {
                "questionString": """<itemBody >
<p>Did you eat breakfast today?</p>
</itemBody>"""}
        }
        req = self.app.post(url,
                            params=json.dumps(payload),
                            headers={'content-type': 'application/json'})
        self.ok(req)
        item = self.json(req)

        url = '{0}/items/{1}/qti'.format(self.url, item['id'])
        req = self.app.get(url)
        self.ok(req)
        qti = BeautifulSoup(req.body, 'xml')
        self.assertIsNone(qti.responseDeclaration)

    def test_getting_qti_for_reflection_single_answer_item_with_no_question_returns_empty_string(self):
        url = '{0}/items'.format(self.url)
        payload = {
            "genusTypeId": str(QTI_ITEM_CHOICE_INTERACTION_SURVEY_GENUS),
            "name": "Question 1",
            "description": "For testing"
        }
        req = self.app.post(url,
                            params=json.dumps(payload),
                            headers={'content-type': 'application/json'})
        self.ok(req)
        item = self.json(req)

        url = '{0}/{1}/qti'.format(url, unquote(item['id']))
        req = self.app.get(url)
        self.ok(req)
        self.assertEqual(req.body, '')

    def test_updating_reflection_single_answer_answer_clears_existing_choices(self):
        url = '{0}/items'.format(self.url)

        payload = {
            "genusTypeId": str(QTI_ITEM_CHOICE_INTERACTION_SURVEY_GENUS),
            "name": "Question 1",
            "description": "For testing",
            "question": {
                "questionString": """<itemBody >
<p>Did you eat breakfast today?</p>
</itemBody>""",
                "choices": [{
                    "id": "id5f1fc52a-a04e-4fa1-b855-51da24967a31",
                    "text": """<simpleChoice identifier="id5f1fc52a-a04e-4fa1-b855-51da24967a31">
<p>Yes</p>
</simpleChoice>"""
                }, {
                    "id": "id31392307-c87e-476b-8f92-b0f12ed66300",
                    "text": """<simpleChoice identifier="id31392307-c87e-476b-8f92-b0f12ed66300">
<p>No</p>
</simpleChoice>"""
                }, {
                    "id": "id8188b5cd-89b0-4140-b12a-aed5426bd81b",
                    "text": """<simpleChoice identifier="id8188b5cd-89b0-4140-b12a-aed5426bd81b">
<p>I don't remember</p>
</simpleChoice>"""
                }],
                "genusTypeId": str(QTI_QUESTION_CHOICE_INTERACTION_SURVEY_GENUS),
                "shuffle": True
            },
            "answers": [{
                "genusTypeId": str(RIGHT_ANSWER_GENUS),
                "choiceIds": ["id5f1fc52a-a04e-4fa1-b855-51da24967a31"],
                "feedback": """<modalFeedback  identifier="Feedback1359458626" outcomeIdentifier="FEEDBACKMODAL" showHide="show">
<p>Thank you for your participation.</p>
</modalFeedback>"""
            }, {
                "genusTypeId": str(RIGHT_ANSWER_GENUS),
                "choiceIds": ["id31392307-c87e-476b-8f92-b0f12ed66300"],
                "feedback": """<modalFeedback  identifier="Feedback1359458626" outcomeIdentifier="FEEDBACKMODAL" showHide="show">
<p>Thank you for your participation.</p>
</modalFeedback>"""
            }, {
                "genusTypeId": str(RIGHT_ANSWER_GENUS),
                "choiceIds": ["id8188b5cd-89b0-4140-b12a-aed5426bd81b"],
                "feedback": """<modalFeedback  identifier="Feedback1359458626" outcomeIdentifier="FEEDBACKMODAL" showHide="show">
<p>Thank you for your participation.</p>
</modalFeedback>"""
            }]
        }
        req = self.app.post(url,
                            params=json.dumps(payload),
                            headers={'content-type': 'application/json'})
        self.ok(req)
        item = self.json(req)

        right_answer = [a for a in item['answers'] if a['genusTypeId'] == str(RIGHT_ANSWER_GENUS)][0]
        previous_right_answer_choice = right_answer['choiceIds'][0]
        new_right_answer_choice = 'foo'

        self.assertNotEqual(previous_right_answer_choice,
                            new_right_answer_choice)

        url = '{0}/{1}'.format(url, item['id'])
        payload = {
            'answers': [{
                'id': right_answer['id'],
                'choiceIds': [new_right_answer_choice]
            }]
        }
        req = self.app.put(url,
                           params=json.dumps(payload),
                           headers={'content-type': 'application/json'})
        self.ok(req)
        data = self.json(req)
        self.assertEqual(data['id'], item['id'])
        self.assertEqual(data['answers'][0]['id'], right_answer['id'])
        self.assertEqual(data['answers'][0]['genusTypeId'], str(RIGHT_ANSWER_GENUS))
        self.assertNotIn(previous_right_answer_choice, data['answers'][0]['choiceIds'])
        self.assertIn(new_right_answer_choice, data['answers'][0]['choiceIds'])
        self.assertEqual(len(data['answers'][0]['choiceIds']), 1)

    def test_can_create_reflection_multi_answer_question_via_rest(self):
        url = '{0}/items'.format(self.url)
        payload = {
            "genusTypeId": str(QTI_ITEM_CHOICE_INTERACTION_MULTI_SELECT_SURVEY_GENUS),
            "name": "Question 1",
            "description": "For testing",
            "question": {
                "questionString": """<itemBody >
<p>Did you eat breakfast today?</p>
</itemBody>""",
                "choices": [{
                    "id": "id5f1fc52a-a04e-4fa1-b855-51da24967a31",
                    "text": """<simpleChoice identifier="id5f1fc52a-a04e-4fa1-b855-51da24967a31">
<p>Yes</p>
</simpleChoice>"""
                }, {
                    "id": "id31392307-c87e-476b-8f92-b0f12ed66300",
                    "text": """<simpleChoice identifier="id31392307-c87e-476b-8f92-b0f12ed66300">
<p>No</p>
</simpleChoice>"""
                }, {
                    "id": "id8188b5cd-89b0-4140-b12a-aed5426bd81b",
                    "text": """<simpleChoice identifier="id8188b5cd-89b0-4140-b12a-aed5426bd81b">
<p>I don't remember</p>
</simpleChoice>"""
                }],
                "genusTypeId": str(QTI_QUESTION_CHOICE_INTERACTION_MULTI_SELECT_SURVEY_GENUS),
                "shuffle": True
            },
            "answers": [{
                "genusTypeId": str(RIGHT_ANSWER_GENUS),
                "choiceIds": ["id5f1fc52a-a04e-4fa1-b855-51da24967a31"],
                "feedback": """<modalFeedback  identifier="Feedback1359458626" outcomeIdentifier="FEEDBACKMODAL" showHide="show">
<p>Thank you for your participation.</p>
</modalFeedback>"""
            }, {
                "genusTypeId": str(RIGHT_ANSWER_GENUS),
                "choiceIds": ["id31392307-c87e-476b-8f92-b0f12ed66300"],
                "feedback": """<modalFeedback  identifier="Feedback1359458626" outcomeIdentifier="FEEDBACKMODAL" showHide="show">
<p>Thank you for your participation.</p>
</modalFeedback>"""
            }, {
                "genusTypeId": str(RIGHT_ANSWER_GENUS),
                "choiceIds": ["id8188b5cd-89b0-4140-b12a-aed5426bd81b"],
                "feedback": """<modalFeedback  identifier="Feedback1359458626" outcomeIdentifier="FEEDBACKMODAL" showHide="show">
<p>Thank you for your participation.</p>
</modalFeedback>"""
            }]
        }
        req = self.app.post(url,
                            params=json.dumps(payload),
                            headers={'content-type': 'application/json'})
        self.ok(req)
        item = self.json(req)

        self.assertEqual(
            item['genusTypeId'],
            str(QTI_ITEM_CHOICE_INTERACTION_MULTI_SELECT_SURVEY_GENUS)
        )

        self.assertEqual(
            item['question']['genusTypeId'],
            str(QTI_QUESTION_CHOICE_INTERACTION_MULTI_SELECT_SURVEY_GENUS)
        )
        self.assertEqual(
            len(item['question']['choices']),
            3
        )
        choice_ids = [c['id'] for c in item['question']['choices']]

        self.assertEqual(
            len(item['answers']),
            3
        )
        for answer in item['answers']:
            self.assertEqual(
                answer['genusTypeId'],
                str(RIGHT_ANSWER_GENUS)
            )
            self.assertIn('Thank you for your participation.', answer['feedbacks'][0]['text'])
            self.assertIn(answer['choiceIds'][0], choice_ids)

        self.assertNotEqual(
            item['id'],
            str(self._item.ident)
        )

        url = '{0}/{1}/qti'.format(url, unquote(item['id']))
        req = self.app.get(url)
        self.ok(req)
        item_qti = BeautifulSoup(req.body, 'lxml-xml').assessmentItem
        item_body = item_qti.itemBody

        choice_interaction = item_body.choiceInteraction.extract()

        expected_string = """<itemBody>
<p>
   Did you eat breakfast today?
  </p>

</itemBody>"""

        self.assertEqual(
            str(item_body),
            expected_string
        )

        self.assertEqual(
            len(choice_interaction.find_all('simpleChoice')),
            3
        )
        self.assertEqual(
            choice_interaction['maxChoices'],
            "0"
        )
        self.assertEqual(
            choice_interaction['responseIdentifier'],
            'RESPONSE_1'
        )
        self.assertEqual(
            choice_interaction['shuffle'],
            'true'
        )

        expected_choices = {
            "id5f1fc52a-a04e-4fa1-b855-51da24967a31": """<simpleChoice identifier="id5f1fc52a-a04e-4fa1-b855-51da24967a31">
<p>
     Yes
    </p>
</simpleChoice>""",
            "id31392307-c87e-476b-8f92-b0f12ed66300": """<simpleChoice identifier="id31392307-c87e-476b-8f92-b0f12ed66300">
<p>
     No
    </p>
</simpleChoice>""",
            "id8188b5cd-89b0-4140-b12a-aed5426bd81b": """<simpleChoice identifier="id8188b5cd-89b0-4140-b12a-aed5426bd81b">
<p>
     I don\'t remember
    </p>
</simpleChoice>"""
        }

        for choice in choice_interaction.find_all('simpleChoice'):
            choice_id = choice['identifier']
            self.assertEqual(
                str(choice),
                expected_choices[choice_id]
            )

    def test_can_add_question_to_existing_reflection_multi_answer_item_via_rest(self):
        url = '{0}/items'.format(self.url)
        payload = {
            "genusTypeId": str(QTI_ITEM_CHOICE_INTERACTION_MULTI_SELECT_SURVEY_GENUS),
            "name": "Question 1",
            "description": "For testing"
        }

        req = self.app.post(url,
                            params=json.dumps(payload),
                            headers={'content-type': 'application/json'})
        self.ok(req)
        item = self.json(req)

        url = '{0}/items/{1}'.format(self.url, item['id'])
        payload = {
            "question": {
                "questionString": """<itemBody >
<p>Did you eat breakfast today?</p>
</itemBody>""",
                "choices": [{
                    "id": "id5f1fc52a-a04e-4fa1-b855-51da24967a31",
                    "text": """<simpleChoice identifier="id5f1fc52a-a04e-4fa1-b855-51da24967a31">
<p>Yes</p>
</simpleChoice>"""
                }, {
                    "id": "id31392307-c87e-476b-8f92-b0f12ed66300",
                    "text": """<simpleChoice identifier="id31392307-c87e-476b-8f92-b0f12ed66300">
<p>No</p>
</simpleChoice>"""
                }, {
                    "id": "id8188b5cd-89b0-4140-b12a-aed5426bd81b",
                    "text": """<simpleChoice identifier="id8188b5cd-89b0-4140-b12a-aed5426bd81b">
<p>I don't remember</p>
</simpleChoice>"""
                }],
                "genusTypeId": str(QTI_QUESTION_CHOICE_INTERACTION_MULTI_SELECT_SURVEY_GENUS),
                "shuffle": True
            },
            "answers": [{
                "genusTypeId": str(RIGHT_ANSWER_GENUS),
                "choiceIds": ["id5f1fc52a-a04e-4fa1-b855-51da24967a31"],
                "feedback": """<modalFeedback  identifier="Feedback1359458626" outcomeIdentifier="FEEDBACKMODAL" showHide="show">
<p>Thank you for your participation.</p>
</modalFeedback>"""
            }, {
                "genusTypeId": str(RIGHT_ANSWER_GENUS),
                "choiceIds": ["id31392307-c87e-476b-8f92-b0f12ed66300"],
                "feedback": """<modalFeedback  identifier="Feedback1359458626" outcomeIdentifier="FEEDBACKMODAL" showHide="show">
<p>Thank you for your participation.</p>
</modalFeedback>"""
            }, {
                "genusTypeId": str(RIGHT_ANSWER_GENUS),
                "choiceIds": ["id8188b5cd-89b0-4140-b12a-aed5426bd81b"],
                "feedback": """<modalFeedback  identifier="Feedback1359458626" outcomeIdentifier="FEEDBACKMODAL" showHide="show">
<p>Thank you for your participation.</p>
</modalFeedback>"""
            }]
        }
        req = self.app.put(url,
                           params=json.dumps(payload),
                           headers={'content-type': 'application/json'})
        self.ok(req)
        item = self.json(req)

        self.assertEqual(
            item['genusTypeId'],
            str(QTI_ITEM_CHOICE_INTERACTION_MULTI_SELECT_SURVEY_GENUS)
        )

        self.assertEqual(
            item['question']['genusTypeId'],
            str(QTI_QUESTION_CHOICE_INTERACTION_MULTI_SELECT_SURVEY_GENUS)
        )
        self.assertEqual(
            len(item['question']['choices']),
            3
        )
        choice_ids = [c['id'] for c in item['question']['choices']]

        self.assertEqual(
            len(item['answers']),
            3
        )
        for answer in item['answers']:
            self.assertEqual(
                answer['genusTypeId'],
                str(RIGHT_ANSWER_GENUS)
            )
            self.assertIn('Thank you for your participation.', answer['feedbacks'][0]['text'])
            self.assertIn(answer['choiceIds'][0], choice_ids)

        self.assertNotEqual(
            item['id'],
            str(self._item.ident)
        )

        url = '{0}/{1}/qti'.format(url, unquote(item['id']))
        req = self.app.get(url)
        self.ok(req)
        item_qti = BeautifulSoup(req.body, 'lxml-xml').assessmentItem
        item_body = item_qti.itemBody

        choice_interaction = item_body.choiceInteraction.extract()

        expected_string = """<itemBody>
<p>
   Did you eat breakfast today?
  </p>

</itemBody>"""

        self.assertEqual(
            str(item_body),
            expected_string
        )

        self.assertEqual(
            len(choice_interaction.find_all('simpleChoice')),
            3
        )
        self.assertEqual(
            choice_interaction['maxChoices'],
            "0"
        )
        self.assertEqual(
            choice_interaction['responseIdentifier'],
            'RESPONSE_1'
        )
        self.assertEqual(
            choice_interaction['shuffle'],
            'true'
        )

        expected_choices = {
            "id5f1fc52a-a04e-4fa1-b855-51da24967a31": """<simpleChoice identifier="id5f1fc52a-a04e-4fa1-b855-51da24967a31">
<p>
     Yes
    </p>
</simpleChoice>""",
            "id31392307-c87e-476b-8f92-b0f12ed66300": """<simpleChoice identifier="id31392307-c87e-476b-8f92-b0f12ed66300">
<p>
     No
    </p>
</simpleChoice>""",
            "id8188b5cd-89b0-4140-b12a-aed5426bd81b": """<simpleChoice identifier="id8188b5cd-89b0-4140-b12a-aed5426bd81b">
<p>
     I don\'t remember
    </p>
</simpleChoice>"""
        }

        for choice in choice_interaction.find_all('simpleChoice'):
            choice_id = choice['identifier']
            self.assertEqual(
                str(choice),
                expected_choices[choice_id]
            )

    def test_can_get_reflection_multi_answer_item_with_no_choices(self):
        url = '{0}/items'.format(self.url)
        payload = {
            "genusTypeId": str(QTI_ITEM_CHOICE_INTERACTION_MULTI_SELECT_SURVEY_GENUS),
            "name": "Question 1",
            "description": "For testing",

            "question": {
                "questionString": """<itemBody >
<p>Did you eat breakfast today?</p>
</itemBody>"""}
        }

        req = self.app.post(url,
                            params=json.dumps(payload),
                            headers={'content-type': 'application/json'})
        self.ok(req)
        item = self.json(req)

        url = '{0}/items/{1}'.format(self.url, item['id'])
        req = self.app.get(url)
        self.ok(req)
        data = self.json(req)
        self.assertEqual(data['question']['choices'], [])

    def test_can_get_reflection_multi_answer_item_qti_with_no_answers(self):
        url = '{0}/items'.format(self.url)
        payload = {
            "genusTypeId": str(QTI_ITEM_CHOICE_INTERACTION_MULTI_SELECT_SURVEY_GENUS),
            "name": "Question 1",
            "description": "For testing",

            "question": {
                "questionString": """<itemBody >
<p>Did you eat breakfast today?</p>
</itemBody>"""}
        }

        req = self.app.post(url,
                            params=json.dumps(payload),
                            headers={'content-type': 'application/json'})
        self.ok(req)
        item = self.json(req)

        url = '{0}/items/{1}/qti'.format(self.url, item['id'])
        req = self.app.get(url)
        self.ok(req)
        qti = BeautifulSoup(req.body, 'xml')
        self.assertIsNone(qti.responseDeclaration)

    def test_getting_qti_for_reflection_multi_answer_item_with_no_question_returns_empty_string(self):
        url = '{0}/items'.format(self.url)
        payload = {
            "genusTypeId": str(QTI_ITEM_CHOICE_INTERACTION_MULTI_SELECT_SURVEY_GENUS),
            "name": "Question 1",
            "description": "For testing"
        }

        req = self.app.post(url,
                            params=json.dumps(payload),
                            headers={'content-type': 'application/json'})
        self.ok(req)
        item = self.json(req)

        url = '{0}/{1}/qti'.format(url, unquote(item['id']))
        req = self.app.get(url)
        self.ok(req)
        self.assertEqual(req.body, '')

    def test_updating_reflection_multi_answer_answers_clears_existing_choices(self):
        url = '{0}/items'.format(self.url)
        payload = {
            "genusTypeId": str(QTI_ITEM_CHOICE_INTERACTION_MULTI_SELECT_SURVEY_GENUS),
            "name": "Question 1",
            "description": "For testing",
            "question": {
                "questionString": """<itemBody >
<p>Did you eat breakfast today?</p>
</itemBody>""",
                "choices": [{
                    "id": "id5f1fc52a-a04e-4fa1-b855-51da24967a31",
                    "text": """<simpleChoice identifier="id5f1fc52a-a04e-4fa1-b855-51da24967a31">
<p>Yes</p>
</simpleChoice>"""
                }, {
                    "id": "id31392307-c87e-476b-8f92-b0f12ed66300",
                    "text": """<simpleChoice identifier="id31392307-c87e-476b-8f92-b0f12ed66300">
<p>No</p>
</simpleChoice>"""
                }, {
                    "id": "id8188b5cd-89b0-4140-b12a-aed5426bd81b",
                    "text": """<simpleChoice identifier="id8188b5cd-89b0-4140-b12a-aed5426bd81b">
<p>I don't remember</p>
</simpleChoice>"""
                }],
                "genusTypeId": str(QTI_QUESTION_CHOICE_INTERACTION_MULTI_SELECT_SURVEY_GENUS),
                "shuffle": True
            },
            "answers": [{
                "genusTypeId": str(RIGHT_ANSWER_GENUS),
                "choiceIds": ["id5f1fc52a-a04e-4fa1-b855-51da24967a31"],
                "feedback": """<modalFeedback  identifier="Feedback1359458626" outcomeIdentifier="FEEDBACKMODAL" showHide="show">
<p>Thank you for your participation.</p>
</modalFeedback>"""
            }, {
                "genusTypeId": str(RIGHT_ANSWER_GENUS),
                "choiceIds": ["id31392307-c87e-476b-8f92-b0f12ed66300"],
                "feedback": """<modalFeedback  identifier="Feedback1359458626" outcomeIdentifier="FEEDBACKMODAL" showHide="show">
<p>Thank you for your participation.</p>
</modalFeedback>"""
            }, {
                "genusTypeId": str(RIGHT_ANSWER_GENUS),
                "choiceIds": ["id8188b5cd-89b0-4140-b12a-aed5426bd81b"],
                "feedback": """<modalFeedback  identifier="Feedback1359458626" outcomeIdentifier="FEEDBACKMODAL" showHide="show">
<p>Thank you for your participation.</p>
</modalFeedback>"""
            }]
        }
        req = self.app.post(url,
                            params=json.dumps(payload),
                            headers={'content-type': 'application/json'})
        self.ok(req)
        item = self.json(req)

        right_answer = [a for a in item['answers'] if a['genusTypeId'] == str(RIGHT_ANSWER_GENUS)][0]
        previous_right_answer_choice = right_answer['choiceIds'][0]
        new_right_answer_choice = 'foo'

        self.assertNotEqual(previous_right_answer_choice,
                            new_right_answer_choice)

        url = '{0}/{1}'.format(url, item['id'])
        payload = {
            'answers': [{
                'id': right_answer['id'],
                'choiceIds': [new_right_answer_choice]
            }]
        }
        req = self.app.put(url,
                           params=json.dumps(payload),
                           headers={'content-type': 'application/json'})
        self.ok(req)
        data = self.json(req)
        self.assertEqual(data['id'], item['id'])
        self.assertEqual(data['answers'][0]['id'], right_answer['id'])
        self.assertEqual(data['answers'][0]['genusTypeId'], str(RIGHT_ANSWER_GENUS))
        self.assertNotIn(previous_right_answer_choice, data['answers'][0]['choiceIds'])
        self.assertIn(new_right_answer_choice, data['answers'][0]['choiceIds'])
        self.assertEqual(len(data['answers'][0]['choiceIds']), 1)

    def test_can_create_audio_record_tool_question_via_rest(self):
        media_files = [self._audio_test_file]

        assets = {}
        for media_file in media_files:
            label = self._label(self._filename(media_file))
            assets[label] = self.upload_media_file(media_file)

        url = '{0}/items'.format(self.url)
        payload = {
            "genusTypeId": str(QTI_ITEM_UPLOAD_INTERACTION_AUDIO_GENUS),
            "name": "Question 1",
            "description": "For testing",
            "question": {
                "questionString": """<itemBody >
<p>
<audio autoplay="autoplay" controls="controls" style="width: 125px">
<source src="AssetContent:audioTestFile__mp3" type="audio/mpeg"/>
</audio></p>
<p>
  <strong>Introducting a new student</strong>
</p>
<p>It's the first day of school after the summer vacations. A new student has joined the class</p>
<p>Student 1 talks to the new student to make him/her feel comfortable.</p>
<p>Student 2 talks about herself or himself and asks a few questions about the new school</p>
</itemBody>""",
                "genusTypeId": str(QTI_QUESTION_UPLOAD_INTERACTION_AUDIO_GENUS),
                "fileIds": {},
                "timeValue": {
                    "hours": 0,
                    "minutes": 0,
                    "seconds": 100
                }
            },
            "answers": [{
                "genusTypeId": str(RIGHT_ANSWER_GENUS),
                "feedback": """<modalFeedback  identifier="Feedback" outcomeIdentifier="FEEDBACKMODAL" showHide="show">
<p></p>
</modalFeedback>"""
            }]
        }

        for label, asset in assets.iteritems():
            payload['question']['fileIds'][label] = {}
            payload['question']['fileIds'][label]['assetId'] = asset['id']
            payload['question']['fileIds'][label]['assetContentId'] = asset['assetContents'][0]['id']
            payload['question']['fileIds'][label]['assetContentTypeId'] = asset['assetContents'][0]['genusTypeId']

        req = self.app.post(url,
                            params=json.dumps(payload),
                            headers={'content-type': 'application/json'})
        self.ok(req)
        item = self.json(req)

        self.assertEqual(
            item['genusTypeId'],
            str(QTI_ITEM_UPLOAD_INTERACTION_AUDIO_GENUS)
        )

        self.assertEqual(
            item['question']['genusTypeId'],
            str(QTI_QUESTION_UPLOAD_INTERACTION_AUDIO_GENUS)
        )

        self.assertEqual(
            item['answers'][0]['genusTypeId'],
            str(RIGHT_ANSWER_GENUS)
        )

        self.assertEqual(
            item['answers'][0]['feedbacks'][0]['text'],
            '<modalFeedback  identifier="Feedback" outcomeIdentifier="FEEDBACKMODAL" showHide="show">\n<p></p>\n</modalFeedback>'
        )

        self.assertNotEqual(
            item['id'],
            str(self._item.ident)
        )

        self.assertIn(
            'timeValue',
            item['question']
        )

        self.assertEqual(
            item['question']['timeValue'],
            {'hours': '00', 'minutes': '01', 'seconds': '40'}
        )

        item_qti_url = '{0}/{1}/qti'.format(url, item['id'])
        req = self.app.get(item_qti_url)
        self.ok(req)
        qti_xml = BeautifulSoup(req.body, 'lxml-xml').assessmentItem
        item_body = qti_xml.itemBody

        audio_asset_label = 'audioTestFile__mp3'
        audio_asset_id = item['question']['fileIds'][audio_asset_label]['assetId']
        audio_asset_content_id = item['question']['fileIds'][audio_asset_label]['assetContentId']

        expected_string = """<itemBody>
<p>
<audio autoplay="autoplay" controls="controls" style="width: 125px">
<source src="/api/v1/repository/repositories/{0}/assets/{1}/contents/{2}/stream" type="audio/mpeg"/>
</audio>
</p>
<p>
<strong>
    Introducting a new student
   </strong>
</p>
<p>
   It's the first day of school after the summer vacations. A new student has joined the class
  </p>
<p>
   Student 1 talks to the new student to make him/her feel comfortable.
  </p>
<p>
   Student 2 talks about herself or himself and asks a few questions about the new school
  </p>
<uploadInteraction responseIdentifier="RESPONSE_1"/>
</itemBody>""".format(str(self._bank.ident).replace('assessment.Bank', 'repository.Repository'),
                      audio_asset_id,
                      audio_asset_content_id)

        self.assertEqual(
            str(item_body),
            expected_string
        )

    def test_can_add_question_to_existing_audio_record_tool_item_via_rest(self):
        url = '{0}/items'.format(self.url)
        payload = {
            "genusTypeId": str(QTI_ITEM_UPLOAD_INTERACTION_AUDIO_GENUS),
            "name": "Question 1",
            "description": "For testing"
        }

        req = self.app.post(url,
                            params=json.dumps(payload),
                            headers={'content-type': 'application/json'})
        self.ok(req)
        item = self.json(req)

        media_files = [self._audio_test_file]

        assets = {}
        for media_file in media_files:
            label = self._label(self._filename(media_file))
            assets[label] = self.upload_media_file(media_file)

        url = '{0}/items/{1}'.format(self.url, item['id'])
        payload = {
            "question": {
                "questionString": """<itemBody >
<p>
<audio autoplay="autoplay" controls="controls" style="width: 125px">
<source src="AssetContent:audioTestFile__mp3" type="audio/mpeg"/>
</audio></p>
<p>
  <strong>Introducting a new student</strong>
</p>
<p>It's the first day of school after the summer vacations. A new student has joined the class</p>
<p>Student 1 talks to the new student to make him/her feel comfortable.</p>
<p>Student 2 talks about herself or himself and asks a few questions about the new school</p>
</itemBody>""",
                "genusTypeId": str(QTI_QUESTION_UPLOAD_INTERACTION_AUDIO_GENUS),
                "fileIds": {},
                "timeValue": {
                    "hours": 0,
                    "minutes": 0,
                    "seconds": 100
                }
            },
            "answers": [{
                "genusTypeId": str(RIGHT_ANSWER_GENUS),
                "feedback": """<modalFeedback  identifier="Feedback" outcomeIdentifier="FEEDBACKMODAL" showHide="show">
<p></p>
</modalFeedback>"""
            }]
        }

        for label, asset in assets.iteritems():
            payload['question']['fileIds'][label] = {}
            payload['question']['fileIds'][label]['assetId'] = asset['id']
            payload['question']['fileIds'][label]['assetContentId'] = asset['assetContents'][0]['id']
            payload['question']['fileIds'][label]['assetContentTypeId'] = asset['assetContents'][0]['genusTypeId']

        req = self.app.put(url,
                           params=json.dumps(payload),
                           headers={'content-type': 'application/json'})
        self.ok(req)
        item = self.json(req)

        self.assertEqual(
            item['genusTypeId'],
            str(QTI_ITEM_UPLOAD_INTERACTION_AUDIO_GENUS)
        )

        self.assertEqual(
            item['question']['genusTypeId'],
            str(QTI_QUESTION_UPLOAD_INTERACTION_AUDIO_GENUS)
        )

        self.assertEqual(
            item['answers'][0]['genusTypeId'],
            str(RIGHT_ANSWER_GENUS)
        )

        self.assertEqual(
            item['answers'][0]['feedbacks'][0]['text'],
            '<modalFeedback  identifier="Feedback" outcomeIdentifier="FEEDBACKMODAL" showHide="show">\n<p></p>\n</modalFeedback>'
        )

        self.assertNotEqual(
            item['id'],
            str(self._item.ident)
        )

        self.assertIn(
            'timeValue',
            item['question']
        )

        self.assertEqual(
            item['question']['timeValue'],
            {'hours': '00', 'minutes': '01', 'seconds': '40'}
        )

        item_qti_url = '{0}/{1}/qti'.format(url, item['id'])
        req = self.app.get(item_qti_url)
        self.ok(req)
        qti_xml = BeautifulSoup(req.body, 'lxml-xml').assessmentItem
        item_body = qti_xml.itemBody

        audio_asset_label = 'audioTestFile__mp3'
        audio_asset_id = item['question']['fileIds'][audio_asset_label]['assetId']
        audio_asset_content_id = item['question']['fileIds'][audio_asset_label]['assetContentId']

        expected_string = """<itemBody>
<p>
<audio autoplay="autoplay" controls="controls" style="width: 125px">
<source src="/api/v1/repository/repositories/{0}/assets/{1}/contents/{2}/stream" type="audio/mpeg"/>
</audio>
</p>
<p>
<strong>
    Introducting a new student
   </strong>
</p>
<p>
   It's the first day of school after the summer vacations. A new student has joined the class
  </p>
<p>
   Student 1 talks to the new student to make him/her feel comfortable.
  </p>
<p>
   Student 2 talks about herself or himself and asks a few questions about the new school
  </p>
<uploadInteraction responseIdentifier="RESPONSE_1"/>
</itemBody>""".format(str(self._bank.ident).replace('assessment.Bank', 'repository.Repository'),
                      audio_asset_id,
                      audio_asset_content_id)

        self.assertEqual(
            str(item_body),
            expected_string
        )

        expected_json_string = """<itemBody>
<p>
<audio autoplay="autoplay" controls="controls" style="width: 125px">
<source src="/api/v1/repository/repositories/{0}/assets/{1}/contents/{2}/stream" type="audio/mpeg"/>
</audio></p>
<p>
<strong>Introducting a new student</strong>
</p>
<p>It's the first day of school after the summer vacations. A new student has joined the class</p>
<p>Student 1 talks to the new student to make him/her feel comfortable.</p>
<p>Student 2 talks about herself or himself and asks a few questions about the new school</p>
</itemBody>""".format(str(self._bank.ident).replace('assessment.Bank', 'repository.Repository'),
                      audio_asset_id,
                      audio_asset_content_id)

        self.assertEqual(
            item['question']['text']['text'],
            expected_json_string
        )

    def test_can_get_audio_record_tool_item_qti_with_no_answers(self):
        url = '{0}/items'.format(self.url)
        payload = {
            "genusTypeId": str(QTI_ITEM_UPLOAD_INTERACTION_AUDIO_GENUS),
            "name": "Question 1",
            "description": "For testing",
            "question": {
                "questionString": """<itemBody >
<p>
<audio autoplay="autoplay" controls="controls" style="width: 125px">
<source src="AssetContent:audioTestFile__mp3" type="audio/mpeg"/>
</audio></p>
<p>
  <strong>Introducting a new student</strong>
</p>
<p>It's the first day of school after the summer vacations. A new student has joined the class</p>
<p>Student 1 talks to the new student to make him/her feel comfortable.</p>
<p>Student 2 talks about herself or himself and asks a few questions about the new school</p>
</itemBody>"""}
        }

        req = self.app.post(url,
                            params=json.dumps(payload),
                            headers={'content-type': 'application/json'})
        self.ok(req)
        item = self.json(req)

        item_qti_url = '{0}/{1}/qti'.format(url, item['id'])
        req = self.app.get(item_qti_url)
        self.ok(req)
        qti = BeautifulSoup(req.body, 'xml')
        self.assertIsNone(qti.responseDeclaration)

    def test_getting_qti_for_audio_record_tool_item_with_no_question_returns_empty_string(self):
        url = '{0}/items'.format(self.url)
        payload = {
            "genusTypeId": str(QTI_ITEM_UPLOAD_INTERACTION_AUDIO_GENUS),
            "name": "Question 1",
            "description": "For testing"
        }

        req = self.app.post(url,
                            params=json.dumps(payload),
                            headers={'content-type': 'application/json'})
        self.ok(req)
        item = self.json(req)

        item_qti_url = '{0}/{1}/qti'.format(url, item['id'])
        req = self.app.get(item_qti_url)
        self.ok(req)
        self.assertEqual(req.body, '')

    def test_item_body_provided_audio_upload(self):
        media_files = [self._audio_test_file]

        assets = {}
        for media_file in media_files:
            label = self._label(self._filename(media_file))
            assets[label] = self.upload_media_file(media_file)

        url = '{0}/items'.format(self.url)
        payload = {
            "genusTypeId": str(QTI_ITEM_UPLOAD_INTERACTION_AUDIO_GENUS),
            "name": "Question 1",
            "description": "For testing",
            "question": {
                "questionString": """<p>
<audio autoplay="autoplay" controls="controls" style="width: 125px">
<source src="AssetContent:audioTestFile__mp3" type="audio/mpeg"/>
</audio></p>
<p>
  <strong>Introducting a new student</strong>
</p>
<p>It's the first day of school after the summer vacations. A new student has joined the class</p>
<p>Student 1 talks to the new student to make him/her feel comfortable.</p>
<p>Student 2 talks about herself or himself and asks a few questions about the new school</p>""",
                "genusTypeId": str(QTI_QUESTION_UPLOAD_INTERACTION_AUDIO_GENUS),
                "fileIds": {}
            },
            "answers": [{
                "genusTypeId": str(RIGHT_ANSWER_GENUS),
                "feedback": """<modalFeedback  identifier="Feedback" outcomeIdentifier="FEEDBACKMODAL" showHide="show">
<p></p>
</modalFeedback>"""
            }]
        }

        for label, asset in assets.iteritems():
            payload['question']['fileIds'][label] = {}
            payload['question']['fileIds'][label]['assetId'] = asset['id']
            payload['question']['fileIds'][label]['assetContentId'] = asset['assetContents'][0]['id']
            payload['question']['fileIds'][label]['assetContentTypeId'] = asset['assetContents'][0]['genusTypeId']

        req = self.app.post(url,
                            params=json.dumps(payload),
                            headers={'content-type': 'application/json'})
        self.ok(req)
        item = self.json(req)

        self.assertEqual(
            item['genusTypeId'],
            str(QTI_ITEM_UPLOAD_INTERACTION_AUDIO_GENUS)
        )

        self.assertEqual(
            item['question']['genusTypeId'],
            str(QTI_QUESTION_UPLOAD_INTERACTION_AUDIO_GENUS)
        )

        self.assertEqual(
            item['answers'][0]['genusTypeId'],
            str(RIGHT_ANSWER_GENUS)
        )

        self.assertEqual(
            item['answers'][0]['feedbacks'][0]['text'],
            '<modalFeedback  identifier="Feedback" outcomeIdentifier="FEEDBACKMODAL" showHide="show">\n<p></p>\n</modalFeedback>'
        )

        self.assertNotEqual(
            item['id'],
            str(self._item.ident)
        )

        item_qti_url = '{0}/{1}/qti'.format(url, item['id'])
        req = self.app.get(item_qti_url)
        self.ok(req)
        qti_xml = BeautifulSoup(req.body, 'lxml-xml').assessmentItem
        item_body = qti_xml.itemBody

        audio_asset_label = 'audioTestFile__mp3'
        audio_asset_id = item['question']['fileIds'][audio_asset_label]['assetId']
        audio_asset_content_id = item['question']['fileIds'][audio_asset_label]['assetContentId']

        expected_string = """<itemBody>
<p>
<audio autoplay="autoplay" controls="controls" style="width: 125px">
<source src="/api/v1/repository/repositories/{0}/assets/{1}/contents/{2}/stream" type="audio/mpeg"/>
</audio>
</p>
<p>
<strong>
    Introducting a new student
   </strong>
</p>
<p>
   It's the first day of school after the summer vacations. A new student has joined the class
  </p>
<p>
   Student 1 talks to the new student to make him/her feel comfortable.
  </p>
<p>
   Student 2 talks about herself or himself and asks a few questions about the new school
  </p>
<uploadInteraction responseIdentifier="RESPONSE_1"/>
</itemBody>""".format(str(self._bank.ident).replace('assessment.Bank', 'repository.Repository'),
                      audio_asset_id,
                      audio_asset_content_id)

        self.assertEqual(
            str(item_body),
            expected_string
        )

    def test_can_create_generic_file_upload_question_via_rest(self):
        url = '{0}/items'.format(self.url)
        payload = {
            "genusTypeId": str(QTI_ITEM_UPLOAD_INTERACTION_GENERIC_GENUS),
            "name": "Question 1",
            "description": "For testing",
            "question": {
                "questionString": """<itemBody>
<p>
<strong>
<span id="docs-internal-guid-46f83555-04c5-4e80-4138-8ed0f8d56345">
     Construct a rhombus of side 200 using Turtle Blocks. Save the shape you draw, and upload it here.
    </span>
<br/>
</strong>
</p>
</itemBody>""",
                "genusTypeId": str(QTI_QUESTION_UPLOAD_INTERACTION_GENERIC_GENUS)
            },
            "answers": [{
                "genusTypeId": str(RIGHT_ANSWER_GENUS),
                "feedback": """<modalFeedback identifier="Feedback464983843" outcomeIdentifier="FEEDBACKMODAL" showHide="show">
<p><strong><span id="docs-internal-guid-46f83555-04c5-8000-2639-b910cd8704bf">Upload successful!</span><br/></strong></p>
</modalFeedback>"""
            }]
        }

        req = self.app.post(url,
                            params=json.dumps(payload),
                            headers={'content-type': 'application/json'})
        self.ok(req)
        item = self.json(req)

        self.assertEqual(
            item['genusTypeId'],
            str(QTI_ITEM_UPLOAD_INTERACTION_GENERIC_GENUS)
        )

        self.assertEqual(
            item['question']['genusTypeId'],
            str(QTI_QUESTION_UPLOAD_INTERACTION_GENERIC_GENUS)
        )

        self.assertEqual(
            item['answers'][0]['genusTypeId'],
            str(RIGHT_ANSWER_GENUS)
        )

        self.assertEqual(
            item['answers'][0]['feedbacks'][0]['text'],
            """<modalFeedback identifier="Feedback464983843" outcomeIdentifier="FEEDBACKMODAL" showHide="show">
<p><strong><span id="docs-internal-guid-46f83555-04c5-8000-2639-b910cd8704bf">Upload successful!</span><br/></strong></p>
</modalFeedback>"""
        )

        self.assertNotEqual(
            item['id'],
            str(self._item.ident)
        )

        item_qti_url = '{0}/{1}/qti'.format(url, item['id'])
        req = self.app.get(item_qti_url)
        self.ok(req)
        qti_xml = BeautifulSoup(req.body, 'lxml-xml').assessmentItem
        item_body = qti_xml.itemBody

        expected_string = """<itemBody>
<p>
<strong>
<span id="docs-internal-guid-46f83555-04c5-4e80-4138-8ed0f8d56345">
     Construct a rhombus of side 200 using Turtle Blocks. Save the shape you draw, and upload it here.
    </span>
<br/>
</strong>
</p>
<uploadInteraction responseIdentifier="RESPONSE_1"/>
</itemBody>"""

        self.assertEqual(
            str(item_body),
            expected_string
        )

    def test_can_add_question_to_existing_generic_file_upload_item_via_rest(self):
        url = '{0}/items'.format(self.url)
        payload = {
            "genusTypeId": str(QTI_ITEM_UPLOAD_INTERACTION_GENERIC_GENUS),
            "name": "Question 1",
            "description": "For testing"
        }

        req = self.app.post(url,
                            params=json.dumps(payload),
                            headers={'content-type': 'application/json'})
        self.ok(req)
        item = self.json(req)

        url = '{0}/items/{1}'.format(self.url, item['id'])

        payload = {
            "question": {
                "questionString": """<itemBody>
<p>
<strong>
<span id="docs-internal-guid-46f83555-04c5-4e80-4138-8ed0f8d56345">
     Construct a rhombus of side 200 using Turtle Blocks. Save the shape you draw, and upload it here.
    </span>
<br/>
</strong>
</p>
</itemBody>""",
                "genusTypeId": str(QTI_QUESTION_UPLOAD_INTERACTION_GENERIC_GENUS)
            },
            "answers": [{
                "genusTypeId": str(RIGHT_ANSWER_GENUS),
                "feedback": """<modalFeedback identifier="Feedback464983843" outcomeIdentifier="FEEDBACKMODAL" showHide="show">
<p><strong><span id="docs-internal-guid-46f83555-04c5-8000-2639-b910cd8704bf">Upload successful!</span><br/></strong></p>
</modalFeedback>"""
            }]
        }

        req = self.app.put(url,
                           params=json.dumps(payload),
                           headers={'content-type': 'application/json'})
        self.ok(req)
        item = self.json(req)

        self.assertEqual(
            item['genusTypeId'],
            str(QTI_ITEM_UPLOAD_INTERACTION_GENERIC_GENUS)
        )

        self.assertEqual(
            item['question']['genusTypeId'],
            str(QTI_QUESTION_UPLOAD_INTERACTION_GENERIC_GENUS)
        )

        self.assertEqual(
            item['answers'][0]['genusTypeId'],
            str(RIGHT_ANSWER_GENUS)
        )

        self.assertEqual(
            item['answers'][0]['feedbacks'][0]['text'],
            """<modalFeedback identifier="Feedback464983843" outcomeIdentifier="FEEDBACKMODAL" showHide="show">
<p><strong><span id="docs-internal-guid-46f83555-04c5-8000-2639-b910cd8704bf">Upload successful!</span><br/></strong></p>
</modalFeedback>"""
        )

        self.assertNotEqual(
            item['id'],
            str(self._item.ident)
        )

        item_qti_url = '{0}/{1}/qti'.format(url, item['id'])
        req = self.app.get(item_qti_url)
        self.ok(req)
        qti_xml = BeautifulSoup(req.body, 'lxml-xml').assessmentItem
        item_body = qti_xml.itemBody

        expected_string = """<itemBody>
<p>
<strong>
<span id="docs-internal-guid-46f83555-04c5-4e80-4138-8ed0f8d56345">
     Construct a rhombus of side 200 using Turtle Blocks. Save the shape you draw, and upload it here.
    </span>
<br/>
</strong>
</p>
<uploadInteraction responseIdentifier="RESPONSE_1"/>
</itemBody>"""

        self.assertEqual(
            str(item_body),
            expected_string
        )

    def test_can_get_generic_file_upload_item_qti_with_no_answers(self):
        url = '{0}/items'.format(self.url)
        payload = {
            "genusTypeId": str(QTI_ITEM_UPLOAD_INTERACTION_GENERIC_GENUS),
            "name": "Question 1",
            "description": "For testing",
            "question": {
                "questionString": """<itemBody>
<p>
<strong>
<span id="docs-internal-guid-46f83555-04c5-4e80-4138-8ed0f8d56345">
     Construct a rhombus of side 200 using Turtle Blocks. Save the shape you draw, and upload it here.
    </span>
<br/>
</strong>
</p>
</itemBody>"""}
        }

        req = self.app.post(url,
                            params=json.dumps(payload),
                            headers={'content-type': 'application/json'})
        self.ok(req)
        item = self.json(req)

        url = '{0}/items/{1}/qti'.format(self.url, item['id'])
        req = self.app.get(url)
        self.ok(req)
        qti = BeautifulSoup(req.body, 'xml')
        self.assertIsNone(qti.responseDeclaration)

    def test_getting_qti_for_generic_file_upload_with_no_question_returns_empty_string(self):
        url = '{0}/items'.format(self.url)
        payload = {
            "genusTypeId": str(QTI_ITEM_UPLOAD_INTERACTION_GENERIC_GENUS),
            "name": "Question 1",
            "description": "For testing"
        }

        req = self.app.post(url,
                            params=json.dumps(payload),
                            headers={'content-type': 'application/json'})
        self.ok(req)
        item = self.json(req)

        item_qti_url = '{0}/{1}/qti'.format(url, item['id'])
        req = self.app.get(item_qti_url)
        self.ok(req)
        self.assertEqual(req.body, '')

    def test_can_create_mw_sentence_question_via_rest(self):
        media_files = [self._intersection_image,
                       self._mw_sentence_audio_file]

        assets = {}
        for media_file in media_files:
            label = self._label(self._filename(media_file))
            assets[label] = self.upload_media_file(media_file)

        url = '{0}/items'.format(self.url)

        payload = {
            "genusTypeId": str(QTI_ITEM_ORDER_INTERACTION_MW_SENTENCE_GENUS),
            "name": "Question 1",
            "description": "For testing",
            "question": {
                "questionString": """<itemBody>
<p>
   Where are Raju's bags?
  </p>
<p>
</p>
<p>
<audio autoplay="autoplay" controls="controls" style="width: 125px">
<source src="AssetContent:ee_u1l01a01r05__mp3" type="audio/mpeg"/>
</audio>
</p>
<p>
<img alt="This is a drawing of a busy intersection." height="100" src="AssetContent:intersection_png" width="100"/>
</p>

</itemBody>""",
                "choices": [{
                    "id": "id51b2feca-d407-46d5-b548-d6645a021008",
                    "text": """<simpleChoice identifier="id51b2feca-d407-46d5-b548-d6645a021008">
<p class=\"noun\">Raju</p>
</simpleChoice>"""
                }, {
                    "id": "id881a8e9c-844b-4394-be62-d28a5fda5296",
                    "text": """<simpleChoice identifier="id881a8e9c-844b-4394-be62-d28a5fda5296">
<p class=\"verb\">left</p>
</simpleChoice>"""
                }, {
                    "id": "idcccac9f8-3b85-4a2f-a95c-1922dec5d04a",
                    "text": """<simpleChoice identifier="idcccac9f8-3b85-4a2f-a95c-1922dec5d04a">
<p class=\"noun\">the bags</p>
</simpleChoice>"""
                }, {
                    "id": "id28a924d9-32ac-4ac5-a4b2-1b1cfe2caba0",
                    "text": """<simpleChoice identifier="id28a924d9-32ac-4ac5-a4b2-1b1cfe2caba0">
<p class=\"adverb\">under</p>
</simpleChoice>"""
                }, {
                    "id": "id78ce22bf-559f-44a4-95ee-156f222ad510",
                    "text": """<simpleChoice identifier="id78ce22bf-559f-44a4-95ee-156f222ad510">
<p class=\"noun\">the seat</p>
</simpleChoice>"""
                }, {
                    "id": "id3045d860-24b4-4b30-9ca1-72408a3bcc9b",
                    "text": """<simpleChoice identifier="id3045d860-24b4-4b30-9ca1-72408a3bcc9b">
<p class=\"prep\">on</p>
</simpleChoice>"""
                }, {
                    "id": "id2cad48be-2782-4625-9669-dfcb2062bf3c",
                    "text": """<simpleChoice identifier="id2cad48be-2782-4625-9669-dfcb2062bf3c">
<p class=\"noun\"the bus</p>
</simpleChoice>"""
                }],
                "genusTypeId": str(QTI_QUESTION_ORDER_INTERACTION_MW_SENTENCE_GENUS),
                "shuffle": True,
                "fileIds": {}
            },
            "answers": [{
                "genusTypeId": str(RIGHT_ANSWER_GENUS),
                "choiceIds": ['id51b2feca-d407-46d5-b548-d6645a021008',
                              'id881a8e9c-844b-4394-be62-d28a5fda5296',
                              'idcccac9f8-3b85-4a2f-a95c-1922dec5d04a',
                              'id28a924d9-32ac-4ac5-a4b2-1b1cfe2caba0',
                              'id78ce22bf-559f-44a4-95ee-156f222ad510',
                              'id3045d860-24b4-4b30-9ca1-72408a3bcc9b',
                              'id2cad48be-2782-4625-9669-dfcb2062bf3c'],
                "feedback": """  <modalFeedback  identifier="Feedback372632509" outcomeIdentifier="FEEDBACKMODAL" showHide="show">
<p>Correct Feedback goes here!</p>
</modalFeedback>"""
            }, {
                "genusTypeId": str(WRONG_ANSWER_GENUS),
                "choiceIds": [None],
                "feedback": """  <modalFeedback  identifier="Feedback2014412711" outcomeIdentifier="FEEDBACKMODAL" showHide="show">
<p>Wrong...Feedback goes here!</p>
</modalFeedback>"""
            }]
        }

        for label, asset in assets.iteritems():
            payload['question']['fileIds'][label] = {}
            payload['question']['fileIds'][label]['assetId'] = asset['id']
            payload['question']['fileIds'][label]['assetContentId'] = asset['assetContents'][0]['id']
            payload['question']['fileIds'][label]['assetContentTypeId'] = asset['assetContents'][0]['genusTypeId']

        req = self.app.post(url,
                            params=json.dumps(payload),
                            headers={'content-type': 'application/json'})
        self.ok(req)
        item = self.json(req)

        self.assertEqual(
            item['genusTypeId'],
            str(QTI_ITEM_ORDER_INTERACTION_MW_SENTENCE_GENUS)
        )

        self.assertEqual(
            item['question']['genusTypeId'],
            str(QTI_QUESTION_ORDER_INTERACTION_MW_SENTENCE_GENUS)
        )

        self.assertEqual(
            item['answers'][0]['genusTypeId'],
            str(RIGHT_ANSWER_GENUS)
        )

        self.assertEqual(
            len(item['answers'][0]['choiceIds']),
            7
        )
        self.assertIn('feedbacks', item['answers'][0])
        self.assertTrue(len(item['answers'][0]['feedbacks']) == 1)

        self.assertEqual(
            item['answers'][1]['genusTypeId'],
            str(WRONG_ANSWER_GENUS)
        )
        self.assertEqual(
            len(item['answers'][1]['choiceIds']),
            1
        )
        self.assertIsNone(item['answers'][1]['choiceIds'][0])
        self.assertIn('feedbacks', item['answers'][1])
        self.assertTrue(len(item['answers'][1]['feedbacks']) == 1)

        self.assertEqual(
            len(item['question']['choices']),
            7
        )

        for choice in item['question']['multiLanguageChoices']:
            self.assertTrue(len(choice['texts']) == 1)
            for text in choice['texts']:
                self.assertIn('<p class="', text['text'])
                if any(n in text['text'] for n in ['the bags', 'the bus', 'the bridge', 'Raju', 'the seat']):
                    self.assertIn('"noun"', text['text'])
                elif any(p in text['text'] for p in ['on']):
                    self.assertIn('"prep"', text['text'])
                elif 'left' in text['text']:
                    self.assertIn('"verb"', text['text'])
                elif 'under' in text['text']:
                    self.assertIn('"adverb"', text['text'])
        for choice in item['question']['choices']:
            self.assertIn('<p class="', choice['text'])
            if any(n in choice['text'] for n in ['the bags', 'the bus', 'the bridge', 'Raju', 'the seat']):
                self.assertIn('"noun"', choice['text'])
            elif any(p in choice['text'] for p in ['on']):
                self.assertIn('"prep"', choice['text'])
            elif 'left' in choice['text']:
                self.assertIn('"verb"', choice['text'])
            elif 'under' in choice['text']:
                self.assertIn('"adverb"', choice['text'])

        self.assertNotEqual(
            item['id'],
            str(self._item.ident)
        )

        item_details_url = '{0}?qti'.format(url)
        req = self.app.get(item_details_url)
        self.ok(req)
        data = self.json(req)
        item = [i for i in data if i['id'] == item['id']][0]
        self.assertIn('qti', item)
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
        image_asset_label = 'intersection_png'
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

    def test_can_add_question_to_existing_mw_sentence_item_via_rest(self):
        url = '{0}/items'.format(self.url)

        payload = {
            "genusTypeId": str(QTI_ITEM_ORDER_INTERACTION_MW_SENTENCE_GENUS),
            "name": "Question 1",
            "description": "For testing"
        }

        req = self.app.post(url,
                            params=json.dumps(payload),
                            headers={'content-type': 'application/json'})
        self.ok(req)
        item = self.json(req)

        media_files = [self._intersection_image,
                       self._mw_sentence_audio_file]

        assets = {}
        for media_file in media_files:
            label = self._label(self._filename(media_file))
            assets[label] = self.upload_media_file(media_file)

        url = '{0}/items/{1}'.format(self.url, item['id'])

        payload = {
            "question": {
                "questionString": """<itemBody>
<p>
   Where are Raju's bags?
  </p>
<p>
</p>
<p>
<audio autoplay="autoplay" controls="controls" style="width: 125px">
<source src="AssetContent:ee_u1l01a01r05__mp3" type="audio/mpeg"/>
</audio>
</p>
<p>
<img alt="This is a drawing of a busy intersection." height="100" src="AssetContent:intersection_png" width="100"/>
</p>

</itemBody>""",
                "choices": [{
                    "id": "id51b2feca-d407-46d5-b548-d6645a021008",
                    "text": u"""<simpleChoice identifier="id51b2feca-d407-46d5-b548-d6645a021008">
<p class=\"noun\">हिंदी</p>
</simpleChoice>"""
                }, {
                    "id": "id881a8e9c-844b-4394-be62-d28a5fda5296",
                    "text": """<simpleChoice identifier="id881a8e9c-844b-4394-be62-d28a5fda5296">
<p class=\"verb\">left</p>
</simpleChoice>"""
                }, {
                    "id": "idcccac9f8-3b85-4a2f-a95c-1922dec5d04a",
                    "text": """<simpleChoice identifier="idcccac9f8-3b85-4a2f-a95c-1922dec5d04a">
<p class=\"noun\">the bags</p>
</simpleChoice>"""
                }, {
                    "id": "id28a924d9-32ac-4ac5-a4b2-1b1cfe2caba0",
                    "text": """<simpleChoice identifier="id28a924d9-32ac-4ac5-a4b2-1b1cfe2caba0">
<p class=\"adverb\">under</p>
</simpleChoice>"""
                }, {
                    "id": "id78ce22bf-559f-44a4-95ee-156f222ad510",
                    "text": """<simpleChoice identifier="id78ce22bf-559f-44a4-95ee-156f222ad510">
<p class=\"noun\">the seat</p>
</simpleChoice>"""
                }, {
                    "id": "id3045d860-24b4-4b30-9ca1-72408a3bcc9b",
                    "text": """<simpleChoice identifier="id3045d860-24b4-4b30-9ca1-72408a3bcc9b">
<p class=\"prep\">on</p>
</simpleChoice>"""
                }, {
                    "id": "id2cad48be-2782-4625-9669-dfcb2062bf3c",
                    "text": """<simpleChoice identifier="id2cad48be-2782-4625-9669-dfcb2062bf3c">
<p class=\"noun\"the bus</p>
</simpleChoice>"""
                }],
                "genusTypeId": str(QTI_QUESTION_ORDER_INTERACTION_MW_SENTENCE_GENUS),
                "shuffle": True,
                "fileIds": {}
            },
            "answers": [{
                "genusTypeId": str(RIGHT_ANSWER_GENUS),
                "choiceIds": ['id51b2feca-d407-46d5-b548-d6645a021008',
                              'id881a8e9c-844b-4394-be62-d28a5fda5296',
                              'idcccac9f8-3b85-4a2f-a95c-1922dec5d04a',
                              'id28a924d9-32ac-4ac5-a4b2-1b1cfe2caba0',
                              'id78ce22bf-559f-44a4-95ee-156f222ad510',
                              'id3045d860-24b4-4b30-9ca1-72408a3bcc9b',
                              'id2cad48be-2782-4625-9669-dfcb2062bf3c'],
                "feedback": """  <modalFeedback  identifier="Feedback372632509" outcomeIdentifier="FEEDBACKMODAL" showHide="show">
<p>Correct Feedback goes here!</p>
</modalFeedback>"""
            }, {
                "genusTypeId": str(WRONG_ANSWER_GENUS),
                "choiceIds": [None],
                "feedback": """  <modalFeedback  identifier="Feedback2014412711" outcomeIdentifier="FEEDBACKMODAL" showHide="show">
<p>Wrong...Feedback goes here!</p>
</modalFeedback>"""
            }]
        }

        for label, asset in assets.iteritems():
            payload['question']['fileIds'][label] = {}
            payload['question']['fileIds'][label]['assetId'] = asset['id']
            payload['question']['fileIds'][label]['assetContentId'] = asset['assetContents'][0]['id']
            payload['question']['fileIds'][label]['assetContentTypeId'] = asset['assetContents'][0]['genusTypeId']

        req = self.app.put(url,
                           params=json.dumps(payload),
                           headers={'content-type': 'application/json'})
        self.ok(req)
        item = self.json(req)

        self.assertEqual(
            item['genusTypeId'],
            str(QTI_ITEM_ORDER_INTERACTION_MW_SENTENCE_GENUS)
        )

        self.assertEqual(
            item['question']['genusTypeId'],
            str(QTI_QUESTION_ORDER_INTERACTION_MW_SENTENCE_GENUS)
        )

        self.assertEqual(
            item['answers'][0]['genusTypeId'],
            str(RIGHT_ANSWER_GENUS)
        )

        self.assertEqual(
            len(item['answers'][0]['choiceIds']),
            7
        )
        self.assertIn('feedbacks', item['answers'][0])
        self.assertTrue(len(item['answers'][0]['feedbacks']) == 1)

        self.assertEqual(
            item['answers'][1]['genusTypeId'],
            str(WRONG_ANSWER_GENUS)
        )
        self.assertEqual(
            len(item['answers'][1]['choiceIds']),
            1
        )
        self.assertIsNone(item['answers'][1]['choiceIds'][0])
        self.assertIn('feedbacks', item['answers'][1])
        self.assertTrue(len(item['answers'][1]['feedbacks']) == 1)

        self.assertEqual(
            len(item['question']['choices']),
            7
        )

        for choice in item['question']['multiLanguageChoices']:
            self.assertTrue(len(choice['texts']) == 1)
            for text in choice['texts']:
                self.assertIn('<p class="', text['text'])
                if any(n in text['text'] for n in ['the bags', 'the bus', 'the bridge', 'Raju', 'the seat']):
                    self.assertIn('"noun"', text['text'])
                elif any(p in text['text'] for p in ['on']):
                    self.assertIn('"prep"', text['text'])
                elif 'left' in text['text']:
                    self.assertIn('"verb"', text['text'])
                elif 'under' in text['text']:
                    self.assertIn('"adverb"', text['text'])
        for choice in item['question']['choices']:
            self.assertIn('<p class="', choice['text'])
            if any(n in choice['text'] for n in ['the bags', 'the bus', 'the bridge', 'Raju', 'the seat']):
                self.assertIn('"noun"', choice['text'])
            elif any(p in choice['text'] for p in ['on']):
                self.assertIn('"prep"', choice['text'])
            elif 'left' in choice['text']:
                self.assertIn('"verb"', choice['text'])
            elif 'under' in choice['text']:
                self.assertIn('"adverb"', choice['text'])

        self.assertNotEqual(
            item['id'],
            str(self._item.ident)
        )

        item_details_url = '{0}/items?qti'.format(self.url)
        req = self.app.get(item_details_url)
        self.ok(req)
        data = self.json(req)
        item = [i for i in data if i['id'] == item['id']][0]
        self.assertIn('qti', item)
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
        image_asset_label = 'intersection_png'
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

        expected_json_string = """<itemBody>
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
            item['question']['text']['text'],
            expected_json_string
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
            "id51b2feca-d407-46d5-b548-d6645a021008": u"""<simpleChoice identifier="id51b2feca-d407-46d5-b548-d6645a021008">
<p class=\"noun\">
     हिंदी
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
            expected = expected_choices[choice_id]
            if isinstance(expected, unicode):
                self.assertEqual(
                    unicode(choice),
                    expected
                )
            else:
                self.assertEqual(
                    str(choice),
                    expected
                )

    def test_can_get_mw_sentence_item_with_no_choices(self):
        url = '{0}/items'.format(self.url)

        media_files = [self._intersection_image,
                       self._mw_sentence_audio_file]

        assets = {}
        for media_file in media_files:
            label = self._label(self._filename(media_file))
            assets[label] = self.upload_media_file(media_file)

        payload = {
            "genusTypeId": str(QTI_ITEM_ORDER_INTERACTION_MW_SENTENCE_GENUS),
            "name": "Question 1",
            "description": "For testing",

            "question": {
                "questionString": """<itemBody>
<p>
   Where are Raju's bags?
  </p>
<p>
</p>
<p>
<audio autoplay="autoplay" controls="controls" style="width: 125px">
<source src="AssetContent:ee_u1l01a01r05__mp3" type="audio/mpeg"/>
</audio>
</p>
<p>
<img alt="This is a drawing of a busy intersection." height="100" src="AssetContent:intersection_png" width="100"/>
</p>

</itemBody>""",
                "fileIds": {}}
        }

        for label, asset in assets.iteritems():
            payload['question']['fileIds'][label] = {}
            payload['question']['fileIds'][label]['assetId'] = asset['id']
            payload['question']['fileIds'][label]['assetContentId'] = asset['assetContents'][0]['id']
            payload['question']['fileIds'][label]['assetContentTypeId'] = asset['assetContents'][0]['genusTypeId']

        req = self.app.post(url,
                            params=json.dumps(payload),
                            headers={'content-type': 'application/json'})
        self.ok(req)
        item = self.json(req)

        url = '{0}/items/{1}'.format(self.url, item['id'])

        req = self.app.get(url)
        self.ok(req)
        data = self.json(req)
        self.assertEqual(data['question']['choices'], [])

    def test_can_get_mw_sentence_item_qti_with_no_answers(self):
        url = '{0}/items'.format(self.url)

        media_files = [self._intersection_image,
                       self._mw_sentence_audio_file]

        assets = {}
        for media_file in media_files:
            label = self._label(self._filename(media_file))
            assets[label] = self.upload_media_file(media_file)

        payload = {
            "genusTypeId": str(QTI_ITEM_ORDER_INTERACTION_MW_SENTENCE_GENUS),
            "name": "Question 1",
            "description": "For testing",

            "question": {
                "questionString": """<itemBody>
<p>
   Where are Raju's bags?
  </p>
<p>
</p>
<p>
<audio autoplay="autoplay" controls="controls" style="width: 125px">
<source src="AssetContent:ee_u1l01a01r05__mp3" type="audio/mpeg"/>
</audio>
</p>
<p>
<img alt="This is a drawing of a busy intersection." height="100" src="AssetContent:intersection_png" width="100"/>
</p>

</itemBody>""",
                "fileIds": {}}
        }

        for label, asset in assets.iteritems():
            payload['question']['fileIds'][label] = {}
            payload['question']['fileIds'][label]['assetId'] = asset['id']
            payload['question']['fileIds'][label]['assetContentId'] = asset['assetContents'][0]['id']
            payload['question']['fileIds'][label]['assetContentTypeId'] = asset['assetContents'][0]['genusTypeId']

        req = self.app.post(url,
                            params=json.dumps(payload),
                            headers={'content-type': 'application/json'})
        self.ok(req)
        item = self.json(req)

        url = '{0}/items/{1}/qti'.format(self.url, item['id'])

        req = self.app.get(url)
        self.ok(req)
        qti = BeautifulSoup(req.body, 'xml')
        self.assertIsNone(qti.responseDeclaration)

    def test_getting_qti_for_mw_sentence_item_with_no_question_returns_empty_string(self):
        url = '{0}/items'.format(self.url)

        payload = {
            "genusTypeId": str(QTI_ITEM_ORDER_INTERACTION_MW_SENTENCE_GENUS),
            "name": "Question 1",
            "description": "For testing"
        }

        req = self.app.post(url,
                            params=json.dumps(payload),
                            headers={'content-type': 'application/json'})
        self.ok(req)
        item = self.json(req)

        item_details_url = '{0}/items/{1}/qti'.format(self.url, unquote(item['id']))
        req = self.app.get(item_details_url)
        self.ok(req)
        self.assertEqual(req.body, '')

    def test_updating_mw_sentence_answer_clears_existing_choices(self):
        url = '{0}/items'.format(self.url)

        media_files = [self._intersection_image,
                       self._mw_sentence_audio_file]

        assets = {}
        for media_file in media_files:
            label = self._label(self._filename(media_file))
            assets[label] = self.upload_media_file(media_file)

        payload = {
            "genusTypeId": str(QTI_ITEM_ORDER_INTERACTION_MW_SENTENCE_GENUS),
            "name": "Question 1",
            "description": "For testing",
            "question": {
                "questionString": """<itemBody>
<p>
   Where are Raju's bags?
  </p>
<p>
</p>
<p>
<audio autoplay="autoplay" controls="controls" style="width: 125px">
<source src="AssetContent:ee_u1l01a01r05__mp3" type="audio/mpeg"/>
</audio>
</p>
<p>
<img alt="This is a drawing of a busy intersection." height="100" src="AssetContent:intersection_png" width="100"/>
</p>

</itemBody>""",
                "choices": [{
                    "id": "id51b2feca-d407-46d5-b548-d6645a021008",
                    "text": """<simpleChoice identifier="id51b2feca-d407-46d5-b548-d6645a021008">
<p class=\"noun\">Raju</p>
</simpleChoice>"""
                }, {
                    "id": "id881a8e9c-844b-4394-be62-d28a5fda5296",
                    "text": """<simpleChoice identifier="id881a8e9c-844b-4394-be62-d28a5fda5296">
<p class=\"verb\">left</p>
</simpleChoice>"""
                }, {
                    "id": "idcccac9f8-3b85-4a2f-a95c-1922dec5d04a",
                    "text": """<simpleChoice identifier="idcccac9f8-3b85-4a2f-a95c-1922dec5d04a">
<p class=\"noun\">the bags</p>
</simpleChoice>"""
                }, {
                    "id": "id28a924d9-32ac-4ac5-a4b2-1b1cfe2caba0",
                    "text": """<simpleChoice identifier="id28a924d9-32ac-4ac5-a4b2-1b1cfe2caba0">
<p class=\"adverb\">under</p>
</simpleChoice>"""
                }, {
                    "id": "id78ce22bf-559f-44a4-95ee-156f222ad510",
                    "text": """<simpleChoice identifier="id78ce22bf-559f-44a4-95ee-156f222ad510">
<p class=\"noun\">the seat</p>
</simpleChoice>"""
                }, {
                    "id": "id3045d860-24b4-4b30-9ca1-72408a3bcc9b",
                    "text": """<simpleChoice identifier="id3045d860-24b4-4b30-9ca1-72408a3bcc9b">
<p class=\"prep\">on</p>
</simpleChoice>"""
                }, {
                    "id": "id2cad48be-2782-4625-9669-dfcb2062bf3c",
                    "text": """<simpleChoice identifier="id2cad48be-2782-4625-9669-dfcb2062bf3c">
<p class=\"noun\"the bus</p>
</simpleChoice>"""
                }],
                "genusTypeId": str(QTI_QUESTION_ORDER_INTERACTION_MW_SENTENCE_GENUS),
                "shuffle": True,
                "fileIds": {}
            },
            "answers": [{
                "genusTypeId": str(RIGHT_ANSWER_GENUS),
                "choiceIds": ['id51b2feca-d407-46d5-b548-d6645a021008',
                              'id881a8e9c-844b-4394-be62-d28a5fda5296',
                              'idcccac9f8-3b85-4a2f-a95c-1922dec5d04a',
                              'id28a924d9-32ac-4ac5-a4b2-1b1cfe2caba0',
                              'id78ce22bf-559f-44a4-95ee-156f222ad510',
                              'id3045d860-24b4-4b30-9ca1-72408a3bcc9b',
                              'id2cad48be-2782-4625-9669-dfcb2062bf3c'],
                "feedback": """  <modalFeedback  identifier="Feedback372632509" outcomeIdentifier="FEEDBACKMODAL" showHide="show">
<p>Correct Feedback goes here!</p>
</modalFeedback>"""
            }, {
                "genusTypeId": str(WRONG_ANSWER_GENUS),
                "choiceIds": [None],
                "feedback": """  <modalFeedback  identifier="Feedback2014412711" outcomeIdentifier="FEEDBACKMODAL" showHide="show">
<p>Wrong...Feedback goes here!</p>
</modalFeedback>"""
            }]
        }

        for label, asset in assets.iteritems():
            payload['question']['fileIds'][label] = {}
            payload['question']['fileIds'][label]['assetId'] = asset['id']
            payload['question']['fileIds'][label]['assetContentId'] = asset['assetContents'][0]['id']
            payload['question']['fileIds'][label]['assetContentTypeId'] = asset['assetContents'][0]['genusTypeId']

        req = self.app.post(url,
                            params=json.dumps(payload),
                            headers={'content-type': 'application/json'})
        self.ok(req)
        item = self.json(req)

        right_answer = [a for a in item['answers'] if a['genusTypeId'] == str(RIGHT_ANSWER_GENUS)][0]
        previous_right_answer_choices = right_answer['choiceIds']
        new_right_answer_choices = ['id51b2feca-d407-46d5-b548-d6645a021008',
                                    'id28a924d9-32ac-4ac5-a4b2-1b1cfe2caba0',
                                    'id881a8e9c-844b-4394-be62-d28a5fda5296',
                                    'id2cad48be-2782-4625-9669-dfcb2062bf3c',
                                    'idcccac9f8-3b85-4a2f-a95c-1922dec5d04a',
                                    'id78ce22bf-559f-44a4-95ee-156f222ad510',
                                    'id3045d860-24b4-4b30-9ca1-72408a3bcc9b']

        self.assertNotEqual(previous_right_answer_choices,
                            new_right_answer_choices)

        url = '{0}/{1}'.format(url, item['id'])
        payload = {
            'answers': [{
                'id': right_answer['id'],
                'choiceIds': new_right_answer_choices
            }]
        }
        req = self.app.put(url,
                           params=json.dumps(payload),
                           headers={'content-type': 'application/json'})
        self.ok(req)
        data = self.json(req)
        self.assertEqual(data['id'], item['id'])
        self.assertEqual(data['answers'][0]['id'], right_answer['id'])
        self.assertEqual(data['answers'][0]['genusTypeId'], str(RIGHT_ANSWER_GENUS))
        self.assertNotEqual(previous_right_answer_choices, data['answers'][0]['choiceIds'])
        self.assertEqual(new_right_answer_choices, data['answers'][0]['choiceIds'])

    def test_can_create_mw_sandbox_question_via_rest(self):
        media_files = [self._mw_sandbox_audio_file]

        assets = {}
        for media_file in media_files:
            label = self._label(self._filename(media_file))
            assets[label] = self.upload_media_file(media_file)

        url = '{0}/items'.format(self.url)

        payload = {
            "genusTypeId": str(QTI_ITEM_ORDER_INTERACTION_MW_SANDBOX_GENUS),
            "name": "Question 1",
            "description": "For testing",
            "question": {
                "questionString": """<itemBody>
<p>
   Movable Word Sandbox:
  </p>
<p>
<audio autoplay="autoplay" controls="controls" style="width: 125px">
<source src="AssetContent:ee_u1l01a01r04__mp3" type="audio/mpeg"/>
</audio>
</p>

</itemBody>""",
                "choices": [{
                    "id": "id14a6824a-79f2-4c00-ac6a-b41cbb64db45",
                    "text": """<simpleChoice identifier="id14a6824a-79f2-4c00-ac6a-b41cbb64db45">
<p class=\"noun\">the bus</p>
</simpleChoice>"""
                }, {
                    "id": "id969e920d-6d22-4d06-b4ac-40a821e350c6",
                    "text": """<simpleChoice identifier="id969e920d-6d22-4d06-b4ac-40a821e350c6">
<p class=\"noun\">the airport</p>
</simpleChoice>"""
                }, {
                    "id": "id820fae90-3794-40d1-bee0-daa36da223b3",
                    "text": """<simpleChoice identifier="id820fae90-3794-40d1-bee0-daa36da223b3">
<p class=\"noun\">the bags</p>
</simpleChoice>"""
                }, {
                    "id": "id2d13b6d7-87e9-4022-a4b6-dcdbba5c8b60",
                    "text": """<simpleChoice identifier="id2d13b6d7-87e9-4022-a4b6-dcdbba5c8b60">
<p class=\"verb\">are</p>
</simpleChoice>"""
                }, {
                    "id": "idf1583dac-fb7a-4365-aa0d-f64e5ab61029",
                    "text": """<simpleChoice identifier="idf1583dac-fb7a-4365-aa0d-f64e5ab61029">
<p class=\"adverb\">under</p>
</simpleChoice>"""
                }, {
                    "id": "idd8449f3e-820f-46f8-9529-7e019fceaaa6",
                    "text": """<simpleChoice identifier="idd8449f3e-820f-46f8-9529-7e019fceaaa6">
<p class=\"prep\">on</p>
</simpleChoice>"""
                }, {
                    "id": "iddd689e9d-0cd0-478d-9d37-2856f866a757",
                    "text": """<simpleChoice identifier="iddd689e9d-0cd0-478d-9d37-2856f866a757">
<p class=\"adverb\">on top of</p>
</simpleChoice>"""
                }, {
                    "id": "id1c0298a6-90ed-4bc9-987a-7fd0165c0fcf",
                    "text": """<simpleChoice identifier="id1c0298a6-90ed-4bc9-987a-7fd0165c0fcf">
<p class=\"noun\">Raju's</p>
</simpleChoice>"""
                }, {
                    "id": "id41288bb9-e76e-4313-bf57-2101edfe3a76",
                    "text": """<simpleChoice identifier="id41288bb9-e76e-4313-bf57-2101edfe3a76">
<p class=\"verb\">left</p>
</simpleChoice>"""
                }, {
                    "id": "id4435ccd8-df65-45e7-8d82-6c077473d8d4",
                    "text": """<simpleChoice identifier="id4435ccd8-df65-45e7-8d82-6c077473d8d4">
<p class=\"noun\">the seat</p>
</simpleChoice>"""
                }, {
                    "id": "idfffc63c0-f227-4ac4-ad0a-2f0b92b28fd1",
                    "text": """<simpleChoice identifier="idfffc63c0-f227-4ac4-ad0a-2f0b92b28fd1">
<p class=\"noun\">the city</p>
</simpleChoice>"""
                }, {
                    "id": "id472afb75-4aa9-4daa-a163-075798ee57ab",
                    "text": """<simpleChoice identifier="id472afb75-4aa9-4daa-a163-075798ee57ab">
<p class=\"noun\">the bicycle</p>
</simpleChoice>"""
                }, {
                    "id": "id8c68713f-8e39-446b-a6c8-df25dfb8118e",
                    "text": """<simpleChoice identifier="id8c68713f-8e39-446b-a6c8-df25dfb8118e">
<p class=\"verb\">dropped</p>
</simpleChoice>"""
                }],
                "genusTypeId": str(QTI_QUESTION_ORDER_INTERACTION_MW_SANDBOX_GENUS),
                "shuffle": True,
                "fileIds": {},
                "timeValue": {
                    "hours": 0,
                    "minutes": 0,
                    "seconds": 360
                }
            },
            "answers": [{
                "genusTypeId": str(RIGHT_ANSWER_GENUS),
                "choiceIds": ['id14a6824a-79f2-4c00-ac6a-b41cbb64db45',
                              'id969e920d-6d22-4d06-b4ac-40a821e350c6',
                              'id820fae90-3794-40d1-bee0-daa36da223b3',
                              'id2d13b6d7-87e9-4022-a4b6-dcdbba5c8b60',
                              'idf1583dac-fb7a-4365-aa0d-f64e5ab61029',
                              'idd8449f3e-820f-46f8-9529-7e019fceaaa6',
                              'iddd689e9d-0cd0-478d-9d37-2856f866a757',
                              'id1c0298a6-90ed-4bc9-987a-7fd0165c0fcf',
                              'id41288bb9-e76e-4313-bf57-2101edfe3a76',
                              'id4435ccd8-df65-45e7-8d82-6c077473d8d4',
                              'idfffc63c0-f227-4ac4-ad0a-2f0b92b28fd1',
                              'id472afb75-4aa9-4daa-a163-075798ee57ab',
                              'id8c68713f-8e39-446b-a6c8-df25dfb8118e'],
                "feedback": """  <modalFeedback  identifier="Feedback372632509" outcomeIdentifier="FEEDBACKMODAL" showHide="show">
<p>Correct Feedback goes here!</p>
</modalFeedback>"""
            }, {
                "genusTypeId": str(WRONG_ANSWER_GENUS),
                "choiceIds": [None],
                "feedback": """  <modalFeedback  identifier="Feedback2014412711" outcomeIdentifier="FEEDBACKMODAL" showHide="show">
<p>Wrong...Feedback goes here!</p>
</modalFeedback>"""
            }]
        }

        for label, asset in assets.iteritems():
            payload['question']['fileIds'][label] = {}
            payload['question']['fileIds'][label]['assetId'] = asset['id']
            payload['question']['fileIds'][label]['assetContentId'] = asset['assetContents'][0]['id']
            payload['question']['fileIds'][label]['assetContentTypeId'] = asset['assetContents'][0]['genusTypeId']

        req = self.app.post(url,
                            params=json.dumps(payload),
                            headers={'content-type': 'application/json'})
        self.ok(req)
        item = self.json(req)

        self.assertEqual(
            item['genusTypeId'],
            str(QTI_ITEM_ORDER_INTERACTION_MW_SANDBOX_GENUS)
        )

        self.assertEqual(
            item['question']['genusTypeId'],
            str(QTI_QUESTION_ORDER_INTERACTION_MW_SANDBOX_GENUS)
        )

        self.assertIn(
            'timeValue',
            item['question']
        )

        self.assertEqual(
            item['question']['timeValue'],
            {'hours': '00', 'minutes': '06', 'seconds': '00'}
        )

        self.assertEqual(
            item['answers'][0]['genusTypeId'],
            str(RIGHT_ANSWER_GENUS)
        )
        self.assertEqual(
            len(item['question']['choices']),
            13
        )

        for choice in item['question']['multiLanguageChoices']:
            self.assertTrue(len(choice['texts']) == 1)
            for text in choice['texts']:
                self.assertIn('<p class="', text['text'])
                if any(n == text['text'] for n in ['the bags', 'the bus',
                                                   'the bridge', "Raju's",
                                                   'the seat', 'the airport',
                                                   'the city', 'the bicycle']):
                    self.assertIn('"noun"', text['text'])
                elif any(p == text['text'] for p in ['on']):
                    self.assertIn('"prep"', text['text'])
                elif any(v == text['text'] for v in ['are', 'left', 'dropped']):
                    self.assertIn('"verb"', text['text'])
                elif any(av == text['text'] for av in ['under', 'on top of']):
                    self.assertIn('"adverb"', text['text'])
        for choice in item['question']['choices']:
            self.assertIn('<p class="', choice['text'])
            if any(n == choice['text'] for n in ['the bags', 'the bus',
                                                 'the bridge', "Raju's",
                                                 'the seat', 'the airport',
                                                 'the city', 'the bicycle']):
                self.assertIn('"noun"', choice['text'])
            elif any(p == choice['text'] for p in ['on']):
                self.assertIn('"prep"', choice['text'])
            elif any(v == choice['text'] for v in ['are', 'left', 'dropped']):
                self.assertIn('"verb"', choice['text'])
            elif any(av == choice['text'] for av in ['under', 'on top of']):
                self.assertIn('"adverb"', choice['text'])

        self.assertNotEqual(
            item['id'],
            str(self._item.ident)
        )

        item_details_url = '{0}?qti'.format(url)
        req = self.app.get(item_details_url)
        self.ok(req)
        data = self.json(req)
        item = [i for i in data if i['id'] == item['id']][0]
        self.assertIn('qti', item)
        item_qti = BeautifulSoup(item['qti'], 'lxml-xml').assessmentItem
        expected_values = ['id14a6824a-79f2-4c00-ac6a-b41cbb64db45',
                           'id969e920d-6d22-4d06-b4ac-40a821e350c6',
                           'id820fae90-3794-40d1-bee0-daa36da223b3',
                           'id2d13b6d7-87e9-4022-a4b6-dcdbba5c8b60',
                           'idf1583dac-fb7a-4365-aa0d-f64e5ab61029',
                           'idd8449f3e-820f-46f8-9529-7e019fceaaa6',
                           'iddd689e9d-0cd0-478d-9d37-2856f866a757',
                           'id1c0298a6-90ed-4bc9-987a-7fd0165c0fcf',
                           'id41288bb9-e76e-4313-bf57-2101edfe3a76',
                           'id4435ccd8-df65-45e7-8d82-6c077473d8d4',
                           'idfffc63c0-f227-4ac4-ad0a-2f0b92b28fd1',
                           'id472afb75-4aa9-4daa-a163-075798ee57ab',
                           'id8c68713f-8e39-446b-a6c8-df25dfb8118e']
        for index, value in enumerate(item_qti.responseDeclaration.correctResponse.find_all('value')):
            self.assertEqual(value.string.strip(), expected_values[index])

        item_body = item_qti.itemBody

        order_interaction = item_body.orderInteraction.extract()

        audio_asset_label = 'ee_u1l01a01r04__mp3'
        asset_id = item['question']['fileIds'][audio_asset_label]['assetId']
        asset_content_id = item['question']['fileIds'][audio_asset_label]['assetContentId']

        expected_string = """<itemBody>
<p>
   Movable Word Sandbox:
  </p>
<p>
<audio autoplay="autoplay" controls="controls" style="width: 125px">
<source src="/api/v1/repository/repositories/{0}/assets/{1}/contents/{2}/stream" type="audio/mpeg"/>
</audio>
</p>

</itemBody>""".format(str(self._bank.ident).replace('assessment.Bank', 'repository.Repository'),
                      asset_id,
                      asset_content_id)

        self.assertEqual(
            str(item_body),
            expected_string
        )

        self.assertEqual(
            len(order_interaction.find_all('simpleChoice')),
            13
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
            "id14a6824a-79f2-4c00-ac6a-b41cbb64db45": """<simpleChoice identifier="id14a6824a-79f2-4c00-ac6a-b41cbb64db45">
<p class="noun">
     the bus
    </p>
</simpleChoice>""",
            "id969e920d-6d22-4d06-b4ac-40a821e350c6": """<simpleChoice identifier="id969e920d-6d22-4d06-b4ac-40a821e350c6">
<p class="noun">
     the airport
    </p>
</simpleChoice>""",
            "id820fae90-3794-40d1-bee0-daa36da223b3": """<simpleChoice identifier="id820fae90-3794-40d1-bee0-daa36da223b3">
<p class="noun">
     the bags
    </p>
</simpleChoice>""",
            "id2d13b6d7-87e9-4022-a4b6-dcdbba5c8b60": """<simpleChoice identifier="id2d13b6d7-87e9-4022-a4b6-dcdbba5c8b60">
<p class="verb">
     are
    </p>
</simpleChoice>""",
            "idf1583dac-fb7a-4365-aa0d-f64e5ab61029": """<simpleChoice identifier="idf1583dac-fb7a-4365-aa0d-f64e5ab61029">
<p class="adverb">
     under
    </p>
</simpleChoice>""",
            "idd8449f3e-820f-46f8-9529-7e019fceaaa6": """<simpleChoice identifier="idd8449f3e-820f-46f8-9529-7e019fceaaa6">
<p class="prep">
     on
    </p>
</simpleChoice>""",
            "iddd689e9d-0cd0-478d-9d37-2856f866a757": """<simpleChoice identifier="iddd689e9d-0cd0-478d-9d37-2856f866a757">
<p class="adverb">
     on top of
    </p>
</simpleChoice>""",
            "id1c0298a6-90ed-4bc9-987a-7fd0165c0fcf": """<simpleChoice identifier="id1c0298a6-90ed-4bc9-987a-7fd0165c0fcf">
<p class="noun">
     Raju's
    </p>
</simpleChoice>""",
            "id41288bb9-e76e-4313-bf57-2101edfe3a76": """<simpleChoice identifier="id41288bb9-e76e-4313-bf57-2101edfe3a76">
<p class="verb">
     left
    </p>
</simpleChoice>""",
            "id4435ccd8-df65-45e7-8d82-6c077473d8d4": """<simpleChoice identifier="id4435ccd8-df65-45e7-8d82-6c077473d8d4">
<p class="noun">
     the seat
    </p>
</simpleChoice>""",
            "idfffc63c0-f227-4ac4-ad0a-2f0b92b28fd1": """<simpleChoice identifier="idfffc63c0-f227-4ac4-ad0a-2f0b92b28fd1">
<p class="noun">
     the city
    </p>
</simpleChoice>""",
            "id472afb75-4aa9-4daa-a163-075798ee57ab": """<simpleChoice identifier="id472afb75-4aa9-4daa-a163-075798ee57ab">
<p class="noun">
     the bicycle
    </p>
</simpleChoice>""",
            "id8c68713f-8e39-446b-a6c8-df25dfb8118e": """<simpleChoice identifier="id8c68713f-8e39-446b-a6c8-df25dfb8118e">
<p class="verb">
     dropped
    </p>
</simpleChoice>"""
        }

        for choice in order_interaction.find_all('simpleChoice'):
            choice_id = choice['identifier']
            self.assertEqual(
                str(choice),
                expected_choices[choice_id]
            )

    def test_can_add_question_to_existing_mw_sandbox_item_via_rest(self):
        url = '{0}/items'.format(self.url)

        payload = {
            "genusTypeId": str(QTI_ITEM_ORDER_INTERACTION_MW_SANDBOX_GENUS),
            "name": "Question 1",
            "description": "For testing"
        }

        req = self.app.post(url,
                            params=json.dumps(payload),
                            headers={'content-type': 'application/json'})
        self.ok(req)
        item = self.json(req)

        media_files = [self._mw_sandbox_audio_file]

        assets = {}
        for media_file in media_files:
            label = self._label(self._filename(media_file))
            assets[label] = self.upload_media_file(media_file)

        url = '{0}/items/{1}'.format(self.url, item['id'])

        payload = {
            "question": {
                "questionString": """<itemBody>
<p>
   Movable Word Sandbox:
  </p>
<p>
<audio autoplay="autoplay" controls="controls" style="width: 125px">
<source src="AssetContent:ee_u1l01a01r04__mp3" type="audio/mpeg"/>
</audio>
</p>

</itemBody>""",
                "choices": [{
                    "id": "id14a6824a-79f2-4c00-ac6a-b41cbb64db45",
                    "text": """<simpleChoice identifier="id14a6824a-79f2-4c00-ac6a-b41cbb64db45">
<p class=\"noun\">the bus</p>
</simpleChoice>"""
                }, {
                    "id": "id969e920d-6d22-4d06-b4ac-40a821e350c6",
                    "text": """<simpleChoice identifier="id969e920d-6d22-4d06-b4ac-40a821e350c6">
<p class=\"noun\">the airport</p>
</simpleChoice>"""
                }, {
                    "id": "id820fae90-3794-40d1-bee0-daa36da223b3",
                    "text": """<simpleChoice identifier="id820fae90-3794-40d1-bee0-daa36da223b3">
<p class=\"noun\">the bags</p>
</simpleChoice>"""
                }, {
                    "id": "id2d13b6d7-87e9-4022-a4b6-dcdbba5c8b60",
                    "text": """<simpleChoice identifier="id2d13b6d7-87e9-4022-a4b6-dcdbba5c8b60">
<p class=\"verb\">are</p>
</simpleChoice>"""
                }, {
                    "id": "idf1583dac-fb7a-4365-aa0d-f64e5ab61029",
                    "text": """<simpleChoice identifier="idf1583dac-fb7a-4365-aa0d-f64e5ab61029">
<p class=\"adverb\">under</p>
</simpleChoice>"""
                }, {
                    "id": "idd8449f3e-820f-46f8-9529-7e019fceaaa6",
                    "text": """<simpleChoice identifier="idd8449f3e-820f-46f8-9529-7e019fceaaa6">
<p class=\"prep\">on</p>
</simpleChoice>"""
                }, {
                    "id": "iddd689e9d-0cd0-478d-9d37-2856f866a757",
                    "text": """<simpleChoice identifier="iddd689e9d-0cd0-478d-9d37-2856f866a757">
<p class=\"adverb\">on top of</p>
</simpleChoice>"""
                }, {
                    "id": "id1c0298a6-90ed-4bc9-987a-7fd0165c0fcf",
                    "text": """<simpleChoice identifier="id1c0298a6-90ed-4bc9-987a-7fd0165c0fcf">
<p class=\"noun\">Raju's</p>
</simpleChoice>"""
                }, {
                    "id": "id41288bb9-e76e-4313-bf57-2101edfe3a76",
                    "text": """<simpleChoice identifier="id41288bb9-e76e-4313-bf57-2101edfe3a76">
<p class=\"verb\">left</p>
</simpleChoice>"""
                }, {
                    "id": "id4435ccd8-df65-45e7-8d82-6c077473d8d4",
                    "text": """<simpleChoice identifier="id4435ccd8-df65-45e7-8d82-6c077473d8d4">
<p class=\"noun\">the seat</p>
</simpleChoice>"""
                }, {
                    "id": "idfffc63c0-f227-4ac4-ad0a-2f0b92b28fd1",
                    "text": """<simpleChoice identifier="idfffc63c0-f227-4ac4-ad0a-2f0b92b28fd1">
<p class=\"noun\">the city</p>
</simpleChoice>"""
                }, {
                    "id": "id472afb75-4aa9-4daa-a163-075798ee57ab",
                    "text": """<simpleChoice identifier="id472afb75-4aa9-4daa-a163-075798ee57ab">
<p class=\"noun\">the bicycle</p>
</simpleChoice>"""
                }, {
                    "id": "id8c68713f-8e39-446b-a6c8-df25dfb8118e",
                    "text": """<simpleChoice identifier="id8c68713f-8e39-446b-a6c8-df25dfb8118e">
<p class=\"verb\">dropped</p>
</simpleChoice>"""
                }],
                "genusTypeId": str(QTI_QUESTION_ORDER_INTERACTION_MW_SANDBOX_GENUS),
                "shuffle": True,
                "fileIds": {},
                "timeValue": {
                    "hours": 0,
                    "minutes": 0,
                    "seconds": 360
                }
            },
            "answers": [{
                "genusTypeId": str(RIGHT_ANSWER_GENUS),
                "choiceIds": ['id14a6824a-79f2-4c00-ac6a-b41cbb64db45',
                              'id969e920d-6d22-4d06-b4ac-40a821e350c6',
                              'id820fae90-3794-40d1-bee0-daa36da223b3',
                              'id2d13b6d7-87e9-4022-a4b6-dcdbba5c8b60',
                              'idf1583dac-fb7a-4365-aa0d-f64e5ab61029',
                              'idd8449f3e-820f-46f8-9529-7e019fceaaa6',
                              'iddd689e9d-0cd0-478d-9d37-2856f866a757',
                              'id1c0298a6-90ed-4bc9-987a-7fd0165c0fcf',
                              'id41288bb9-e76e-4313-bf57-2101edfe3a76',
                              'id4435ccd8-df65-45e7-8d82-6c077473d8d4',
                              'idfffc63c0-f227-4ac4-ad0a-2f0b92b28fd1',
                              'id472afb75-4aa9-4daa-a163-075798ee57ab',
                              'id8c68713f-8e39-446b-a6c8-df25dfb8118e'],
                "feedback": """  <modalFeedback  identifier="Feedback372632509" outcomeIdentifier="FEEDBACKMODAL" showHide="show">
<p>Correct Feedback goes here!</p>
</modalFeedback>"""
            }, {
                "genusTypeId": str(WRONG_ANSWER_GENUS),
                "choiceIds": [None],
                "feedback": """  <modalFeedback  identifier="Feedback2014412711" outcomeIdentifier="FEEDBACKMODAL" showHide="show">
<p>Wrong...Feedback goes here!</p>
</modalFeedback>"""
            }]
        }

        for label, asset in assets.iteritems():
            payload['question']['fileIds'][label] = {}
            payload['question']['fileIds'][label]['assetId'] = asset['id']
            payload['question']['fileIds'][label]['assetContentId'] = asset['assetContents'][0]['id']
            payload['question']['fileIds'][label]['assetContentTypeId'] = asset['assetContents'][0]['genusTypeId']

        req = self.app.put(url,
                           params=json.dumps(payload),
                           headers={'content-type': 'application/json'})
        self.ok(req)
        item = self.json(req)

        self.assertEqual(
            item['genusTypeId'],
            str(QTI_ITEM_ORDER_INTERACTION_MW_SANDBOX_GENUS)
        )

        self.assertEqual(
            item['question']['genusTypeId'],
            str(QTI_QUESTION_ORDER_INTERACTION_MW_SANDBOX_GENUS)
        )

        self.assertIn(
            'timeValue',
            item['question']
        )

        self.assertEqual(
            item['question']['timeValue'],
            {'hours': '00', 'minutes': '06', 'seconds': '00'}
        )

        self.assertEqual(
            item['answers'][0]['genusTypeId'],
            str(RIGHT_ANSWER_GENUS)
        )
        self.assertEqual(
            len(item['question']['choices']),
            13
        )

        for choice in item['question']['multiLanguageChoices']:
            self.assertTrue(len(choice['texts']) == 1)
            for text in choice['texts']:
                self.assertIn('<p class="', text['text'])
                if any(n == text['text'] for n in ['the bags', 'the bus',
                                                   'the bridge', "Raju's",
                                                   'the seat', 'the airport',
                                                   'the city', 'the bicycle']):
                    self.assertIn('"noun"', text['text'])
                elif any(p == text['text'] for p in ['on']):
                    self.assertIn('"prep"', text['text'])
                elif any(v == text['text'] for v in ['are', 'left', 'dropped']):
                    self.assertIn('"verb"', text['text'])
                elif any(av == text['text'] for av in ['under', 'on top of']):
                    self.assertIn('"adverb"', text['text'])
        for choice in item['question']['choices']:
            self.assertIn('<p class="', choice['text'])
            if any(n == choice['text'] for n in ['the bags', 'the bus',
                                                 'the bridge', "Raju's",
                                                 'the seat', 'the airport',
                                                 'the city', 'the bicycle']):
                self.assertIn('"noun"', choice['text'])
            elif any(p == choice['text'] for p in ['on']):
                self.assertIn('"prep"', choice['text'])
            elif any(v == choice['text'] for v in ['are', 'left', 'dropped']):
                self.assertIn('"verb"', choice['text'])
            elif any(av == choice['text'] for av in ['under', 'on top of']):
                self.assertIn('"adverb"', choice['text'])

        self.assertNotEqual(
            item['id'],
            str(self._item.ident)
        )

        item_details_url = '{0}/items?qti'.format(self.url)
        req = self.app.get(item_details_url)
        self.ok(req)
        data = self.json(req)
        item = [i for i in data if i['id'] == item['id']][0]
        self.assertIn('qti', item)
        item_qti = BeautifulSoup(item['qti'], 'lxml-xml').assessmentItem
        self.assertEqual(len(item_qti.responseDeclaration.correctResponse.find_all('value')),
                         0)
        # expected_values = ['id14a6824a-79f2-4c00-ac6a-b41cbb64db45',
        #                    'id969e920d-6d22-4d06-b4ac-40a821e350c6',
        #                    'id820fae90-3794-40d1-bee0-daa36da223b3',
        #                    'id2d13b6d7-87e9-4022-a4b6-dcdbba5c8b60',
        #                    'idf1583dac-fb7a-4365-aa0d-f64e5ab61029',
        #                    'idd8449f3e-820f-46f8-9529-7e019fceaaa6',
        #                    'iddd689e9d-0cd0-478d-9d37-2856f866a757',
        #                    'id1c0298a6-90ed-4bc9-987a-7fd0165c0fcf',
        #                    'id41288bb9-e76e-4313-bf57-2101edfe3a76',
        #                    'id4435ccd8-df65-45e7-8d82-6c077473d8d4',
        #                    'idfffc63c0-f227-4ac4-ad0a-2f0b92b28fd1',
        #                    'id472afb75-4aa9-4daa-a163-075798ee57ab',
        #                    'id8c68713f-8e39-446b-a6c8-df25dfb8118e']
        # for index, value in enumerate():
        #     self.assertEqual(value.string.strip(), expected_values[index])

        item_body = item_qti.itemBody

        order_interaction = item_body.orderInteraction.extract()

        audio_asset_label = 'ee_u1l01a01r04__mp3'
        asset_id = item['question']['fileIds'][audio_asset_label]['assetId']
        asset_content_id = item['question']['fileIds'][audio_asset_label]['assetContentId']

        expected_string = """<itemBody>
<p>
   Movable Word Sandbox:
  </p>
<p>
<audio autoplay="autoplay" controls="controls" style="width: 125px">
<source src="/api/v1/repository/repositories/{0}/assets/{1}/contents/{2}/stream" type="audio/mpeg"/>
</audio>
</p>

</itemBody>""".format(str(self._bank.ident).replace('assessment.Bank', 'repository.Repository'),
                      asset_id,
                      asset_content_id)

        self.assertEqual(
            str(item_body),
            expected_string
        )

        expected_json_string = """<itemBody>
<p>
   Movable Word Sandbox:
  </p>
<p>
<audio autoplay="autoplay" controls="controls" style="width: 125px">
<source src="/api/v1/repository/repositories/{0}/assets/{1}/contents/{2}/stream" type="audio/mpeg"/>
</audio>
</p>
</itemBody>""".format(str(self._bank.ident).replace('assessment.Bank', 'repository.Repository'),
                      asset_id,
                      asset_content_id)

        self.assertEqual(
            item['question']['text']['text'],
            expected_json_string
        )

        self.assertEqual(
            len(order_interaction.find_all('simpleChoice')),
            13
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
            "id14a6824a-79f2-4c00-ac6a-b41cbb64db45": """<simpleChoice identifier="id14a6824a-79f2-4c00-ac6a-b41cbb64db45">
<p class="noun">
     the bus
    </p>
</simpleChoice>""",
            "id969e920d-6d22-4d06-b4ac-40a821e350c6": """<simpleChoice identifier="id969e920d-6d22-4d06-b4ac-40a821e350c6">
<p class="noun">
     the airport
    </p>
</simpleChoice>""",
            "id820fae90-3794-40d1-bee0-daa36da223b3": """<simpleChoice identifier="id820fae90-3794-40d1-bee0-daa36da223b3">
<p class="noun">
     the bags
    </p>
</simpleChoice>""",
            "id2d13b6d7-87e9-4022-a4b6-dcdbba5c8b60": """<simpleChoice identifier="id2d13b6d7-87e9-4022-a4b6-dcdbba5c8b60">
<p class="verb">
     are
    </p>
</simpleChoice>""",
            "idf1583dac-fb7a-4365-aa0d-f64e5ab61029": """<simpleChoice identifier="idf1583dac-fb7a-4365-aa0d-f64e5ab61029">
<p class="adverb">
     under
    </p>
</simpleChoice>""",
            "idd8449f3e-820f-46f8-9529-7e019fceaaa6": """<simpleChoice identifier="idd8449f3e-820f-46f8-9529-7e019fceaaa6">
<p class="prep">
     on
    </p>
</simpleChoice>""",
            "iddd689e9d-0cd0-478d-9d37-2856f866a757": """<simpleChoice identifier="iddd689e9d-0cd0-478d-9d37-2856f866a757">
<p class="adverb">
     on top of
    </p>
</simpleChoice>""",
            "id1c0298a6-90ed-4bc9-987a-7fd0165c0fcf": """<simpleChoice identifier="id1c0298a6-90ed-4bc9-987a-7fd0165c0fcf">
<p class="noun">
     Raju's
    </p>
</simpleChoice>""",
            "id41288bb9-e76e-4313-bf57-2101edfe3a76": """<simpleChoice identifier="id41288bb9-e76e-4313-bf57-2101edfe3a76">
<p class="verb">
     left
    </p>
</simpleChoice>""",
            "id4435ccd8-df65-45e7-8d82-6c077473d8d4": """<simpleChoice identifier="id4435ccd8-df65-45e7-8d82-6c077473d8d4">
<p class="noun">
     the seat
    </p>
</simpleChoice>""",
            "idfffc63c0-f227-4ac4-ad0a-2f0b92b28fd1": """<simpleChoice identifier="idfffc63c0-f227-4ac4-ad0a-2f0b92b28fd1">
<p class="noun">
     the city
    </p>
</simpleChoice>""",
            "id472afb75-4aa9-4daa-a163-075798ee57ab": """<simpleChoice identifier="id472afb75-4aa9-4daa-a163-075798ee57ab">
<p class="noun">
     the bicycle
    </p>
</simpleChoice>""",
            "id8c68713f-8e39-446b-a6c8-df25dfb8118e": """<simpleChoice identifier="id8c68713f-8e39-446b-a6c8-df25dfb8118e">
<p class="verb">
     dropped
    </p>
</simpleChoice>"""
        }

        for choice in order_interaction.find_all('simpleChoice'):
            choice_id = choice['identifier']
            self.assertEqual(
                str(choice),
                expected_choices[choice_id]
            )

    def test_can_get_mw_sandbox_item_with_no_choices(self):
        url = '{0}/items'.format(self.url)

        media_files = [self._mw_sandbox_audio_file]

        assets = {}
        for media_file in media_files:
            label = self._label(self._filename(media_file))
            assets[label] = self.upload_media_file(media_file)

        payload = {
            "genusTypeId": str(QTI_ITEM_ORDER_INTERACTION_MW_SANDBOX_GENUS),
            "name": "Question 1",
            "description": "For testing",
            "question": {
                "questionString": """<itemBody>
<p>
   Movable Word Sandbox:
  </p>
<p>
<audio autoplay="autoplay" controls="controls" style="width: 125px">
<source src="AssetContent:ee_u1l01a01r04__mp3" type="audio/mpeg"/>
</audio>
</p>

</itemBody>""",
                "fileIds": {}}
        }

        for label, asset in assets.iteritems():
            payload['question']['fileIds'][label] = {}
            payload['question']['fileIds'][label]['assetId'] = asset['id']
            payload['question']['fileIds'][label]['assetContentId'] = asset['assetContents'][0]['id']
            payload['question']['fileIds'][label]['assetContentTypeId'] = asset['assetContents'][0]['genusTypeId']

        req = self.app.post(url,
                            params=json.dumps(payload),
                            headers={'content-type': 'application/json'})
        self.ok(req)
        item = self.json(req)

        url = '{0}/items/{1}'.format(self.url, item['id'])

        req = self.app.get(url)
        self.ok(req)
        data = self.json(req)
        self.assertEqual(data['question']['choices'], [])

    def test_can_get_mw_sandbox_item_qti_with_no_answers(self):
        url = '{0}/items'.format(self.url)

        media_files = [self._mw_sandbox_audio_file]

        assets = {}
        for media_file in media_files:
            label = self._label(self._filename(media_file))
            assets[label] = self.upload_media_file(media_file)

        payload = {
            "genusTypeId": str(QTI_ITEM_ORDER_INTERACTION_MW_SANDBOX_GENUS),
            "name": "Question 1",
            "description": "For testing",
            "question": {
                "questionString": """<itemBody>
<p>
   Movable Word Sandbox:
  </p>
<p>
<audio autoplay="autoplay" controls="controls" style="width: 125px">
<source src="AssetContent:ee_u1l01a01r04__mp3" type="audio/mpeg"/>
</audio>
</p>

</itemBody>""",
                "fileIds": {}}
        }

        for label, asset in assets.iteritems():
            payload['question']['fileIds'][label] = {}
            payload['question']['fileIds'][label]['assetId'] = asset['id']
            payload['question']['fileIds'][label]['assetContentId'] = asset['assetContents'][0]['id']
            payload['question']['fileIds'][label]['assetContentTypeId'] = asset['assetContents'][0]['genusTypeId']

        req = self.app.post(url,
                            params=json.dumps(payload),
                            headers={'content-type': 'application/json'})
        self.ok(req)
        item = self.json(req)

        url = '{0}/items/{1}/qti'.format(self.url, item['id'])

        req = self.app.get(url)
        self.ok(req)
        qti = BeautifulSoup(req.body, 'xml')
        self.assertIsNotNone(qti.responseDeclaration)

    def test_getting_qti_for_mw_sandbox_item_with_no_question_returns_empty_string(self):
        url = '{0}/items'.format(self.url)

        payload = {
            "genusTypeId": str(QTI_ITEM_ORDER_INTERACTION_MW_SANDBOX_GENUS),
            "name": "Question 1",
            "description": "For testing"
        }

        req = self.app.post(url,
                            params=json.dumps(payload),
                            headers={'content-type': 'application/json'})
        self.ok(req)
        item = self.json(req)

        item_details_url = '{0}/items/{1}/qti'.format(self.url, unquote(item['id']))
        req = self.app.get(item_details_url)
        self.ok(req)
        self.assertEqual(req.body, '')

    def test_can_create_fill_in_the_blank_question_via_rest(self):
        url = '{0}/items'.format(self.url)

        payload = {
            "genusTypeId": str(QTI_ITEM_INLINE_CHOICE_INTERACTION_GENUS),
            "name": "Question 1",
            "description": "For testing",
            "question": {
                "questionString": """<itemBody>
<p>
<span data-sheets-userformat=\"{\" data-sheets-value=\"{\">
<p>
<p class="other">
      Putting things away
     </p>
<p class="preposition">
      in
     </p>
<p class="other">
      the
     </p>
<p class="adjective">
      proper
     </p>
<p class="noun">
      place
     </p>
<p class="verb">
      makes
     </p>
<p class="noun">
      it
     </p>
</p>

<inlineChoiceInteraction responseIdentifier="RESPONSE_1" shuffle="false" />

<p>
<p class="other">
      to
     </p>
<p class="verb">
      find
     </p>
<p class="noun">
      them
     </p>
<p class="adverb">
      later
     </p>
     .
    </p>
</span>
</p>
</itemBody>""",
                "inlineRegions": {
                    "RESPONSE_1": {
                        "choices": [{
                            "id": "[_1_1",
                            "text": """<inlineChoice identifier="[_1_1"><p class="adjective">easy</p></inlineChoice>"""
                        }, {
                            "id": "[_1_1_1",
                            "text": """<inlineChoice identifier="[_1_1_1"><p class="adjective">neat</p></inlineChoice>"""
                        }, {
                            "id": "[_2_1_1",
                            "text": """<inlineChoice identifier="[_2_1_1"><p class="adjective">fast</p></inlineChoice>"""
                        }, {
                            "id": "[_3_1_1",
                            "text": """<inlineChoice identifier="[_3_1_1"><p class="adjective">good</p></inlineChoice>"""
                        }],
                    }
                },
                "genusTypeId": str(QTI_QUESTION_INLINE_CHOICE_INTERACTION_GENUS),
                "shuffle": True
            },
            "answers": [{
                "genusTypeId": str(RIGHT_ANSWER_GENUS),
                "choiceIds": ['[_1_1'],
                "region": "RESPONSE_1",
                "feedback": """  <modalFeedback  identifier="Feedback372632509" outcomeIdentifier="FEEDBACKMODAL" showHide="show">
<p>You are right! Please try the next question.</p>
</modalFeedback>"""
            }, {
                "genusTypeId": str(WRONG_ANSWER_GENUS),
                "choiceIds": [None],
                "region": "RESPONSE_1",
                "feedback": """  <modalFeedback  identifier="Feedback2014412711" outcomeIdentifier="FEEDBACKMODAL" showHide="show">
<p>Please try again.</p>
</modalFeedback>"""
            }]
        }

        req = self.app.post(url,
                            params=json.dumps(payload),
                            headers={'content-type': 'application/json'})
        self.ok(req)
        item = self.json(req)

        self.assertEqual(
            item['genusTypeId'],
            str(QTI_ITEM_INLINE_CHOICE_INTERACTION_GENUS)
        )

        self.assertEqual(
            item['question']['genusTypeId'],
            str(QTI_QUESTION_INLINE_CHOICE_INTERACTION_GENUS)
        )

        self.assertIn('RESPONSE_1', item['question']['choices'])

        response_1_choice_ids = [c['id'] for c in item['question']['choices']['RESPONSE_1']]

        self.assertIn('[_1_1', response_1_choice_ids)

        self.assertEqual(
            len(item['answers']),
            2
        )

        self.assertEqual(
            item['answers'][0]['genusTypeId'],
            str(RIGHT_ANSWER_GENUS)
        )
        self.assertIn('RESPONSE_1', item['answers'][0]['inlineRegions'])

        self.assertEqual(
            item['answers'][0]['inlineRegions']['RESPONSE_1']['choiceIds'],
            ['[_1_1']
        )
        self.assertIn('You are right! Please try the next question.', item['answers'][0]['feedbacks'][0]['text'])

        self.assertEqual(
            item['answers'][1]['genusTypeId'],
            str(WRONG_ANSWER_GENUS)
        )

        self.assertIn('Please try again.', item['answers'][1]['feedbacks'][0]['text'])

        self.assertNotEqual(
            item['id'],
            str(self._item.ident)
        )

        # now verify the QTI XML matches the JSON format
        url = '{0}/{1}/qti'.format(url, unquote(item['id']))
        req = self.app.get(url)
        self.ok(req)
        qti_xml = BeautifulSoup(req.body, 'lxml-xml').assessmentItem
        item_body = qti_xml.itemBody

        inline_choice_interaction = item_body.inlineChoiceInteraction.extract()

        expected_string = """<itemBody>
<p>
<span data-sheets-userformat=\"{\" data-sheets-value=\"{\">
<p>
<p class="other">
      Putting things away
     </p>
<p class="preposition">
      in
     </p>
<p class="other">
      the
     </p>
<p class="adjective">
      proper
     </p>
<p class="noun">
      place
     </p>
<p class="verb">
      makes
     </p>
<p class="noun">
      it
     </p>
</p>

<p>
<p class="other">
      to
     </p>
<p class="verb">
      find
     </p>
<p class="noun">
      them
     </p>
<p class="adverb">
      later
     </p>
     .
    </p>
</span>
</p>
</itemBody>"""

        self.assertEqual(
            str(item_body),
            expected_string
        )

        self.assertEqual(
            len(inline_choice_interaction.find_all('inlineChoice')),
            4
        )
        self.assertEqual(
            inline_choice_interaction['responseIdentifier'],
            'RESPONSE_1'
        )
        self.assertEqual(
            inline_choice_interaction['shuffle'],
            'false'
        )

        expected_choices = {
            "[_1_1": """<inlineChoice identifier="[_1_1">
<p class="adjective">
      easy
     </p>
</inlineChoice>""",
            "[_1_1_1": """<inlineChoice identifier="[_1_1_1">
<p class="adjective">
      neat
     </p>
</inlineChoice>""",
            "[_2_1_1": """<inlineChoice identifier="[_2_1_1">
<p class="adjective">
      fast
     </p>
</inlineChoice>""",
            "[_3_1_1": """<inlineChoice identifier="[_3_1_1">
<p class="adjective">
      good
     </p>
</inlineChoice>"""
        }

        for choice in inline_choice_interaction.find_all('simpleChoice'):
            choice_id = choice['identifier']
            self.assertEqual(
                str(choice),
                expected_choices[choice_id]
            )

    def test_can_add_question_to_existing_fill_in_the_blank_item_via_rest(self):
        url = '{0}/items'.format(self.url)
        payload = {
            "genusTypeId": str(QTI_ITEM_INLINE_CHOICE_INTERACTION_GENUS),
            "name": "Question 1",
            "description": "For testing"
        }
        req = self.app.post(url,
                            params=json.dumps(payload),
                            headers={'content-type': 'application/json'})
        self.ok(req)
        item = self.json(req)

        url = '{0}/items/{1}'.format(self.url, item['id'])

        payload = {
            "question": {
                "questionString": """<itemBody>
<p>
<span data-sheets-userformat=\"{\" data-sheets-value=\"{\">
<p>
<p class="other">
      Putting things away
     </p>
<p class="preposition">
      in
     </p>
<p class="other">
      the
     </p>
<p class="adjective">
      proper
     </p>
<p class="noun">
      place
     </p>
<p class="verb">
      makes
     </p>
<p class="noun">
      it
     </p>
</p>

<inlineChoiceInteraction responseIdentifier="RESPONSE_1" shuffle="false" />

<p>
<p class="other">
      to
     </p>
<p class="verb">
      find
     </p>
<p class="noun">
      them
     </p>
<p class="adverb">
      later
     </p>
     .
    </p>
</span>
</p>
</itemBody>""",
                "inlineRegions": {
                    "RESPONSE_1": {
                        "choices": [{
                            "id": "[_1_1",
                            "text": """<inlineChoice identifier="[_1_1"><p class="adjective">easy</p></inlineChoice>"""
                        }, {
                            "id": "[_1_1_1",
                            "text": """<inlineChoice identifier="[_1_1_1"><p class="adjective">neat</p></inlineChoice>"""
                        }, {
                            "id": "[_2_1_1",
                            "text": """<inlineChoice identifier="[_2_1_1"><p class="adjective">fast</p></inlineChoice>"""
                        }, {
                            "id": "[_3_1_1",
                            "text": """<inlineChoice identifier="[_3_1_1"><p class="adjective">good</p></inlineChoice>"""
                        }],
                    }
                },
                "genusTypeId": str(QTI_QUESTION_INLINE_CHOICE_INTERACTION_GENUS),
                "shuffle": True
            },
            "answers": [{
                "genusTypeId": str(RIGHT_ANSWER_GENUS),
                "choiceIds": ['[_1_1'],
                "region": "RESPONSE_1",
                "feedback": """  <modalFeedback  identifier="Feedback372632509" outcomeIdentifier="FEEDBACKMODAL" showHide="show">
<p>You are right! Please try the next question.</p>
</modalFeedback>"""
            }, {
                "genusTypeId": str(WRONG_ANSWER_GENUS),
                "choiceIds": [None],
                "region": "RESPONSE_1",
                "feedback": """  <modalFeedback  identifier="Feedback2014412711" outcomeIdentifier="FEEDBACKMODAL" showHide="show">
<p>Please try again.</p>
</modalFeedback>"""
            }]
        }

        req = self.app.put(url,
                           params=json.dumps(payload),
                           headers={'content-type': 'application/json'})
        self.ok(req)
        item = self.json(req)

        self.assertEqual(
            item['genusTypeId'],
            str(QTI_ITEM_INLINE_CHOICE_INTERACTION_GENUS)
        )

        self.assertEqual(
            item['question']['genusTypeId'],
            str(QTI_QUESTION_INLINE_CHOICE_INTERACTION_GENUS)
        )

        self.assertIn('RESPONSE_1', item['question']['choices'])

        response_1_choice_ids = [c['id'] for c in item['question']['choices']['RESPONSE_1']]

        self.assertIn('[_1_1', response_1_choice_ids)

        self.assertEqual(
            len(item['answers']),
            2
        )

        self.assertEqual(
            item['answers'][0]['genusTypeId'],
            str(RIGHT_ANSWER_GENUS)
        )
        self.assertIn('RESPONSE_1', item['answers'][0]['inlineRegions'])

        self.assertEqual(
            item['answers'][0]['inlineRegions']['RESPONSE_1']['choiceIds'],
            ['[_1_1']
        )
        self.assertIn('You are right! Please try the next question.', item['answers'][0]['feedbacks'][0]['text'])

        self.assertEqual(
            item['answers'][1]['genusTypeId'],
            str(WRONG_ANSWER_GENUS)
        )

        self.assertIn('Please try again.', item['answers'][1]['feedbacks'][0]['text'])

        self.assertNotEqual(
            item['id'],
            str(self._item.ident)
        )

        # now verify the QTI XML matches the JSON format
        url = '{0}/{1}/qti'.format(url, unquote(item['id']))
        req = self.app.get(url)
        self.ok(req)
        qti_xml = BeautifulSoup(req.body, 'lxml-xml').assessmentItem
        item_body = qti_xml.itemBody

        inline_choice_interaction = item_body.inlineChoiceInteraction.extract()

        expected_string = """<itemBody>
<p>
<span data-sheets-userformat=\"{\" data-sheets-value=\"{\">
<p>
<p class="other">
      Putting things away
     </p>
<p class="preposition">
      in
     </p>
<p class="other">
      the
     </p>
<p class="adjective">
      proper
     </p>
<p class="noun">
      place
     </p>
<p class="verb">
      makes
     </p>
<p class="noun">
      it
     </p>
</p>

<p>
<p class="other">
      to
     </p>
<p class="verb">
      find
     </p>
<p class="noun">
      them
     </p>
<p class="adverb">
      later
     </p>
     .
    </p>
</span>
</p>
</itemBody>"""

        self.assertEqual(
            str(item_body),
            expected_string
        )

        self.assertEqual(
            len(inline_choice_interaction.find_all('inlineChoice')),
            4
        )
        self.assertEqual(
            inline_choice_interaction['responseIdentifier'],
            'RESPONSE_1'
        )
        self.assertEqual(
            inline_choice_interaction['shuffle'],
            'false'
        )

        expected_choices = {
            "[_1_1": """<inlineChoice identifier="[_1_1">
<p class="adjective">
      easy
     </p>
</inlineChoice>""",
            "[_1_1_1": """<inlineChoice identifier="[_1_1_1">
<p class="adjective">
      neat
     </p>
</inlineChoice>""",
            "[_2_1_1": """<inlineChoice identifier="[_2_1_1">
<p class="adjective">
      fast
     </p>
</inlineChoice>""",
            "[_3_1_1": """<inlineChoice identifier="[_3_1_1">
<p class="adjective">
      good
     </p>
</inlineChoice>"""
        }

        for choice in inline_choice_interaction.find_all('simpleChoice'):
            choice_id = choice['identifier']
            self.assertEqual(
                str(choice),
                expected_choices[choice_id]
            )

    def test_can_get_fill_in_the_blank_item_with_no_choices(self):
        url = '{0}/items'.format(self.url)
        payload = {
            "genusTypeId": str(QTI_ITEM_INLINE_CHOICE_INTERACTION_GENUS),
            "name": "Question 1",
            "description": "For testing",
            "question": {
                "questionString": """<itemBody>
<p>
<span data-sheets-userformat=\"{\" data-sheets-value=\"{\">
<p>
<p class="other">
      Putting things away
     </p>
<p class="preposition">
      in
     </p>
<p class="other">
      the
     </p>
<p class="adjective">
      proper
     </p>
<p class="noun">
      place
     </p>
<p class="verb">
      makes
     </p>
<p class="noun">
      it
     </p>
</p>

<inlineChoiceInteraction responseIdentifier="RESPONSE_1" shuffle="false" />

<p>
<p class="other">
      to
     </p>
<p class="verb">
      find
     </p>
<p class="noun">
      them
     </p>
<p class="adverb">
      later
     </p>
     .
    </p>
</span>
</p>
</itemBody>"""}
        }
        req = self.app.post(url,
                            params=json.dumps(payload),
                            headers={'content-type': 'application/json'})
        self.ok(req)
        item = self.json(req)

        url = '{0}/items/{1}'.format(self.url, item['id'])
        req = self.app.get(url)
        self.ok(req)
        data = self.json(req)
        self.assertEqual(data['question']['choices'], {})

    def test_can_get_fill_in_the_blank_item_qti_with_no_answers(self):
        url = '{0}/items'.format(self.url)
        payload = {
            "genusTypeId": str(QTI_ITEM_INLINE_CHOICE_INTERACTION_GENUS),
            "name": "Question 1",
            "description": "For testing",
            "question": {
                "questionString": """<itemBody>
<p>
<span data-sheets-userformat=\"{\" data-sheets-value=\"{\">
<p>
<p class="other">
      Putting things away
     </p>
<p class="preposition">
      in
     </p>
<p class="other">
      the
     </p>
<p class="adjective">
      proper
     </p>
<p class="noun">
      place
     </p>
<p class="verb">
      makes
     </p>
<p class="noun">
      it
     </p>
</p>

<inlineChoiceInteraction responseIdentifier="RESPONSE_1" shuffle="false" />

<p>
<p class="other">
      to
     </p>
<p class="verb">
      find
     </p>
<p class="noun">
      them
     </p>
<p class="adverb">
      later
     </p>
     .
    </p>
</span>
</p>
</itemBody>"""}
        }
        req = self.app.post(url,
                            params=json.dumps(payload),
                            headers={'content-type': 'application/json'})
        self.ok(req)
        item = self.json(req)

        url = '{0}/items/{1}/qti'.format(self.url, item['id'])
        req = self.app.get(url)
        self.ok(req)
        qti = BeautifulSoup(req.body, 'xml')
        self.assertIsNone(qti.responseDeclaration)

    def test_getting_qti_for_fill_in_the_blank_with_no_question_returns_empty_string(self):
        url = '{0}/items'.format(self.url)
        payload = {
            "genusTypeId": str(QTI_ITEM_INLINE_CHOICE_INTERACTION_GENUS),
            "name": "Question 1",
            "description": "For testing"
        }
        req = self.app.post(url,
                            params=json.dumps(payload),
                            headers={'content-type': 'application/json'})
        self.ok(req)
        item = self.json(req)

        # now verify the QTI XML is empty string
        url = '{0}/{1}/qti'.format(url, unquote(item['id']))
        req = self.app.get(url)
        self.ok(req)
        self.assertEqual(req.body, '')

    def test_updating_fill_in_the_blank_answer_choices_clears_existing_choices(self):
        url = '{0}/items'.format(self.url)

        payload = {
            "genusTypeId": str(QTI_ITEM_INLINE_CHOICE_INTERACTION_GENUS),
            "name": "Question 1",
            "description": "For testing",
            "question": {
                "questionString": """<itemBody>
<p>
<span data-sheets-userformat=\"{\" data-sheets-value=\"{\">
<p>
<p class="other">
      Putting things away
     </p>
<p class="preposition">
      in
     </p>
<p class="other">
      the
     </p>
<p class="adjective">
      proper
     </p>
<p class="noun">
      place
     </p>
<p class="verb">
      makes
     </p>
<p class="noun">
      it
     </p>
</p>

<inlineChoiceInteraction responseIdentifier="RESPONSE_1" shuffle="false" />

<p>
<p class="other">
      to
     </p>
<p class="verb">
      find
     </p>
<p class="noun">
      them
     </p>
<p class="adverb">
      later
     </p>
     .
    </p>
</span>
</p>
</itemBody>""",
                "inlineRegions": {
                    "RESPONSE_1": {
                        "choices": [{
                            "id": "[_1_1",
                            "text": """<inlineChoice identifier="[_1_1"><p class="adjective">easy</p></inlineChoice>"""
                        }, {
                            "id": "[_1_1_1",
                            "text": """<inlineChoice identifier="[_1_1_1"><p class="adjective">neat</p></inlineChoice>"""
                        }, {
                            "id": "[_2_1_1",
                            "text": """<inlineChoice identifier="[_2_1_1"><p class="adjective">fast</p></inlineChoice>"""
                        }, {
                            "id": "[_3_1_1",
                            "text": """<inlineChoice identifier="[_3_1_1"><p class="adjective">good</p></inlineChoice>"""
                        }],
                    }
                },
                "genusTypeId": str(QTI_QUESTION_INLINE_CHOICE_INTERACTION_GENUS),
                "shuffle": True
            },
            "answers": [{
                "genusTypeId": str(RIGHT_ANSWER_GENUS),
                "choiceIds": ['[_1_1'],
                "region": "RESPONSE_1",
                "feedback": """  <modalFeedback  identifier="Feedback372632509" outcomeIdentifier="FEEDBACKMODAL" showHide="show">
<p>You are right! Please try the next question.</p>
</modalFeedback>"""
            }, {
                "genusTypeId": str(WRONG_ANSWER_GENUS),
                "choiceIds": [None],
                "region": "RESPONSE_1",
                "feedback": """  <modalFeedback  identifier="Feedback2014412711" outcomeIdentifier="FEEDBACKMODAL" showHide="show">
<p>Please try again.</p>
</modalFeedback>"""
            }]
        }

        req = self.app.post(url,
                            params=json.dumps(payload),
                            headers={'content-type': 'application/json'})
        self.ok(req)
        item = self.json(req)

        region = 'RESPONSE_1'

        right_answer = [a for a in item['answers'] if a['genusTypeId'] == str(RIGHT_ANSWER_GENUS)][0]
        previous_right_answer_choice = right_answer['inlineRegions'][region]['choiceIds'][0]
        new_right_answer_choice = '[_2_1_1'

        self.assertNotEqual(previous_right_answer_choice,
                            new_right_answer_choice)

        url = '{0}/{1}'.format(url, item['id'])
        payload = {
            'answers': [{
                'id': right_answer['id'],
                'choiceIds': [new_right_answer_choice],
                'region': region
            }]
        }
        req = self.app.put(url,
                           params=json.dumps(payload),
                           headers={'content-type': 'application/json'})
        self.ok(req)
        data = self.json(req)
        self.assertEqual(data['id'], item['id'])
        self.assertEqual(data['answers'][0]['id'], right_answer['id'])
        self.assertEqual(data['answers'][0]['genusTypeId'], str(RIGHT_ANSWER_GENUS))
        self.assertNotIn(previous_right_answer_choice,
                         data['answers'][0]['inlineRegions'][region]['choiceIds'])
        self.assertIn(new_right_answer_choice,
                      data['answers'][0]['inlineRegions'][region]['choiceIds'])
        self.assertEqual(len(data['answers'][0]['inlineRegions'][region]['choiceIds']), 1)

    def test_item_body_and_inline_choice_tags_provided_inline_choice(self):
        url = '{0}/items'.format(self.url)

        payload = {
            "genusTypeId": str(QTI_ITEM_INLINE_CHOICE_INTERACTION_GENUS),
            "name": "Question 1",
            "description": "For testing",
            "question": {
                "questionString": """<p>
<span data-sheets-userformat=\"{\" data-sheets-value=\"{\">
<p>
<p class="other">
      Putting things away
     </p>
<p class="preposition">
      in
     </p>
<p class="other">
      the
     </p>
<p class="adjective">
      proper
     </p>
<p class="noun">
      place
     </p>
<p class="verb">
      makes
     </p>
<p class="noun">
      it
     </p>
</p>

<inlineChoiceInteraction responseIdentifier="RESPONSE_1" shuffle="false" />

<p>
<p class="other">
      to
     </p>
<p class="verb">
      find
     </p>
<p class="noun">
      them
     </p>
<p class="adverb">
      later
     </p>
     .
    </p>
</span>
</p>""",
                "inlineRegions": {
                    "RESPONSE_1": {
                        "choices": [{
                            "id": "[_1_1",
                            "text": """<p class="adjective">easy</p>"""
                        }, {
                            "id": "[_1_1_1",
                            "text": """<p class="adjective">neat</p>"""
                        }, {
                            "id": "[_2_1_1",
                            "text": """<p class="adjective">fast</p>"""
                        }, {
                            "id": "[_3_1_1",
                            "text": """<p class="adjective">good</p>"""
                        }],
                    }
                },
                "genusTypeId": str(QTI_QUESTION_INLINE_CHOICE_INTERACTION_GENUS),
                "shuffle": True
            },
            "answers": [{
                "genusTypeId": str(RIGHT_ANSWER_GENUS),
                "choiceIds": ['[_1_1'],
                "region": "RESPONSE_1",
                "feedback": """  <modalFeedback  identifier="Feedback372632509" outcomeIdentifier="FEEDBACKMODAL" showHide="show">
<p>You are right! Please try the next question.</p>
</modalFeedback>"""
            }, {
                "genusTypeId": str(WRONG_ANSWER_GENUS),
                "choiceIds": [None],
                "region": "RESPONSE_1",
                "feedback": """  <modalFeedback  identifier="Feedback2014412711" outcomeIdentifier="FEEDBACKMODAL" showHide="show">
<p>Please try again.</p>
</modalFeedback>"""
            }]
        }

        req = self.app.post(url,
                            params=json.dumps(payload),
                            headers={'content-type': 'application/json'})
        self.ok(req)
        item = self.json(req)

        self.assertEqual(
            item['genusTypeId'],
            str(QTI_ITEM_INLINE_CHOICE_INTERACTION_GENUS)
        )

        self.assertEqual(
            item['question']['genusTypeId'],
            str(QTI_QUESTION_INLINE_CHOICE_INTERACTION_GENUS)
        )

        self.assertIn('RESPONSE_1', item['question']['choices'])

        response_1_choice_ids = [c['id'] for c in item['question']['choices']['RESPONSE_1']]

        self.assertIn('[_1_1', response_1_choice_ids)

        self.assertEqual(
            len(item['answers']),
            2
        )

        self.assertEqual(
            item['answers'][0]['genusTypeId'],
            str(RIGHT_ANSWER_GENUS)
        )
        self.assertIn('RESPONSE_1', item['answers'][0]['inlineRegions'])

        self.assertEqual(
            item['answers'][0]['inlineRegions']['RESPONSE_1']['choiceIds'],
            ['[_1_1']
        )
        self.assertIn('You are right! Please try the next question.', item['answers'][0]['feedbacks'][0]['text'])

        self.assertEqual(
            item['answers'][1]['genusTypeId'],
            str(WRONG_ANSWER_GENUS)
        )

        self.assertIn('Please try again.', item['answers'][1]['feedbacks'][0]['text'])

        self.assertNotEqual(
            item['id'],
            str(self._item.ident)
        )

        # now verify the QTI XML matches the JSON format
        url = '{0}/{1}/qti'.format(url, unquote(item['id']))
        req = self.app.get(url)
        self.ok(req)
        qti_xml = BeautifulSoup(req.body, 'lxml-xml').assessmentItem
        item_body = qti_xml.itemBody

        inline_choice_interaction = item_body.inlineChoiceInteraction.extract()

        expected_string = """<itemBody>
<p>
<span data-sheets-userformat=\"{\" data-sheets-value=\"{\">
<p>
<p class="other">
      Putting things away
     </p>
<p class="preposition">
      in
     </p>
<p class="other">
      the
     </p>
<p class="adjective">
      proper
     </p>
<p class="noun">
      place
     </p>
<p class="verb">
      makes
     </p>
<p class="noun">
      it
     </p>
</p>

<p>
<p class="other">
      to
     </p>
<p class="verb">
      find
     </p>
<p class="noun">
      them
     </p>
<p class="adverb">
      later
     </p>
     .
    </p>
</span>
</p>
</itemBody>"""

        self.assertEqual(
            str(item_body),
            expected_string
        )

        self.assertEqual(
            len(inline_choice_interaction.find_all('inlineChoice')),
            4
        )
        self.assertEqual(
            inline_choice_interaction['responseIdentifier'],
            'RESPONSE_1'
        )
        self.assertEqual(
            inline_choice_interaction['shuffle'],
            'false'
        )

        expected_choices = {
            "[_1_1": """<inlineChoice identifier="[_1_1">
<p class="adjective">
      easy
     </p>
</inlineChoice>""",
            "[_1_1_1": """<inlineChoice identifier="[_1_1_1">
<p class="adjective">
      neat
     </p>
</inlineChoice>""",
            "[_2_1_1": """<inlineChoice identifier="[_2_1_1">
<p class="adjective">
      fast
     </p>
</inlineChoice>""",
            "[_3_1_1": """<inlineChoice identifier="[_3_1_1">
<p class="adjective">
      good
     </p>
</inlineChoice>"""
        }

        for choice in inline_choice_interaction.find_all('simpleChoice'):
            choice_id = choice['identifier']
            self.assertEqual(
                str(choice),
                expected_choices[choice_id]
            )

    def test_can_create_short_answer_question_via_rest(self):
        media_files = [self._shapes_image]

        assets = {}
        for media_file in media_files:
            label = self._label(self._filename(media_file))
            assets[label] = self.upload_media_file(media_file)

        url = '{0}/items'.format(self.url)

        payload = {
            "genusTypeId": str(QTI_ITEM_EXTENDED_TEXT_INTERACTION_GENUS),
            "name": "Question 1",
            "description": "For testing",
            "question": {
                "questionString": """<itemBody>
<p>
<strong>
<span id="docs-internal-guid-46f83555-04bd-94f0-a53d-94c5c97ab6e6">
     Which of the following figure(s) is/are parallelogram(s)? Give a reason for your choice.
    </span>
<br/>
</strong>
</p>
<p>
<strong>
<img alt="A set of four shapes." height="204" src="AssetContent:shapes_png" width="703"/>
</strong>
</p>
</itemBody>""",
                "maxStrings": 300,
                "expectedLength": 100,
                "expectedLines": 5,
                "genusTypeId": str(QTI_QUESTION_EXTENDED_TEXT_INTERACTION_GENUS),
                "fileIds": {}
            },
            "answers": [{
                "genusTypeId": str(RIGHT_ANSWER_GENUS),
                "choiceIds": ["idc561552b-ed48-46c3-b20d-873150dfd4a2"],
                "feedback": """<modalFeedback  identifier="Feedback933928139" outcomeIdentifier="FEEDBACKMODAL" showHide="show">
<p></p>
</modalFeedback>"""
            }]
        }

        for label, asset in assets.iteritems():
            payload['question']['fileIds'][label] = {}
            payload['question']['fileIds'][label]['assetId'] = asset['id']
            payload['question']['fileIds'][label]['assetContentId'] = asset['assetContents'][0]['id']
            payload['question']['fileIds'][label]['assetContentTypeId'] = asset['assetContents'][0]['genusTypeId']

        req = self.app.post(url,
                            params=json.dumps(payload),
                            headers={'content-type': 'application/json'})
        self.ok(req)
        item = self.json(req)

        self.assertEqual(
            item['genusTypeId'],
            str(QTI_ITEM_EXTENDED_TEXT_INTERACTION_GENUS)
        )

        self.assertEqual(
            item['question']['genusTypeId'],
            str(QTI_QUESTION_EXTENDED_TEXT_INTERACTION_GENUS)
        )

        self.assertEqual(
            len(item['answers']),
            1
        )

        self.assertEqual(
            item['answers'][0]['genusTypeId'],
            str(RIGHT_ANSWER_GENUS)
        )

        self.assertIn('<p></p>', item['answers'][0]['feedbacks'][0]['text'])

        self.assertNotEqual(
            item['id'],
            str(self._item.ident)
        )

        self.assertEqual(item['question']['maxStrings'], 300)
        self.assertEqual(item['question']['expectedLength'], 100)
        self.assertEqual(item['question']['expectedLines'], 5)

        # now verify the QTI XML matches the JSON format
        url = '{0}/{1}/qti'.format(url, unquote(item['id']))
        req = self.app.get(url)
        self.ok(req)
        qti_xml = BeautifulSoup(req.body, 'lxml-xml').assessmentItem
        item_body = qti_xml.itemBody
        asset_label = item['question']['fileIds'].keys()[0]
        asset_id = item['question']['fileIds'][asset_label]['assetId']
        asset_content_id = item['question']['fileIds'][asset_label]['assetContentId']

        expected_string = """<itemBody>
<p>
<strong>
<span id="docs-internal-guid-46f83555-04bd-94f0-a53d-94c5c97ab6e6">
     Which of the following figure(s) is/are parallelogram(s)? Give a reason for your choice.
    </span>
<br/>
</strong>
</p>
<p>
<strong>
<img alt="A set of four shapes." height="204" src="/api/v1/repository/repositories/{0}/assets/{1}/contents/{2}/stream" width="703"/>
</strong>
</p>
<extendedTextInteraction expectedLength="100" expectedLines="5" maxStrings="300" responseIdentifier="RESPONSE_1"/>
</itemBody>""".format(str(self._bank.ident).replace('assessment.Bank', 'repository.Repository'),
                      asset_id,
                      asset_content_id)
        self.assertEqual(
            str(item_body),
            expected_string
        )

    def test_can_add_question_to_existing_short_answer_item_via_rest(self):
        url = '{0}/items'.format(self.url)

        payload = {
            "genusTypeId": str(QTI_ITEM_EXTENDED_TEXT_INTERACTION_GENUS),
            "name": "Question 1",
            "description": "For testing"
        }

        req = self.app.post(url,
                            params=json.dumps(payload),
                            headers={'content-type': 'application/json'})
        self.ok(req)
        item = self.json(req)

        media_files = [self._shapes_image]

        assets = {}
        for media_file in media_files:
            label = self._label(self._filename(media_file))
            assets[label] = self.upload_media_file(media_file)

        url = '{0}/items/{1}'.format(self.url, item['id'])

        payload = {
            "question": {
                "questionString": """<itemBody>
<p>
<strong>
<span id="docs-internal-guid-46f83555-04bd-94f0-a53d-94c5c97ab6e6">
     Which of the following figure(s) is/are parallelogram(s)? Give a reason for your choice.
    </span>
<br/>
</strong>
</p>
<p>
<strong>
<img alt="A set of four shapes." height="204" src="AssetContent:shapes_png" width="703"/>
</strong>
</p>
</itemBody>""",
                "maxStrings": 300,
                "expectedLength": 100,
                "expectedLines": 5,
                "genusTypeId": str(QTI_QUESTION_EXTENDED_TEXT_INTERACTION_GENUS),
                "fileIds": {}
            },
            "answers": [{
                "genusTypeId": str(RIGHT_ANSWER_GENUS),
                "choiceIds": ["idc561552b-ed48-46c3-b20d-873150dfd4a2"],
                "feedback": """<modalFeedback  identifier="Feedback933928139" outcomeIdentifier="FEEDBACKMODAL" showHide="show">
<p></p>
</modalFeedback>"""
            }]
        }

        for label, asset in assets.iteritems():
            payload['question']['fileIds'][label] = {}
            payload['question']['fileIds'][label]['assetId'] = asset['id']
            payload['question']['fileIds'][label]['assetContentId'] = asset['assetContents'][0]['id']
            payload['question']['fileIds'][label]['assetContentTypeId'] = asset['assetContents'][0]['genusTypeId']

        req = self.app.put(url,
                           params=json.dumps(payload),
                           headers={'content-type': 'application/json'})
        self.ok(req)
        item = self.json(req)

        self.assertEqual(
            item['genusTypeId'],
            str(QTI_ITEM_EXTENDED_TEXT_INTERACTION_GENUS)
        )

        self.assertEqual(
            item['question']['genusTypeId'],
            str(QTI_QUESTION_EXTENDED_TEXT_INTERACTION_GENUS)
        )

        self.assertEqual(
            len(item['answers']),
            1
        )

        self.assertEqual(
            item['answers'][0]['genusTypeId'],
            str(RIGHT_ANSWER_GENUS)
        )

        self.assertIn('<p></p>', item['answers'][0]['feedbacks'][0]['text'])

        self.assertNotEqual(
            item['id'],
            str(self._item.ident)
        )

        self.assertEqual(item['question']['maxStrings'], 300)
        self.assertEqual(item['question']['expectedLength'], 100)
        self.assertEqual(item['question']['expectedLines'], 5)

        # now verify the QTI XML matches the JSON format
        url = '{0}/{1}/qti'.format(url, unquote(item['id']))
        req = self.app.get(url)
        self.ok(req)
        qti_xml = BeautifulSoup(req.body, 'lxml-xml').assessmentItem
        item_body = qti_xml.itemBody
        asset_label = item['question']['fileIds'].keys()[0]
        asset_id = item['question']['fileIds'][asset_label]['assetId']
        asset_content_id = item['question']['fileIds'][asset_label]['assetContentId']

        expected_string = """<itemBody>
<p>
<strong>
<span id="docs-internal-guid-46f83555-04bd-94f0-a53d-94c5c97ab6e6">
     Which of the following figure(s) is/are parallelogram(s)? Give a reason for your choice.
    </span>
<br/>
</strong>
</p>
<p>
<strong>
<img alt="A set of four shapes." height="204" src="/api/v1/repository/repositories/{0}/assets/{1}/contents/{2}/stream" width="703"/>
</strong>
</p>
<extendedTextInteraction expectedLength="100" expectedLines="5" maxStrings="300" responseIdentifier="RESPONSE_1"/>
</itemBody>""".format(str(self._bank.ident).replace('assessment.Bank', 'repository.Repository'),
                      asset_id,
                      asset_content_id)
        self.assertEqual(
            str(item_body),
            expected_string
        )

    def test_can_get_short_answer_item_qti_with_no_answers(self):
        url = '{0}/items'.format(self.url)

        payload = {
            "genusTypeId": str(QTI_ITEM_EXTENDED_TEXT_INTERACTION_GENUS),
            "name": "Question 1",
            "description": "For testing",
            "question": {
                "questionString": """<itemBody>
<p>
<strong>
<span id="docs-internal-guid-46f83555-04bd-94f0-a53d-94c5c97ab6e6">
     Which of the following figure(s) is/are parallelogram(s)? Give a reason for your choice.
    </span>
<br/>
</strong>
</p>
<p>
<strong>
<img alt="A set of four shapes." height="204" src="AssetContent:shapes_png" width="703"/>
</strong>
</p>
</itemBody>"""}
        }

        req = self.app.post(url,
                            params=json.dumps(payload),
                            headers={'content-type': 'application/json'})
        self.ok(req)
        item = self.json(req)

        url = '{0}/items/{1}/qti'.format(self.url, item['id'])

        req = self.app.get(url)
        self.ok(req)
        qti = BeautifulSoup(req.body, 'xml')
        self.assertIsNotNone(qti.responseDeclaration)

    def test_getting_qti_for_short_answer_item_with_no_question_returns_empty_string(self):
        url = '{0}/items'.format(self.url)

        payload = {
            "genusTypeId": str(QTI_ITEM_EXTENDED_TEXT_INTERACTION_GENUS),
            "name": "Question 1",
            "description": "For testing"
        }

        req = self.app.post(url,
                            params=json.dumps(payload),
                            headers={'content-type': 'application/json'})
        self.ok(req)
        item = self.json(req)
        url = '{0}/{1}/qti'.format(url, unquote(item['id']))
        req = self.app.get(url)
        self.ok(req)
        self.assertEqual(req.body, '')

    def test_can_create_image_sequence_question_via_rest(self):
        media_files = [self._audio_test_file,
                       self._picture1,
                       self._picture2,
                       self._picture3,
                       self._picture4]

        assets = {}
        for media_file in media_files:
            label = self._label(self._filename(media_file))
            assets[label] = self.upload_media_file(media_file)

        url = '{0}/items'.format(self.url)

        payload = {
            "genusTypeId": str(QTI_ITEM_ORDER_INTERACTION_OBJECT_MANIPULATION_GENUS),
            "name": "Question 1",
            "description": "For testing",
            "question": {
                "questionString": """<itemBody>
<p>
   Listen to each audio clip and put the pictures of the story in order.
  </p>
<p>
<audio autoplay="autoplay" controls="controls" style="width: 125px">
<source src="AssetContent:audioTestFile__mp3" type="audio/mpeg"/>
</audio>
</p>

</itemBody>""",
                "choices": [{
                    "id": "idb4f6cd03-cf58-4391-9ca2-44b7bded3d4b",
                    "text": """<simpleChoice identifier="idb4f6cd03-cf58-4391-9ca2-44b7bded3d4b">
<p>
  <img src="AssetContent:Picture1_png" alt="Picture 1" width="100" height="100" />
</p>
</simpleChoice>"""
                }, {
                    "id": "id127df214-2a19-44da-894a-853948313dae",
                    "text": """<simpleChoice identifier="id127df214-2a19-44da-894a-853948313dae">
<p>
  <img src="AssetContent:Picture2_png" alt="Picture 2" width="100" height="100" />
</p>
</simpleChoice>"""
                }, {
                    "id": "iddcbf40ab-782e-4d4f-9020-6b8414699a72",
                    "text": """<simpleChoice identifier="iddcbf40ab-782e-4d4f-9020-6b8414699a72">
<p>
  <img src="AssetContent:Picture3_png" alt="Picture 3" width="100" height="100" />
</p>
</simpleChoice>"""
                }, {
                    "id": "ide576c9cc-d20e-4ba3-8881-716100b796a0",
                    "text": """<simpleChoice identifier="ide576c9cc-d20e-4ba3-8881-716100b796a0">
<p>
  <img src="AssetContent:Picture4_png" alt="Picture 4" width="100" height="100" />
</p>
</simpleChoice>"""
                }],
                "genusTypeId": str(QTI_QUESTION_ORDER_INTERACTION_OBJECT_MANIPULATION_GENUS),
                "shuffle": True,
                "fileIds": {}
            },
            "answers": [{
                "genusTypeId": str(RIGHT_ANSWER_GENUS),
                "choiceIds": ['id127df214-2a19-44da-894a-853948313dae',
                              'iddcbf40ab-782e-4d4f-9020-6b8414699a72',
                              'idb4f6cd03-cf58-4391-9ca2-44b7bded3d4b',
                              'ide576c9cc-d20e-4ba3-8881-716100b796a0'],
                "feedback": """<modalFeedback  identifier="Feedback933928139" outcomeIdentifier="FEEDBACKMODAL" showHide="show">
  <p id="docs-internal-guid-46f83555-04cc-a70f-2574-1b5c79fe206e" dir="ltr">You are correct! A square has the properties of both a rectangle, and a rhombus. Hence, it can also occupy the shaded region.</p>
</modalFeedback>"""
            }]
        }

        for label, asset in assets.iteritems():
            payload['question']['fileIds'][label] = {}
            payload['question']['fileIds'][label]['assetId'] = asset['id']
            payload['question']['fileIds'][label]['assetContentId'] = asset['assetContents'][0]['id']
            payload['question']['fileIds'][label]['assetContentTypeId'] = asset['assetContents'][0]['genusTypeId']

        req = self.app.post(url,
                            params=json.dumps(payload),
                            headers={'content-type': 'application/json'})
        self.ok(req)
        item = self.json(req)

        self.assertEqual(
            item['genusTypeId'],
            str(QTI_ITEM_ORDER_INTERACTION_OBJECT_MANIPULATION_GENUS)
        )

        self.assertEqual(
            item['question']['genusTypeId'],
            str(QTI_QUESTION_ORDER_INTERACTION_OBJECT_MANIPULATION_GENUS)
        )

        self.assertEqual(
            item['answers'][0]['genusTypeId'],
            str(RIGHT_ANSWER_GENUS)
        )
        self.assertEqual(
            len(item['answers'][0]['choiceIds']),
            4
        )
        self.assertEqual(
            len(item['question']['choices']),
            4
        )

        self.assertNotEqual(
            item['id'],
            str(self._item.ident)
        )

        url = '{0}/{1}/qti'.format(url, unquote(item['id']))
        req = self.app.get(url)
        self.ok(req)
        item_qti = BeautifulSoup(req.body, 'lxml-xml').assessmentItem
        expected_values = ['id127df214-2a19-44da-894a-853948313dae',
                           'iddcbf40ab-782e-4d4f-9020-6b8414699a72',
                           'idb4f6cd03-cf58-4391-9ca2-44b7bded3d4b',
                           'ide576c9cc-d20e-4ba3-8881-716100b796a0']
        for index, value in enumerate(item_qti.responseDeclaration.correctResponse.find_all('value')):
            self.assertEqual(value.string.strip(), expected_values[index])

        item_body = item_qti.itemBody

        order_interaction = item_body.orderInteraction.extract()

        repository_id = str(self._bank.ident).replace('assessment.Bank', 'repository.Repository')
        audio_asset_label = 'audioTestFile__mp3'
        image_1_asset_label = 'Picture1_png'
        image_2_asset_label = 'Picture2_png'
        image_3_asset_label = 'Picture3_png'
        image_4_asset_label = 'Picture4_png'
        audio_asset_id = item['question']['fileIds'][audio_asset_label]['assetId']
        audio_asset_content_id = item['question']['fileIds'][audio_asset_label]['assetContentId']
        image_1_asset_id = item['question']['fileIds'][image_1_asset_label]['assetId']
        image_1_asset_content_id = item['question']['fileIds'][image_1_asset_label]['assetContentId']
        image_2_asset_id = item['question']['fileIds'][image_2_asset_label]['assetId']
        image_2_asset_content_id = item['question']['fileIds'][image_2_asset_label]['assetContentId']
        image_3_asset_id = item['question']['fileIds'][image_3_asset_label]['assetId']
        image_3_asset_content_id = item['question']['fileIds'][image_3_asset_label]['assetContentId']
        image_4_asset_id = item['question']['fileIds'][image_4_asset_label]['assetId']
        image_4_asset_content_id = item['question']['fileIds'][image_4_asset_label]['assetContentId']

        expected_string = """<itemBody>
<p>
   Listen to each audio clip and put the pictures of the story in order.
  </p>
<p>
<audio autoplay="autoplay" controls="controls" style="width: 125px">
<source src="/api/v1/repository/repositories/{0}/assets/{1}/contents/{2}/stream" type="audio/mpeg"/>
</audio>
</p>

</itemBody>""".format(repository_id,
                      audio_asset_id,
                      audio_asset_content_id)

        self.assertEqual(
            str(item_body),
            expected_string
        )

        self.assertEqual(
            len(order_interaction.find_all('simpleChoice')),
            4
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
            "idb4f6cd03-cf58-4391-9ca2-44b7bded3d4b": """<simpleChoice identifier="idb4f6cd03-cf58-4391-9ca2-44b7bded3d4b">
<p>
<img alt="Picture 1" height="100" src="/api/v1/repository/repositories/{0}/assets/{1}/contents/{2}/stream" width="100"/>
</p>
</simpleChoice>""".format(repository_id,
                          image_1_asset_id,
                          image_1_asset_content_id),
            "id127df214-2a19-44da-894a-853948313dae": """<simpleChoice identifier="id127df214-2a19-44da-894a-853948313dae">
<p>
<img alt="Picture 2" height="100" src="/api/v1/repository/repositories/{0}/assets/{1}/contents/{2}/stream" width="100"/>
</p>
</simpleChoice>""".format(repository_id,
                          image_2_asset_id,
                          image_2_asset_content_id),
            "iddcbf40ab-782e-4d4f-9020-6b8414699a72": """<simpleChoice identifier="iddcbf40ab-782e-4d4f-9020-6b8414699a72">
<p>
<img alt="Picture 3" height="100" src="/api/v1/repository/repositories/{0}/assets/{1}/contents/{2}/stream" width="100"/>
</p>
</simpleChoice>""".format(repository_id,
                          image_3_asset_id,
                          image_3_asset_content_id),
            "ide576c9cc-d20e-4ba3-8881-716100b796a0": """<simpleChoice identifier="ide576c9cc-d20e-4ba3-8881-716100b796a0">
<p>
<img alt="Picture 4" height="100" src="/api/v1/repository/repositories/{0}/assets/{1}/contents/{2}/stream" width="100"/>
</p>
</simpleChoice>""".format(repository_id,
                          image_4_asset_id,
                          image_4_asset_content_id)
        }

        for choice in order_interaction.find_all('simpleChoice'):
            choice_id = choice['identifier']
            self.assertEqual(
                str(choice),
                expected_choices[choice_id]
            )

    def test_can_add_question_to_existing_image_sequence_item_via_rest(self):
        url = '{0}/items'.format(self.url)

        payload = {
            "genusTypeId": str(QTI_ITEM_ORDER_INTERACTION_OBJECT_MANIPULATION_GENUS),
            "name": "Question 1",
            "description": "For testing"
        }

        req = self.app.post(url,
                            params=json.dumps(payload),
                            headers={'content-type': 'application/json'})
        self.ok(req)
        item = self.json(req)

        media_files = [self._audio_test_file,
                       self._picture1,
                       self._picture2,
                       self._picture3,
                       self._picture4]

        assets = {}
        for media_file in media_files:
            label = self._label(self._filename(media_file))
            assets[label] = self.upload_media_file(media_file)

        url = '{0}/items/{1}'.format(self.url, item['id'])

        payload = {
            "question": {
                "questionString": """<itemBody>
<p>
   Listen to each audio clip and put the pictures of the story in order.
  </p>
<p>
<audio autoplay="autoplay" controls="controls" style="width: 125px">
<source src="AssetContent:audioTestFile__mp3" type="audio/mpeg"/>
</audio>
</p>

</itemBody>""",
                "choices": [{
                    "id": "idb4f6cd03-cf58-4391-9ca2-44b7bded3d4b",
                    "text": """<simpleChoice identifier="idb4f6cd03-cf58-4391-9ca2-44b7bded3d4b">
<p>
  <img src="AssetContent:Picture1_png" alt="Picture 1" width="100" height="100" />
</p>
</simpleChoice>"""
                }, {
                    "id": "id127df214-2a19-44da-894a-853948313dae",
                    "text": """<simpleChoice identifier="id127df214-2a19-44da-894a-853948313dae">
<p>
  <img src="AssetContent:Picture2_png" alt="Picture 2" width="100" height="100" />
</p>
</simpleChoice>"""
                }, {
                    "id": "iddcbf40ab-782e-4d4f-9020-6b8414699a72",
                    "text": """<simpleChoice identifier="iddcbf40ab-782e-4d4f-9020-6b8414699a72">
<p>
  <img src="AssetContent:Picture3_png" alt="Picture 3" width="100" height="100" />
</p>
</simpleChoice>"""
                }, {
                    "id": "ide576c9cc-d20e-4ba3-8881-716100b796a0",
                    "text": """<simpleChoice identifier="ide576c9cc-d20e-4ba3-8881-716100b796a0">
<p>
  <img src="AssetContent:Picture4_png" alt="Picture 4" width="100" height="100" />
</p>
</simpleChoice>"""
                }],
                "genusTypeId": str(QTI_QUESTION_ORDER_INTERACTION_OBJECT_MANIPULATION_GENUS),
                "shuffle": True,
                "fileIds": {}
            },
            "answers": [{
                "genusTypeId": str(RIGHT_ANSWER_GENUS),
                "choiceIds": ['id127df214-2a19-44da-894a-853948313dae',
                              'iddcbf40ab-782e-4d4f-9020-6b8414699a72',
                              'idb4f6cd03-cf58-4391-9ca2-44b7bded3d4b',
                              'ide576c9cc-d20e-4ba3-8881-716100b796a0'],
                "feedback": """<modalFeedback  identifier="Feedback933928139" outcomeIdentifier="FEEDBACKMODAL" showHide="show">
  <p id="docs-internal-guid-46f83555-04cc-a70f-2574-1b5c79fe206e" dir="ltr">You are correct! A square has the properties of both a rectangle, and a rhombus. Hence, it can also occupy the shaded region.</p>
</modalFeedback>"""
            }]
        }

        for label, asset in assets.iteritems():
            payload['question']['fileIds'][label] = {}
            payload['question']['fileIds'][label]['assetId'] = asset['id']
            payload['question']['fileIds'][label]['assetContentId'] = asset['assetContents'][0]['id']
            payload['question']['fileIds'][label]['assetContentTypeId'] = asset['assetContents'][0]['genusTypeId']

        req = self.app.put(url,
                           params=json.dumps(payload),
                           headers={'content-type': 'application/json'})
        self.ok(req)
        item = self.json(req)

        self.assertEqual(
            item['genusTypeId'],
            str(QTI_ITEM_ORDER_INTERACTION_OBJECT_MANIPULATION_GENUS)
        )

        self.assertEqual(
            item['question']['genusTypeId'],
            str(QTI_QUESTION_ORDER_INTERACTION_OBJECT_MANIPULATION_GENUS)
        )

        self.assertEqual(
            item['answers'][0]['genusTypeId'],
            str(RIGHT_ANSWER_GENUS)
        )
        self.assertEqual(
            len(item['answers'][0]['choiceIds']),
            4
        )
        self.assertEqual(
            len(item['question']['choices']),
            4
        )

        self.assertNotEqual(
            item['id'],
            str(self._item.ident)
        )

        url = '{0}/{1}/qti'.format(url, unquote(item['id']))
        req = self.app.get(url)
        self.ok(req)
        item_qti = BeautifulSoup(req.body, 'lxml-xml').assessmentItem
        expected_values = ['id127df214-2a19-44da-894a-853948313dae',
                           'iddcbf40ab-782e-4d4f-9020-6b8414699a72',
                           'idb4f6cd03-cf58-4391-9ca2-44b7bded3d4b',
                           'ide576c9cc-d20e-4ba3-8881-716100b796a0']
        for index, value in enumerate(item_qti.responseDeclaration.correctResponse.find_all('value')):
            self.assertEqual(value.string.strip(), expected_values[index])

        item_body = item_qti.itemBody

        order_interaction = item_body.orderInteraction.extract()

        repository_id = str(self._bank.ident).replace('assessment.Bank', 'repository.Repository')
        audio_asset_label = 'audioTestFile__mp3'
        image_1_asset_label = 'Picture1_png'
        image_2_asset_label = 'Picture2_png'
        image_3_asset_label = 'Picture3_png'
        image_4_asset_label = 'Picture4_png'
        audio_asset_id = item['question']['fileIds'][audio_asset_label]['assetId']
        audio_asset_content_id = item['question']['fileIds'][audio_asset_label]['assetContentId']
        image_1_asset_id = item['question']['fileIds'][image_1_asset_label]['assetId']
        image_1_asset_content_id = item['question']['fileIds'][image_1_asset_label]['assetContentId']
        image_2_asset_id = item['question']['fileIds'][image_2_asset_label]['assetId']
        image_2_asset_content_id = item['question']['fileIds'][image_2_asset_label]['assetContentId']
        image_3_asset_id = item['question']['fileIds'][image_3_asset_label]['assetId']
        image_3_asset_content_id = item['question']['fileIds'][image_3_asset_label]['assetContentId']
        image_4_asset_id = item['question']['fileIds'][image_4_asset_label]['assetId']
        image_4_asset_content_id = item['question']['fileIds'][image_4_asset_label]['assetContentId']

        expected_string = """<itemBody>
<p>
   Listen to each audio clip and put the pictures of the story in order.
  </p>
<p>
<audio autoplay="autoplay" controls="controls" style="width: 125px">
<source src="/api/v1/repository/repositories/{0}/assets/{1}/contents/{2}/stream" type="audio/mpeg"/>
</audio>
</p>

</itemBody>""".format(repository_id,
                      audio_asset_id,
                      audio_asset_content_id)

        self.assertEqual(
            str(item_body),
            expected_string
        )

        expected_json_string = """<itemBody>
<p>
   Listen to each audio clip and put the pictures of the story in order.
  </p>
<p>
<audio autoplay="autoplay" controls="controls" style="width: 125px">
<source src="/api/v1/repository/repositories/{0}/assets/{1}/contents/{2}/stream" type="audio/mpeg"/>
</audio>
</p>
</itemBody>""".format(repository_id,
                      audio_asset_id,
                      audio_asset_content_id)
        self.assertEqual(
            item['question']['text']['text'],
            expected_json_string
        )

        self.assertEqual(
            len(order_interaction.find_all('simpleChoice')),
            4
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
            "idb4f6cd03-cf58-4391-9ca2-44b7bded3d4b": """<simpleChoice identifier="idb4f6cd03-cf58-4391-9ca2-44b7bded3d4b">
<p>
<img alt="Picture 1" height="100" src="/api/v1/repository/repositories/{0}/assets/{1}/contents/{2}/stream" width="100"/>
</p>
</simpleChoice>""".format(repository_id,
                          image_1_asset_id,
                          image_1_asset_content_id),
            "id127df214-2a19-44da-894a-853948313dae": """<simpleChoice identifier="id127df214-2a19-44da-894a-853948313dae">
<p>
<img alt="Picture 2" height="100" src="/api/v1/repository/repositories/{0}/assets/{1}/contents/{2}/stream" width="100"/>
</p>
</simpleChoice>""".format(repository_id,
                          image_2_asset_id,
                          image_2_asset_content_id),
            "iddcbf40ab-782e-4d4f-9020-6b8414699a72": """<simpleChoice identifier="iddcbf40ab-782e-4d4f-9020-6b8414699a72">
<p>
<img alt="Picture 3" height="100" src="/api/v1/repository/repositories/{0}/assets/{1}/contents/{2}/stream" width="100"/>
</p>
</simpleChoice>""".format(repository_id,
                          image_3_asset_id,
                          image_3_asset_content_id),
            "ide576c9cc-d20e-4ba3-8881-716100b796a0": """<simpleChoice identifier="ide576c9cc-d20e-4ba3-8881-716100b796a0">
<p>
<img alt="Picture 4" height="100" src="/api/v1/repository/repositories/{0}/assets/{1}/contents/{2}/stream" width="100"/>
</p>
</simpleChoice>""".format(repository_id,
                          image_4_asset_id,
                          image_4_asset_content_id)
        }

        for choice in order_interaction.find_all('simpleChoice'):
            choice_id = choice['identifier']
            self.assertEqual(
                str(choice),
                expected_choices[choice_id]
            )
        for choice in item['question']['choices']:
            self.assertEqual(
                choice['text'],
                expected_choices[choice['id']]
            )

    def test_can_get_image_sequence_item_with_no_choices(self):
        url = '{0}/items'.format(self.url)

        media_files = [self._audio_test_file]

        assets = {}
        for media_file in media_files:
            label = self._label(self._filename(media_file))
            assets[label] = self.upload_media_file(media_file)

        payload = {
            "genusTypeId": str(QTI_ITEM_ORDER_INTERACTION_OBJECT_MANIPULATION_GENUS),
            "name": "Question 1",
            "description": "For testing",
            "question": {
                "questionString": """<itemBody>
<p>
   Listen to each audio clip and put the pictures of the story in order.
  </p>
<p>
<audio autoplay="autoplay" controls="controls" style="width: 125px">
<source src="AssetContent:audioTestFile__mp3" type="audio/mpeg"/>
</audio>
</p>

</itemBody>""",
                "fileIds": {}}
        }

        for label, asset in assets.iteritems():
            payload['question']['fileIds'][label] = {}
            payload['question']['fileIds'][label]['assetId'] = asset['id']
            payload['question']['fileIds'][label]['assetContentId'] = asset['assetContents'][0]['id']
            payload['question']['fileIds'][label]['assetContentTypeId'] = asset['assetContents'][0]['genusTypeId']

        req = self.app.post(url,
                            params=json.dumps(payload),
                            headers={'content-type': 'application/json'})
        self.ok(req)
        item = self.json(req)

        url = '{0}/{1}'.format(url, unquote(item['id']))
        req = self.app.get(url)
        self.ok(req)
        data = self.json(req)
        self.assertEqual(data['question']['choices'], [])

    def test_can_get_image_sequence_item_qti_with_no_answers(self):
        url = '{0}/items'.format(self.url)

        media_files = [self._audio_test_file]

        assets = {}
        for media_file in media_files:
            label = self._label(self._filename(media_file))
            assets[label] = self.upload_media_file(media_file)

        payload = {
            "genusTypeId": str(QTI_ITEM_ORDER_INTERACTION_OBJECT_MANIPULATION_GENUS),
            "name": "Question 1",
            "description": "For testing",
            "question": {
                "questionString": """<itemBody>
<p>
   Listen to each audio clip and put the pictures of the story in order.
  </p>
<p>
<audio autoplay="autoplay" controls="controls" style="width: 125px">
<source src="AssetContent:audioTestFile__mp3" type="audio/mpeg"/>
</audio>
</p>

</itemBody>""",
                "fileIds": {}}
        }

        for label, asset in assets.iteritems():
            payload['question']['fileIds'][label] = {}
            payload['question']['fileIds'][label]['assetId'] = asset['id']
            payload['question']['fileIds'][label]['assetContentId'] = asset['assetContents'][0]['id']
            payload['question']['fileIds'][label]['assetContentTypeId'] = asset['assetContents'][0]['genusTypeId']

        req = self.app.post(url,
                            params=json.dumps(payload),
                            headers={'content-type': 'application/json'})
        self.ok(req)
        item = self.json(req)

        url = '{0}/{1}/qti'.format(url, unquote(item['id']))
        req = self.app.get(url)
        self.ok(req)
        qti = BeautifulSoup(req.body, 'xml')
        self.assertIsNone(qti.responseDeclaration)

    def test_getting_qti_for_image_sequence_with_no_question_returns_empty_string(self):
        url = '{0}/items'.format(self.url)

        payload = {
            "genusTypeId": str(QTI_ITEM_ORDER_INTERACTION_OBJECT_MANIPULATION_GENUS),
            "name": "Question 1",
            "description": "For testing"
        }

        req = self.app.post(url,
                            params=json.dumps(payload),
                            headers={'content-type': 'application/json'})
        self.ok(req)
        item = self.json(req)

        url = '{0}/{1}/qti'.format(url, unquote(item['id']))
        req = self.app.get(url)
        self.ok(req)
        self.assertEqual(req.body, '')

    def test_updating_image_sequence_answer_choices_clears_existing_choices(self):
        url = '{0}/items'.format(self.url)

        media_files = [self._audio_test_file,
                       self._picture1,
                       self._picture2,
                       self._picture3,
                       self._picture4]

        assets = {}
        for media_file in media_files:
            label = self._label(self._filename(media_file))
            assets[label] = self.upload_media_file(media_file)

        payload = {
            "genusTypeId": str(QTI_ITEM_ORDER_INTERACTION_OBJECT_MANIPULATION_GENUS),
            "name": "Question 1",
            "description": "For testing",
            "question": {
                "questionString": """<itemBody>
<p>
   Listen to each audio clip and put the pictures of the story in order.
  </p>
<p>
<audio autoplay="autoplay" controls="controls" style="width: 125px">
<source src="AssetContent:audioTestFile__mp3" type="audio/mpeg"/>
</audio>
</p>

</itemBody>""",
                "choices": [{
                    "id": "idb4f6cd03-cf58-4391-9ca2-44b7bded3d4b",
                    "text": """<simpleChoice identifier="idb4f6cd03-cf58-4391-9ca2-44b7bded3d4b">
<p>
  <img src="AssetContent:Picture1_png" alt="Picture 1" width="100" height="100" />
</p>
</simpleChoice>"""
                }, {
                    "id": "id127df214-2a19-44da-894a-853948313dae",
                    "text": """<simpleChoice identifier="id127df214-2a19-44da-894a-853948313dae">
<p>
  <img src="AssetContent:Picture2_png" alt="Picture 2" width="100" height="100" />
</p>
</simpleChoice>"""
                }, {
                    "id": "iddcbf40ab-782e-4d4f-9020-6b8414699a72",
                    "text": """<simpleChoice identifier="iddcbf40ab-782e-4d4f-9020-6b8414699a72">
<p>
  <img src="AssetContent:Picture3_png" alt="Picture 3" width="100" height="100" />
</p>
</simpleChoice>"""
                }, {
                    "id": "ide576c9cc-d20e-4ba3-8881-716100b796a0",
                    "text": """<simpleChoice identifier="ide576c9cc-d20e-4ba3-8881-716100b796a0">
<p>
  <img src="AssetContent:Picture4_png" alt="Picture 4" width="100" height="100" />
</p>
</simpleChoice>"""
                }],
                "genusTypeId": str(QTI_QUESTION_ORDER_INTERACTION_OBJECT_MANIPULATION_GENUS),
                "shuffle": True,
                "fileIds": {}
            },
            "answers": [{
                "genusTypeId": str(RIGHT_ANSWER_GENUS),
                "choiceIds": ['id127df214-2a19-44da-894a-853948313dae',
                              'iddcbf40ab-782e-4d4f-9020-6b8414699a72',
                              'idb4f6cd03-cf58-4391-9ca2-44b7bded3d4b',
                              'ide576c9cc-d20e-4ba3-8881-716100b796a0'],
                "feedback": """<modalFeedback  identifier="Feedback933928139" outcomeIdentifier="FEEDBACKMODAL" showHide="show">
  <p id="docs-internal-guid-46f83555-04cc-a70f-2574-1b5c79fe206e" dir="ltr">You are correct! A square has the properties of both a rectangle, and a rhombus. Hence, it can also occupy the shaded region.</p>
</modalFeedback>"""
            }]
        }

        for label, asset in assets.iteritems():
            payload['question']['fileIds'][label] = {}
            payload['question']['fileIds'][label]['assetId'] = asset['id']
            payload['question']['fileIds'][label]['assetContentId'] = asset['assetContents'][0]['id']
            payload['question']['fileIds'][label]['assetContentTypeId'] = asset['assetContents'][0]['genusTypeId']

        req = self.app.post(url,
                            params=json.dumps(payload),
                            headers={'content-type': 'application/json'})
        self.ok(req)
        item = self.json(req)

        right_answer = [a for a in item['answers'] if a['genusTypeId'] == str(RIGHT_ANSWER_GENUS)][0]
        previous_right_answer_choices = right_answer['choiceIds']
        new_right_answer_choices = ['idb4f6cd03-cf58-4391-9ca2-44b7bded3d4b',
                                    'id127df214-2a19-44da-894a-853948313dae',
                                    'iddcbf40ab-782e-4d4f-9020-6b8414699a72',
                                    'ide576c9cc-d20e-4ba3-8881-716100b796a0']

        self.assertNotEqual(previous_right_answer_choices,
                            new_right_answer_choices)

        url = '{0}/{1}'.format(url, item['id'])
        payload = {
            'answers': [{
                'id': right_answer['id'],
                'choiceIds': new_right_answer_choices
            }]
        }
        req = self.app.put(url,
                           params=json.dumps(payload),
                           headers={'content-type': 'application/json'})
        self.ok(req)
        data = self.json(req)
        self.assertEqual(data['id'], item['id'])
        self.assertEqual(data['answers'][0]['id'], right_answer['id'])
        self.assertEqual(data['answers'][0]['genusTypeId'], str(RIGHT_ANSWER_GENUS))
        self.assertNotEqual(previous_right_answer_choices, data['answers'][0]['choiceIds'])
        self.assertEqual(new_right_answer_choices, data['answers'][0]['choiceIds'])

    def test_item_body_and_simple_choice_tags_provided_order_interaction(self):
        media_files = [self._audio_test_file,
                       self._picture1,
                       self._picture2,
                       self._picture3,
                       self._picture4]

        assets = {}
        for media_file in media_files:
            label = self._label(self._filename(media_file))
            assets[label] = self.upload_media_file(media_file)

        url = '{0}/items'.format(self.url)

        payload = {
            "genusTypeId": str(QTI_ITEM_ORDER_INTERACTION_OBJECT_MANIPULATION_GENUS),
            "name": "Question 1",
            "description": "For testing",
            "question": {
                "questionString": """<p>
   Listen to each audio clip and put the pictures of the story in order.
  </p>
<p>
<audio autoplay="autoplay" controls="controls" style="width: 125px">
<source src="AssetContent:audioTestFile__mp3" type="audio/mpeg"/>
</audio>
</p>""",
                "choices": [{
                    "id": "idb4f6cd03-cf58-4391-9ca2-44b7bded3d4b",
                    "text": """<p>
  <img src="AssetContent:Picture1_png" alt="Picture 1" width="100" height="100" />
</p>"""
                }, {
                    "id": "id127df214-2a19-44da-894a-853948313dae",
                    "text": """<p>
  <img src="AssetContent:Picture2_png" alt="Picture 2" width="100" height="100" />
</p>"""
                }, {
                    "id": "iddcbf40ab-782e-4d4f-9020-6b8414699a72",
                    "text": """<p>
  <img src="AssetContent:Picture3_png" alt="Picture 3" width="100" height="100" />
</p>"""
                }, {
                    "id": "ide576c9cc-d20e-4ba3-8881-716100b796a0",
                    "text": """<p>
  <img src="AssetContent:Picture4_png" alt="Picture 4" width="100" height="100" />
</p>"""
                }],
                "genusTypeId": str(QTI_QUESTION_ORDER_INTERACTION_OBJECT_MANIPULATION_GENUS),
                "shuffle": True,
                "fileIds": {}
            },
            "answers": [{
                "genusTypeId": str(RIGHT_ANSWER_GENUS),
                "choiceIds": ['id127df214-2a19-44da-894a-853948313dae',
                              'iddcbf40ab-782e-4d4f-9020-6b8414699a72',
                              'idb4f6cd03-cf58-4391-9ca2-44b7bded3d4b',
                              'ide576c9cc-d20e-4ba3-8881-716100b796a0'],
                "feedback": """<modalFeedback  identifier="Feedback933928139" outcomeIdentifier="FEEDBACKMODAL" showHide="show">
  <p id="docs-internal-guid-46f83555-04cc-a70f-2574-1b5c79fe206e" dir="ltr">You are correct! A square has the properties of both a rectangle, and a rhombus. Hence, it can also occupy the shaded region.</p>
</modalFeedback>"""
            }]
        }

        for label, asset in assets.iteritems():
            payload['question']['fileIds'][label] = {}
            payload['question']['fileIds'][label]['assetId'] = asset['id']
            payload['question']['fileIds'][label]['assetContentId'] = asset['assetContents'][0]['id']
            payload['question']['fileIds'][label]['assetContentTypeId'] = asset['assetContents'][0]['genusTypeId']

        req = self.app.post(url,
                            params=json.dumps(payload),
                            headers={'content-type': 'application/json'})
        self.ok(req)
        item = self.json(req)

        self.assertEqual(
            item['genusTypeId'],
            str(QTI_ITEM_ORDER_INTERACTION_OBJECT_MANIPULATION_GENUS)
        )

        self.assertEqual(
            item['question']['genusTypeId'],
            str(QTI_QUESTION_ORDER_INTERACTION_OBJECT_MANIPULATION_GENUS)
        )

        self.assertEqual(
            item['answers'][0]['genusTypeId'],
            str(RIGHT_ANSWER_GENUS)
        )
        self.assertEqual(
            len(item['answers'][0]['choiceIds']),
            4
        )
        self.assertEqual(
            len(item['question']['choices']),
            4
        )

        self.assertNotEqual(
            item['id'],
            str(self._item.ident)
        )

        url = '{0}/{1}/qti'.format(url, unquote(item['id']))
        req = self.app.get(url)
        self.ok(req)
        item_qti = BeautifulSoup(req.body, 'lxml-xml').assessmentItem
        expected_values = ['id127df214-2a19-44da-894a-853948313dae',
                           'iddcbf40ab-782e-4d4f-9020-6b8414699a72',
                           'idb4f6cd03-cf58-4391-9ca2-44b7bded3d4b',
                           'ide576c9cc-d20e-4ba3-8881-716100b796a0']
        for index, value in enumerate(item_qti.responseDeclaration.correctResponse.find_all('value')):
            self.assertEqual(value.string.strip(), expected_values[index])

        item_body = item_qti.itemBody

        order_interaction = item_body.orderInteraction.extract()

        repository_id = str(self._bank.ident).replace('assessment.Bank', 'repository.Repository')
        audio_asset_label = 'audioTestFile__mp3'
        image_1_asset_label = 'Picture1_png'
        image_2_asset_label = 'Picture2_png'
        image_3_asset_label = 'Picture3_png'
        image_4_asset_label = 'Picture4_png'
        audio_asset_id = item['question']['fileIds'][audio_asset_label]['assetId']
        audio_asset_content_id = item['question']['fileIds'][audio_asset_label]['assetContentId']
        image_1_asset_id = item['question']['fileIds'][image_1_asset_label]['assetId']
        image_1_asset_content_id = item['question']['fileIds'][image_1_asset_label]['assetContentId']
        image_2_asset_id = item['question']['fileIds'][image_2_asset_label]['assetId']
        image_2_asset_content_id = item['question']['fileIds'][image_2_asset_label]['assetContentId']
        image_3_asset_id = item['question']['fileIds'][image_3_asset_label]['assetId']
        image_3_asset_content_id = item['question']['fileIds'][image_3_asset_label]['assetContentId']
        image_4_asset_id = item['question']['fileIds'][image_4_asset_label]['assetId']
        image_4_asset_content_id = item['question']['fileIds'][image_4_asset_label]['assetContentId']

        expected_string = """<itemBody>
<p>
   Listen to each audio clip and put the pictures of the story in order.
  </p>
<p>
<audio autoplay="autoplay" controls="controls" style="width: 125px">
<source src="/api/v1/repository/repositories/{0}/assets/{1}/contents/{2}/stream" type="audio/mpeg"/>
</audio>
</p>

</itemBody>""".format(repository_id,
                      audio_asset_id,
                      audio_asset_content_id)

        self.assertEqual(
            str(item_body),
            expected_string
        )

        self.assertEqual(
            len(order_interaction.find_all('simpleChoice')),
            4
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
            "idb4f6cd03-cf58-4391-9ca2-44b7bded3d4b": """<simpleChoice identifier="idb4f6cd03-cf58-4391-9ca2-44b7bded3d4b">
<p>
<img alt="Picture 1" height="100" src="/api/v1/repository/repositories/{0}/assets/{1}/contents/{2}/stream" width="100"/>
</p>
</simpleChoice>""".format(repository_id,
                          image_1_asset_id,
                          image_1_asset_content_id),
            "id127df214-2a19-44da-894a-853948313dae": """<simpleChoice identifier="id127df214-2a19-44da-894a-853948313dae">
<p>
<img alt="Picture 2" height="100" src="/api/v1/repository/repositories/{0}/assets/{1}/contents/{2}/stream" width="100"/>
</p>
</simpleChoice>""".format(repository_id,
                          image_2_asset_id,
                          image_2_asset_content_id),
            "iddcbf40ab-782e-4d4f-9020-6b8414699a72": """<simpleChoice identifier="iddcbf40ab-782e-4d4f-9020-6b8414699a72">
<p>
<img alt="Picture 3" height="100" src="/api/v1/repository/repositories/{0}/assets/{1}/contents/{2}/stream" width="100"/>
</p>
</simpleChoice>""".format(repository_id,
                          image_3_asset_id,
                          image_3_asset_content_id),
            "ide576c9cc-d20e-4ba3-8881-716100b796a0": """<simpleChoice identifier="ide576c9cc-d20e-4ba3-8881-716100b796a0">
<p>
<img alt="Picture 4" height="100" src="/api/v1/repository/repositories/{0}/assets/{1}/contents/{2}/stream" width="100"/>
</p>
</simpleChoice>""".format(repository_id,
                          image_4_asset_id,
                          image_4_asset_content_id)
        }

        for choice in order_interaction.find_all('simpleChoice'):
            choice_id = choice['identifier']
            self.assertEqual(
                str(choice),
                expected_choices[choice_id]
            )

    def test_can_create_numeric_response_question_via_rest(self):
        url = '{0}/items'.format(self.url)

        payload = {
            "genusTypeId": str(QTI_ITEM_NUMERIC_RESPONSE_INTERACTION_GENUS),
            "name": "Question 1",
            "description": "For testing",
            "question": {
                "questionString": """<itemBody>
<p>
   Please solve:
</p>
<p>
   <printedVariable identifier="var1"/>
   +
   <printedVariable identifier="var2"/>
   =
   <textEntryInteraction responseIdentifier="RESPONSE"/>
</p>
</itemBody>""",
                "variables": [{
                    "id": "var1",
                    "format": "%.4f",
                    "type": "float",
                    "min": 1.0,
                    "max": 10.0,
                    "step": 0.1
                }, {
                    "id": "var2",
                    "type": "integer",
                    "min": 1,
                    "max": 10
                }],
                "genusTypeId": str(QTI_QUESTION_NUMERIC_RESPONSE_INTERACTION_GENUS)
            },
            "answers": [{
                "genusTypeId": str(RIGHT_ANSWER_GENUS),
                "feedback": """<modalFeedback  identifier="Feedback933928139" outcomeIdentifier="FEEDBACKMODAL" showHide="show">
<p></p>
</modalFeedback>"""
            }, {
                "genusTypeId": str(WRONG_ANSWER_GENUS),
                "feedback": """<modalFeedback  identifier="Feedback933928139" outcomeIdentifier="FEEDBACKMODAL" showHide="show">
<p></p>
</modalFeedback>"""
            }]
        }

        req = self.app.post(url,
                            params=json.dumps(payload),
                            headers={'content-type': 'application/json'})
        self.ok(req)
        item = self.json(req)

        self.assertEqual(
            item['genusTypeId'],
            str(QTI_ITEM_NUMERIC_RESPONSE_INTERACTION_GENUS)
        )

        self.assertEqual(
            item['question']['genusTypeId'],
            str(QTI_QUESTION_NUMERIC_RESPONSE_INTERACTION_GENUS)
        )

        self.assertIn('var1', item['question']['variables'])
        self.assertIn('var2', item['question']['variables'])

        self.assertEqual(
            item['question']['variables']['var1']['min_value'],
            1.0
        )
        self.assertEqual(
            item['question']['variables']['var1']['max_value'],
            10.0
        )
        self.assertEqual(
            item['question']['variables']['var1']['type'],
            'float'
        )
        self.assertEqual(
            item['question']['variables']['var1']['format'],
            '%.4f'
        )
        self.assertEqual(
            item['question']['variables']['var2']['min_value'],
            1
        )
        self.assertEqual(
            item['question']['variables']['var2']['max_value'],
            10
        )
        self.assertEqual(
            item['question']['variables']['var2']['type'],
            'integer'
        )
        self.assertEqual(
            item['question']['variables']['var2']['step'],
            1
        )

        self.assertEqual(
            item['answers'][0]['genusTypeId'],
            str(RIGHT_ANSWER_GENUS)
        )
        self.assertIn('<p></p>', item['answers'][0]['feedbacks'][0]['text'])
        self.assertIn('<p></p>', item['answers'][1]['feedbacks'][0]['text'])

        self.assertNotEqual(
            item['id'],
            str(self._item.ident)
        )

        url = '{0}/{1}/qti'.format(url, unquote(item['id']))
        req = self.app.get(url)
        self.ok(req)
        item_qti = BeautifulSoup(req.body, 'lxml-xml').assessmentItem
        item_body = item_qti.itemBody

        expected_string = """<itemBody>
<p>
   Please solve:
</p>
<p>
   <printedVariable format="%.4f" identifier="var1"/>
   +
   <printedVariable identifier="var2"/>
   =
   <textEntryInteraction responseIdentifier="RESPONSE"/>
</p>
</itemBody>"""

        self.assertNotEqual(
            str(item_body),
            expected_string
        )

        # make sure some random numbers are inserted that meet the requirements
        expression = self._grab_expression(str(item_body))
        var1 = float(expression[0:expression.index('+')].strip())
        var2 = int(expression[expression.index('+') + 1::].strip())

        self.assertTrue(1.0 <= var1 <= 10.0)
        self.assertTrue(1 <= var2 <= 10)

        # make sure the questionId is "magical"
        self.assertNotEqual(
            item['id'],
            item['question']['id']
        )
        self.assertNotIn('?', item['question']['id'])
        self.assertEqual(
            item['question']['id'].split('%40')[-1],
            'qti-numeric-response'
        )
        self.assertIn('var1', item['question']['id'].split('%3A')[-1].split('%40')[0])
        self.assertIn('var2', item['question']['id'].split('%3A')[-1].split('%40')[0])

    def test_can_add_question_to_existing_numeric_response_item_via_rest(self):
        url = '{0}/items'.format(self.url)

        payload = {
            "genusTypeId": str(QTI_ITEM_NUMERIC_RESPONSE_INTERACTION_GENUS),
            "name": "Question 1",
            "description": "For testing"
        }

        req = self.app.post(url,
                            params=json.dumps(payload),
                            headers={'content-type': 'application/json'})
        self.ok(req)
        item = self.json(req)

        url = '{0}/items/{1}'.format(self.url, item['id'])

        payload = {
            "question": {
                "questionString": """<itemBody>
<p>
   Please solve:
</p>
<p>
   <printedVariable identifier="var1"/>
   +
   <printedVariable identifier="var2"/>
   =
   <textEntryInteraction responseIdentifier="RESPONSE"/>
</p>
</itemBody>""",
                "variables": [{
                    "id": "var1",
                    "format": "%.4f",
                    "type": "float",
                    "min": 1.0,
                    "max": 10.0,
                    "step": 0.1
                }, {
                    "id": "var2",
                    "type": "integer",
                    "min": 1,
                    "max": 10
                }],
                "genusTypeId": str(QTI_QUESTION_NUMERIC_RESPONSE_INTERACTION_GENUS)
            },
            "answers": [{
                "genusTypeId": str(RIGHT_ANSWER_GENUS),
                "feedback": """<modalFeedback  identifier="Feedback933928139" outcomeIdentifier="FEEDBACKMODAL" showHide="show">
<p></p>
</modalFeedback>"""
            }, {
                "genusTypeId": str(WRONG_ANSWER_GENUS),
                "feedback": """<modalFeedback  identifier="Feedback933928139" outcomeIdentifier="FEEDBACKMODAL" showHide="show">
<p></p>
</modalFeedback>"""
            }]
        }

        req = self.app.put(url,
                           params=json.dumps(payload),
                           headers={'content-type': 'application/json'})
        self.ok(req)
        item = self.json(req)

        self.assertEqual(
            item['genusTypeId'],
            str(QTI_ITEM_NUMERIC_RESPONSE_INTERACTION_GENUS)
        )

        self.assertEqual(
            item['question']['genusTypeId'],
            str(QTI_QUESTION_NUMERIC_RESPONSE_INTERACTION_GENUS)
        )

        self.assertIn('var1', item['question']['variables'])
        self.assertIn('var2', item['question']['variables'])

        self.assertEqual(
            item['question']['variables']['var1']['min_value'],
            1.0
        )
        self.assertEqual(
            item['question']['variables']['var1']['max_value'],
            10.0
        )
        self.assertEqual(
            item['question']['variables']['var1']['type'],
            'float'
        )
        self.assertEqual(
            item['question']['variables']['var1']['format'],
            '%.4f'
        )
        self.assertEqual(
            item['question']['variables']['var2']['min_value'],
            1
        )
        self.assertEqual(
            item['question']['variables']['var2']['max_value'],
            10
        )
        self.assertEqual(
            item['question']['variables']['var2']['type'],
            'integer'
        )
        self.assertEqual(
            item['question']['variables']['var2']['step'],
            1
        )

        self.assertEqual(
            item['answers'][0]['genusTypeId'],
            str(RIGHT_ANSWER_GENUS)
        )
        self.assertIn('<p></p>', item['answers'][0]['feedbacks'][0]['text'])
        self.assertIn('<p></p>', item['answers'][1]['feedbacks'][0]['text'])

        self.assertNotEqual(
            item['id'],
            str(self._item.ident)
        )

        url = '{0}/{1}/qti'.format(url, unquote(item['id']))
        req = self.app.get(url)
        self.ok(req)
        item_qti = BeautifulSoup(req.body, 'lxml-xml').assessmentItem
        item_body = item_qti.itemBody

        expected_string = """<itemBody>
<p>
   Please solve:
</p>
<p>
   <printedVariable format="%.4f" identifier="var1"/>
   +
   <printedVariable identifier="var2"/>
   =
   <textEntryInteraction responseIdentifier="RESPONSE"/>
</p>
</itemBody>"""

        self.assertNotEqual(
            str(item_body),
            expected_string
        )

        # make sure some random numbers are inserted that meet the requirements
        expression = self._grab_expression(str(item_body))
        var1 = float(expression[0:expression.index('+')].strip())
        var2 = int(expression[expression.index('+') + 1::].strip())

        self.assertTrue(1.0 <= var1 <= 10.0)
        self.assertTrue(1 <= var2 <= 10)

        # make sure the questionId is "magical"
        self.assertNotEqual(
            item['id'],
            item['question']['id']
        )
        self.assertNotIn('?', item['question']['id'])
        self.assertEqual(
            item['question']['id'].split('%40')[-1],
            'qti-numeric-response'
        )
        self.assertIn('var1', item['question']['id'].split('%3A')[-1].split('%40')[0])
        self.assertIn('var2', item['question']['id'].split('%3A')[-1].split('%40')[0])

    def test_can_get_numeric_response_item_qti_with_no_answers(self):
        url = '{0}/items'.format(self.url)

        payload = {
            "genusTypeId": str(QTI_ITEM_NUMERIC_RESPONSE_INTERACTION_GENUS),
            "name": "Question 1",
            "description": "For testing",
            "question": {
                "questionString": """<itemBody>
<p>
   Please solve:
</p>
<p>
   <printedVariable identifier="var1"/>
   +
   <printedVariable identifier="var2"/>
   =
   <textEntryInteraction responseIdentifier="RESPONSE"/>
</p>
</itemBody>"""}
        }

        req = self.app.post(url,
                            params=json.dumps(payload),
                            headers={'content-type': 'application/json'})
        self.ok(req)
        item = self.json(req)

        url = '{0}/items/{1}/qti'.format(self.url, item['id'])

        req = self.app.get(url)
        self.ok(req)
        qti = BeautifulSoup(req.body, 'xml')
        self.assertIsNotNone(qti.responseDeclaration)

    def test_getting_qti_for_numeric_response_item_with_no_question_returns_empty_string(self):
        url = '{0}/items'.format(self.url)

        payload = {
            "genusTypeId": str(QTI_ITEM_NUMERIC_RESPONSE_INTERACTION_GENUS),
            "name": "Question 1",
            "description": "For testing"
        }

        req = self.app.post(url,
                            params=json.dumps(payload),
                            headers={'content-type': 'application/json'})
        self.ok(req)
        item = self.json(req)

        url = '{0}/{1}/qti'.format(url, unquote(item['id']))
        req = self.app.get(url)
        self.ok(req)
        self.assertEqual(req.body, '')

    def test_item_body_provided_numeric_response(self):
        url = '{0}/items'.format(self.url)

        payload = {
            "genusTypeId": str(QTI_ITEM_NUMERIC_RESPONSE_INTERACTION_GENUS),
            "name": "Question 1",
            "description": "For testing",
            "question": {
                "questionString": """<p>
   Please solve:
</p>
<p>
   <printedVariable identifier="var1"/>
   +
   <printedVariable identifier="var2"/>
   =
   <textEntryInteraction responseIdentifier="RESPONSE"/>
</p>""",
                "variables": [{
                    "id": "var1",
                    "format": "%.4f",
                    "type": "float",
                    "min": 1.0,
                    "max": 10.0,
                    "step": 0.1
                }, {
                    "id": "var2",
                    "type": "integer",
                    "min": 1,
                    "max": 10
                }],
                "genusTypeId": str(QTI_QUESTION_NUMERIC_RESPONSE_INTERACTION_GENUS)
            },
            "answers": [{
                "genusTypeId": str(RIGHT_ANSWER_GENUS),
                "feedback": """<modalFeedback  identifier="Feedback933928139" outcomeIdentifier="FEEDBACKMODAL" showHide="show">
<p></p>
</modalFeedback>"""
            }, {
                "genusTypeId": str(WRONG_ANSWER_GENUS),
                "feedback": """<modalFeedback  identifier="Feedback933928139" outcomeIdentifier="FEEDBACKMODAL" showHide="show">
<p></p>
</modalFeedback>"""
            }]
        }

        req = self.app.post(url,
                            params=json.dumps(payload),
                            headers={'content-type': 'application/json'})
        self.ok(req)
        item = self.json(req)

        self.assertEqual(
            item['genusTypeId'],
            str(QTI_ITEM_NUMERIC_RESPONSE_INTERACTION_GENUS)
        )

        self.assertEqual(
            item['question']['genusTypeId'],
            str(QTI_QUESTION_NUMERIC_RESPONSE_INTERACTION_GENUS)
        )

        self.assertIn('var1', item['question']['variables'])
        self.assertIn('var2', item['question']['variables'])

        self.assertEqual(
            item['question']['variables']['var1']['min_value'],
            1.0
        )
        self.assertEqual(
            item['question']['variables']['var1']['max_value'],
            10.0
        )
        self.assertEqual(
            item['question']['variables']['var1']['type'],
            'float'
        )
        self.assertEqual(
            item['question']['variables']['var1']['format'],
            '%.4f'
        )
        self.assertEqual(
            item['question']['variables']['var2']['min_value'],
            1
        )
        self.assertEqual(
            item['question']['variables']['var2']['max_value'],
            10
        )
        self.assertEqual(
            item['question']['variables']['var2']['type'],
            'integer'
        )
        self.assertEqual(
            item['question']['variables']['var2']['step'],
            1
        )

        self.assertEqual(
            item['answers'][0]['genusTypeId'],
            str(RIGHT_ANSWER_GENUS)
        )
        self.assertIn('<p></p>', item['answers'][0]['feedbacks'][0]['text'])
        self.assertIn('<p></p>', item['answers'][1]['feedbacks'][0]['text'])

        self.assertNotEqual(
            item['id'],
            str(self._item.ident)
        )

        url = '{0}/{1}/qti'.format(url, unquote(item['id']))
        req = self.app.get(url)
        self.ok(req)
        item_qti = BeautifulSoup(req.body, 'lxml-xml').assessmentItem
        item_body = item_qti.itemBody

        expected_string = """<itemBody>
<p>
   Please solve:
</p>
<p>
   <printedVariable format="%.4f" identifier="var1"/>
   +
   <printedVariable identifier="var2"/>
   =
   <textEntryInteraction responseIdentifier="RESPONSE"/>
</p>
</itemBody>"""

        self.assertNotEqual(
            str(item_body),
            expected_string
        )

        # make sure some random numbers are inserted that meet the requirements
        expression = self._grab_expression(str(item_body))
        var1 = float(expression[0:expression.index('+')].strip())
        var2 = int(expression[expression.index('+') + 1::].strip())

        self.assertTrue(1.0 <= var1 <= 10.0)
        self.assertTrue(1 <= var2 <= 10)

        # make sure the questionId is "magical"
        self.assertNotEqual(
            item['id'],
            item['question']['id']
        )
        self.assertNotIn('?', item['question']['id'])
        self.assertEqual(
            item['question']['id'].split('%40')[-1],
            'qti-numeric-response'
        )
        self.assertIn('var1', item['question']['id'].split('%3A')[-1].split('%40')[0])
        self.assertIn('var2', item['question']['id'].split('%3A')[-1].split('%40')[0])

    def test_can_change_item_genus_type_id(self):
        url = '{0}/items'.format(self.url)

        payload = {
            "genusTypeId": str(QTI_ITEM_CHOICE_INTERACTION_GENUS),
            "name": "Question 1",
            "description": "For testing"
        }

        req = self.app.post(url,
                            params=json.dumps(payload),
                            headers={'content-type': 'application/json'})
        self.ok(req)
        item = self.json(req)
        self.assertEqual(item['genusTypeId'], str(QTI_ITEM_CHOICE_INTERACTION_GENUS))

        url = '{0}/{1}'.format(url, item['id'])
        payload = {
            "genusTypeId": str(QTI_ITEM_CHOICE_INTERACTION_SURVEY_GENUS)
        }

        req = self.app.put(url,
                           params=json.dumps(payload),
                           headers={'content-type': 'application/json'})
        self.ok(req)
        item = self.json(req)
        self.assertEqual(item['genusTypeId'], str(QTI_ITEM_CHOICE_INTERACTION_SURVEY_GENUS))

    def test_can_change_question_genus_type_id(self):
        url = '{0}/items'.format(self.url)

        payload = {
            "genusTypeId": str(QTI_ITEM_CHOICE_INTERACTION_GENUS),
            "name": "Question 1",
            "description": "For testing",
            "question": {
                "genusTypeId": str(QTI_QUESTION_CHOICE_INTERACTION_GENUS)
            }
        }

        req = self.app.post(url,
                            params=json.dumps(payload),
                            headers={'content-type': 'application/json'})
        self.ok(req)
        item = self.json(req)
        self.assertEqual(item['question']['genusTypeId'], str(QTI_QUESTION_CHOICE_INTERACTION_GENUS))

        url = '{0}/{1}'.format(url, item['id'])
        payload = {
            "question": {
                "genusTypeId": str(QTI_QUESTION_CHOICE_INTERACTION_SURVEY_GENUS)
            }
        }

        req = self.app.put(url,
                           params=json.dumps(payload),
                           headers={'content-type': 'application/json'})
        self.ok(req)
        item = self.json(req)
        self.assertEqual(item['question']['genusTypeId'], str(QTI_QUESTION_CHOICE_INTERACTION_SURVEY_GENUS))
