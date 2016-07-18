import re
import json
import web
import zipfile

from bs4 import BeautifulSoup
from bson.errors import InvalidId

from cStringIO import StringIO

from dlkit_edx.errors import *
from dlkit_edx.primordium import Type, DataInputStream
from records.registry import ANSWER_GENUS_TYPES,\
    ASSESSMENT_TAKEN_RECORD_TYPES, COMMENT_RECORD_TYPES, BANK_RECORD_TYPES,\
    QUESTION_RECORD_TYPES, ANSWER_RECORD_TYPES, ITEM_RECORD_TYPES, ITEM_GENUS_TYPES,\
    ASSESSMENT_RECORD_TYPES

import assessment_utilities as autils
import utilities

ADVANCED_QUERY_ASSESSMENT_TAKEN_RECORD_TYPE = Type(**ASSESSMENT_TAKEN_RECORD_TYPES['advanced-query'])
CHOICE_INTERACTION_GENUS = Type(**ITEM_GENUS_TYPES['qti-choice-interaction'])
COLOR_BANK_RECORD_TYPE = Type(**BANK_RECORD_TYPES['bank-color'])
FILE_COMMENT_RECORD_TYPE = Type(**COMMENT_RECORD_TYPES['file-comment'])
ORDER_INTERACTION_MW_SENTENCE_GENUS = Type(**ITEM_GENUS_TYPES['qti-order-interaction-mw-sentence'])
PROVENANCE_ITEM_RECORD = Type(**ITEM_RECORD_TYPES['provenance'])
QTI_ANSWER = Type(**ANSWER_RECORD_TYPES['qti'])
QTI_ITEM = Type(**ITEM_RECORD_TYPES['qti'])
QTI_QUESTION = Type(**QUESTION_RECORD_TYPES['qti'])
REVIEWABLE_TAKEN = Type(**ASSESSMENT_TAKEN_RECORD_TYPES['review-options'])
SIMPLE_SEQUENCE_ASSESSMENT = Type(**ASSESSMENT_RECORD_TYPES['simple-child-sequencing'])
WRONG_ANSWER_ITEM = Type(**ITEM_RECORD_TYPES['wrong-answer'])


