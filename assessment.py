import re
import json
import web
import zipfile

from bs4 import BeautifulSoup
from bson.errors import InvalidId

from cStringIO import StringIO

from dlkit_runtime.errors import *
from dlkit_runtime.primordium import Type, DataInputStream, DisplayText
from records.registry import ANSWER_GENUS_TYPES,\
    ASSESSMENT_TAKEN_RECORD_TYPES, COMMENT_RECORD_TYPES, BANK_RECORD_TYPES,\
    QUESTION_RECORD_TYPES, ANSWER_RECORD_TYPES, ITEM_RECORD_TYPES, ITEM_GENUS_TYPES,\
    ASSESSMENT_RECORD_TYPES, QUESTION_GENUS_TYPES

from urllib import quote

import assessment_utilities as autils
import repository_utilities as rutils
import utilities

ADVANCED_QUERY_ASSESSMENT_TAKEN_RECORD_TYPE = Type(**ASSESSMENT_TAKEN_RECORD_TYPES['advanced-query'])
CHOICE_INTERACTION_GENUS = Type(**ITEM_GENUS_TYPES['qti-choice-interaction'])
CHOICE_INTERACTION_MULTI_GENUS = Type(**ITEM_GENUS_TYPES['qti-choice-interaction-multi-select'])
CHOICE_INTERACTION_SURVEY_GENUS = Type(**ITEM_GENUS_TYPES['qti-choice-interaction-survey'])
CHOICE_INTERACTION_MULTI_SELECT_SURVEY_GENUS = Type(**ITEM_GENUS_TYPES['qti-choice-interaction-multi-select-survey'])
CHOICE_INTERACTION_QUESTION_GENUS = Type(**QUESTION_GENUS_TYPES['qti-choice-interaction'])
CHOICE_INTERACTION_MULTI_QUESTION_GENUS = Type(**QUESTION_GENUS_TYPES['qti-choice-interaction-multi-select'])
CHOICE_INTERACTION_SURVEY_QUESTION_GENUS = Type(**QUESTION_GENUS_TYPES['qti-choice-interaction-survey'])
CHOICE_INTERACTION_MULTI_SELECT_SURVEY_QUESTION_GENUS = Type(**QUESTION_GENUS_TYPES['qti-choice-interaction-multi-select-survey'])

COLOR_BANK_RECORD_TYPE = Type(**BANK_RECORD_TYPES['bank-color'])
FILE_COMMENT_RECORD_TYPE = Type(**COMMENT_RECORD_TYPES['file-comment'])
FILES_ANSWER_RECORD = Type(**ANSWER_RECORD_TYPES['files'])
FILE_SUBMISSION_ANSWER_RECORD = Type(**ANSWER_RECORD_TYPES['file-submission'])

EXTENDED_TEXT_INTERACTION_GENUS = Type(**ITEM_GENUS_TYPES['qti-extended-text-interaction'])
EXTENDED_TEXT_INTERACTION_ANSWER_RECORD = Type(**ANSWER_RECORD_TYPES['extended-text-answer'])
EXTENDED_TEXT_INTERACTION_QUESTION_GENUS = Type(**QUESTION_GENUS_TYPES['qti-extended-text-interaction'])

INLINE_CHOICE_ITEM_RECORD = Type(**ITEM_RECORD_TYPES['qti-inline-choice'])
INLINE_CHOICE_INTERACTION_GENUS = Type(**ITEM_GENUS_TYPES['qti-inline-choice-interaction-mw-fill-in-the-blank'])
INLINE_CHOICE_MW_FITB_INTERACTION_QUESTION_GENUS = Type(**QUESTION_GENUS_TYPES['qti-inline-choice-interaction-mw-fill-in-the-blank'])

NUMERIC_RESPONSE_RECORD = Type(**ITEM_RECORD_TYPES['qti-numeric-response'])
NUMERIC_RESPONSE_INTERACTION_GENUS = Type(**ITEM_GENUS_TYPES['qti-numeric-response'])
NUMERIC_RESPONSE_QUESTION_GENUS = Type(**QUESTION_GENUS_TYPES['qti-numeric-response'])

RANDOMIZED_MULTI_CHOICE_ITEM_RECORD = Type(**ITEM_RECORD_TYPES['multi-choice-randomized'])
RANDOMIZED_MULTI_CHOICE_QUESTION_RECORD = Type(**QUESTION_RECORD_TYPES['multi-choice-randomized'])

UPLOAD_INTERACTION_AUDIO_GENUS = Type(**ITEM_GENUS_TYPES['qti-upload-interaction-audio'])
UPLOAD_INTERACTION_GENERIC_GENUS = Type(**ITEM_GENUS_TYPES['qti-upload-interaction-generic'])
UPLOAD_INTERACTION_AUDIO_QUESTION_GENUS = Type(**QUESTION_GENUS_TYPES['qti-upload-interaction-audio'])
UPLOAD_INTERACTION_GENERIC_QUESTION_GENUS = Type(**QUESTION_GENUS_TYPES['qti-upload-interaction-generic'])

ORDER_INTERACTION_MW_SENTENCE_GENUS = Type(**ITEM_GENUS_TYPES['qti-order-interaction-mw-sentence'])
ORDER_INTERACTION_MW_SANDBOX_GENUS = Type(**ITEM_GENUS_TYPES['qti-order-interaction-mw-sandbox'])
ORDER_INTERACTION_OBJECT_MANIPULATION_GENUS = Type(**ITEM_GENUS_TYPES['qti-order-interaction-object-manipulation'])
ORDER_INTERACTION_MW_SENTENCE_QUESTION_GENUS = Type(**QUESTION_GENUS_TYPES['qti-order-interaction-mw-sentence'])
ORDER_INTERACTION_MW_SANDBOX_QUESTION_GENUS = Type(**QUESTION_GENUS_TYPES['qti-order-interaction-mw-sandbox'])
ORDER_INTERACTION_OBJECT_MANIPULATION_QUESTION_GENUS = Type(**QUESTION_GENUS_TYPES['qti-order-interaction-object-manipulation'])

SIMPLE_INLINE_CHOICE_ANSWER_RECORD = Type(**ANSWER_RECORD_TYPES['inline-choice-answer'])
SIMPLE_MULTIPLE_CHOICE_ANSWER_RECORD = Type(**ANSWER_RECORD_TYPES['multi-choice-answer'])
MULTI_LANGUAGE_NUMERIC_RESPONSE_ANSWER_RECORD = Type(**ANSWER_RECORD_TYPES['multi-language-numeric-response-with-feedback'])
MULTI_LANGUAGE_QUESTION_STRING_RECORD = Type(**QUESTION_RECORD_TYPES['multi-language-question-string'])
MULTI_LANGUAGE_MULTIPLE_CHOICE_QUESTION_RECORD = Type(**QUESTION_RECORD_TYPES['multi-language-multiple-choice'])
MULTI_LANGUAGE_ORDERED_CHOICE_QUESTION_RECORD = Type(**QUESTION_RECORD_TYPES['multi-language-ordered-choice'])
MULTI_LANGUAGE_INLINE_CHOICE_QUESTION_RECORD = Type(**QUESTION_RECORD_TYPES['multi-language-inline-choice'])
MULTI_LANGUAGE_EXTENDED_TEXT_INTERACTION_QUESTION_RECORD = Type(**QUESTION_RECORD_TYPES['multi-language-text-interaction'])
MULTI_LANGUAGE_FILE_UPLOAD_QUESTION_RECORD = Type(**QUESTION_RECORD_TYPES['multi-language-file-submission'])
MULTI_LANGUAGE_NUMERIC_RESPONSE_QUESTION_RECORD = Type(**QUESTION_RECORD_TYPES['multi-language-numeric-response'])

PROVENANCE_ITEM_RECORD = Type(**ITEM_RECORD_TYPES['provenance'])
QTI_ANSWER = Type(**ANSWER_RECORD_TYPES['qti'])
QTI_ITEM = Type(**ITEM_RECORD_TYPES['qti'])
QTI_QUESTION = Type(**QUESTION_RECORD_TYPES['qti'])
QUESTION_WITH_FILES = Type(**QUESTION_RECORD_TYPES['files'])
REVIEWABLE_TAKEN = Type(**ASSESSMENT_TAKEN_RECORD_TYPES['review-options'])
SIMPLE_SEQUENCE_ASSESSMENT = Type(**ASSESSMENT_RECORD_TYPES['simple-child-sequencing'])
WRONG_ANSWER_ITEM = Type(**ITEM_RECORD_TYPES['wrong-answer'])
WRONG_ANSWER_GENUS = Type(**ANSWER_GENUS_TYPES['wrong-answer'])
RIGHT_ANSWER_GENUS = Type(**ANSWER_GENUS_TYPES['right-answer'])

# Multilanguage records
MULTI_LANGUAGE_ITEM_RECORD = Type(**ITEM_RECORD_TYPES['multi-language'])
MULTI_LANGUAGE_QUESTION_RECORD = Type(**QUESTION_RECORD_TYPES['multi-language'])
MULTI_LANGUAGE_FEEDBACK_ANSWER_RECORD = Type(**ANSWER_RECORD_TYPES['multi-language-answer-with-feedback'])


urls = (
    "/banks/(.*)/assessmentsoffered/(.*)/assessmentstaken", "AssessmentsTaken",
    "/banks/(.*)/assessmentsoffered/(.*)/results", "AssessmentOfferedResults",
    "/banks/(.*)/assessmentsoffered/(.*)", "AssessmentOfferedDetails",
    "/banks/(.*)/assessmentstaken/(.*)/questions/(.*)/qti", "AssessmentTakenQuestionQTIDetails",
    "/banks/(.*)/assessmentstaken/(.*)/questions/(.*)/status", "AssessmentTakenQuestionStatus",
    "/banks/(.*)/assessmentstaken/(.*)/questions/(.*)/submit", "AssessmentTakenQuestionSubmit",
    "/banks/(.*)/assessmentstaken/(.*)/questions/(.*)", "AssessmentTakenQuestionDetails",
    "/banks/(.*)/assessmentstaken/(.*)/questions", "AssessmentTakenQuestions",
    "/banks/(.*)/assessmentstaken/(.*)/finish", "FinishAssessmentTaken",
    "/banks/(.*)/assessmentstaken/(.*)", "AssessmentTakenDetails",
    "/banks/(.*)/assessments/(.*)/assessmentsoffered", "AssessmentsOffered",
    "/banks/(.*)/assessments/(.*)/assignedbankids/(.*)", "AssessmentRemoveAssignedBankIds",
    "/banks/(.*)/assessments/(.*)/assignedbankids", "AssessmentAssignedBankIds",
    "/banks/(.*)/assessments/(.*)/items/(.*)", "AssessmentItemDetails",
    "/banks/(.*)/assessments/(.*)/items", "AssessmentItemsList",
    "/banks/(.*)/assessments/(.*)", "AssessmentDetails",
    "/banks/(.*)/assessments", "AssessmentsList",
    "/banks/(.*)/items/(.*)/videoreplacement", "ItemVideoTagReplacement",
    "/banks/(.*)/items/(.*)/qti", "ItemQTIDetails",
    "/banks/(.*)/items/(.*)", "ItemDetails",
    "/banks/(.*)/items", "ItemsList",
    "/banks/(.*)", "AssessmentBankDetails",
    "/banks", "AssessmentBanksList",
    "/hierarchies/roots/(.*)", "AssessmentHierarchiesRootDetails",
    "/hierarchies/roots", "AssessmentHierarchiesRootsList",
    "/hierarchies/nodes/(.*)/children", "AssessmentHierarchiesNodeChildrenList",
    "/hierarchies/nodes/(.*)", "AssessmentHierarchiesNodeDetails"
)


