import re
import json
import web

from bs4 import BeautifulSoup

from dlkit_edx.errors import *
from dlkit_edx.primordium import Type
from records.registry import ANSWER_GENUS_TYPES,\
    ASSESSMENT_TAKEN_RECORD_TYPES, COMMENT_RECORD_TYPES, BANK_RECORD_TYPES

import assessment_utilities as autils
import utilities

ADVANCED_QUERY_ASSESSMENT_TAKEN_RECORD_TYPE = Type(**ASSESSMENT_TAKEN_RECORD_TYPES['advanced-query'])
COLOR_BANK_RECORD_TYPE = Type(**BANK_RECORD_TYPES['bank-color'])
FILE_COMMENT_RECORD_TYPE = Type(**COMMENT_RECORD_TYPES['file-comment'])
REVIEWABLE_TAKEN = Type(**ASSESSMENT_TAKEN_RECORD_TYPES['review-options'])

urls = (
    "/banks/(.*)/items/(.*)", "ItemDetails",
    "/banks/(.*)/items", "ItemsList",
    "/banks/(.*)", "AssessmentBankDetails",
    "/banks", "AssessmentBanksList"
)


class AssessmentBanksList(utilities.BaseClass):
    """
    List all available assessment banks.
    api/v2/assessment/banks/

    POST allows you to create a new assessment bank, requires two parameters:
      * name
      * description

    Note that for RESTful calls, you need to set the request header
    'content-type' to 'application/json'

    Example (note the use of double quotes!!):
      {"name" : "a new bank","description" : "this is a test"}
    """
    def GET(self):
        """
        List all available assessment banks
        """
        try:
            assessment_banks = session._initializer['am'].banks
            banks = utilities.extract_items(assessment_banks)
            return banks
        except PermissionDenied as ex:
            utilities.handle_exceptions(ex)

    def POST(self):
        """
        Create a new assessment bank, if authorized
        Create a new group in IS&T Membership service

        """
        try:
            form = session._initializer['am'].get_bank_form_for_create([])

            form = utilities.set_form_basics(form, self.data())

            new_bank = utilities.convert_dl_object(session._initializer['am'].create_bank(form))

            return new_bank
        except (PermissionDenied, InvalidArgument) as ex:
            utilities.handle_exceptions(ex)


class AssessmentBankDetails(utilities.BaseClass):
    """
    Shows details for a specific assessment bank.
    api/v2/assessment/banks/<bank_id>/

    GET, PUT, DELETE
    PUT will update the assessment bank. Only changed attributes need to be sent.
    DELETE will remove the assessment bank.

    Note that for RESTful calls, you need to set the request header
    'content-type' to 'application/json'

    Example (note the use of double quotes!!):
       {"name" : "a new bank"}
    """
    def DELETE(self, bank_id):
        try:
            data = session._initializer['am'].delete_bank(utilities.clean_id(bank_id))
            return data
        except (PermissionDenied, IllegalState) as ex:
            utilities.handle_exceptions(ex)

    def GET(self, bank_id):
        try:
            assessment_bank = session._initializer['am'].get_bank(utilities.clean_id(bank_id))
            bank = utilities.convert_dl_object(assessment_bank)
            return bank
        except (PermissionDenied, NotFound) as ex:
            utilities.handle_exceptions(ex)

    def PUT(self, bank_id):
        try:
            form = session._initializer['am'].get_bank_form_for_update(utilities.clean_id(bank_id))

            form = utilities.set_form_basics(form, self.data())
            updated_bank = session._initializer['am'].update_bank(form)
            bank = utilities.convert_dl_object(updated_bank)
            return bank
        except (PermissionDenied, InvalidArgument) as ex:
            utilities.handle_exceptions(ex)