urls = (
    "/banks/(.*)/assessmentsoffered/(.*)/assessmentstaken", "AssessmentsTaken",
    "/banks/(.*)/assessmentsoffered/(.*)", "AssessmentOfferedDetails",
    "/banks/(.*)/assessmentstaken/(.*)/questions/(.*)/qti", "AssessmentTakenQuestionQTIDetails",
    "/banks/(.*)/assessmentstaken/(.*)/questions/(.*)/status", "AssessmentTakenQuestionStatus",
    "/banks/(.*)/assessmentstaken/(.*)/questions/(.*)/submit", "AssessmentTakenQuestionSubmit",
    "/banks/(.*)/assessmentstaken/(.*)/questions/(.*)", "AssessmentTakenQuestionDetails",
    "/banks/(.*)/assessmentstaken/(.*)/questions", "AssessmentTakenQuestions",
    "/banks/(.*)/assessmentstaken/(.*)/finish", "FinishAssessmentTaken",
    "/banks/(.*)/assessmentstaken/(.*)", "AssessmentTakenDetails",
    "/banks/(.*)/assessments/(.*)/assessmentsoffered", "AssessmentsOffered",
    "/banks/(.*)/assessments/(.*)/items/(.*)", "AssessmentItemDetails",
    "/banks/(.*)/assessments/(.*)/items", "AssessmentItemsList",
    "/banks/(.*)/assessments/(.*)", "AssessmentDetails",
    "/banks/(.*)/assessments", "AssessmentsList",
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

            form = utilities.set_form_basics(form, self.data())

            new_bank = utilities.convert_dl_object(am.create_bank(form))

            return new_bank
        except (PermissionDenied, InvalidArgument) as ex:
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
            form = am.get_bank_form_for_update(utilities.clean_id(bank_id))

            form = utilities.set_form_basics(form, self.data())
            updated_bank = am.update_bank(form)
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
            items = assessment_bank.get_items()

            if 'qti' in web.input():
                data = []

                for item in items:
                    item_map = item.object_map
                    item_map.update({
                        'qti': item.get_qti_xml(media_file_root_path=autils.get_media_path(assessment_bank))
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
            try:
                x = web.input(qtiFile={})
                bank = am.get_bank(utilities.clean_id(bank_id))
                # get each set of files individually, because
                # we are doing this in memory, so the file pointer changes
                # once we read in a file
                # https://docs.python.org/2/library/zipfile.html
                keywords = []
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
                                    if '[type]' in keyword.string:
                                        keywords.append(keyword.string.replace('[type]', '').replace('<', '').replace('>', ''))

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
                            qti_file = qti_zip.open(zip_file_name)

                    qti_xml = qti_file.read()
                    soup = BeautifulSoup(qti_xml, 'xml')

                    # QTI ID alias check to see if this item exists already
                    # if so, create a new item and provenance it...
                    original_qti_id = utilities.construct_qti_id(soup.assessmentItem['identifier'])
                    try:
                        parent_item = bank.get_item(original_qti_id)
                        add_provenance_parent = True
                    except (NotFound, InvalidId):
                        parent_item = None
                        add_provenance_parent = False

                    form = bank.get_item_form_for_create([QTI_ITEM,
                                                          PROVENANCE_ITEM_RECORD,
                                                          WRONG_ANSWER_ITEM])
                    form.display_name = soup.assessmentItem['title']
                    form.description = 'QTI AssessmentItem'
                    form.load_from_qti_item(qti_xml,
                                            keywords=keywords)

                    if add_provenance_parent:
                        form.set_provenance(str(parent_item.ident))

                    new_item = bank.create_item(form)

                    # ID Alias with the QTI ID from Onyx
                    bank.alias_item(new_item.ident,
                                    original_qti_id)

                    q_form = bank.get_question_form_for_create(new_item.ident, [QTI_QUESTION])

                    if len(media_files) > 0:
                        q_form.load_from_qti_item(qti_xml,
                                                  media_files=media_files,
                                                  keywords=keywords)
                    else:
                        q_form.load_from_qti_item(qti_xml,
                                                  keywords=keywords)
                    question = bank.create_question(q_form)

                    if str(new_item.genus_type) in [str(CHOICE_INTERACTION_GENUS),
                                                    str(ORDER_INTERACTION_MW_SENTENCE_GENUS)]:
                        choices = question.get_choices()
                    else:
                        choices = None

                    # correct answer
                    a_form = bank.get_answer_form_for_create(new_item.ident, [QTI_ANSWER])
                    a_form.load_from_qti_item(qti_xml,
                                              keywords=keywords,
                                              correct=True,
                                              feedback_choice_id='correct')
                    answer = bank.create_answer(a_form)

                    # now let's do the incorrect answers with feedback, if available
                    if choices is not None:
                        # what if there are multiple right answer choices,
                        #  i.e. movable words?
                        right_answers = answer.object_map['choiceIds']
                        wrong_answers = [c for c in choices if c['id'] not in right_answers]

                        if len(wrong_answers) > 0:
                            for wrong_answer in wrong_answers:
                                a_form = bank.get_answer_form_for_create(new_item.ident, [QTI_ANSWER])
                                a_form.load_from_qti_item(qti_xml,
                                                          keywords=keywords,
                                                          correct=False,
                                                          feedback_choice_id=wrong_answer['id'])

                                bank.create_answer(a_form)
                        else:
                            # create a generic one
                            a_form = bank.get_answer_form_for_create(new_item.ident, [QTI_ANSWER])
                            a_form.load_from_qti_item(qti_xml,
                                                      keywords=keywords,
                                                      correct=False,
                                                      feedback_choice_id='incorrect')

                            bank.create_answer(a_form)

            except AttributeError:  #'dict' object has no attribute 'file'
                expected = ['name', 'description']
                utilities.verify_keys_present(self.data(), expected)
                bank = am.get_bank(utilities.clean_id(bank_id))
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
            am = autils.get_assessment_manager()
            bank = am.get_bank(utilities.clean_id(bank_id))
            form = bank.get_assessment_form_for_update(utilities.clean_id(sub_id))

            form = utilities.set_form_basics(form, self.data())

            updated_assessment = bank.update_assessment(form)

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
        try:
            am = autils.get_assessment_manager()
            if 'descendants' in web.input():
                descendant_levels = int(web.input()['descendants'])
            else:
                descendant_levels = 1
            nodes = am.get_bank_nodes(utilities.clean_id(bank_id),
                                                              0, descendant_levels, False)
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
                                                    'weight', 'difficulty', 'discrimination']):
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
            else:
                updated_item = bank.get_item(utilities.clean_id(sub_id))

            if 'question' in local_data_map:
                question = local_data_map['question']
                existing_question = updated_item.get_question()
                q_id = existing_question.ident

                if 'type' not in question:
                    question['type'] = existing_question.object_map['recordTypeIds'][0]

                if 'rerandomize' in local_data_map and 'rerandomize' not in question:
                    question['rerandomize'] = local_data_map['rerandomize']

                qfu = bank.get_question_form_for_update(q_id)
                qfu = autils.update_question_form(question, qfu)
                updated_question = bank.update_question(qfu)

            if 'answers' in local_data_map:
                for answer in local_data_map['answers']:
                    if 'id' in answer:
                        a_id = utilities.clean_id(answer['id'])
                        afu = bank.get_answer_form_for_update(a_id)
                        afu = autils.update_answer_form(answer, afu)
                        afu = autils.set_answer_form_genus_and_feedback(answer, afu)
                        bank.update_answer(afu)
                    else:
                        a_types = autils.get_answer_records(answer)
                        afc = bank.get_answer_form_for_create(utilities.clean_id(sub_id),
                                                              a_types)
                        afc = autils.set_answer_form_genus_and_feedback(answer, afc)
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

            item_bank = am.get_bank(utilities.clean_id(item.object_map['bankId']))
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
                    item_map = item.object_map
                    item_map.update({
                        'qti': item.get_qti_xml(media_file_root_path=autils.get_media_path(bank))
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
                    question_map = question.object_map
                    question_map.update({
                        'qti': question.get_qti_xml(media_file_root_path=autils.get_media_path(bank))
                    })
                    data.append(question_map)
                data = json.dumps(data)
            else:
                data = utilities.extract_items(questions)

            # if 'files' in self.data():
            #     for question in data['data']['results']:
            #         if 'fileIds' in question:
            #             question['files'] = bank.get_question(first_section.ident,
            #                                                   utilities.clean_id(question['id'])).get_files()

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
            data.update(status)

            if 'fileIds' in data:
                data['files'] = question.get_files()
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
                local_data_map['files'] = {'submission': x['submission'].file}
            except AttributeError:
                pass

            update_form = autils.update_response_form(local_data_map, response_form)
            bank.submit_response(first_section.ident, question.ident, update_form)
            # the above code logs the response in Mongo

            # Now need to actually check the answers against the
            # item answers.
            answers = bank.get_answers(first_section.ident, question.ident)
            # compare these answers to the submitted response

            correct = autils.validate_response(local_data_map, answers)

            feedback = 'No feedback available.'

            return_data = {
                'correct': correct,
                'feedback': feedback
            }
            # update with item solution, if available
            try:
                taken = bank.get_assessment_taken(utilities.clean_id(taken_id))
                feedback = taken.get_solution_for_question(
                    utilities.clean_id(question_id))['explanation']
                return_data.update({
                    'feedback': feedback
                })
            except (IllegalState, TypeError, AttributeError):
                # update with answer feedback, if available
                # for now, just support this for multiple choice questions...
                if autils.is_multiple_choice(local_data_map):
                    submissions = autils.get_response_submissions(local_data_map)
                    answers = bank.get_answers(first_section.ident, question.ident)
                    feedback_strings = []
                    confused_los = []
                    for answer in answers:
                        if answer.get_choice_ids()[0] in submissions:
                            try:
                                if any('qti' in answer_record
                                       for answer_record in answer.object_map['recordTypeIds']):
                                    feedback_strings.append(answer.get_qti_xml(media_file_root_path=autils.get_media_path(bank)))
                                else:
                                    feedback_strings.append(answer.feedback)
                            except (KeyError, AttributeError):
                                pass
                            try:
                                confused_los += answer.confused_learning_objective_ids
                            except (KeyError, AttributeError):
                                pass
                    if len(feedback_strings) > 0:
                        feedback = '; '.join(feedback_strings)
                        return_data.update({
                            'feedback': feedback
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

app_assessment = web.application(urls, locals())
# session = utilities.activate_managers(web.session.Session(app_assessment,
#                                       web.session.DiskStore('sessions'),
#                                       initializer={
#                                           'am': None,
#                                           'logm': None,
#                                           'rm': None
#                                       }))