class AssessmentBanksList(utilities.BaseClass):
    """
    List all available assessment banks.
    api/v1/assessment/banks/

    POST allows you to create a new assessment bank, requires two parameters:
      * name
      * description

    Note that for RESTful calls, you need to set the request header
    'content-type' to 'application/json'

    Example (note the use of double quotes!!):
      {"name" : "a new bank","description" : "this is a test"}
    """
    @utilities.format_response
    def GET(self):
        """
        List all available assessment banks
        """
        try:
            am = autils.get_assessment_manager()
            inputs = web.input()
            if 'displayName' in inputs or 'genusTypeId' in inputs:
                querier = am.get_bank_query()
                if 'displayName' in inputs:
                    if autils._unescaped(inputs['displayName']):
                        querier.match_display_name(quote(inputs['displayName'], safe='/ '), match=True)
                    else:
                        querier.match_display_name(inputs['displayName'], match=True)
                if 'genusTypeId' in inputs:
                    if (autils._unescaped(inputs['genusTypeId'])):
                        querier.match_genus_type(quote(inputs['genusTypeId'], safe='/ '), match=True)
                    else:
                        querier.match_genus_type(inputs['genusTypeId'], match=True)
                assessment_banks = am.get_banks_by_query(querier)
            else:
                assessment_banks = am.banks
            banks = utilities.extract_items(assessment_banks)
            return banks
        except PermissionDenied as ex:
            utilities.handle_exceptions(ex)

    @utilities.format_response
    def POST(self):
        """
        Create a new assessment bank, if authorized
        Create a new group in IS&T Membership service

        """
        try:
            am = autils.get_assessment_manager()
            form = am.get_bank_form_for_create([])
            data = self.data()

            form = utilities.set_form_basics(form, data)

            new_bank = utilities.convert_dl_object(am.create_bank(form))

            if 'aliasId' in data:
                am.alias_bank(utilities.clean_id(json.loads(new_bank)['id']),
                              utilities.clean_id(data['aliasId']))

            return new_bank
        except (PermissionDenied, InvalidArgument) as ex:
            utilities.handle_exceptions(ex)


class AssessmentRemoveAssignedBankIds(utilities.BaseClass):
    """Remove a single bankId from the list of assignedBankIds"""
    @utilities.format_response
    def DELETE(self, bank_id, assessment_id, assigned_bank_id):
        try:
            am = autils.get_assessment_manager()
            assigned_bank_id = am.get_bank(utilities.clean_id(assigned_bank_id)).ident
            am.unassign_assessment_from_bank(utilities.clean_id(assessment_id),
                                             assigned_bank_id)
            return web.Accepted()
        except (PermissionDenied, IllegalState, InvalidId, OperationFailed) as ex:
            utilities.handle_exceptions(ex)


class AssessmentAssignedBankIds(utilities.BaseClass):
    """Add the provided bankIds to the list of assignedBankIds"""
    @utilities.format_response
    def POST(self, bank_id, assessment_id):
        try:
            am = autils.get_assessment_manager()
            if 'assignedBankIds' in self.data():
                assessment_id = utilities.clean_id(assessment_id)
                for assigned_bank_id in self.data()['assignedBankIds']:
                    assigned_bank_id = am.get_bank(utilities.clean_id(assigned_bank_id)).ident
                    am.assign_assessment_to_bank(assessment_id,
                                                 assigned_bank_id)
            return web.Accepted()
        except (PermissionDenied, IllegalState, InvalidId) as ex:
            utilities.handle_exceptions(ex)


class AssessmentBankDetails(utilities.BaseClass):
    """
    Shows details for a specific assessment bank.
    api/v1/assessment/banks/<bank_id>/

    GET, PUT, DELETE
    PUT will update the assessment bank. Only changed attributes need to be sent.
    DELETE will remove the assessment bank.

    Note that for RESTful calls, you need to set the request header
    'content-type' to 'application/json'

    Example (note the use of double quotes!!):
       {"name" : "a new bank"}
    """
    @utilities.format_response
    def DELETE(self, bank_id):
        try:
            am = autils.get_assessment_manager()
            data = am.delete_bank(utilities.clean_id(bank_id))
            return web.Accepted()
        except (PermissionDenied, IllegalState, InvalidId) as ex:
            utilities.handle_exceptions(ex)

    @utilities.format_response
    def GET(self, bank_id):
        try:
            am = autils.get_assessment_manager()
            assessment_bank = am.get_bank(utilities.clean_id(bank_id))
            bank = utilities.convert_dl_object(assessment_bank)
            return bank
        except (PermissionDenied, NotFound, InvalidId) as ex:
            utilities.handle_exceptions(ex)

    @utilities.format_response
    def PUT(self, bank_id):
        try:
            am = autils.get_assessment_manager()
            data = self.data()

            form = am.get_bank_form_for_update(utilities.clean_id(bank_id))

            form = utilities.set_form_basics(form, data)
            updated_bank = am.update_bank(form)

            if 'aliasId' in data:
                am.alias_bank(updated_bank.ident, utilities.clean_id(data['aliasId']))

            bank = utilities.convert_dl_object(updated_bank)
            return bank
        except (PermissionDenied, InvalidArgument, InvalidId) as ex:
            utilities.handle_exceptions(ex)


class AssessmentsList(utilities.BaseClass):
    """
    Get a list of all assessments in the specified bank
    api/v1/assessment/banks/<bank_id>/assessments/

    GET, POST
    POST creates a new assessment

    Note that "times" like duration and startTime for offerings should be
    input as JSON objects when using the RESTful API. Example:
        "startTime":{"year":2015,"month":1,"day":15}

    In this UI, you can put an object into the textarea below, and it will work fine.

    Note that duration only returns days / minutes / seconds

    Note that for RESTful calls, you need to set the request header
    'content-type' to 'application/json'

    POST example (note the use of double quotes!!):
       {"name" : "an assessment","description" : "this is a hard pset","itemIds" : ["assessment.Item%3A539ef3a3ea061a0cb4fba0a3%40birdland.mit.edu"]}
    """
    @utilities.format_response
    def GET(self, bank_id):
        try:
            am = autils.get_assessment_manager()
            assessment_bank = am.get_bank(utilities.clean_id(bank_id))
            if "isolated" in self.data():
                assessment_bank.use_isolated_bank_view()

            assessments = assessment_bank.get_assessments()

            data = utilities.extract_items(assessments)
            return data
        except (PermissionDenied, InvalidId) as ex:
            utilities.handle_exceptions(ex)

    @utilities.format_response
    def POST(self, bank_id):
        try:
            am = autils.get_assessment_manager()
            # TODO: create a QTI record and version of this...
            bank = am.get_bank(utilities.clean_id(bank_id))

            try:
                x = web.input(qtiFile={})
                with zipfile.ZipFile(x['qtiFile'].file) as qti_zip:
                    qti_file = None

                    for zip_file_name in qti_zip.namelist():
                        if zip_file_name == 'imsmanifest.xml':
                            pass
                        elif '.xml' in zip_file_name:
                            # should be the actual item XML at this point
                            qti_file = qti_zip.open(zip_file_name)

                    qti_xml = qti_file.read()
                    soup = BeautifulSoup(qti_xml, 'xml')

                    # TODO: add in alias checking to see if this assessment exists already
                    # if so, create a new assessment and provenance it...remove the alias
                    # on the previous assessment.

                    form = bank.get_assessment_form_for_create([QTI_ITEM])
                    form.display_name = soup.assessmentItem['title']
                    form.description = 'QTI AssessmentItem'
                    form.load_from_qti_item(qti_xml)

                    new_item = bank.create_item(form)

                    # ID Alias with the QTI ID from Onyx
                    bank.alias_item(new_item.ident,
                                    utilities.construct_qti_id(soup.assessmentItem['identifier']))

                    q_form = bank.get_question_form_for_create(new_item.ident, [QTI_QUESTION])

                    if len(media_files) > 0:
                        q_form.load_from_qti_item(qti_xml, media_files=media_files)
                    else:
                        q_form.load_from_qti_item(qti_xml)
                    bank.create_question(q_form)

                    a_form = bank.get_answer_form_for_create(new_item.ident, [QTI_ANSWER])
                    a_form.load_from_qti_item(qti_xml)
                    bank.create_answer(a_form)
            except AttributeError:  #'dict' object has no attribute 'file'
                form = bank.get_assessment_form_for_create([SIMPLE_SEQUENCE_ASSESSMENT])

                form = utilities.set_form_basics(form, self.data())

                new_assessment = bank.create_assessment(form)
                # if item IDs are included in the assessment, append them.
                if 'itemIds' in self.data():
                    if isinstance(self.data()['itemIds'], basestring):
                        items = json.loads(self.data()['itemIds'])
                    else:
                        items = self.data()['itemIds']

                    if not isinstance(items, list):
                        try:
                            utilities.clean_id(items)  # use this as proxy to test if a valid OSID ID
                            items = [items]
                        except:
                            raise InvalidArgument

                    for item_id in items:
                        try:
                            bank.add_item(new_assessment.ident, utilities.clean_id(item_id))
                        except:
                            raise NotFound()

                full_assessment = bank.get_assessment(new_assessment.ident)

            if 'assignedBankIds' in self.data():
                # on POST, don't need to delete previous because there are no previous ones!
                # need the non-aliased IDs for assignment
                for bank_id in self.data()['assignedBankIds']:
                    bank_id = am.get_bank(utilities.clean_id(bank_id)).ident
                    am.assign_assessment_to_bank(full_assessment.ident, bank_id)
                full_assessment = bank.get_assessment(full_assessment.ident)

            data = utilities.convert_dl_object(full_assessment)
            return data
        except (PermissionDenied, NotFound, InvalidArgument, InvalidId) as ex:
            utilities.handle_exceptions(ex)