class AssessmentsList(utilities.BaseClass):
    """
    Get a list of all assessments in the specified bank
    api/v2/assessment/banks/<bank_id>/assessments/

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
    def GET(self, bank_id):
        try:
            assessment_bank = session._initializer['am'].get_bank(utilities.clean_id(bank_id))
            assessments = assessment_bank.get_assessments()

            data = utilities.extract_items(assessments)
            return data
        except PermissionDenied as ex:
            utilities.handle_exceptions(ex)

    def POST(self, bank_id):
        try:
            bank = new_assessment = None
            bank = session._initializer['am'].get_bank(utilities.clean_id(bank_id))
            form = bank.get_assessment_form_for_create([])

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
        except (PermissionDenied, NotFound, InvalidArgument) as ex:
            utilities.handle_exceptions(ex)


class ItemsList(utilities.BaseClass):
    """
    Return list of items in the given assessment bank. Make sure to embed
    the question and answers in the JSON.
    api/v2/assessment/banks/<bank_id>/items/

    GET, POST
    POST creates a new item

    Note that for RESTful calls, you need to set the request header
    'content-type' to 'application/json'

    Example (note the use of double quotes!!):
       This UI: {"name" : "an assessment item","description" : "this is a hard quiz problem","question":{"type":"question-record-type%3Aresponse-string%40ODL.MIT.EDU","questionString":"Where am I?"},"answers":[{"type":"answer-record-type%3Aresponse-string%40ODL.MIT.EDU","responseString":"Here"}]}
    """
    def GET(self, bank_id=None):
        try:
            if bank_id is None:
                raise PermissionDenied

            assessment_bank = session._initializer['am'].get_bank(utilities.clean_id(bank_id))

            items = assessment_bank.get_items()
            data = utilities.extract_items(items)

            return data
        except PermissionDenied as ex:
            utilities.handle_exceptions(ex)

    def POST(self, bank_id=None):
        try:
            bank = new_item = None

            if bank_id is None:
                utilities.verify_keys_present(self.data(), ['bankId'])
                bank_id = self.data()['bankId']

            expected = ['name', 'description']
            utilities.verify_keys_present(self.data(), expected)
            bank = session._initializer['am'].get_bank(utilities.clean_id(bank_id))
            # new_item = autils.create_new_item(bank, self.data())
            # create questions and answers if they are part of the
            # input data. There must be a better way to figure out
            # which attributes I should set, given the
            # question type?
            # if 'question' in self.data():
            #     question = self.data()['question']
            #
            #     if isinstance(question, basestring):
            #         question = json.loads(question)
            #
            #     if 'rerandomize' in self.data() and 'rerandomize' not in question:
            #         question['rerandomize'] = self.data()['rerandomize']
            #
            #     q_type = Type(question['type'])
            #     qfc = bank.get_question_form_for_create(item_id=new_item.ident,
            #                                             question_record_types=[q_type])
            #     qfc = autils.update_question_form(request, question, qfc, create=True)
            #
            #     if 'genus' in question:
            #         qfc.genus_type = Type(question['genus'])
            #
            #     if ('fileIds' in new_item.object_map and
            #             len(new_item.object_map['fileIds'].keys()) > 0):
            #         # add these files to the question, too
            #         file_ids = new_item.object_map['fileIds']
            #         qfc = autils.add_file_ids_to_form(qfc, file_ids)
            #
            #     new_question = bank.create_question(qfc)
            #
            # if 'answers' in self.data():
            #     answers = self.data()['answers']
            #     if isinstance(answers, basestring):
            #         answers = json.loads(answers)
            #     for answer in answers:
            #         a_types = autils.get_answer_records(answer)
            #
            #         afc = bank.get_answer_form_for_create(new_item.ident,
            #                                               a_types)
            #
            #         if 'multi-choice' in answer['type']:
            #             # because multiple choice answers need to match to
            #             # the actual MC3 ChoiceIds, NOT the index passed
            #             # in by the consumer.
            #             if not new_question:
            #                 raise NullArgument('Question')
            #             afc = autils.update_answer_form(answer, afc, new_question)
            #         else:
            #             afc = autils.update_answer_form(answer, afc)
            #
            #         afc = autils.set_answer_form_genus_and_feedback(answer, afc)
            #         new_answer = bank.create_answer(afc)

            full_item = bank.get_item(new_item.ident)
            return_data = utilities.convert_dl_object(full_item)

            # for convenience, also return the wrong answers
            try:
                wrong_answers = full_item.get_wrong_answers()
                for wa in wrong_answers:
                    return_data['answers'].append(wa.object_map)
            except AttributeError:
                pass

            return return_data
        except (KeyError, PermissionDenied, Unsupported,
                InvalidArgument, NullArgument) as ex:
            utilities.handle_exceptions(ex)


class AssessmentDetails(utilities.BaseClass):
    """
    Get assessment details for the given bank
    api/v2/assessment/banks/<bank_id>/assessments/<assessment_id>/

    GET, PUT, DELETE
    PUT to modify an existing assessment. Include only the changed parameters.
    DELETE to remove from the repository.

    Note that for RESTful calls, you need to set the request header
    'content-type' to 'application/json'

    Example (note the use of double quotes!!):
       {"name" : "an updated assessment"}
    """
    def DELETE(self, bank_id, sub_id):
        try:
            bank = session._initializer['am'].get_bank(utilities.clean_id(bank_id))
            data = bank.delete_assessment(utilities.clean_id(sub_id))
            return data
        except (PermissionDenied, IllegalState) as ex:
            utilities.handle_exceptions(ex)

    def GET(self, bank_id, sub_id):
        try:
            bank = session._initializer['am'].get_bank(utilities.clean_id(bank_id))
            data = utilities.convert_dl_object(bank.get_assessment(utilities.clean_id(sub_id)))
            return data
        except (PermissionDenied, NotFound) as ex:
            utilities.handle_exceptions(ex)

    def PUT(self, bank_id, sub_id):
        try:
            bank = session._initializer['am'].get_bank(utilities.clean_id(bank_id))
            form = bank.get_assessment_form_for_update(utilities.clean_id(sub_id))

            form = utilities.set_form_basics(form, self.data())

            updated_assessment = bank.update_assessment(form)

            full_assessment = bank.get_assessment(updated_assessment.ident)
            data = utilities.convert_dl_object(full_assessment)

            return data
        except (PermissionDenied, InvalidArgument) as ex:
            utilities.handle_exceptions(ex)


class ItemDetails(utilities.BaseClass):
    """
    Get item details for the given bank
    api/v2/assessment/banks/<bank_id>/items/<item_id>/

    GET, PUT, DELETE
    PUT to modify an existing item. Include only the changed parameters.
    DELETE to remove from the repository.

    Note that for RESTful calls, you need to set the request header
    'content-type' to 'application/json'

    Example (note the use of double quotes!!):
       {"name" : "an updated item"}
    """
    def DELETE(self, bank_id, sub_id):
        try:
            bank = session._initializer['am'].get_bank(utilities.clean_id(bank_id))
            data = bank.delete_item(utilities.clean_id(sub_id))
            return data
        except PermissionDenied as ex:
            utilities.handle_exceptions(ex)
        except IllegalState as ex:
            utilities.handle_exceptions(type(ex)('This Item is being used in one or more '
                                              'Assessments. Delink it first, before '
                                              'deleting it.'))

    def GET(self, bank_id, sub_id):
        try:
            bank = session._initializer['am'].get_bank(utilities.clean_id(bank_id))

            item = bank.get_item(utilities.clean_id(sub_id))
            data = utilities.convert_dl_object(item)

            if 'fileIds' in data:
                data['files'] = item.get_files()
            if data['question'] and 'fileIds' in data['question']:
                data['question']['files'] = item.get_question().get_files()

            # for convenience, also return the wrong answers
            try:
                wrong_answers = item.get_wrong_answers()
                for wa in wrong_answers:
                    data['answers'].append(wa.object_map)
            except AttributeError:
                pass

            return data
        except (PermissionDenied, NotFound) as ex:
            utilities.handle_exceptions(ex)

    def PUT(self, bank_id, sub_id):
        try:
            bank = session._initializer['am'].get_bank(utilities.clean_id(bank_id))

            if any(attr in self.data() for attr in ['name', 'description', 'learningObjectiveIds',
                                                   'attempts', 'markdown', 'showanswer',
                                                   'weight', 'difficulty', 'discrimination']):
                form = bank.get_item_form_for_update(utilities.clean_id(sub_id))

                form = utilities.set_form_basics(form, self.data())

                # update the item before the questions / answers,
                # because otherwise the old form will over-write the
                # new question / answer data
                # for edX items, update any metadata passed in
                if 'type' not in self.data():
                    if len(form._my_map['recordTypeIds']) > 0:
                        self.data()['type'] = form._my_map['recordTypeIds'][0]
                    else:
                        self.data()['type'] = ''

                # form = autils.update_item_metadata(self.data(), form)

                updated_item = bank.update_item(form)
            else:
                updated_item = bank.get_item(utilities.clean_id(sub_id))

            if 'question' in self.data():
                question = self.data()['question']
                existing_question = updated_item.get_question()
                q_id = existing_question.ident

                if 'type' not in question:
                    question['type'] = existing_question.object_map['recordTypeIds'][0]

                if 'rerandomize' in self.data() and 'rerandomize' not in question:
                    question['rerandomize'] = self.data()['rerandomize']

                qfu = bank.get_question_form_for_update(q_id)
                # qfu = autils.update_question_form(request, question, qfu)
                updated_question = bank.update_question(qfu)

            if 'answers' in self.data():
                for answer in self.data()['answers']:
                    if 'id' in answer:
                        a_id = utilities.clean_id(answer['id'])
                        afu = bank.get_answer_form_for_update(a_id)
                        # afu = autils.update_answer_form(answer, afu)
                        bank.update_answer(afu)
                    else:
                        # a_types = autils.get_answer_records(answer)
                        a_types = []
                        afc = bank.get_answer_form_for_create(utilities.clean_id(sub_id),
                                                              a_types)
                        # afc = autils.set_answer_form_genus_and_feedback(answer, afc)
                        if 'multi-choice' in answer['type']:
                            # because multiple choice answers need to match to
                            # the actual MC3 ChoiceIds, NOT the index passed
                            # in by the consumer.
                            question = updated_item.get_question()
                            # afc = autils.update_answer_form(answer, afc, question)
                        else:
                            # afc = autils.update_answer_form(answer, afc)
                            pass
                        bank.create_answer(afc)

            full_item = bank.get_item(utilities.clean_id(sub_id))

            return_data = utilities.convert_dl_object(full_item)

            # for convenience, also return the wrong answers
            try:
                wrong_answers = full_item.get_wrong_answers()
                for wa in wrong_answers:
                    return_data['answers'].append(wa.object_map)
            except AttributeError:
                pass

            return return_data
        except (PermissionDenied, Unsupported, InvalidArgument, NotFound) as ex:
            utilities.handle_exceptions(ex)


class AssessmentItemsList(utilities.BaseClass):
    """
    Get or link items in an assessment
    api/v2/assessment/banks/<bank_id>/assessments/<assessment_id>/items/

    GET, POST
    GET to view currently linked items
    POST to link a new item (appended to the current list)

    Note that for RESTful calls, you need to set the request header
    'content-type' to 'application/json'

    Example (note the use of double quotes!!):
       {"itemIds" : ["assessment.Item%3A539ef3a3ea061a0cb4fba0a3%40birdland.mit.edu"]}
    """
    def GET(self, bank_id, sub_id):
        try:
            bank = session._initializer['am'].get_bank(utilities.clean_id(bank_id))
            items = bank.get_assessment_items(utilities.clean_id(sub_id))
            data = utilities.extract_items(items)

            if 'files' in self.data():
                for item in data['data']['results']:
                    dlkit_item = bank.get_item(utilities.clean_id(item['id']))

                    if 'fileIds' in item:
                        item['files'] = dlkit_item.get_files()
                    if item['question'] and 'fileIds' in item['question']:
                        item['question']['files'] = dlkit_item.get_question().get_files()
            return data
        except (PermissionDenied, NotFound) as ex:
            utilities.handle_exceptions(ex)

    def POST(self, bank_id, sub_id):
        try:
            bank = session._initializer['am'].get_bank(utilities.clean_id(bank_id))

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
                    bank.add_item(utilities.clean_id(sub_id),
                                  utilities.clean_id(item_id))

            items = bank.get_assessment_items(utilities.clean_id(sub_id))
            data = utilities.extract_items(items)
            return data
        except (PermissionDenied, InvalidArgument) as ex:
            utilities.handle_exceptions(ex)

    def PUT(self, bank_id, sub_id):
        """Use put to support full-replacement of the item list"""
        try:
            bank = session._initializer['am'].get_bank(utilities.clean_id(bank_id))

            if 'itemIds' in self.data():
                # first clear out existing items
                for item in bank.get_assessment_items(utilities.clean_id(sub_id)):
                    bank.remove_item(utilities.clean_id(sub_id), item.ident)

                # now add the new ones
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
                    bank.add_item(utilities.clean_id(sub_id), utilities.clean_id(item_id))

            items = bank.get_assessment_items(utilities.clean_id(sub_id))
            data = utilities.extract_items(items)
            return data
        except (PermissionDenied, InvalidArgument) as ex:
            utilities.handle_exceptions(ex)


class AssessmentItemDetails(utilities.BaseClass):
    """
    Get item details for the given assessment
    api/v2/assessment/banks/<bank_id>/assessments/<assessment_id>/items/<item_id>/

    GET, DELETE
    GET to view the item
    DELETE to remove item from the assessment (NOT from the repo)
    """
    def DELETE(self, bank_id, sub_id, item_id):
        try:
            bank = session._initializer['am'].get_bank(utilities.clean_id(bank_id))
            data = bank.remove_item(utilities.clean_id(sub_id), utilities.clean_id(item_id))
            return data
        except (PermissionDenied, IllegalState) as ex:
            utilities.handle_exceptions(ex)

    # def GET(self, bank_id, sub_id, item_id):
    #     view = ItemDetails.as_view()
    #     return view(request, bank_id=bank_id, sub_id=item_id, format=format)
    #
    # def put(self, request, bank_id, sub_id, item_id, format=None):
    #     view = ItemDetails.as_view()
    #     return view(request, bank_id, item_id, format)


class AssessmentsOffered(utilities.BaseClass):
    """
    Get or create offerings of an assessment
    api/v2/assessment/banks/<bank_id>/assessments/<assessment_id>/assessmentsoffered/

    GET, POST
    GET to view current offerings
    POST to create a new offering (appended to the current offerings)

    Note that for RESTful calls, you need to set the request header
    'content-type' to 'application/json'

    Example (note the use of double quotes!!):
        [{"startTime" : {"year":2015,"month":1,"day":15},"duration": {"days":1}},{"startTime" : {"year":2015,"month":9,"day":15},"duration": {"days":1}}]
    """
    def GET(self, bank_id, sub_id):
        try:
            bank = session._initializer['am'].get_bank(utilities.clean_id(bank_id))
            offerings = bank.get_assessments_offered_for_assessment(utilities.clean_id(sub_id))
            data = utilities.extract_items(offerings)
            return data
        except (PermissionDenied, NotFound) as ex:
            utilities.handle_exceptions(ex)

    def POST(self, bank_id, sub_id):
        # Cannot create offerings if no items attached to assessment
        try:
            bank = session._initializer['am'].get_bank(utilities.clean_id(bank_id))

            autils.check_assessment_has_items(bank, utilities.clean_id(sub_id))

            if isinstance(self.data(), list):
                return_data = autils.set_assessment_offerings(bank,
                                                              self.data(),
                                                              utilities.clean_id(sub_id))
                data = utilities.extract_items(return_data)
            elif isinstance(self.data(), dict):
                return_data = autils.set_assessment_offerings(bank,
                                                              [self.data()],
                                                              utilities.clean_id(sub_id))
                data = utilities.convert_dl_object(return_data[0])
            else:
                raise InvalidArgument()
            return data
        except (PermissionDenied, InvalidArgument) as ex:
            utilities.handle_exceptions(ex)
        except LookupError as ex:
            utilities.handle_exceptions(type(ex)('Cannot create an assessment offering for '
                                              'an assessment with no items.'))


class AssessmentOfferedDetails(utilities.BaseClass):
    """
    Get, edit, or delete offerings of an assessment
    api/v2/assessment/banks/<bank_id>/assessmentsoffered/<offered_id>/
    api/v2/assessment/banks/<bank_id>/assessments/<assessment_id>/assessments_offered/<offered_id>/

    GET, PUT, DELETE
    GET to view a specific offering
    PUT to edit the offering parameters
    DELETE to remove the offering

    Note that for RESTful calls, you need to set the request header
    'content-type' to 'application/json'

    Example (note the use of double quotes!!):
        This UI: {"startTime" : {"year":2015,"month":1,"day":15},"duration": {"days":5}}
    """
    def DELETE(self, bank_id, offering_id):
        try:
            bank = session._initializer['am'].get_bank(utilities.clean_id(bank_id))
            data = bank.delete_assessment_offered(utilities.clean_id(offering_id))
            return data
        except PermissionDenied as ex:
            utilities.handle_exceptions(ex)
        except IllegalState as ex:
            utilities.handle_exceptions(type(ex)('There are still AssessmentTakens '
                                              'associated with this AssessmentOffered. '
                                              'Delete them first.'))

    def GET(self, bank_id, offering_id):
        try:
            bank = session._initializer['am'].get_bank(utilities.clean_id(bank_id))

            offering = bank.get_assessment_offered(utilities.clean_id(offering_id))
            data = utilities.convert_dl_object(offering)
            return data
        except (PermissionDenied, NotFound) as ex:
            utilities.handle_exceptions(ex)

    def PUT(self, bank_id, offering_id):
        try:
            bank = session._initializer['am'].get_bank(utilities.clean_id(bank_id))

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
        except (PermissionDenied, InvalidArgument) as ex:
            utilities.handle_exceptions(ex)


class AssessmentsTaken(utilities.BaseClass):
    """
    Get or link takens of an assessment. Input can be from an offering or from an assessment --
    so will have to take that into account in the views.
    api/v2/assessment/banks/<bank_id>/assessments/<assessment_id>/assessmentstaken/
    api/v2/assessment/banks/<bank_id>/assessmentsoffered/<offered_id>/assessmentstaken/

    POST can only happen from an offering (need the offering ID to create a taken)
    GET, POST
    GET to view current assessment takens
    POST to link a new item (appended to the current list) --
            ONLY from offerings/<offering_id>/takens/

    Note that for RESTful calls, you need to set the request header
    'content-type' to 'application/json'

    Create example: POST with no data.
    """
    def GET(self, bank_id, sub_id):
        try:
            bank = session._initializer['am'].get_bank(utilities.clean_id(bank_id))

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
        except (PermissionDenied, NotFound) as ex:
            utilities.handle_exceptions(ex)

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
            bank = session._initializer['am'].get_bank(utilities.clean_id(bank_id))

            # first check if a taken exists for the user / offering
            user_id = session._initializer['am'].effective_agent_id
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
        except (PermissionDenied, InvalidArgument) as ex:
            utilities.handle_exceptions(ex)
        except Unsupported as ex:
            utilities.handle_exceptions(type(ex)('Can only create AssessmentTaken from an '
                                                 'AssessmentOffered root URL.'))


class AssessmentTakenDetails(utilities.BaseClass):
    """
    Get a single taken instance of an assessment. Not used for much
    except to point you towards the /take endpoint...
    api/v2/assessment/banks/<bank_id>/assessmentstaken/<taken_id>/

    GET, DELETE
    GET to view a specific taken
    DELETE to remove the taken

    Note that for RESTful calls, you need to set the request header
    'content-type' to 'application/json'
    """
    def DELETE(self, bank_id, taken_id):
        try:
            bank = session._initializer['am'].get_bank(utilities.clean_id(bank_id))
            data = bank.delete_assessment_taken(utilities.clean_id(taken_id))
            return data
        except (PermissionDenied, NotFound) as ex:
            utilities.handle_exceptions(ex)

    def GET(self, bank_id, taken_id):
        try:
            bank = session._initializer['am'].get_bank(utilities.clean_id(bank_id))
            taken = bank.get_assessment_taken(utilities.clean_id(taken_id))
            data = utilities.convert_dl_object(taken)
            return data
        except (PermissionDenied, NotFound) as ex:
            utilities.handle_exceptions(ex)


class ItemQuestion(utilities.BaseClass):
    """Edit question for an existing item

    api/v2/assessment/banks/<bank_id>/items/<item_id>/question/

    GET, PUT
    GET to get the question.
    PUT to modify the question.

    Note that for RESTful calls, you need to set the request header
    'content-type' to 'application/json'

    Example (note the use of double quotes!!):
       {"questionString" : "What is 1 + 1?"}
    """
    def GET(self, bank_id, sub_id):
        try:
            bank = session._initializer['am'].get_bank(utilities.clean_id(bank_id))

            item = bank.get_item(utilities.clean_id(sub_id))
            existing_question = item.get_question()
            data = utilities.convert_dl_object(existing_question)
            if 'fileIds' in data:
                data.update({
                    'files': existing_question.get_files()
                })
            return data
        except (PermissionDenied, InvalidArgument) as ex:
            utilities.handle_exceptions(ex)

    def PUT(self, bank_id, sub_id):
        # TODO: handle updating of question files (manip and ortho view set)
        try:
            bank = session._initializer['am'].get_bank(utilities.clean_id(bank_id))

            item = bank.get_item(utilities.clean_id(sub_id))
            existing_question = item.get_question()

            if 'type' not in self.data():
                # kind of a hack
                self.data()['type'] = existing_question.object_map['recordTypeIds'][0]

            q_id = existing_question.ident
            qfu = bank.get_question_form_for_update(q_id)
            # qfu = autils.update_question_form(request, self.data(), qfu)
            updated_question = bank.update_question(qfu)

            full_item = bank.get_item(utilities.clean_id(sub_id))
            data = utilities.convert_dl_object(full_item)
            return data
        except (PermissionDenied, Unsupported, InvalidArgument) as ex:
            utilities.handle_exceptions(ex)


class ItemTextAsFormat(utilities.BaseClass):
    """Request item text in specific format

    Returns the item text in a specific format. For example, edxml, QTI, etc.
    api/v2/assessment/banks/<bank_id>/items/<item_id>/<format>/

    GET
    GET to get the question.
    """
    def GET(self, bank_id, item_id, output_format):
        try:
            supported_item_formats = ['edxml']
            if output_format not in supported_item_formats:
                raise InvalidArgument('"{0}" is not a supported item text format.'.format(output_format))

            bank = session._initializer['am'].get_bank(utilities.clean_id(bank_id))
            item = bank.get_item(utilities.clean_id(item_id))
            if 'fileIds' in item.object_map:
                #  need to get the right extension onto the files
                file_labels = item.object_map['fileIds']
                files = item.get_files()
                data = {
                    'files' : {}
                }
                for label, content in file_labels.iteritems():
                    file_type_id = utilities.clean_id(content['assetContentTypeId'])
                    extension = file_type_id.identifier
                    data['files'][label + '.' + extension] = files[label]
            else:
                data = {}
            if output_format == 'edxml':
                if 'files' in data:
                    raw_edxml = item.get_edxml()
                    soup = BeautifulSoup(raw_edxml, 'xml')
                    labels = []
                    label_filename_map = {}
                    for filename in data['files'].keys():
                        label = filename.split('.')[0]
                        labels.append(label)
                        label_filename_map[label] = filename
                    attrs = {
                        'draggable'             : 'icon',
                        'drag_and_drop_input'   : 'img',
                        'files'                 : 'included_files',
                        'img'                   : 'src'
                    }
                    local_regex = re.compile('[^http]')
                    for key, attr in attrs.iteritems():
                        search = {attr : local_regex}
                        tags = soup.find_all(**search)
                        for item in tags:
                            if key == 'files' or item.name == key:
                                if item[attr] in labels:
                                    item[attr] = label_filename_map[item[attr]]
                    data['data'] = soup.find('problem').prettify()
                else:
                    data['data'] = item.get_edxml()

            return data
        except (PermissionDenied, NotFound, LookupError, InvalidArgument) as ex:
            utilities.handle_exceptions(ex)


class ItemAnswers(utilities.BaseClass):
    """
    Edit answers for an existing item
    api/v2/assessment/banks/<bank_id>/items/<item_id>/answers/

    GET, POST
    GET to get current list of answers
    POST to add a new answer

    Note that for RESTful calls, you need to set the request header
    'content-type' to 'application/json'

    Example (note the use of double quotes!!):
       {"responseString" : "2"}
    """
    def GET(self, bank_id, sub_id):
        try:
            bank = session._initializer['am'].get_bank(utilities.clean_id(bank_id))

            item = bank.get_item(utilities.clean_id(sub_id))
            existing_answers = item.get_answers()

            data = utilities.extract_items(existing_answers)
            return data
        except PermissionDenied as ex:
            utilities.handle_exceptions(ex)

    def POST(self, bank_id, sub_id):
        try:
            bank = session._initializer['am'].get_bank(utilities.clean_id(bank_id))

            item = bank.get_item(utilities.clean_id(sub_id))

            # if isinstance(self.data(), list):
            #     for answer in self.data():
            #         a_types = autils.get_answer_records(answer)
            #         afc = bank.get_answer_form_for_create(utilities.clean_id(sub_id),
            #                                               a_types)
            #         afc = autils.update_answer_form(answer, afc)
            #         afc = autils.set_answer_form_genus_and_feedback(answer, afc)
            #         bank.create_answer(afc)
            # elif isinstance(self.data(), dict):
            #     a_types = autils.get_answer_records(self.data())
            #     afc = bank.get_answer_form_for_create(utilities.clean_id(sub_id),
            #                                           a_types)
            #     afc = autils.set_answer_form_genus_and_feedback(self.data(), afc)
            #     # for multi-choice-ortho, need to send the questions
            #     if 'multi-choice' in self.data()['type']:
            #         question = item.get_question()
            #         afc = autils.update_answer_form(self.data(), afc, question)
            #     else:
            #         afc = autils.update_answer_form(self.data(), afc)
            #     bank.create_answer(afc)
            # else:
            #     raise InvalidArgument()

            new_item = bank.get_item(utilities.clean_id(sub_id))
            existing_answers = new_item.get_answers()
            data = utilities.extract_items(existing_answers)
            return data
        except (PermissionDenied, Unsupported, InvalidArgument) as ex:
            utilities.handle_exceptions(ex)


class FinishAssessmentTaken(utilities.BaseClass):
    """
    "finish" the assessment to indicate that student has ended his/her attempt
    api/v2/assessment/banks/<bank_id>/assessmentstaken/<taken_id>/finish/

    POST empty data
    """
    def POST(self, bank_id, taken_id):
        try:
            bank = session._initializer['am'].get_bank(utilities.clean_id(bank_id))
            # "finish" the assessment section
            # bank.finished_assessment_section(first_section.ident)
            bank.finish_assessment(utilities.clean_id(taken_id))
            data = {
                'success': True
            }
            return data
        except (PermissionDenied, IllegalState, NotFound) as ex:
            utilities.handle_exceptions(ex)


class ItemAnswerDetails(utilities.BaseClass):
    """
    Edit answers for an existing item answer
    api/v2/assessment/banks/<bank_id>/items/<item_id>/answers/<answer_id>/

    GET, PUT, DELETE
    GET to get this answer
    PUT to edit this answer
    DELETE to remove this answer

    Note that for RESTful calls, you need to set the request header
    'content-type' to 'application/json'

    Example (note the use of double quotes!!):
       {"responseString" : "2"}
    """
    def DELETE(self, bank_id, sub_id, ans_id):
        try:
            # TODO: check that the answer is part of the sub_id item...
            bank = session._initializer['am'].get_bank(utilities.clean_id(bank_id))
            data = bank.delete_answer(utilities.clean_id(ans_id))
            return data
        except (PermissionDenied, IllegalState) as ex:
            utilities.handle_exceptions(ex)

    def GET(self, bank_id, sub_id, ans_id):
        try:
            bank = session._initializer['am'].get_bank(utilities.clean_id(bank_id))

            item = bank.get_item(utilities.clean_id(sub_id))
            answers = item.get_answers()  # need to get_answers() and filter out

            existing_answer = None
            for answer in answers:
                if answer.ident == utilities.clean_id(ans_id):
                    existing_answer = answer
                    break
            if not existing_answer:
                raise NotFound()

            data = utilities.convert_dl_object(existing_answer)
            return data
        except (PermissionDenied, NotFound) as ex:
            utilities.handle_exceptions(ex)

    def PUT(self, bank_id, sub_id, ans_id):
        try:
            bank = session._initializer['am'].get_bank(utilities.clean_id(bank_id))

            item = bank.get_item(utilities.clean_id(sub_id))
            try:
                answers = list(item.get_answers()) + list(item.get_wrong_answers())
            except AttributeError:
                answers = item.get_answers()

            answer = autils.find_answer_in_answers(utilities.clean_id(ans_id), answers)

            if 'type' not in self.data():
                self.data()['type'] = answer.object_map['recordTypeIds'][0]

            a_id = utilities.clean_id(ans_id)
            afu = bank.get_answer_form_for_update(a_id)
            afu = autils.update_answer_form(self.data(), afu)

            afu = autils.set_answer_form_genus_and_feedback(self.data(), afu)

            updated_answer = bank.update_answer(afu)

            data = utilities.convert_dl_object(updated_answer)
            return data
        except (PermissionDenied, Unsupported, InvalidArgument) as ex:
            utilities.handle_exceptions(ex)


class TakeAssessment(utilities.BaseClass):
    """
    Get the next question available in the taken...DLkit tracks
    state of what is the next available. If files are included
    in the assessment type, they will be returned with
    the question text.
    api/v2/assessment/banks/<bank_id>/assessmentstaken/<taken_id>/take/

    GET only is supported?
    GET to get the next uncompleted question for the given user

    Note that for RESTful calls, you need to set the request header
    'content-type' to 'application/json'
    """
    def GET(self, bank_id, taken_id):
        try:
            bank = session._initializer['am'].get_bank(utilities.clean_id(bank_id))
            first_section = bank.get_first_assessment_section(utilities.clean_id(taken_id))
            question = bank.get_first_unanswered_question(first_section.ident)
            data = utilities.convert_dl_object(question)

            if 'fileIds' in data:
                data.update({
                    'files': question.get_files()
                })

            return data
        except (PermissionDenied, IllegalState, NotFound) as ex:
            utilities.handle_exceptions(ex)


class TakeAssessmentFiles(utilities.BaseClass):
    """
    Lists the files for the next assessment section, if it has
    any.
    api/v2/assessment/banks/<bank_id>/assessmentstaken/<taken_id>/files/

    GET only is supported
    GET to get a list of files for the next unanswered section
    """
    def GET(self, bank_id, taken_id):
        try:
            bank = session._initializer['am'].get_bank(utilities.clean_id(bank_id))
            first_section = bank.get_first_assessment_section(utilities.clean_id(taken_id))
            question = bank.get_first_unanswered_question(first_section.ident)
            if 'question-record-type%3Alabel-ortho-faces%40ODL.MIT.EDU' in question.object_map['recordTypeIds']:
                question_files = question.get_files()
                data = {
                    'manip' : question_files['manip']
                }
                if question.has_ortho_view_set:
                    data['front'] = question_files['frontView']
                    data['side'] = question_files['sideView']
                    data['top'] = question_files['topView']
            else:
                raise LookupError('No files for this question.')
            return data
        except (PermissionDenied, IllegalState, NotFound, LookupError) as ex:
            utilities.handle_exceptions(ex)


class SubmitAssessment(utilities.BaseClass):
    """
    POST the student's response to the active item. DLKit
    tracks which question / item the student is currently
    interacting with.
    api/v2/assessment/banks/<bank_id>/assessmentstaken/<taken_id>/submit/

    POST student response

    Note that for RESTful calls, you need to set the request header
    'content-type' to 'application/json'

    Example (for an Ortho3D manipulatable - label type):
        {"responseSet":{
                "frontFaceEnum" : 0,
                "sideFaceEnum"  : 1,
                "topFaceEnum"   : 2
            }
        }
    """
    def POST(self, bank_id, taken_id):
        try:
            bank = session._initializer['am'].get_bank(utilities.clean_id(bank_id))

            first_section = bank.get_first_assessment_section(utilities.clean_id(taken_id))
            question = bank.get_first_unanswered_question(first_section.ident)
            response_form = bank.get_response_form(assessment_section_id=first_section.ident,
                                                   item_id=question.ident)

            if 'type' not in self.data():
                # kind of a hack
                self.data()['type'] = question.object_map['recordTypeIds'][0]
                self.data()['type'] = self.data()['type'].replace('question-record-type',
                                                              'answer-record-type')

            update_form = autils.update_response_form(self.data(), response_form)
            bank.submit_response(first_section.ident, question.ident, update_form)
            # the above code logs the response in Mongo

            # "finish" the assessment section
            # bank.finished_assessment_section(first_section.ident)
            bank.finish_assessment_section(first_section.ident)

            # Now need to actually check the answers against the
            # item answers.
            answers = bank.get_answers(first_section.ident, question.ident)
            # compare these answers to the submitted response
            correct = autils.validate_response(self.data(), answers)

            data = {
                'correct': correct
            }

            # should send back if there are more questions, so the
            # client knows
            try:
                bank.get_first_unanswered_question(first_section.ident)
                data['hasNext'] = True
            except:
                data['hasNext'] = False

            return data
        except (PermissionDenied, IllegalState, NotFound) as ex:
            utilities.handle_exceptions(ex)


class AssessmentTakenQuestions(utilities.BaseClass):
    """
    Returns all of the questions for a given assessment taken.
    Assumes that only one section per assessment.
    api/v2/assessment/banks/<bank_id>/assessmentstaken/<taken_id>/questions/

    GET only
    """

    def GET(self, bank_id, taken_id):
        try:
            bank = session._initializer['am'].get_bank(utilities.clean_id(bank_id))
            first_section = bank.get_first_assessment_section(utilities.clean_id(taken_id))
            questions = bank.get_questions(first_section.ident)
            data = utilities.extract_items(questions)

            if 'files' in self.data():
                for question in data['data']['results']:
                    if 'fileIds' in question:
                        question['files'] = bank.get_question(first_section.ident,
                                                              utilities.clean_id(question['id'])).get_files()

            return data
        except (PermissionDenied, IllegalState, NotFound) as ex:
            utilities.handle_exceptions(ex)


class AssessmentTakenQuestionDetails(utilities.BaseClass):
    """
    Returns the specified question
    api/v2/assessment/banks/<bank_id>/assessmentstaken/<taken_id>/questions/<question_id>/

    GET only
    """

    def GET(self, bank_id, taken_id, question_id):
        try:
            bank = session._initializer['am'].get_bank(utilities.clean_id(bank_id))
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
        except (PermissionDenied, IllegalState, NotFound) as ex:
            utilities.handle_exceptions(ex)


class AssessmentTakenQuestionFiles(utilities.BaseClass):
    """
    Returns the files for the specified question
    api/v2/assessment/banks/<bank_id>/assessmentstaken/<taken_id>/questions/<question_id>/files/

    GET only
    """
    def GET(self, bank_id, taken_id, question_id):
        try:
            bank = session._initializer['am'].get_bank(utilities.clean_id(bank_id))
            first_section = bank.get_first_assessment_section(utilities.clean_id(taken_id))
            question = bank.get_question(first_section.ident,
                                         utilities.clean_id(question_id))
            try:
                question_files = question.get_files()
                data = {
                    'manip': question_files['manip'],
                    'front': question_files['frontView'],
                    'side': question_files['sideView'],
                    'top': question_files['topView']
                }
            except:
                data = {'details': 'No files for this question.'}

            return data
        except (PermissionDenied, IllegalState, NotFound) as ex:
            utilities.handle_exceptions(ex)


class AssessmentTakenQuestionResponses(utilities.BaseClass):
    """
    Gets the student responses to a question
    api/v2/assessment/banks/<bank_id>/assessmentstaken/<taken_id>/questions/<question_id>/responses/

    GET only

    Example (for an Ortho3D manipulatable - label type):
        [{"integerValues": {
            "frontFaceValue" : 0,
            "sideFaceValue"  : 1,
            "topFaceValue"   : 2
        },{
            "frontFaceValue" : 3,
            "sideFaceValue"  : 1,
            "topFaceValue"   : 2
        }]
    """

    def GET(self, bank_id, taken_id, question_id):
        try:
            bank = session._initializer['am'].get_bank(utilities.clean_id(bank_id))
            first_section = bank.get_first_assessment_section(utilities.clean_id(taken_id))
            response = bank.get_response(first_section.ident, utilities.clean_id(question_id))
            data = response.object_map

            # if 'files' in params:
            if 'fileIds' in data:
                data['files'] = response.get_files()  # return files by default, until we have a list

            return data
        except (PermissionDenied, NotFound) as ex:
            utilities.handle_exceptions(ex)


class AssessmentTakenQuestionSolution(utilities.BaseClass):
    """
    Returns the solution / explanation when available
    api/v2/assessment/banks/<bank_id>/assessmentstaken/<taken_id>/questions/<question_id>/solution/

    GET only

    Example (for an Ortho3D manipulatable - label type):
        {}
    """

    def GET(self, bank_id, taken_id, question_id):
        try:
            bank = session._initializer['am'].get_bank(utilities.clean_id(bank_id))
            taken = bank.get_assessment_taken(utilities.clean_id(taken_id))
            try:
                solution = taken.get_solution_for_question(utilities.clean_id(question_id))
            except IllegalState:
                solution = 'No solution available.'

            return solution
        except (PermissionDenied, IllegalState, NotFound, InvalidArgument) as ex:
            utilities.handle_exceptions(ex)


class AssessmentTakenQuestionStatus(utilities.BaseClass):
    """
    Gets the current status of a question in a taken -- responded to or not, correct or incorrect
    response (if applicable)
    api/v2/assessment/banks/<bank_id>/assessmentstaken/<taken_id>/questions/<question_id>/status/

    GET only

    Example (for an Ortho3D manipulatable - label type):
        {"responded": True,
         "correct"  : False
        }
    """
    def GET(self, bank_id, taken_id, question_id):
        try:
            bank = session._initializer['am'].get_bank(utilities.clean_id(bank_id))
            first_section = bank.get_first_assessment_section(utilities.clean_id(taken_id))
            question = bank.get_question(first_section.ident,
                                         utilities.clean_id(question_id))

            data = autils.get_question_status(bank, first_section,
                                              utilities.clean_id(question_id))

            return data
        except (PermissionDenied, NotFound) as ex:
            utilities.handle_exceptions(ex)


class AssessmentTakenQuestionSubmit(utilities.BaseClass):
    """
    Submits a student response for the specified question
    Returns correct or not
    Does NOTHING to flag if the section is done or not...
    api/v2/assessment/banks/<bank_id>/assessmentstaken/<taken_id>/questions/<question_id>/submit/

    POST only

    Example (for an Ortho3D manipulatable - label type):
        {"integerValues":{
                "frontFaceValue" : 0,
                "sideFaceValue"  : 1,
                "topFaceValue"   : 2
            }
        }
    """
    def POST(self, bank_id, taken_id, question_id):
        try:
            bank = session._initializer['am'].get_bank(utilities.clean_id(bank_id))
            first_section = bank.get_first_assessment_section(utilities.clean_id(taken_id))
            question = bank.get_question(first_section.ident,
                                         utilities.clean_id(question_id))
            response_form = bank.get_response_form(assessment_section_id=first_section.ident,
                                                   item_id=question.ident)

            if 'type' not in self.data():
                # kind of a hack
                self.data()['type'] = question.object_map['recordTypeIds'][0]
                self.data()['type'] = self.data()['type'].replace('question-record-type',
                                                              'answer-record-type')

            update_form = autils.update_response_form(self.data(), response_form)
            bank.submit_response(first_section.ident, question.ident, update_form)
            # the above code logs the response in Mongo

            # Now need to actually check the answers against the
            # item answers.
            answers = bank.get_answers(first_section.ident, question.ident)
            # compare these answers to the submitted response

            correct = autils.validate_response(self.data(), answers)

            feedback = 'No feedback available.'

            return_data = {
                'correct': correct,
                'feedback': feedback
            }
            if correct:
                # update with item solution, if available
                try:
                    taken = bank.get_assessment_taken(utilities.clean_id(taken_id))
                    feedback = taken.get_solution_for_question(
                        utilities.clean_id(question_id))['explanation']
                    return_data.update({
                        'feedback': feedback
                    })
                except (IllegalState, TypeError, AttributeError):
                    pass
            else:
                # update with answer feedback, if available
                # for now, just support this for multiple choice questions...
                if autils.is_multiple_choice(self.data()):
                    submissions = autils.get_response_submissions(self.data())
                    answers = bank.get_answers(first_section.ident, question.ident)
                    wrong_answers = [a for a in answers
                                     if a.genus_type == Type(**ANSWER_GENUS_TYPES['wrong-answer'])]
                    feedback_strings = []
                    confused_los = []
                    for wrong_answer in wrong_answers:
                        if wrong_answer.get_choice_ids()[0] in submissions:
                            try:
                                feedback_strings.append(wrong_answer.feedback)
                            except KeyError:
                                pass
                            try:
                                confused_los += wrong_answer.confused_learning_objective_ids
                            except KeyError:
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
        except (PermissionDenied, IllegalState, NotFound, InvalidArgument) as ex:
            utilities.handle_exceptions(ex)


class AssessmentTakenQuestionSurrender(utilities.BaseClass):
    """
    Returns the answer if a student gives up and wants to just see the answer
    api/v2/assessment/banks/<bank_id>/assessmentstaken/<taken_id>/questions/<question_id>/surrender/

    POST only, no data

    Example (for an Ortho3D manipulatable - label type):
        {}
    """
    def POST(self, bank_id, taken_id, question_id):
        try:
            bank = session._initializer['am'].get_bank(utilities.clean_id(bank_id))
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
        except (PermissionDenied, IllegalState, NotFound) as ex:
            utilities.handle_exceptions(ex)

app_assessment = web.application(urls, locals())
session = utilities.activate_managers(web.session.Session(app_assessment,
                                      web.session.DiskStore('sessions'),
                                      initializer={
                                          'am': None,
                                          'logm': None
                                      }))