class ItemsList(utilities.BaseClass):
    """
    Return list of items in the given assessment bank. Make sure to embed
    the question and answers in the JSON.
    api/v1/assessment/banks/<bank_id>/items/

    GET, POST
    POST creates a new item

    Note that for RESTful calls, you need to set the request header
    'content-type' to 'application/json'

    Example (note the use of double quotes!!):
       This UI: {"name" : "an assessment item","description" : "this is a hard quiz problem","question":{"type":"question-record-type%3Aresponse-string%40ODL.MIT.EDU","questionString":"Where am I?"},"answers":[{"type":"answer-record-type%3Aresponse-string%40ODL.MIT.EDU","responseString":"Here"}]}
    """
    @utilities.format_response
    def GET(self, bank_id=None):
        try:
            if bank_id is None:
                raise PermissionDenied
            am = autils.get_assessment_manager()
            assessment_bank = am.get_bank(utilities.clean_id(bank_id))

            inputs = web.input()
            if any(term in inputs for term in ['displayName', 'displayNames',
                                               'genusTypeId']):
                querier = assessment_bank.get_item_query()
                if 'displayName' in inputs:
                    if autils._unescaped(inputs['displayName']):
                        querier.match_display_name(quote(inputs['displayName'], safe='/ '), match=True)
                    else:
                        querier.match_display_name(inputs['displayName'], match=True)
                if 'displayNames' in inputs:
                    if autils._unescaped(inputs['displayNames']):
                        querier.match_display_names(quote(inputs['displayNames'], safe='/ '), match=True)
                    else:
                        querier.match_display_names(inputs['displayNames'], match=True)
                if 'genusTypeId' in inputs:
                    if (autils._unescaped(inputs['genusTypeId'])):
                        querier.match_genus_type(quote(inputs['genusTypeId'], safe='/ '), match=True)
                    else:
                        querier.match_genus_type(inputs['genusTypeId'], match=True)
                items = assessment_bank.get_items_by_query(querier)
            else:
                items = assessment_bank.get_items()

            if 'qti' in web.input():
                data = []

                for item in items:
                    # do this first to not mess up unrandomized MC choices
                    item_qti = item.get_qti_xml(media_file_root_path=autils.get_media_path(assessment_bank))
                    item_map = item.object_map
                    item_map.update({
                        'qti': item_qti
                    })
                    data.append(item_map)
                data = json.dumps(data)
            else:
                data = utilities.extract_items(items)

            return data
        except (PermissionDenied, InvalidId) as ex:
            utilities.handle_exceptions(ex)

    @utilities.format_response
    def POST(self, bank_id=None, assessment_id=None):
        try:
            am = autils.get_assessment_manager()
            if bank_id is None:
                utilities.verify_keys_present(self.data(), ['bankId'])
                bank_id = self.data()['bankId']
            bank = am.get_bank(utilities.clean_id(bank_id))

            try:
                x = web.input(qtiFile={})
                # get each set of files individually, because
                # we are doing this in memory, so the file pointer changes
                # once we read in a file
                # https://docs.python.org/2/library/zipfile.html
                keywords = []
                description = ''
                learning_objective = None
                media_files = {}
                qti_file = None

                # get manifest keywords first
                with zipfile.ZipFile(x['qtiFile'].file) as qti_zip:
                    for zip_file_name in qti_zip.namelist():
                        if zip_file_name == 'imsmanifest.xml':
                            manifest = qti_zip.open(zip_file_name)
                            manifest_xml = manifest.read()
                            manifest_soup = BeautifulSoup(manifest_xml, 'lxml-xml')
                            if manifest_soup.resources.resource.metadata.general.description:
                                for keyword in manifest_soup.resources.resource.metadata.general.description:
                                    if keyword is not None and keyword.string is not None:
                                        if '[type]' in keyword.string:
                                            split_keywords = keyword.string.split('}')
                                            type_tag = split_keywords[0]
                                            keywords.append(type_tag.replace('[type]', '').replace('<', '').replace('>', '').replace('{', '').replace('}', ''))
                                            if len(split_keywords) > 1:
                                                description += '\n'.join(split_keywords[1::]).strip()
                                        else:
                                            description += keyword.string
                            if manifest_soup.resources.lom:
                                for classification in manifest_soup.resources.lom.find_all('classification'):
                                    if classification.purpose.value.string == 'target audience':
                                        learning_objective = classification.taxonPath.taxon.entry.string.string

                # now get media files
                with zipfile.ZipFile(x['qtiFile'].file) as qti_zip:
                    for zip_file_name in qti_zip.namelist():
                        if 'media/' in zip_file_name and zip_file_name != 'media/':
                            # this method must match what is in the QTI QuestionFormRecord
                            file_name = zip_file_name.replace('media/', '').replace('.', '_')
                            file_obj = DataInputStream(StringIO(qti_zip.open(zip_file_name).read()))
                            file_obj.name = zip_file_name
                            media_files[file_name] = file_obj

                # now deal with the question xml
                with zipfile.ZipFile(x['qtiFile'].file) as qti_zip:
                    for zip_file_name in qti_zip.namelist():
                        if ('.xml' in zip_file_name and
                                'media/' not in zip_file_name and
                                zip_file_name != 'imsmanifest.xml'):
                            qti_file = qti_zip.open(zip_file_name, 'rU')

                    qti_xml = qti_file.read()

                    # clean out &nbsp; non-breaking spaces (unicode char \xa0)
                    qti_xml = qti_xml.replace('\xa0', ' ').replace('\xc2', ' ')

                    # to handle video tags, we need to do a blanket replace
                    # of  &lt; => <
                    # and &gt; => >
                    # with the assumption that will not break anything else ...
                    # clean_qti_xml = qti_xml.replace('&lt;', '<').replace('&gt;', '>')
                    # deprecated
                    clean_qti_xml = qti_xml

                    soup = BeautifulSoup(clean_qti_xml, 'xml')

                    # QTI ID alias check to see if this item exists already
                    # if so, create a new item and provenance it...
                    original_qti_id = utilities.construct_qti_id(soup.assessmentItem['identifier'])
                    try:
                        parent_item = bank.get_item(original_qti_id)
                        add_provenance_parent = True
                    except (NotFound, InvalidId):
                        parent_item = None
                        add_provenance_parent = False

                    # if this is a numeric response, do not add the wrong answer item
                    # record, because need that to go through the magical items
                    if soup.itemBody.textEntryInteraction and soup.templateDeclaration:
                        items_records_list = [QTI_ITEM,
                                              PROVENANCE_ITEM_RECORD,
                                              MULTI_LANGUAGE_ITEM_RECORD]
                    else:
                        items_records_list = [QTI_ITEM,
                                              PROVENANCE_ITEM_RECORD,
                                              WRONG_ANSWER_ITEM,
                                              MULTI_LANGUAGE_ITEM_RECORD]
                    form = bank.get_item_form_for_create(items_records_list)

                    # in order to support multi-languages, let's keep the title
                    # but minus the last language code
                    # i.e. ee_u1l01a01q01_en
                    # keep ee_u1l01a01q01 as the item name
                    item_name = soup.assessmentItem['title']
                    language_code = None
                    if any(lang_code in item_name for lang_code in ['en', 'hi', 'te']):
                        language_code = item_name.split('_')[-1]
                        item_name = '_'.join(item_name.split('_')[0:-1])

                    form.add_display_name(utilities.create_display_text(item_name,
                                                                        language_code))

                    form.add_description(utilities.create_display_text(description or 'QTI AssessmentItem',
                                                                       language_code))
                    form.load_from_qti_item(clean_qti_xml,
                                            keywords=keywords)
                    if learning_objective is not None:
                        # let's use unicode by default ...
                        # try:
                        #     form.set_learning_objectives([utilities.clean_id('learning.Objective%3A{0}%40CLIX.TISS.EDU'.format(learning_objective))])
                        # except UnicodeEncodeError:
                        form.set_learning_objectives([utilities.clean_id(u'learning.Objective%3A{0}%40CLIX.TISS.EDU'.format(learning_objective).encode('utf8'))])
                    if add_provenance_parent:
                        form.set_provenance(str(parent_item.ident))
                        # and also archive the parent
                        autils.archive_item(bank, parent_item)
                    new_item = bank.create_item(form)

                    # ID Alias with the QTI ID from Onyx
                    bank.alias_item(new_item.ident,
                                    original_qti_id)

                    q_form = bank.get_question_form_for_create(new_item.ident, [QTI_QUESTION,
                                                                                MULTI_LANGUAGE_QUESTION_RECORD])
                    if len(media_files) == 0:
                        media_files = None

                    q_form.load_from_qti_item(clean_qti_xml,
                                              media_files=media_files,
                                              keywords=keywords)
                    question = bank.create_question(q_form)

                    local_map = {
                        'type': str(new_item.genus_type)
                    }
                    if (autils.is_multiple_choice(local_map) or
                            autils.is_ordered_choice(local_map)):
                        choices = question.get_choices()
                    else:
                        choices = None
                    answer_record_types = [QTI_ANSWER,
                                           MULTI_LANGUAGE_FEEDBACK_ANSWER_RECORD,
                                           FILES_ANSWER_RECORD]
                    # correct answer
                    # need a default one, even for extended text interaction
                    a_form = bank.get_answer_form_for_create(new_item.ident, answer_record_types)
                    a_form.load_from_qti_item(clean_qti_xml,
                                              keywords=keywords,
                                              correct=True,
                                              feedback_choice_id='correct',
                                              media_files=media_files)
                    answer = bank.create_answer(a_form)

                    # now let's do the incorrect answers with feedback, if available
                    if choices is not None:
                        # what if there are multiple right answer choices,
                        #  i.e. movable words?
                        right_answers = answer.object_map['choiceIds']
                        wrong_answers = [c for c in choices if c['id'] not in right_answers]

                        # survey questions should mark all choices as correct,
                        # because Onyx only lets you pick one ... so let's fix that ...
                        if autils.is_survey(local_map):
                            for wrong_answer in wrong_answers:
                                a_form = bank.get_answer_form_for_create(new_item.ident, answer_record_types)
                                # force to True in load_from_qti_item, once the choiceId is set
                                a_form.load_from_qti_item(clean_qti_xml,
                                                          keywords=keywords,
                                                          correct=False,
                                                          feedback_choice_id=wrong_answer['id'],
                                                          media_files=media_files)

                                bank.create_answer(a_form)
                        else:
                            # for now only support a generic wrong answer feedback for
                            # mc multi-select ... otherwise have to do scoring somehow
                            if (len(wrong_answers) > 0 and
                                    str(new_item.genus_type) != str(CHOICE_INTERACTION_MULTI_GENUS)):
                                for wrong_answer in wrong_answers:
                                    a_form = bank.get_answer_form_for_create(new_item.ident, answer_record_types)
                                    a_form.load_from_qti_item(clean_qti_xml,
                                                              keywords=keywords,
                                                              correct=False,
                                                              feedback_choice_id=wrong_answer['id'],
                                                              media_files=media_files)

                                    bank.create_answer(a_form)
                            else:
                                # create a generic one
                                a_form = bank.get_answer_form_for_create(new_item.ident, answer_record_types)
                                a_form.load_from_qti_item(clean_qti_xml,
                                                          keywords=keywords,
                                                          correct=False,
                                                          feedback_choice_id='incorrect',
                                                          media_files=media_files)

                                bank.create_answer(a_form)
                    elif str(new_item.genus_type) in [str(INLINE_CHOICE_INTERACTION_GENUS),
                                                      str(NUMERIC_RESPONSE_INTERACTION_GENUS)]:
                        # create a generic one
                        a_form = bank.get_answer_form_for_create(new_item.ident, answer_record_types)
                        a_form.load_from_qti_item(clean_qti_xml,
                                                  keywords=keywords,
                                                  correct=False,
                                                  feedback_choice_id='incorrect',
                                                  media_files=media_files)

                        bank.create_answer(a_form)

            except AttributeError:  #'dict' object has no attribute 'file'
                # let's do QTI questions differently
                if 'genusTypeId' in self.data() and 'qti' in self.data()['genusTypeId']:
                    # do QTI-ish stuff
                    # QTI ID alias check to see if this item exists already
                    # if so, create a new item and provenance it...
                    item_json = self.data()
                    item_genus = Type(item_json['genusTypeId'])

                    if item_genus not in [CHOICE_INTERACTION_MULTI_SELECT_SURVEY_GENUS,
                                          CHOICE_INTERACTION_SURVEY_GENUS,
                                          CHOICE_INTERACTION_GENUS,
                                          CHOICE_INTERACTION_MULTI_GENUS,
                                          UPLOAD_INTERACTION_AUDIO_GENUS,
                                          UPLOAD_INTERACTION_GENERIC_GENUS,
                                          ORDER_INTERACTION_MW_SENTENCE_GENUS,
                                          ORDER_INTERACTION_MW_SANDBOX_GENUS,
                                          ORDER_INTERACTION_OBJECT_MANIPULATION_GENUS,
                                          EXTENDED_TEXT_INTERACTION_GENUS,
                                          INLINE_CHOICE_INTERACTION_GENUS,
                                          NUMERIC_RESPONSE_INTERACTION_GENUS]:
                        raise OperationFailed('Item type not supported, or unrecognized')

                    add_provenance_parent = False
                    parent_item = None

                    if 'provenanceItemId' in item_json:
                        try:
                            original_item_id = utilities.clean_id(item_json['provenanceItemId'])
                            parent_item = bank.get_item(original_item_id)
                            add_provenance_parent = True
                        except (NotFound, InvalidId):
                            pass

                    # if this is a numeric response, do not add the wrong answer item
                    # record, because need that to go through the magical items
                    if item_json['genusTypeId'] == str(NUMERIC_RESPONSE_INTERACTION_GENUS):
                        items_records_list = [QTI_ITEM,
                                              PROVENANCE_ITEM_RECORD,
                                              MULTI_LANGUAGE_ITEM_RECORD,
                                              NUMERIC_RESPONSE_RECORD]
                    elif item_json['genusTypeId'] == str(INLINE_CHOICE_INTERACTION_GENUS):
                        items_records_list = [QTI_ITEM,
                                              PROVENANCE_ITEM_RECORD,
                                              WRONG_ANSWER_ITEM,
                                              MULTI_LANGUAGE_ITEM_RECORD,
                                              INLINE_CHOICE_ITEM_RECORD]
                    else:
                        items_records_list = [QTI_ITEM,
                                              PROVENANCE_ITEM_RECORD,
                                              WRONG_ANSWER_ITEM,
                                              MULTI_LANGUAGE_ITEM_RECORD]

                    if item_genus in [CHOICE_INTERACTION_MULTI_SELECT_SURVEY_GENUS,
                                      CHOICE_INTERACTION_SURVEY_GENUS,
                                      CHOICE_INTERACTION_GENUS,
                                      CHOICE_INTERACTION_MULTI_GENUS,
                                      ORDER_INTERACTION_MW_SENTENCE_GENUS,
                                      ORDER_INTERACTION_MW_SANDBOX_GENUS,
                                      ORDER_INTERACTION_OBJECT_MANIPULATION_GENUS]:
                        items_records_list.append(RANDOMIZED_MULTI_CHOICE_ITEM_RECORD)

                    form = bank.get_item_form_for_create(items_records_list)
                    form = utilities.set_form_basics(form, item_json)

                    if 'learningObjectiveId' in item_json:
                        form.set_learning_objectives([utilities.clean_id(item_json['learningObjectiveId'])])
                    if add_provenance_parent:
                        form.set_provenance(str(parent_item.ident))
                        # and also archive the parent
                        autils.archive_item(bank, parent_item)

                    new_item = bank.create_item(form)

                    if 'question' in item_json:
                        question = item_json['question']
                        # need to add the right records here, depending on question / item type
                        question_record_types = [QTI_QUESTION, MULTI_LANGUAGE_QUESTION_RECORD]
                        question_type = Type(question['genusTypeId'])

                        if question_type in [CHOICE_INTERACTION_QUESTION_GENUS,
                                             CHOICE_INTERACTION_MULTI_QUESTION_GENUS,
                                             CHOICE_INTERACTION_SURVEY_QUESTION_GENUS,
                                             CHOICE_INTERACTION_MULTI_SELECT_SURVEY_QUESTION_GENUS,
                                             ORDER_INTERACTION_MW_SENTENCE_QUESTION_GENUS,
                                             ORDER_INTERACTION_MW_SANDBOX_QUESTION_GENUS,
                                             ORDER_INTERACTION_OBJECT_MANIPULATION_QUESTION_GENUS]:
                            question_record_types.append(RANDOMIZED_MULTI_CHOICE_QUESTION_RECORD)

                        if question_type in [CHOICE_INTERACTION_QUESTION_GENUS,
                                             CHOICE_INTERACTION_MULTI_QUESTION_GENUS,
                                             CHOICE_INTERACTION_SURVEY_QUESTION_GENUS,
                                             CHOICE_INTERACTION_MULTI_SELECT_SURVEY_QUESTION_GENUS]:
                            question_record_types.append(MULTI_LANGUAGE_MULTIPLE_CHOICE_QUESTION_RECORD)
                        elif question_type in [UPLOAD_INTERACTION_AUDIO_QUESTION_GENUS,
                                               UPLOAD_INTERACTION_GENERIC_QUESTION_GENUS]:
                            question_record_types.append(MULTI_LANGUAGE_FILE_UPLOAD_QUESTION_RECORD)
                        elif question_type in [ORDER_INTERACTION_MW_SENTENCE_QUESTION_GENUS,
                                               ORDER_INTERACTION_MW_SANDBOX_QUESTION_GENUS,
                                               ORDER_INTERACTION_OBJECT_MANIPULATION_QUESTION_GENUS]:
                            question_record_types.append(MULTI_LANGUAGE_ORDERED_CHOICE_QUESTION_RECORD)
                        elif question_type in [EXTENDED_TEXT_INTERACTION_QUESTION_GENUS]:
                            question_record_types.append(MULTI_LANGUAGE_EXTENDED_TEXT_INTERACTION_QUESTION_RECORD)
                        elif question_type in [INLINE_CHOICE_MW_FITB_INTERACTION_QUESTION_GENUS]:
                            question_record_types.append(MULTI_LANGUAGE_INLINE_CHOICE_QUESTION_RECORD)
                        elif question_type in [NUMERIC_RESPONSE_QUESTION_GENUS]:
                            question_record_types.append(MULTI_LANGUAGE_NUMERIC_RESPONSE_QUESTION_RECORD)

                        q_form = bank.get_question_form_for_create(new_item.ident,
                                                                   question_record_types)

                        # need to set name / description and genusTypeId
                        q_form = utilities.set_form_basics(q_form, question)

                        # update_question_form should handle everything else
                        # this recordTypeIds info is needed for both update_question_form methods
                        question['recordTypeIds'] = [str(t) for t in question_record_types]
                        q_form = autils.update_question_form(question, q_form)

                        # need to also handle fileIds / images / media attached to the question
                        q_form = autils.update_question_form_with_files(q_form, question)

                        bank.create_question(q_form)

                    if 'answers' in item_json:
                        for answer in item_json['answers']:
                            # records depends on the genusTypeId of the ITEM
                            # can't rely on answer genus type because that's used for
                            # right / wrong answers
                            answer_record_types = [QTI_ANSWER,
                                                   MULTI_LANGUAGE_FEEDBACK_ANSWER_RECORD,
                                                   FILES_ANSWER_RECORD]
                            if item_genus in [CHOICE_INTERACTION_MULTI_SELECT_SURVEY_GENUS,
                                              CHOICE_INTERACTION_SURVEY_GENUS,
                                              CHOICE_INTERACTION_GENUS,
                                              CHOICE_INTERACTION_MULTI_GENUS,
                                              ORDER_INTERACTION_MW_SENTENCE_GENUS,
                                              ORDER_INTERACTION_OBJECT_MANIPULATION_GENUS]:
                                answer_record_types.append(SIMPLE_MULTIPLE_CHOICE_ANSWER_RECORD)
                            elif item_genus in [ORDER_INTERACTION_MW_SANDBOX_GENUS,
                                                UPLOAD_INTERACTION_AUDIO_GENUS,
                                                UPLOAD_INTERACTION_GENERIC_GENUS]:
                                answer_record_types.append(FILE_SUBMISSION_ANSWER_RECORD)
                            elif item_json['genusTypeId'] == str(EXTENDED_TEXT_INTERACTION_GENUS):
                                answer_record_types.append(EXTENDED_TEXT_INTERACTION_ANSWER_RECORD)
                            elif item_json['genusTypeId'] == str(INLINE_CHOICE_INTERACTION_GENUS):
                                answer_record_types.append(SIMPLE_INLINE_CHOICE_ANSWER_RECORD)
                            elif item_json['genusTypeId'] == str(NUMERIC_RESPONSE_INTERACTION_GENUS):
                                answer_record_types.append(MULTI_LANGUAGE_NUMERIC_RESPONSE_ANSWER_RECORD)

                            a_form = bank.get_answer_form_for_create(new_item.ident, answer_record_types)

                            # set genusTypeId to right / wrong and feedback
                            a_form = autils.set_answer_form_genus_and_feedback(answer, a_form)

                            # add media via fileIds
                            # this update to recordTypeIds needed for both update_answer_form methods
                            answer['recordTypeIds'] = [str(t) for t in answer_record_types]
                            a_form = autils.update_answer_form_with_files(a_form, answer)

                            # set conditions / choiceIds
                            a_form = autils.update_answer_form(answer, a_form)

                            bank.create_answer(a_form)
                else:
                    expected = ['name', 'description']
                    utilities.verify_keys_present(self.data(), expected)
                    new_item = autils.create_new_item(bank, self.data())
                    # create questions and answers if they are part of the
                    # input data. There must be a better way to figure out
                    # which attributes I should set, given the
                    # question type?
                    if 'question' in self.data():
                        question = self.data()['question']

                        if isinstance(question, basestring):
                            question = json.loads(question)

                        if 'rerandomize' in self.data() and 'rerandomize' not in question:
                            question['rerandomize'] = self.data()['rerandomize']

                        q_type = Type(question['type'])
                        qfc = bank.get_question_form_for_create(item_id=new_item.ident,
                                                                question_record_types=[q_type])
                        qfc = autils.update_question_form(question, qfc, create=True)

                        if 'genus' in question:
                            qfc.genus_type = Type(question['genus'])

                        if ('fileIds' in new_item.object_map and
                                len(new_item.object_map['fileIds'].keys()) > 0):
                            # add these files to the question, too
                            file_ids = new_item.object_map['fileIds']
                            qfc = autils.add_file_ids_to_form(qfc, file_ids)

                        new_question = bank.create_question(qfc)
                    if 'answers' in self.data():
                        answers = self.data()['answers']
                        if isinstance(answers, basestring):
                            answers = json.loads(answers)
                        for answer in answers:
                            a_types = autils.get_answer_records(answer)

                            afc = bank.get_answer_form_for_create(new_item.ident,
                                                                  a_types)

                            if 'multi-choice' in answer['type']:
                                # because multiple choice answers need to match to
                                # the actual MC3 ChoiceIds, NOT the index passed
                                # in by the consumer.
                                if not new_question:
                                    raise NullArgument('Question')
                                afc = autils.update_answer_form(answer, afc, new_question)
                            else:
                                afc = autils.update_answer_form(answer, afc)

                            if 'genus' not in answer:
                                answer['genus'] = str(RIGHT_ANSWER_GENUS)

                            afc = autils.set_answer_form_genus_and_feedback(answer, afc)
                            new_answer = bank.create_answer(afc)

            full_item = bank.get_item(new_item.ident)
            return_data = utilities.convert_dl_object(full_item)

            # for convenience, also return the wrong answers
            try:
                wrong_answers = full_item.get_wrong_answers()
                return_data = json.loads(return_data)
                for wa in wrong_answers:
                    return_data['answers'].append(wa.object_map)
                return_data = json.dumps(return_data)
            except AttributeError:
                pass
            return return_data
        except (KeyError, PermissionDenied, Unsupported,
                InvalidArgument, NullArgument, TypeError, InvalidId) as ex:
            utilities.handle_exceptions(ex)


class AssessmentDetails(utilities.BaseClass):
    """
    Get assessment details for the given bank
    api/v1/assessment/banks/<bank_id>/assessments/<assessment_id>/

    GET, PUT, DELETE
    PUT to modify an existing assessment. Include only the changed parameters.
    DELETE to remove from the repository.

    Note that for RESTful calls, you need to set the request header
    'content-type' to 'application/json'

    Example (note the use of double quotes!!):
       {"name" : "an updated assessment"}
    """
    @utilities.format_response
    def DELETE(self, bank_id, sub_id):
        try:
            am = autils.get_assessment_manager()
            bank = am.get_bank(utilities.clean_id(bank_id))
            data = bank.delete_assessment(utilities.clean_id(sub_id))
            return web.Accepted()
        except (PermissionDenied, IllegalState, InvalidId) as ex:
            utilities.handle_exceptions(ex)

    @utilities.format_response
    def GET(self, bank_id, sub_id):
        try:
            am = autils.get_assessment_manager()
            als = am.get_assessment_lookup_session()
            als.use_federated_bank_view()
            data = utilities.convert_dl_object(als.get_assessment(utilities.clean_id(sub_id)))
            return data
        except (PermissionDenied, NotFound, InvalidId) as ex:
            utilities.handle_exceptions(ex)

    @utilities.format_response
    def PUT(self, bank_id, sub_id):
        try:
            local_data_map = self.data()
            am = autils.get_assessment_manager()
            bank = am.get_bank(utilities.clean_id(bank_id))
            form = bank.get_assessment_form_for_update(utilities.clean_id(sub_id))

            form = utilities.set_form_basics(form, local_data_map)

            updated_assessment = bank.update_assessment(form)

            if 'itemIds' in local_data_map:
                # first clear out existing items
                for item in bank.get_assessment_items(utilities.clean_id(sub_id)):
                    bank.remove_item(utilities.clean_id(sub_id), item.ident)

                # now add the new ones
                if isinstance(local_data_map['itemIds'], basestring):
                    items = json.loads(local_data_map['itemIds'])
                else:
                    items = local_data_map['itemIds']

                if not isinstance(items, list):
                    try:
                        utilities.clean_id(items)  # use this as proxy to test if a valid OSID ID
                        items = [items]
                    except:
                        raise InvalidArgument

                for item_id in items:
                    bank.add_item(utilities.clean_id(sub_id), utilities.clean_id(item_id))

            full_assessment = bank.get_assessment(updated_assessment.ident)
            data = utilities.convert_dl_object(full_assessment)

            return data
        except (PermissionDenied, InvalidArgument, InvalidId) as ex:
            utilities.handle_exceptions(ex)


class AssessmentHierarchiesNodeChildrenList(utilities.BaseClass):
    """
    List the children for a root bank.
    api/v1/assessment/hierarchies/nodes/<bank_id>/children/

    POST allows you to update the children list (bulk update)

    Note that for RESTful calls, you need to set the request header
    'content-type' to 'application/json'

    Example (note the use of double quotes!!):
      {"id": "assessment.Bank:54f9e39833bb7293e9da5b44@oki-dev.MIT.EDU"}

    """
    @utilities.format_response
    def GET(self, bank_id):
        """
        List children of a node
        """
        def update_bank_names(node_list):
            for node in node_list:
                bank = am.get_bank(utilities.clean_id(node['id']))
                node['displayName'] = {
                    'text': bank.display_name.text
                }
                update_bank_names(node['childNodes'])

        try:
            am = autils.get_assessment_manager()
            if 'descendants' in web.input():
                descendant_levels = int(web.input()['descendants'])
            else:
                descendant_levels = 1
            nodes = am.get_bank_nodes(utilities.clean_id(bank_id),
                                      0, descendant_levels, False)
            if 'display_names' in web.input():
                data = json.loads(utilities.extract_items(nodes.get_child_bank_nodes()))
                update_bank_names(data)
                data = json.dumps(data)
            else:
                data = utilities.extract_items(nodes.get_child_bank_nodes())
            return data
        except (PermissionDenied, InvalidId) as ex:
            utilities.handle_exceptions(ex)

    @utilities.format_response
    def POST(self, bank_id):
        """
        """
        try:
            utilities.verify_keys_present(self.data(), 'ids')
            am = autils.get_assessment_manager()

            # first remove current child banks, if present
            try:
                am.remove_child_banks(utilities.clean_id(bank_id))
            except NotFound:
                pass

            if not isinstance(self.data()['ids'], list):
                self.data()['ids'] = [self.data()['ids']]
            for child_id in self.data()['ids']:
                child_bank = am.get_bank(utilities.clean_id(child_id))
                am.add_child_bank(utilities.clean_id(bank_id),
                                                          child_bank.ident)
            return web.Created()
        except (PermissionDenied, NotFound, KeyError, InvalidId) as ex:
            utilities.handle_exceptions(ex)


class AssessmentHierarchiesNodeDetails(utilities.BaseClass):
    """
    List the bank details for a node bank.
    api/v1/assessment/hierarchies/nodes/<bank_id>/

    GET only. Can provide ?ancestors and ?descendants values to
              get nodes up and down the hierarchy.

    Note that for RESTful calls, you need to set the request header
    'content-type' to 'application/json'
    """
    @utilities.format_response
    def GET(self, bank_id):
        """
        List details of a node bank
        """
        try:
            if 'ancestors' in web.input():
                ancestor_levels = int(web.input()['ancestors'])
            else:
                ancestor_levels = 0
            if 'descendants' in web.input():
                descendant_levels = int(web.input()['descendants'])
            else:
                descendant_levels = 0
            include_siblings = False

            am = autils.get_assessment_manager()
            node_data = am.get_bank_nodes(utilities.clean_id(bank_id),
                                                                  ancestor_levels,
                                                                  descendant_levels,
                                                                  include_siblings)

            data = node_data.get_object_node_map()
            return data
        except (PermissionDenied, InvalidId) as ex:
            utilities.handle_exceptions(ex)


class AssessmentHierarchiesRootsList(utilities.BaseClass):
    """
    List all available assessment hierarchy root nodes.
    api/v1/assessment/hierarchies/roots/

    POST allows you to add an existing bank as a root bank in
    the hierarchy.

    Note that for RESTful calls, you need to set the request header
    'content-type' to 'application/json'

    Example (note the use of double quotes!!):
      {"id": "assessment.Bank:54f9e39833bb7293e9da5b44@oki-dev.MIT.EDU"}
    """
    @utilities.format_response
    def GET(self):
        """
        List all available root assessment banks
        """
        try:
            am = autils.get_assessment_manager()
            root_banks = am.get_root_banks()
            banks = utilities.extract_items(root_banks)
            return banks
        except (PermissionDenied, InvalidId) as ex:
            utilities.handle_exceptions(ex)

    @utilities.format_response
    def POST(self):
        """
        Add a bank as a root to the hierarchy

        """
        try:
            utilities.verify_keys_present(self.data(), ['id'])
            am = autils.get_assessment_manager()
            try:
                am.get_bank(utilities.clean_id(self.data()['id']))
            except:
                raise InvalidArgument()

            am.add_root_bank(utilities.clean_id(self.data()['id']))
            return web.Created()
        except (PermissionDenied, InvalidArgument, InvalidId) as ex:
            utilities.handle_exceptions(ex)


class AssessmentHierarchiesRootDetails(utilities.BaseClass):
    """
    List the bank details for a root bank. Allow you to remove it as a root
    api/v1/assessment/hierarchies/roots/<bank_id>/

    DELETE allows you to remove a root bank.

    Note that for RESTful calls, you need to set the request header
    'content-type' to 'application/json'
    """
    @utilities.format_response
    def DELETE(self, bank_id):
        """
        Remove bank as root bank
        """
        try:
            am = autils.get_assessment_manager()
            root_bank_ids = am.get_root_bank_ids()
            if utilities.clean_id(bank_id) in root_bank_ids:
                am.remove_root_bank(utilities.clean_id(bank_id))
            else:
                raise IllegalState('That bank is not a root.')
            return web.Accepted()
        except (PermissionDenied, IllegalState, InvalidId) as ex:
            utilities.handle_exceptions(ex)

    @utilities.format_response
    def GET(self, bank_id):
        """
        List details of a root bank
        """
        try:
            am = autils.get_assessment_manager()
            root_bank_ids = am.get_root_bank_ids()
            if utilities.clean_id(bank_id) in root_bank_ids:
                bank = am.get_bank(utilities.clean_id(bank_id))
            else:
                raise IllegalState('That bank is not a root.')

            data = bank.object_map
            return data
        except (PermissionDenied, IllegalState, InvalidId) as ex:
            utilities.handle_exceptions(ex)


class ItemDetails(utilities.BaseClass):
    """
    Get item details for the given bank
    api/v1/assessment/banks/<bank_id>/items/<item_id>/

    GET, PUT, DELETE
    PUT to modify an existing item. Include only the changed parameters.
    DELETE to remove from the repository.

    Note that for RESTful calls, you need to set the request header
    'content-type' to 'application/json'

    Example (note the use of double quotes!!):
       {"name" : "an updated item"}
    """
    @utilities.format_response
    def DELETE(self, bank_id, sub_id):
        try:
            am = autils.get_assessment_manager()
            bank = am.get_bank(utilities.clean_id(bank_id))
            data = bank.delete_item(utilities.clean_id(sub_id))
            return web.Accepted()
        except (PermissionDenied, InvalidId) as ex:
            utilities.handle_exceptions(ex)
        except IllegalState as ex:
            utilities.handle_exceptions(type(ex)('This Item is being used in one or more '
                                              'Assessments. Delink it first, before '
                                              'deleting it.'))

    @utilities.format_response
    def GET(self, bank_id, sub_id):
        try:
            am = autils.get_assessment_manager()
            ils = am.get_item_lookup_session()
            ils.use_federated_bank_view()

            item = ils.get_item(utilities.clean_id(sub_id))
            data = utilities.convert_dl_object(item)

            # if 'fileIds' in data:
            #     data['files'] = item.get_files()
            # if data['question'] and 'fileIds' in data['question']:
            #     data['question']['files'] = item.get_question().get_files()

            # for convenience, also return the wrong answers
            try:
                data = json.loads(data)
                wrong_answers = item.get_wrong_answers()
                for wa in wrong_answers:
                    data['answers'].append(wa.object_map)
                data = json.dumps(data)
            except AttributeError:
                pass

            return data
        except (PermissionDenied, NotFound, InvalidId) as ex:
            utilities.handle_exceptions(ex)

    @utilities.format_response
    def PUT(self, bank_id, sub_id):
        try:
            am = autils.get_assessment_manager()
            bank = am.get_bank(utilities.clean_id(bank_id))
            local_data_map = self.data()

            if any(attr in local_data_map for attr in ['name', 'description', 'learningObjectiveIds',
                                                       'attempts', 'markdown', 'showanswer',
                                                       'weight', 'difficulty', 'discrimination',
                                                       'removeName', 'editName', 'removeDescription',
                                                       'editDescription', 'aliasId']):
                form = bank.get_item_form_for_update(utilities.clean_id(sub_id))

                form = utilities.set_form_basics(form, local_data_map)

                # update the item before the questions / answers,
                # because otherwise the old form will over-write the
                # new question / answer data
                # for edX items, update any metadata passed in
                if 'type' not in local_data_map:
                    if len(form._my_map['recordTypeIds']) > 0:
                        local_data_map['type'] = form._my_map['recordTypeIds'][0]
                    else:
                        local_data_map['type'] = ''

                form = autils.update_item_metadata(local_data_map, form)

                updated_item = bank.update_item(form)

                if 'aliasId' in local_data_map:
                    bank.alias_item(updated_item.ident,
                                    utilities.clean_id(local_data_map['aliasId']))
            else:
                updated_item = bank.get_item(utilities.clean_id(sub_id))

            if 'question' in local_data_map:
                question = local_data_map['question']
                existing_question = updated_item.get_question()
                existing_question_map = existing_question.object_map
                q_id = existing_question.ident

                if 'type' not in question:
                    question['type'] = existing_question_map['recordTypeIds'][0]
                if 'recordTypeIds' not in question:
                    question['recordTypeIds'] = existing_question_map['recordTypeIds']

                if 'rerandomize' in local_data_map and 'rerandomize' not in question:
                    question['rerandomize'] = local_data_map['rerandomize']

                qfu = bank.get_question_form_for_update(updated_item.ident)
                qfu = autils.update_question_form(question, qfu)

                qfu = autils.update_question_form_with_files(qfu, question)

                updated_question = bank.update_question(qfu)

            if 'answers' in local_data_map:
                for answer in local_data_map['answers']:
                    if 'id' in answer:
                        a_id = utilities.clean_id(answer['id'])
                        afu = bank.get_answer_form_for_update(a_id)

                        if 'recordTypeIds' not in answer:
                            answer['recordTypeIds'] = afu._my_map['recordTypeIds']

                        afu = autils.update_answer_form_with_files(afu, answer)

                        afu = autils.update_answer_form(answer, afu)
                        afu = autils.set_answer_form_genus_and_feedback(answer, afu)
                        bank.update_answer(afu)
                    else:
                        # also let you add files here?
                        a_types = autils.get_answer_records(answer)
                        afc = bank.get_answer_form_for_create(utilities.clean_id(sub_id),
                                                              a_types)
                        afc = autils.set_answer_form_genus_and_feedback(answer, afc)
                        if 'recordTypeIds' not in answer:
                            answer['recordTypeIds'] = [str(t) for t in a_types]

                        if 'multi-choice' in answer['type']:
                            # because multiple choice answers need to match to
                            # the actual MC3 ChoiceIds, NOT the index passed
                            # in by the consumer.
                            question = updated_item.get_question()
                            afc = autils.update_answer_form(answer, afc, question)
                        else:
                            afc = autils.update_answer_form(answer, afc)
                        bank.create_answer(afc)

            full_item = bank.get_item(utilities.clean_id(sub_id))

            return_data = utilities.convert_dl_object(full_item)

            # for convenience, also return the wrong answers
            try:
                wrong_answers = full_item.get_wrong_answers()
                return_data = json.loads(return_data)
                for wa in wrong_answers:
                    return_data['answers'].append(wa.object_map)
                return_data = json.dumps(return_data)
            except AttributeError:
                pass

            return return_data
        except (PermissionDenied, Unsupported, InvalidArgument, NotFound, InvalidId) as ex:
            utilities.handle_exceptions(ex)


class ItemQTIDetails(utilities.BaseClass):
    """
    Get QTI version of an item
    api/v1/assessment/banks/<bank_id>/items/<item_id>/qti

    GET
    """
    @utilities.format_xml_response
    def GET(self, bank_id, sub_id):
        try:
            am = autils.get_assessment_manager()
            ils = am.get_item_lookup_session()
            ils.use_federated_bank_view()

            item = ils.get_item(utilities.clean_id(sub_id))

            # don't do item.object_map here to get the bankId,
            # we've "gotten" the question and set the choice order (for randomized
            # MC). So by getting the QTI XML here, it's impossible to get the
            # original choice order, if shuffle = False...
            item_bank = am.get_bank(utilities.clean_id(item._my_map['assignedBankIds'][0]))

            return item.get_qti_xml(media_file_root_path=autils.get_media_path(item_bank))
        except (PermissionDenied, NotFound) as ex:
            utilities.handle_exceptions(ex)



class AssessmentItemsList(utilities.BaseClass):
    """
    Get or link items in an assessment
    api/v1/assessment/banks/<bank_id>/assessments/<assessment_id>/items/

    GET, POST
    GET to view currently linked items
    POST to link a new item (appended to the current list)

    Note that for RESTful calls, you need to set the request header
    'content-type' to 'application/json'

    Example (note the use of double quotes!!):
       {"itemIds" : ["assessment.Item%3A539ef3a3ea061a0cb4fba0a3%40birdland.mit.edu"]}
    """
    @utilities.format_response
    def GET(self, bank_id, sub_id):
        try:
            am = autils.get_assessment_manager()
            bank = am.get_bank(utilities.clean_id(bank_id))
            items = bank.get_assessment_items(utilities.clean_id(sub_id))

            if 'qti' in web.input():
                data = []

                for item in items:
                    # do this first, to not mess up unrandomized choices
                    item_qti_xml = item.get_qti_xml(media_file_root_path=autils.get_media_path(bank))
                    item_map = item.object_map
                    item_map.update({
                        'qti': item_qti_xml
                    })
                    data.append(item_map)
                data = json.dumps(data)
            else:
                data = utilities.extract_items(items)

            if 'files' in web.input():
                for item in data['data']['results']:
                    dlkit_item = bank.get_item(utilities.clean_id(item['id']))

                    if 'fileIds' in item:
                        item['files'] = dlkit_item.get_files()
                    if item['question'] and 'fileIds' in item['question']:
                        item['question']['files'] = dlkit_item.get_question().get_files()
            return data
        except (PermissionDenied, NotFound, InvalidId) as ex:
            utilities.handle_exceptions(ex)

    @utilities.format_response
    def POST(self, bank_id, sub_id):
        try:
            am = autils.get_assessment_manager()
            bank = am.get_bank(utilities.clean_id(bank_id))
            local_data_map = self.data()
            if 'itemIds' in local_data_map:
                if isinstance(local_data_map['itemIds'], basestring):
                    items = json.loads(local_data_map['itemIds'])
                else:
                    items = local_data_map['itemIds']

                if not isinstance(items, list):
                    try:
                        utilities.clean_id(items)  # use this as proxy to test if a valid OSID ID
                        items = [items]
                    except:
                        raise InvalidArgument

                for item_id in items:
                    bank.add_item(utilities.clean_id(sub_id),
                                  utilities.clean_id(item_id))

            items = bank.get_assessment_items(utilities.clean_id(sub_id))
            data = utilities.extract_items(items)
            return data
        except (PermissionDenied, InvalidArgument, InvalidId) as ex:
            utilities.handle_exceptions(ex)

    @utilities.format_response
    def PUT(self, bank_id, sub_id):
        """Use put to support full-replacement of the item list"""
        try:
            am = autils.get_assessment_manager()
            bank = am.get_bank(utilities.clean_id(bank_id))
            local_data_map = self.data()
            if 'itemIds' in local_data_map:
                # first clear out existing items
                for item in bank.get_assessment_items(utilities.clean_id(sub_id)):
                    bank.remove_item(utilities.clean_id(sub_id), item.ident)

                # now add the new ones
                if isinstance(local_data_map['itemIds'], basestring):
                    items = json.loads(local_data_map['itemIds'])
                else:
                    items = local_data_map['itemIds']

                if not isinstance(items, list):
                    try:
                        utilities.clean_id(items)  # use this as proxy to test if a valid OSID ID
                        items = [items]
                    except:
                        raise InvalidArgument

                for item_id in items:
                    bank.add_item(utilities.clean_id(sub_id), utilities.clean_id(item_id))

            items = bank.get_assessment_items(utilities.clean_id(sub_id))
            data = utilities.extract_items(items)
            return data
        except (PermissionDenied, InvalidArgument, InvalidId) as ex:
            utilities.handle_exceptions(ex)


class AssessmentItemDetails(utilities.BaseClass):
    """
    Get item details for the given assessment
    api/v1/assessment/banks/<bank_id>/assessments/<assessment_id>/items/<item_id>/

    GET, DELETE
    GET to view the item
    DELETE to remove item from the assessment (NOT from the repo)
    """
    @utilities.format_response
    def DELETE(self, bank_id, sub_id, item_id):
        try:
            am = autils.get_assessment_manager()
            bank = am.get_bank(utilities.clean_id(bank_id))
            data = bank.remove_item(utilities.clean_id(sub_id), utilities.clean_id(item_id))
            return web.Accepted()
        except (PermissionDenied, IllegalState, InvalidId) as ex:
            utilities.handle_exceptions(ex)


class AssessmentsOffered(utilities.BaseClass):
    """
    Get or create offerings of an assessment
    api/v1/assessment/banks/<bank_id>/assessments/<assessment_id>/assessmentsoffered/

    GET, POST
    GET to view current offerings
    POST to create a new offering (appended to the current offerings)

    Note that for RESTful calls, you need to set the request header
    'content-type' to 'application/json'

    Example (note the use of double quotes!!):
        [{"startTime" : {"year":2015,"month":1,"day":15},"duration": {"days":1}},{"startTime" : {"year":2015,"month":9,"day":15},"duration": {"days":1}}]
    """
    @utilities.format_response
    def GET(self, bank_id, sub_id):
        try:
            am = autils.get_assessment_manager()
            bank = am.get_bank(utilities.clean_id(bank_id))
            offerings = bank.get_assessments_offered_for_assessment(utilities.clean_id(sub_id))
            data = utilities.extract_items(offerings)
            return data
        except (PermissionDenied, NotFound, InvalidId) as ex:
            utilities.handle_exceptions(ex)

    @utilities.format_response
    def POST(self, bank_id, sub_id):
        # Cannot create offerings if no items attached to assessment
        try:
            am = autils.get_assessment_manager()
            bank = am.get_bank(utilities.clean_id(bank_id))
            autils.check_assessment_has_items(bank, utilities.clean_id(sub_id))

            if isinstance(self.data(), list):
                return_data = autils.set_assessment_offerings(bank,
                                                              self.data(),
                                                              utilities.clean_id(sub_id))
                data = utilities.extract_items(return_data)
            elif isinstance(self.data(), dict) and len(self.data().keys()) > 0:
                return_data = autils.set_assessment_offerings(bank,
                                                              [self.data()],
                                                              utilities.clean_id(sub_id))
                data = utilities.convert_dl_object(return_data[0])
            else:
                raise InvalidArgument()
            return data
        except (PermissionDenied, InvalidArgument, InvalidId) as ex:
            utilities.handle_exceptions(ex)
        except LookupError as ex:
            utilities.handle_exceptions(type(ex)('Cannot create an assessment offering for '
                                              'an assessment with no items.'))


class AssessmentOfferedDetails(utilities.BaseClass):
    """
    Get, edit, or delete offerings of an assessment
    api/v1/assessment/banks/<bank_id>/assessmentsoffered/<offered_id>/
    api/v1/assessment/banks/<bank_id>/assessments/<assessment_id>/assessments_offered/<offered_id>/

    GET, PUT, DELETE
    GET to view a specific offering
    PUT to edit the offering parameters
    DELETE to remove the offering

    Note that for RESTful calls, you need to set the request header
    'content-type' to 'application/json'

    Example (note the use of double quotes!!):
        This UI: {"startTime" : {"year":2015,"month":1,"day":15},"duration": {"days":5}}
    """
    @utilities.format_response
    def DELETE(self, bank_id, offering_id):
        try:
            am = autils.get_assessment_manager()
            bank = am.get_bank(utilities.clean_id(bank_id))
            data = bank.delete_assessment_offered(utilities.clean_id(offering_id))
            return web.Accepted()
        except (PermissionDenied, InvalidId) as ex:
            utilities.handle_exceptions(ex)
        except IllegalState as ex:
            utilities.handle_exceptions(type(ex)('There are still AssessmentTakens '
                                              'associated with this AssessmentOffered. '
                                              'Delete them first.'))

    @utilities.format_response
    def GET(self, bank_id, offering_id):
        try:
            am = autils.get_assessment_manager()
            aols = am.get_assessment_offered_lookup_session()
            aols.use_federated_bank_view()

            offering = aols.get_assessment_offered(utilities.clean_id(offering_id))
            data = utilities.convert_dl_object(offering)
            return data
        except (PermissionDenied, NotFound) as ex:
            utilities.handle_exceptions(ex)

    @utilities.format_response
    def PUT(self, bank_id, offering_id):
        try:
            am = autils.get_assessment_manager()
            bank = am.get_bank(utilities.clean_id(bank_id))

            if isinstance(self.data(), list):
                if len(self.data()) == 1:
                    return_data = autils.set_assessment_offerings(bank,
                                                                  self.data(),
                                                                  utilities.clean_id(offering_id),
                                                                  update=True)
                    data = utilities.extract_items(return_data)
                else:
                    raise InvalidArgument('Too many items.')
            elif isinstance(self.data(), dict):
                return_data = autils.set_assessment_offerings(bank,
                                                              [self.data()],
                                                              utilities.clean_id(offering_id),
                                                              update=True)
                data = utilities.convert_dl_object(return_data[0])
            else:
                raise InvalidArgument()
            return data
        except (PermissionDenied, InvalidArgument, InvalidId) as ex:
            utilities.handle_exceptions(ex)


class AssessmentOfferedResults(utilities.BaseClass):
    """
    Get the class results for an assessment offered (all the takens)
    api/v2/assessment/banks/<bank_id>/assessmentsoffered/<offered_id>/results/


    GET
    GET to view a specific offering
    """
    @utilities.format_response
    def GET(self, bank_id, offering_id):
        try:
            am = autils.get_assessment_manager()
            bank = am.get_bank(utilities.clean_id(bank_id))

            takens = bank.get_assessments_taken_for_assessment_offered(utilities.clean_id(offering_id))
            data = []
            for taken in takens:
                taken_map = taken.object_map

                # let's get the questions first ... we need to inject that information into
                # the response, so that UI side we can match on the original, canonical itemId
                # also need to include the questions's learningObjectiveIds
                sections = taken._get_assessment_sections()
                question_maps = []
                answers = []
                for section in sections:
                    questions = section.get_questions(update=False)
                    for index, question in enumerate(questions):
                        question_map = question.object_map
                        question_map.update({
                            'itemId': section._my_map['questions'][index]['itemId'],
                            'responses': []
                        })
                        question_maps.append(question_map)
                        answers.append(bank.get_answers(section.ident, question.ident))

                responses = bank.get_assessment_taken_responses(taken.ident)
                for index, response in enumerate(responses):
                    try:
                        response_map = response.object_map
                        response_map['type'] = response_map['recordTypeIds']
                        try:
                            response_map.update({
                                'isCorrect': response.is_correct()
                            })
                        except (AttributeError, IllegalState):
                            response_map.update({
                                'isCorrect': autils.validate_response(response_map, answers[index])
                            })
                        question_maps[index]['responses'].append(response_map)
                    except IllegalState:
                        question_maps[index]['responses'].append(None)
                taken_map.update({
                    'questions': question_maps
                })
                data.append(taken_map)
            data = utilities.extract_items(data)
            return data
        except (PermissionDenied, NotFound) as ex:
            utilities.handle_exceptions(ex)


class AssessmentsTaken(utilities.BaseClass):
    """
    Get or link takens of an assessment. Input can be from an offering or from an assessment --
    so will have to take that into account in the views.
    api/v1/assessment/banks/<bank_id>/assessments/<assessment_id>/assessmentstaken/
    api/v1/assessment/banks/<bank_id>/assessmentsoffered/<offered_id>/assessmentstaken/

    POST can only happen from an offering (need the offering ID to create a taken)
    GET, POST
    GET to view current assessment takens
    POST to link a new item (appended to the current list) --
            ONLY from offerings/<offering_id>/takens/

    Note that for RESTful calls, you need to set the request header
    'content-type' to 'application/json'

    Create example: POST with no data.
    """
    @utilities.format_response
    def GET(self, bank_id, sub_id):
        try:
            am = autils.get_assessment_manager()
            bank = am.get_bank(utilities.clean_id(bank_id))

            # use canSearch assessment takens as proxy for learner vs. instructor
            # learners should ideally only see their takens...not everyone else's
            if not bank.can_search_assessments_taken():
                raise PermissionDenied('You are not authorized to view this.')

            if 'assessment.AssessmentOffered' in sub_id:
                takens = bank.get_assessments_taken_for_assessment_offered(
                    utilities.clean_id(sub_id))
            else:
                takens = bank.get_assessments_taken_for_assessment(utilities.clean_id(sub_id))
            data = utilities.extract_items(takens)
            return data
        except (PermissionDenied, NotFound, InvalidId) as ex:
            utilities.handle_exceptions(ex)

    @utilities.format_response
    def POST(self, bank_id, sub_id):
        # when trying to create a taken for a user, check first
        # that a taken does not already exist, using
        # get_assessments_taken_for_taker_and_assessment_offered().
        # If it does exist, return that taken.
        # If one does not exist, create a new taken.
        try:
            # Kind of hokey, but need to get the sub_id type from a string...
            if 'assessment.AssessmentOffered' not in sub_id:
                raise Unsupported()
            am = autils.get_assessment_manager()
            bank = am.get_bank(utilities.clean_id(bank_id))

            # first check if a taken exists for the user / offering
            user_id = am.effective_agent_id
            takens = bank.get_assessments_taken_for_taker_and_assessment_offered(user_id,
                                                                                 utilities.clean_id(sub_id))

            create_new_taken = False
            if takens.available() > 0:
                # return the first taken ONLY if not finished -- user has attempted this problem
                # before. If finished, create a new one.
                first_taken = takens.next()
                if first_taken.has_ended():
                    # create new one
                    create_new_taken = True
                else:
                    data = utilities.convert_dl_object(first_taken)
            else:
                # create a new taken
                create_new_taken = True

            if create_new_taken:
                # use our new Taken Record object, which has a "can_review_whether_correct()"
                # method.
                form = bank.get_assessment_taken_form_for_create(utilities.clean_id(sub_id),
                                                                 [REVIEWABLE_TAKEN])
                data = utilities.convert_dl_object(bank.create_assessment_taken(form))

            return data
        except (PermissionDenied, InvalidArgument, InvalidId) as ex:
            utilities.handle_exceptions(ex)
        except Unsupported as ex:
            utilities.handle_exceptions(type(ex)('Can only create AssessmentTaken from an '
                                                 'AssessmentOffered root URL.'))


class AssessmentTakenDetails(utilities.BaseClass):
    """
    Get a single taken instance of an assessment. Not used for much
    except to point you towards the /take endpoint...
    api/v1/assessment/banks/<bank_id>/assessmentstaken/<taken_id>/

    GET, DELETE
    GET to view a specific taken
    DELETE to remove the taken

    Note that for RESTful calls, you need to set the request header
    'content-type' to 'application/json'
    """
    @utilities.format_response
    def DELETE(self, bank_id, taken_id):
        try:
            am = autils.get_assessment_manager()
            bank = am.get_bank(utilities.clean_id(bank_id))
            data = bank.delete_assessment_taken(utilities.clean_id(taken_id))
            return web.Accepted()
        except (PermissionDenied, NotFound, InvalidId) as ex:
            utilities.handle_exceptions(ex)

    @utilities.format_response
    def GET(self, bank_id, taken_id):
        try:
            am = autils.get_assessment_manager()
            atls = am.get_assessment_taken_lookup_session()
            atls.use_federated_bank_view()
            taken = atls.get_assessment_taken(utilities.clean_id(taken_id))
            data = utilities.convert_dl_object(taken)
            return data
        except (PermissionDenied, NotFound, InvalidId) as ex:
            utilities.handle_exceptions(ex)


class FinishAssessmentTaken(utilities.BaseClass):
    """
    "finish" the assessment to indicate that student has ended his/her attempt
    api/v1/assessment/banks/<bank_id>/assessmentstaken/<taken_id>/finish/

    POST empty data
    """
    @utilities.format_response
    def POST(self, bank_id, taken_id):
        try:
            am = autils.get_assessment_manager()
            assessment_session = am.get_assessment_session()
            # "finish" the assessment section
            # bank.finished_assessment_section(first_section.ident)
            assessment_session.finish_assessment(utilities.clean_id(taken_id))
            data = {
                'success': True
            }
            return data
        except (PermissionDenied, IllegalState, NotFound, InvalidId) as ex:
            utilities.handle_exceptions(ex)


class AssessmentTakenQuestions(utilities.BaseClass):
    """
    Returns all of the questions for a given assessment taken.
    Assumes that only one section per assessment.
    api/v1/assessment/banks/<bank_id>/assessmentstaken/<taken_id>/questions/

    Can add ?qti to get the QTI version of all questions (if available)

    GET only
    """
    @utilities.format_response
    @utilities.format_response_mit_type
    def GET(self, bank_id, taken_id):
        try:
            am = autils.get_assessment_manager()
            bank = am.get_bank(utilities.clean_id(bank_id))
            first_section = bank.get_first_assessment_section(utilities.clean_id(taken_id))
            questions = bank.get_questions(first_section.ident)
            if 'qti' in web.input():
                data = []
                for question in questions:
                    # do this first, to not mess up unrandomized choices
                    question_qti = question.get_qti_xml(media_file_root_path=autils.get_media_path(bank))
                    question_map = question.object_map
                    question_map.update({
                        'qti': question_qti
                    })
                    data.append(question_map)
                data = json.dumps(data)
            else:
                data = utilities.extract_items(questions)

            return data
        except (PermissionDenied, IllegalState, NotFound, InvalidId) as ex:
            utilities.handle_exceptions(ex)


class AssessmentTakenQuestionDetails(utilities.BaseClass):
    """
    Returns the specified question
    api/v1/assessment/banks/<bank_id>/assessmentstaken/<taken_id>/questions/<question_id>/

    GET only
    """
    @utilities.format_response
    def GET(self, bank_id, taken_id, question_id):
        try:
            am = autils.get_assessment_manager()
            bank = am.get_bank(utilities.clean_id(bank_id))
            first_section = bank.get_first_assessment_section(utilities.clean_id(taken_id))
            question = bank.get_question(first_section.ident,
                                         utilities.clean_id(question_id))
            data = utilities.convert_dl_object(question)

            status = autils.get_question_status(bank,
                                                first_section,
                                                utilities.clean_id(question_id))
            data = json.loads(data)
            data.update(status)

            # if 'fileIds' in data:
            #     data['files'] = question.get_files()

            data = json.dumps(data)
            return data
        except (PermissionDenied, IllegalState, NotFound, InvalidId) as ex:
            utilities.handle_exceptions(ex)


class AssessmentTakenQuestionQTIDetails(utilities.BaseClass):
    """
    Returns the specified question in QTI XML format
    api/v1/assessment/banks/<bank_id>/assessmentstaken/<taken_id>/questions/<question_id>/qti

    GET only
    """
    @utilities.format_xml_response
    def GET(self, bank_id, taken_id, question_id):
        try:
            am = autils.get_assessment_manager()
            bank = am.get_bank(utilities.clean_id(bank_id))
            first_section = bank.get_first_assessment_section(utilities.clean_id(taken_id))
            question = bank.get_question(first_section.ident,
                                         utilities.clean_id(question_id))
            data = question.get_qti_xml(media_file_root_path=autils.get_media_path(bank))
            # if 'fileIds' in data:
            #     data['files'] = question.get_files()
            return data
        except (PermissionDenied, IllegalState, NotFound, InvalidId) as ex:
            utilities.handle_exceptions(ex)


class AssessmentTakenQuestionStatus(utilities.BaseClass):
    """
    Gets the current status of a question in a taken -- responded to or not, correct or incorrect
    response (if applicable)
    api/v1/assessment/banks/<bank_id>/assessmentstaken/<taken_id>/questions/<question_id>/status/

    GET only

    Example (for an Ortho3D manipulatable - label type):
        {"responded": True,
         "correct"  : False
        }
    """
    @utilities.format_response
    def GET(self, bank_id, taken_id, question_id):
        try:
            am = autils.get_assessment_manager()
            bank = am.get_bank(utilities.clean_id(bank_id))
            first_section = bank.get_first_assessment_section(utilities.clean_id(taken_id))
            question = bank.get_question(first_section.ident,
                                         utilities.clean_id(question_id))

            data = autils.get_question_status(bank, first_section,
                                              utilities.clean_id(question_id))

            return data
        except (PermissionDenied, NotFound, InvalidId) as ex:
            utilities.handle_exceptions(ex)


class AssessmentTakenQuestionSubmit(utilities.BaseClass):
    """
    Submits a student response for the specified question
    Returns correct or not
    Does NOTHING to flag if the section is done or not...
    api/v1/assessment/banks/<bank_id>/assessmentstaken/<taken_id>/questions/<question_id>/submit/

    POST only

    Example (for an Ortho3D manipulatable - label type):
        {"integerValues":{
                "frontFaceValue" : 0,
                "sideFaceValue"  : 1,
                "topFaceValue"   : 2
            }
        }
    """
    @utilities.format_response
    def POST(self, bank_id, taken_id, question_id):
        try:
            x = web.input(submission={})

            am = autils.get_assessment_manager()
            bank = am.get_bank(utilities.clean_id(bank_id))
            first_section = bank.get_first_assessment_section(utilities.clean_id(taken_id))
            question = bank.get_question(first_section.ident,
                                         utilities.clean_id(question_id))
            response_form = bank.get_response_form(assessment_section_id=first_section.ident,
                                                   item_id=question.ident)
            local_data_map = self.data()
            if 'type' not in local_data_map:
                # kind of a hack
                question_map = question.object_map['genusTypeId']
                if question_map != 'GenusType%3ADEFAULT%40DLKIT.MIT.EDU':
                    local_data_map['type'] = question.object_map['genusTypeId']
                    local_data_map['type'] = local_data_map['type'].replace('question-type',
                                                                            'answer-type')
                else:
                    local_data_map['type'] = question.object_map['recordTypeIds'][0]
                    local_data_map['type'] = local_data_map['type'].replace('question-record-type',
                                                                            'answer-record-type')

            try:
                filename = x['submission'].filename
                if '.' not in filename:
                    extension = x['submission'].__dict__['type'].split('/')[-1]  # make assumption about mimetype
                    if extension not in ['mp3', 'wav']:
                        extension = 'wav'  # this is horrible ...
                    if extension not in filename:
                        filename = '{0}.{1}'.format(filename, extension)
                local_data_map['files'] = {filename: x['submission'].file}
            except AttributeError:
                if autils.is_file_submission(local_data_map) and not autils.is_mw_sandbox(local_data_map):
                    # TODO: for now, take empty response for MW Sandbox
                    raise IllegalState('You must supply a file with an audio response question')

            update_form = autils.update_response_form(local_data_map, response_form)
            bank.submit_response(first_section.ident, question.ident, update_form)
            # the above code logs the response in Mongo

            try:
                response = bank.get_response(first_section.ident, question.ident)
                correct = response.is_correct()
            except (AttributeError, IllegalState):
                # Now need to actually check the answers against the
                # item answers.
                answers = bank.get_answers(first_section.ident, question.ident)
                # compare these answers to the submitted response

                correct = autils.validate_response(local_data_map, answers)
            feedback = "No feedback available."
            return_data = {
                'correct': correct,
                'feedback': feedback
            }
            # update with item solution, if available
            feedback_strings = []
            confused_los = []
            try:
                taken = bank.get_assessment_taken(utilities.clean_id(taken_id))
                feedback = taken.get_solution_for_question(
                    utilities.clean_id(question_id))['explanation']
                if isinstance(feedback, basestring):
                    feedback = {
                        'text': feedback
                    }
                return_data.update({
                    'feedback': feedback
                })
            except (IllegalState, TypeError, AttributeError):
                # update with answer feedback, if available
                # for now, just support this for multiple choice questions...
                if (autils.is_multiple_choice(local_data_map) or
                        autils.is_ordered_choice(local_data_map)):
                    submissions = autils.get_response_submissions(local_data_map)
                    answers = bank.get_answers(first_section.ident, question.ident)

                    exact_answer_match = None
                    default_answer_match = None
                    for answer in answers:
                        correct_submissions = 0
                        answer_choice_ids = list(answer.get_choice_ids())
                        number_choices = len(answer_choice_ids)
                        if len(submissions) == number_choices:
                            for index, choice_id in enumerate(answer_choice_ids):
                                if autils.is_multiple_choice(local_data_map):
                                    if str(choice_id) in submissions:
                                        correct_submissions += 1
                        if not correct and str(answer.genus_type) == str(WRONG_ANSWER_GENUS):
                            # take the first wrong answer by default ... just in case
                            # we don't have an exact match
                            default_answer_match = answer
                        elif correct and str(answer.genus_type) == str(RIGHT_ANSWER_GENUS):
                            default_answer_match = answer

                        # try to find an exact answer match, first
                        if (correct_submissions == number_choices and
                                len(submissions) == number_choices):
                            exact_answer_match = answer

                    # now that we have either an exact match or a default (wrong) answer
                    # let's calculate the feedback and the confused LOs
                    answer_to_use = default_answer_match
                    if exact_answer_match is not None:
                        answer_to_use = exact_answer_match
                    try:
                        if any('qti' in answer_record
                               for answer_record in answer_to_use.object_map['recordTypeIds']):
                            feedback_strings.append(answer_to_use.get_qti_xml(media_file_root_path=autils.get_media_path(bank)))
                        else:
                            feedback_strings.append(answer_to_use.feedback.text)
                    except (KeyError, AttributeError):
                        pass
                    try:
                        confused_los += answer_to_use.confused_learning_objective_ids
                    except (KeyError, AttributeError):
                        pass
                elif (autils.is_file_submission(local_data_map) or
                        autils.is_short_answer(local_data_map)):
                    # right now assume one "correct" answer with generic feedback
                    answers = bank.get_answers(first_section.ident, question.ident)
                    feedback_strings = []
                    confused_los = []
                    for answer in answers:
                        if (correct and
                                str(answer.genus_type) == str(RIGHT_ANSWER_GENUS)):
                            try:
                                if any('qti' in answer_record
                                       for answer_record in answer.object_map['recordTypeIds']):
                                    feedback_strings.append(answer.get_qti_xml(media_file_root_path=autils.get_media_path(bank)))
                                else:
                                    feedback_strings.append(answer.feedback['text'])
                            except (KeyError, AttributeError):
                                pass
                            try:
                                confused_los += answer.confused_learning_objective_ids
                            except (KeyError, AttributeError):
                                pass
                            # only take the first feedback / confused LO for now
                            break
                elif autils.is_inline_choice(local_data_map):
                    answer_match = autils.match_submission_to_answer(answers, local_data_map)
                    try:
                        if any('qti' in answer_record
                               for answer_record in answer_match.object_map['recordTypeIds']):
                            feedback_strings.append(answer_match.get_qti_xml(media_file_root_path=autils.get_media_path(bank)))
                        else:
                            feedback_strings.append(answer_match.feedback['text'])
                    except (KeyError, AttributeError):
                        pass
                    try:
                        confused_los += answer_match.confused_learning_objective_ids
                    except (KeyError, AttributeError):
                        pass
                elif autils.is_numeric_response(local_data_map):
                    answers = bank.get_answers(first_section.ident, question.ident)
                    feedback_strings = []
                    confused_los = []
                    for answer in answers:
                        if ((correct and
                                str(answer.genus_type) == str(RIGHT_ANSWER_GENUS)) or (
                                not correct and str(answer.genus_type) == str(WRONG_ANSWER_GENUS))):
                            try:
                                if any('qti' in answer_record
                                       for answer_record in answer.object_map['recordTypeIds']):
                                    feedback_strings.append(answer.get_qti_xml(media_file_root_path=autils.get_media_path(bank)))
                                else:
                                    feedback_strings.append(answer.feedback['text'])
                            except (KeyError, AttributeError):
                                pass
                            try:
                                confused_los += answer.confused_learning_objective_ids
                            except (KeyError, AttributeError):
                                pass
                            # only take the first feedback / confused LO for now
                            break
            if len(feedback_strings) > 0:
                return_data.update({
                    'feedback': feedback_strings[0]
                })
            if len(confused_los) > 0:
                return_data.update({
                    'confusedLearningObjectiveIds': confused_los
                })

            return return_data
        except (PermissionDenied, IllegalState, NotFound, InvalidArgument, InvalidId) as ex:
            utilities.handle_exceptions(ex)


class AssessmentTakenQuestionSurrender(utilities.BaseClass):
    """
    Returns the answer if a student gives up and wants to just see the answer
    api/v1/assessment/banks/<bank_id>/assessmentstaken/<taken_id>/questions/<question_id>/surrender/

    POST only, no data

    Example (for an Ortho3D manipulatable - label type):
        {}
    """
    def POST(self, bank_id, taken_id, question_id):
        try:
            am = autils.get_assessment_manager()
            bank = am.get_bank(utilities.clean_id(bank_id))
            first_section = bank.get_first_assessment_section(utilities.clean_id(taken_id))
            question = bank.get_question(first_section.ident,
                                         utilities.clean_id(question_id))
            response_form = bank.get_response_form(assessment_section_id=first_section.ident,
                                                   item_id=question.ident)

            response_form.display_name = 'I surrendered'
            bank.submit_response(first_section.ident, question.ident, response_form)
            # the above code logs the response in Mongo

            answers = bank.get_answers(first_section.ident, question.ident)
            data = utilities.extract_items(answers)

            return data
        except (PermissionDenied, IllegalState, NotFound, InvalidId) as ex:
            utilities.handle_exceptions(ex)


class ItemVideoTagReplacement(utilities.BaseClass):
    """
    If a `[type]{video}` text tag is found in the item QTI / question text, this will
    replace it with the provided HTML markup, and also attempt to inject
    the right `AssetContent:<file_label>` replacement so that it can be
    output with the right relative URLs later.

    This assumes that all the files have been uploaded into a single asset,
    and the filename source in the HTML markup matches the displayName of
    the uploaded assetContent (i.e. it matches the original filename).

    api/v1/assessment/banks/<bank_id>/items/<item_id>/videoreplacement

    POST
    POST {
        "assetId": "asset%3A1%40CLIx",
        "html": "<video><track /></video>"
    }

    Note that for RESTful calls, you need to set the request header
    'content-type' to 'application/json'

    Example (note the use of double quotes!!):
       This UI: {"name" : "an assessment item","description" : "this is a hard quiz problem","question":{"type":"question-record-type%3Aresponse-string%40ODL.MIT.EDU","questionString":"Where am I?"},"answers":[{"type":"answer-record-type%3Aresponse-string%40ODL.MIT.EDU","responseString":"Here"}]}
    """
    @utilities.format_response
    def POST(self, bank_id, item_id):
        am = autils.get_assessment_manager()
        bank = am.get_bank(utilities.clean_id(bank_id))
        item = bank.get_item(utilities.clean_id(item_id))
        question = item.get_question()

        if 'texts' in question._my_map:
            question_texts_list = question._my_map['texts']
        else:
            question_texts_list = [question._my_map['text']]

        for question_text in question_texts_list:
            original_question_text = question_text['text']
            params = self.data()
            if ('[type]{video}' in original_question_text and
                    'html' in params and
                    'assetId' in params):
                rm = rutils.get_repository_manager()
                repository = rm.get_repository(bank.ident)
                asset = repository.get_asset(utilities.clean_id(params['assetId']))
                asset_contents = list(asset.get_asset_contents())

                if str(QUESTION_WITH_FILES) not in question.object_map['recordTypeIds']:
                    # this is so bad. Don't do this normally.
                    # use item.ident to avoid issues with magic sessions
                    form = bank.get_question_form_for_update(item.ident)
                    form._for_update = False
                    record = form.get_question_form_record(QUESTION_WITH_FILES)
                    record._init_metadata()
                    record._init_map()
                    form._for_update = True
                    bank.update_question(form)

                # use item.ident to avoid issues with magic sessions
                form = bank.get_question_form_for_update(item.ident)

                # first, update the text with just the new markup
                updated_text = original_question_text.replace('[type]{video}', params['html'])

                # second, update the question's fileList with the assets
                #     def add_asset(self, asset_id, asset_content_id=None, label=None, asset_content_type=None):
                for asset_content in asset_contents:
                    form.add_asset(asset.ident,
                                   asset_content_id=asset_content.ident,
                                   label=rutils.convert_ac_name_to_label(asset_content),
                                   asset_content_type=asset_content.genus_type)

                # third, replace the source attributes in the markup with
                # the AssetContent placeholders
                soup = BeautifulSoup(updated_text, 'xml')
                new_media_regex = re.compile('^(?!AssetContent).*$')
                for new_media in soup.find_all(src=new_media_regex):
                    original_file_name = new_media['src']
                    asset_content = rutils.match_asset_content_by_name(asset_contents,
                                                                       original_file_name)
                    if asset_content is not None:
                        new_media['src'] = 'AssetContent:{0}'.format(rutils.convert_ac_name_to_label(asset_content))

                # fourth, inject a crossorigin attribute for the video tag
                # per NickBenoit@AtomicJolt
                for video in soup.find_all('video'):
                    video['crossorigin'] = 'anonymous'

                # save it back
                original_text = DisplayText(display_text_map=question_text)
                updated_text = DisplayText(display_text_map={
                    'text': str(soup.itemBody),
                    'languageTypeId': question_text['languageTypeId'],
                    'formatTypeId': question_text['formatTypeId'],
                    'scriptTypeId': question_text['scriptTypeId']
                })
                try:
                    form.edit_text(original_text, updated_text)
                except AttributeError:
                    form.set_text(str(soup.itemBody))

                bank.update_question(form)
                item = bank.get_item(item.ident)

        return utilities.convert_dl_object(item)

app_assessment = web.application(urls, locals())
# session = utilities.activate_managers(web.session.Session(app_assessment,
#                                       web.session.DiskStore('sessions'),
#                                       initializer={
#                                           'am': None,
#                                           'logm': None,
#                                           'rm': None
#                                       }))
