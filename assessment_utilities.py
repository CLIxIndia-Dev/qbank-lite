import json
import os
import re
import web

from bs4 import BeautifulSoup

from dlkit_edx import PROXY_SESSION, RUNTIME
from dlkit_edx.errors import InvalidArgument, Unsupported, NotFound, NullArgument,\
    IllegalState
from dlkit_edx.primordium import Duration, DateTime, Id, Type,\
    DataInputStream
from dlkit_edx.proxy_example import TestRequest

from inflection import underscore

from records.registry import ASSESSMENT_OFFERED_RECORD_TYPES,\
    ANSWER_GENUS_TYPES, ANSWER_RECORD_TYPES, ASSET_GENUS_TYPES,\
    ITEM_RECORD_TYPES, ITEM_GENUS_TYPES, ASSET_CONTENT_GENUS_TYPES

from urllib import quote

import repository_utilities as rutils
import utilities

ANSWER_WITH_FEEDBACK = Type(**ANSWER_RECORD_TYPES['answer-with-feedback'])
EDX_FILE_ASSET_GENUS_TYPE = Type(**ASSET_GENUS_TYPES['edx-file-asset'])
EDX_IMAGE_ASSET_GENUS_TYPE = Type(**ASSET_GENUS_TYPES['edx-image-asset'])
EDX_ITEM_RECORD_TYPE = Type(**ITEM_RECORD_TYPES['edx_item'])
EDX_MULTI_CHOICE_PROBLEM_TYPE = Type(**ITEM_GENUS_TYPES['multi-choice-edx'])
EDX_NUMERIC_RESPONSE_PROBLEM_GENUS_TYPE = Type(**ITEM_GENUS_TYPES['numeric-response-edx'])
GENERIC_ASSET_CONTENT_GENUS_TYPE = Type(**ASSET_CONTENT_GENUS_TYPES['generic'])
ITEM_WITH_WRONG_ANSWERS_RECORD_TYPE = Type(**ITEM_RECORD_TYPES['wrong-answer'])
JAVASCRIPT_ASSET_CONTENT_GENUS_TYPE = Type(**ASSET_CONTENT_GENUS_TYPES['javascript'])
JPG_ASSET_CONTENT_GENUS_TYPE = Type(**ASSET_CONTENT_GENUS_TYPES['jpg'])
JSON_ASSET_CONTENT_GENUS_TYPE = Type(**ASSET_CONTENT_GENUS_TYPES['json'])
LATEX_ASSET_CONTENT_GENUS_TYPE = Type(**ASSET_CONTENT_GENUS_TYPES['latex'])
PNG_ASSET_CONTENT_GENUS_TYPE = Type(**ASSET_CONTENT_GENUS_TYPES['png'])
REVIEWABLE_OFFERED = Type(**ASSESSMENT_OFFERED_RECORD_TYPES['review-options'])
N_OF_M_OFFERED = Type(**ASSESSMENT_OFFERED_RECORD_TYPES['n-of-m'])
WRONG_ANSWER = Type(**ANSWER_GENUS_TYPES['wrong-answer'])
RIGHT_ANSWER = Type(**ANSWER_GENUS_TYPES['right-answer'])


def add_file_ids_to_form(form, file_ids):
    """
    Add existing asset_ids to a form
    :param form:
    :param image_ids:
    :return:
    """
    for label, file_id in file_ids.iteritems():
        form.add_asset(Id(file_id['assetId']), label, Id(file_id['assetContentTypeId']))
    return form

def add_files_to_form(form, files):
    """
    Whether an item form or a question form
    :param form:
    :return:
    """
    def _clean(label):
        return re.sub(r'[^\w\d]', '_', label)

    def _get_file_label(file_path):
        # http://stackoverflow.com/questions/678236/how-to-get-the-filename-without-the-extension-from-a-path-in-python
        return os.path.splitext(os.path.basename(file_path))[0]

    def _get_file_extension(file_name):
        return os.path.splitext(os.path.basename(file_name))[-1]

    def _infer_display_name(text):
        text = text.strip()
        if text == '':
            return 'Unknown Display Name'
        if '_' not in text:
            return text

        if text.split('_')[0].startswith('lec'):
            first_part = text.split('_')[0]
            text = 'Lecture ' + first_part.split('lec')[-1] + '_' + text.split('_')[-1]
        elif text.split('_')[0].startswith('ps'):
            first_part = text.split('_')[0]
            text = 'Problem Set ' + first_part.split('ps')[-1] + '_' + text.split('_')[-1]
        elif text.split('_')[0].startswith('ex'):
            first_part = text.split('_')[0]
            text = 'Exam ' + first_part.split('ex')[-1] + '_' + text.split('_')[-1]

        if text.split('_')[-1].startswith('p'):
            second_part = text.split('_')[-1]
            text = text.split('_')[0] + ': Problem ' + second_part.split('p')[-1]
        elif text.split('_')[-1].startswith('Q'):
            second_part = text.split('_')[-1]
            text = text.split('_')[0] + ': Question ' + second_part.split('Q')[-1]
        return text

    for file_name, file_data in files.iteritems():
        # default assume is a file
        prettify_type = 'file'
        genus = EDX_FILE_ASSET_GENUS_TYPE
        file_type = _get_file_extension(file_name).lower()
        label = _get_file_label(file_name)
        if file_type:
            if 'png' in file_type:
                ac_genus_type = PNG_ASSET_CONTENT_GENUS_TYPE
                genus = EDX_IMAGE_ASSET_GENUS_TYPE
                prettify_type = 'image'
            elif 'jpg' in file_type:
                ac_genus_type = JPG_ASSET_CONTENT_GENUS_TYPE
                genus = EDX_IMAGE_ASSET_GENUS_TYPE
                prettify_type = 'image'
            elif 'json' in file_type:
                ac_genus_type = JSON_ASSET_CONTENT_GENUS_TYPE
            elif 'tex' in file_type:
                ac_genus_type = LATEX_ASSET_CONTENT_GENUS_TYPE
            elif 'javascript' in file_type:
                ac_genus_type = JAVASCRIPT_ASSET_CONTENT_GENUS_TYPE
            else:
                ac_genus_type = GENERIC_ASSET_CONTENT_GENUS_TYPE
        else:
            ac_genus_type = GENERIC_ASSET_CONTENT_GENUS_TYPE

        display_name = _infer_display_name(label) + ' ' + prettify_type.title()
        description = ('Supporting ' + prettify_type + ' for assessment Question: ' +
                       _infer_display_name(label))
        form.add_file(file_data, _clean(label), genus, ac_genus_type, display_name, description)
    return form

def archive_bank_names(original_id):
    return 'Archive for {0}'.format(str(original_id))

def archive_bank_genus():
    return Type('bank-genus-type%3Aclix-archive%40ODL.MIT.EDU')

def archive_item(original_bank, item):
    """archive this item to a clone of the original bank
    Create the archive bank if it does not exist"""

    # NOTE: instead of using two query params, the expected_name
    #       AND the expected_genus, we need to resort to using
    #       only the genus and match on the name ourselves
    #       There seems to be mismatching regex behavior between
    #       the deployment Ubuntu and Mac, where Mac will find
    #       the archive files using both params, but Ubuntu will not...
    am = get_assessment_manager()

    querier = am.get_bank_query()

    expected_name = archive_bank_names(original_bank.ident)
    expected_genus = archive_bank_genus()

    # querier.match_display_name(expected_name, match=True)
    querier.match_genus_type(expected_genus, match=True)

    banks = am.get_banks_by_query(querier)
    if banks.available() == 0:
        # create the bank
        form = am.get_bank_form_for_create([])
        form.set_genus_type(expected_genus)
        form.display_name = expected_name
        form.description = 'For Archiving Items'
        archive = am.create_bank(form)
    else:
        archive = None
        for bank in banks:
            if bank.display_name.text == expected_name:
                archive = bank
                break
        if archive is None:
            # create the bank
            form = am.get_bank_form_for_create([])
            form.set_genus_type(expected_genus)
            form.display_name = expected_name
            form.description = 'For Archiving Items'
            archive = am.create_bank(form)
        
    am.assign_item_to_bank(item.ident, archive.ident)
    am.unassign_item_from_bank(item.ident, original_bank.ident)

def check_assessment_has_items(bank, assessment_id):
    """
    Before creating an assessment offered, check that the assessment
    has items in it.
    :param assessment_id:
    :return:
    """
    items = bank.get_assessment_items(assessment_id)
    if not items.available():
        raise LookupError('No items')

def create_new_item(bank, data):
    if ('question' in data and
            'type' in data['question'] and
            'edx' in data['question']['type']):
        # should have body / setup
        # should have list of choices
        # should have set of right answers
        # metadata (if not present, it is okay):
        #  * max attempts
        #  * weight
        #  * showanswer
        #  * rerandomize
        #  * author username
        #  * student display name
        #  * author comments
        #  * extra python script
        # any files?
        form = bank.get_item_form_for_create([EDX_ITEM_RECORD_TYPE,
                                              ITEM_WITH_WRONG_ANSWERS_RECORD_TYPE])
        form.display_name = data['name']
        form.description = data['description']
        question_type = data['question']['type']
        if 'multi-choice' in question_type:
            form.set_genus_type(EDX_MULTI_CHOICE_PROBLEM_TYPE)
        elif 'numeric-response' in question_type:
            form.set_genus_type(EDX_NUMERIC_RESPONSE_PROBLEM_GENUS_TYPE)

        if 'learningObjectiveIds' in data:
            form = set_item_learning_objectives(data, form)

        expected = ['question']
        utilities.verify_keys_present(data, expected)

        expected = ['questionString']
        utilities.verify_keys_present(data['question'], expected)

        form.add_text(data['question']['questionString'], 'questionString')

        optional = ['python_script','latex','edxml','solution']
        for opt in optional:
            if opt in data:
                form.add_text(data[opt], opt)

        metadata = ['attempts','markdown','showanswer','weight']
        # metadata = ['attempts','markdown','rerandomize','showanswer','weight']
                    # 'author','author_comments','student_display_name']
        for datum in metadata:
            if datum in data:
                method = getattr(form, 'add_' + datum)
                method(data[datum])

        irt = ['difficulty','discrimination']
        for datum in irt:
            if datum in data:
                method = getattr(form, 'set_' + datum + '_value')
                method(data[datum])

        if 'files' in data:
            files_list = {}
            for filename, file in data['files'].iteritems():
                files_list[filename] = DataInputStream(file)
            form = add_files_to_form(form, files_list)
    else:
        form = bank.get_item_form_for_create([ITEM_WITH_WRONG_ANSWERS_RECORD_TYPE])
        form.display_name = str(data['name'])
        form.description = str(data['description'])
        if 'genus' in data:
            form.set_genus_type(Type(data['genus']))

        if 'learningObjectiveIds' in data:
            form = set_item_learning_objectives(data, form)

    new_item = bank.create_item(form)
    return new_item

def evaluate_inline_choice(answers, submission):
    correct = False
    right_answers = [a for a in answers
                     if is_right_answer(a)]

    for answer in right_answers:
        answer_choices = answer.get_inline_choice_ids()
        num_total = 0
        num_right = 0
        for inline_region, data in answer_choices.iteritems():
            num_total += data['choiceIds'].available()
        if len(submission.keys()) == len(answer_choices.keys()):
            # assume order doesn't matter within the region -- though
            # per QTI spec, I think it's only 1 choice per inline region
            for inline_region, data in answer_choices.iteritems():
                if ('choiceIds' in submission[inline_region] and
                        len(submission[inline_region]['choiceIds']) == data['choiceIds'].available()):
                    for choice_id in data['choiceIds']:
                        if str(choice_id) in submission[inline_region]['choiceIds']:
                            num_right += 1
        if num_right == num_total:
            correct = True
    return correct

def find_answer_in_answers(ans_id, ans_list):
    for ans in ans_list:
        if ans.ident == ans_id:
            return ans
    return None

def get_answer_records(answer):
    """answer is a dictionary"""
    # check for wrong-answer genus type to get the right
    # record types for feedback
    a_type = Type(answer['type'])
    if 'genus' in answer and answer['genus'] == str(Type(**ANSWER_GENUS_TYPES['wrong-answer'])):
        a_types = [a_type, ANSWER_WITH_FEEDBACK]
    else:
        a_types = [a_type]
    return a_types

def get_assessment_manager():
    condition = PROXY_SESSION.get_proxy_condition()
    dummy_request = TestRequest(username=web.ctx.env.get('HTTP_X_API_PROXY', 'student@tiss.edu'),
                                authenticated=True)
    condition.set_http_request(dummy_request)
    proxy = PROXY_SESSION.get_proxy(condition)
    return RUNTIME.get_service_manager('ASSESSMENT',
                                       proxy=proxy)

def get_choice_files(files):
    """
    Adapted from http://stackoverflow.com/questions/4558983/slicing-a-dictionary-by-keys-that-start-with-a-certain-string
    :param files:
    :return:
    """
    # return {k:v for k,v in files.iteritems() if k.startswith('choice')}
    return dict((k, files[k]) for k in files.keys() if k.startswith('choice'))

def get_media_path(bank):
    host_path = web.ctx.get('homedomain', '')
    rm = rutils.get_repository_manager()
    repo = rm.get_repository(bank.ident)
    return '{0}/api/v1/repository/repositories/{1}/assets'.format(host_path,
                                                                  str(repo.ident))

def get_object_bank(manager, object_id, object_type='item', bank_id=None):
    """Get the object's bank even without the bankId"""
    # primarily used for Item and AssessmentsOffered
    if bank_id is None:
        lookup_session = getattr(manager, 'get_{0}_lookup_session'.format(object_type))()
        lookup_session.use_federated_bank_view()
        object_ = getattr(lookup_session, 'get_{0}'.format(object_type))(utilities.clean_id(object_id))
        bank_id = object_.object_map['assignedBankIds'][0]
    return manager.get_bank(utilities.clean_id(bank_id))

def get_ovs_file_set(files, index):
    choice_files = get_choice_files(files)
    if len(choice_files.keys()) % 2 != 0:
        raise NullArgument('Large and small image files')
    small_file = choice_files['choice' + str(index) + 'small']
    big_file = choice_files['choice' + str(index) + 'big']
    return (small_file, big_file)


def get_question_status(bank, section, question_id):
    """
    Return the question status of answered or not, and if so, right or wrong
    :param bank:
    :param section:
    :param question:
    :return:
    """
    try:
        student_response = bank.get_response(section.ident, question_id)
        student_response.object_map
    except (NotFound, IllegalState):
        student_response = None

    if student_response:
        # Now need to actually check the answers against the
        # item answers.
        answers = bank.get_answers(section.ident, question_id)
        # compare these answers to the submitted response
        response = student_response._my_map
        response.update({
            'type' : str(response['recordTypeIds'][0]).replace('answer-record-type', 'answer-record-type')
        })
        correct = validate_response(student_response._my_map, answers)
        data = {
            'responded' : True,
            'correct'   : correct
        }
    else:
        data = {
            'responded' : False
        }
    return data

def get_response_submissions(response):
    if response['type'] == 'answer-record-type%3Alabel-ortho-faces%40ODL.MIT.EDU':
        submission = response['integerValues']
    elif is_multiple_choice(response) or is_ordered_choice(response):
        if isinstance(response, dict):
            if isinstance(response['choiceIds'], list):
                submission = response['choiceIds']
            else:
                submission = [response['choiceIds']]
        else:
            submission = response.getlist('choiceIds')
    elif response['type'] == 'answer-record-type%3Anumeric-response-edx%40ODL.MIT.EDU':
        submission = float(response['decimalValue'])
    elif is_inline_choice(response):
        submission = response['inlineRegions']
    elif is_numeric_response(response):
        # just take the first region for now
        submission = response[response.keys()[0]]
    else:
        raise Unsupported
    return submission

def is_file_submission(response):
    if isinstance(response['type'], list):
        return any(mc in r
                   for r in response['type']
                   for mc in ['files-submission',
                              'qti-upload-interaction-audio',
                              'qti-upload-interaction-generic',
                              'qti-order-interaction-mw-sandbox'])
    else:
        return any(mc in response['type'] for mc in ['files-submission',
                                                     'qti-upload-interaction-audio',
                                                     'qti-upload-interaction-generic',
                                                     'qti-order-interaction-mw-sandbox'])

def is_inline_choice(response):
    if isinstance(response['type'], list):
        return any(mc in r
                   for r in response['type']
                   for mc in ['qti-inline-choice-interaction-mw-fill-in-the-blank'])
    else:
        return any(mc in response['type'] for mc in ['qti-inline-choice-interaction-mw-fill-in-the-blank'])

def is_multiple_choice(response):
    if isinstance(response['type'], list):
        return any(mc in r
                   for r in response['type']
                   for mc in ['multi-choice-ortho',
                              'multi-choice-edx',
                              'multi-choice-with-files-and-feedback',
                              'qti-choice-interaction',
                              'qti-choice-interaction-multi-select',
                              'qti-choice-interaction-survey',
                              'qti-choice-interaction-multi-select-survey'])
    else:
        return any(mc in response['type'] for mc in ['multi-choice-ortho',
                                                     'multi-choice-edx',
                                                     'multi-choice-with-files-and-feedback',
                                                     'qti-choice-interaction',
                                                     'qti-choice-interaction-multi-select',
                                                     'qti-choice-interaction-survey',
                                                     'qti-choice-interaction-multi-select-survey'])

def is_mw_sandbox(response):
    if isinstance(response['type'], list):
        return any(mc in r
                   for r in response['type']
                   for mc in ['qti-order-interaction-mw-sandbox'])
    else:
        return any(mc in response['type'] for mc in ['qti-order-interaction-mw-sandbox'])

def is_numeric_response(response):
    if isinstance(response['type'], list):
        return any(mc in r
                   for r in response['type']
                   for mc in ['qti-numeric-response'])
    else:
        return any(mc in response['type'] for mc in ['qti-numeric-response'])

def is_ordered_choice(response):
    if isinstance(response['type'], list):
        return any(mc in r
                   for r in response['type']
                   for mc in ['qti-order-interaction-mw-sentence',
                              'qti-order-interaction-object-manipulation'])
    else:
        return any(mc in response['type'] for mc in ['qti-order-interaction-mw-sentence',
                                                     'qti-order-interaction-object-manipulation'])

def is_short_answer(response):
    if isinstance(response['type'], list):
        return any(mc in r
                   for r in response['type']
                   for mc in ['qti-extended-text-interaction'])
    else:
        return any(mc in response['type'] for mc in ['qti-extended-text-interaction'])

def is_survey(response):
    if isinstance(response['type'], list):
        return any(mc in r
                   for r in response['type']
                   for mc in ['qti-choice-interaction-survey',
                              'qti-choice-interaction-multi-select-survey'])
    else:
        return any(mc in response['type'] for mc in ['qti-choice-interaction-survey',
                                                     'qti-choice-interaction-multi-select-survey'])

def is_right_answer(answer):
    return (answer.genus_type == Type(**ANSWER_GENUS_TYPES['right-answer']) or
            str(answer.genus_type).lower() == 'genustype%3adefault%40dlkit.mit.edu')

def match_submission_to_answer(answers, response):
    submission = get_response_submissions(response)
    answer_match = None
    default_answer = None
    match = False

    if is_inline_choice(response):
        # try to find an exact match response according to the regions + choiceIds
        # if no exact match found, just look for a "wrong answer" answer with no inlineRegions
        for answer in answers:
            answer_regions = answer.get_inline_choice_ids()
            if answer_regions == {} and str(answer.genus_type) == str(WRONG_ANSWER):
                default_answer = answer
            num_total = 0
            num_right = 0
            for inline_region, data in answer_regions.iteritems():
                num_total += data['choiceIds'].available()
            if len(answer_regions.keys()) == len(submission.keys()):
                for inline_region, data in answer_regions.iteritems():
                    if data['choiceIds'].available() == len(submission[inline_region]['choiceIds']):
                        for choice_id in data['choiceIds']:
                            if str(choice_id) in submission[inline_region]['choiceIds']:
                                num_right += 1
            if num_total == num_right:
                match = True
                answer_match = answer
                break
    if not match:
        return default_answer
    else:
        return answer_match

def set_answer_form_genus_and_feedback(answer, answer_form):
    """answer is a dictionary"""
    if 'genus' in answer:
        answer_form.genus_type = Type(answer['genus'])

    if 'feedback' in answer:
        if str(ANSWER_WITH_FEEDBACK) not in answer_form._my_map['recordTypeIds']:
            record = answer_form.get_answer_form_record(ANSWER_WITH_FEEDBACK)
            record._init_metadata()
            record._init_map()
        if 'modalFeedback' in answer['feedback']:
            feedback_xml = BeautifulSoup(answer['feedback'], 'xml')
            answer_form.set_feedback(str(feedback_xml.modalFeedback))
        else:
            answer_form.set_feedback(u'{0}'.format(answer['feedback']).encode('utf8'))
    if 'confusedLearningObjectiveIds' in answer:
        if not isinstance(answer['confusedLearningObjectiveIds'], list):
            los = [answer['confusedLearningObjectiveIds']]
        else:
            los = answer['confusedLearningObjectiveIds']
        answer_form.set_confused_learning_objective_ids(los)
    return answer_form

def set_assessment_offerings(bank, offerings, assessment_id, update=False):
    return_data = []
    for offering in offerings:
        if isinstance(offering, basestring):
            offering = json.loads(offering)

        if update:
            offering_form = bank.get_assessment_offered_form_for_update(assessment_id)
            execute = bank.update_assessment_offered
        else:
            # use our new Offered Record object, which lets us do
            # "can_review_whether_correct()" on the Taken.
            offering_form = bank.get_assessment_offered_form_for_create(assessment_id,
                                                                        [REVIEWABLE_OFFERED,
                                                                         N_OF_M_OFFERED])
            execute = bank.create_assessment_offered

        if 'duration' in offering:
            if isinstance(offering['duration'], basestring):
                duration = json.loads(offering['duration'])
            else:
                duration = offering['duration']
            offering_form.duration = Duration(**duration)
        if 'gradeSystem' in offering:
            offering_form.grade_system = Id(offering['gradeSystem'])
        if 'level' in offering:
            offering_form.level = Id(offering['level'])
        if 'startTime' in offering:
            if isinstance(offering['startTime'], basestring):
                start_time = json.loads(offering['startTime'])
            else:
                start_time = offering['startTime']
            offering_form.start_time = DateTime(**start_time)
        if 'scoreSystem' in offering:
            offering_form.score_system = Id(offering['scoreSystem'])

        if 'reviewOptions' in offering and 'whetherCorrect' in offering['reviewOptions']:
            for timing, value in offering['reviewOptions']['whetherCorrect'].iteritems():
                offering_form.set_review_whether_correct(**{underscore(timing) : value})

        if 'reviewOptions' in offering and 'solution' in offering['reviewOptions']:
            for timing, value in offering['reviewOptions']['solution'].iteritems():
                offering_form.set_review_solution(**{underscore(timing) : value})

        if 'maxAttempts' in offering:
            offering_form.set_max_attempts(offering['maxAttempts'])

        if 'nOfM' in offering:
            offering_form.set_n_of_m(int(offering['nOfM']))

        new_offering = execute(offering_form)
        return_data.append(new_offering)
    return return_data

def set_item_learning_objectives(data, form):
    # over-writes current ID list
    id_list = []
    if not isinstance(data['learningObjectiveIds'], list):
        data['learningObjectiveIds'] = [data['learningObjectiveIds']]
    for _id in data['learningObjectiveIds']:
        if '@' in _id:
            id_list.append(Id(quote(_id)))
        else:
            id_list.append(Id(_id))
    form.set_learning_objectives(id_list)
    return form

def update_answer_form(answer, form, question=None):
    if answer['type'] == 'answer-record-type%3Ashort-text-answer%40ODL.MIT.EDU':
        if 'responseString' in answer:
            form.set_text(answer['responseString'])
    elif answer['type'] == 'answer-record-type%3Alabel-ortho-faces%40ODL.MIT.EDU':
        if 'integerValues' in answer:
            form.set_face_values(front_face_value=answer['integerValues']['frontFaceValue'],
                                 side_face_value=answer['integerValues']['sideFaceValue'],
                                 top_face_value=answer['integerValues']['topFaceValue'])
    elif answer['type'] == 'answer-record-type%3Aeuler-rotation%40ODL.MIT.EDU':
        if 'integerValues' in answer:
            form.set_euler_angle_values(x_angle=answer['integerValues']['xAngle'],
                                        y_angle=answer['integerValues']['yAngle'],
                                        z_angle=answer['integerValues']['zAngle'])
    elif (answer['type'] == 'answer-record-type%3Amulti-choice-ortho%40ODL.MIT.EDU' or
          answer['type'] == 'answer-record-type%3Amulti-choice-edx%40ODL.MIT.EDU'):
        if question is None and 'choiceId' in answer:
            raise InvalidArgument('Missing question parameter for multi-choice')
        if not form.is_for_update():
            utilities.verify_keys_present(answer, ['choiceId'])
        if 'choiceId' in answer:
            # need to find the actual choiceIds (MC3 IDs), and match the index
            # to the one(s) passed in as part of the answer
            choices = question.get_choices()
            if int(answer['choiceId']) > len(choices):
                raise KeyError('Correct answer ' + str(answer['choiceId']) + ' is not valid. '
                               'Not that many choices!')
            elif int(answer['choiceId']) < 1:
                raise KeyError('Correct answer ' + str(answer['choiceId']) + ' is not valid. '
                               'Must be between 1 and # of choices.')

            # choices are 0 indexed
            choice_id = choices[int(answer['choiceId']) - 1]  # not sure if we need the OSID Id or string
            form.add_choice_id(choice_id['id'])  # just include the MongoDB ObjectId, not the whole dict

    elif answer['type'] == 'answer-record-type%3Afiles-submission%40ODL.MIT.EDU':
        # no correct answers here...
        return form
    elif answer['type'] == 'answer-record-type%3Anumeric-response-edx%40ODL.MIT.EDU':
        if 'decimalValue' in answer:
            form.set_decimal_value(float(answer['decimalValue']))
        if 'tolerance' in answer:
            form.set_tolerance_value(float(answer['tolerance']))
    elif 'qti' in answer['type']:
        pass
    else:
        raise Unsupported()

    return form

def update_item_metadata(data, form):
    """Update the metadata / IRT for an edX item

    :param request:
    :param data:
    :param form:
    :return:
    """
    if ('type' in data and
        'edx' in data['type']):
        valid_fields = ['attempts','markdown','showanswer','weight',
                        'difficulty','discrimination']
        for field in valid_fields:
            if field in data:
                if hasattr(form, 'add_' + field):
                    update_method = getattr(form, 'add_' + field)
                elif hasattr(form, 'set_' + field):
                    update_method = getattr(form, 'set_' + field)
                else:
                    update_method = getattr(form, 'set_' + field + '_value')
                # These forms are very strict (Java), so
                # have to know the exact input type. We
                # can't predict, so try a couple variations
                # if this fails...yes we're silly.
                val = data[field]
                try:
                    try:
                        try:
                            update_method(str(val))
                        except:
                            update_method(int(val))
                    except:
                        update_method(float(val))
                except:
                    raise LookupError
    else:
        # do nothing here for other types of problems
        pass

    return form

def update_question_form(question, form, create=False):
    """
    Check the create flag--if creating the question, then all 3 viewset files
    are needed. If not creating, can update only a single file.
    """
    if question['type'] == 'question-record-type%3Ashort-text-answer%40ODL.MIT.EDU':
        form.set_text(question['questionString'])
    elif (question['type'] == 'question-record-type%3Alabel-ortho-faces%40ODL.MIT.EDU' or
          question['type'] == 'question-record-type%3Aeuler-rotation%40ODL.MIT.EDU'):
        # need to differentiate on create here because update might not use all
        # the fields, whereas we need to enforce a minimum of data on create
        if create:
            if 'questionString' in question:
                form.set_text(question['questionString'])
            else:
                raise NullArgument('questionString')

            if 'firstAngle' in question:
                form.set_first_angle_projection(question['firstAngle'])

            # files = request.FILES
            files = {}
            # if 'manip' in files:
            #     form.set_manip(DataInputStream(files['manip']))
            # else:
            #     raise NullArgument('manip file')
            # if not ('frontView' in files and 'sideView' in files and 'topView' in files):
            #     raise NullArgument('All three view set attribute(s) required for Ortho-3D items.')
            # else:
            #     form.set_ortho_view_set(front_view=DataInputStream(files['frontView']),
            #                             side_view=DataInputStream(files['sideView']),
            #                             top_view=DataInputStream(files['topView']))
        else:
            if 'questionString' in question:
                form.set_text(question['questionString'])
            if 'firstAngle' in question:
                form.set_first_angle_projection(question['firstAngle'])
            # files = request.FILES
            # files = {}
            # if 'manip' in files:
            #     form.set_manip(DataInputStream(files['manip']))
            # if 'frontView' in files:
            #     form.set_ovs_view(DataInputStream(files['frontView']), 'frontView')
            # if 'sideView' in files:
            #     form.set_ovs_view(DataInputStream(files['sideView']), 'sideView')
            # if 'topView' in files:
            #     form.set_ovs_view(DataInputStream(files['topView']), 'topView')
    elif question['type'] == 'question-record-type%3Amulti-choice-ortho%40ODL.MIT.EDU':
        # need to differentiate on create here because update might not use all
        # the fields, whereas we need to enforce a minimum of data on create
        if create:
            if 'questionString' in question:
                form.set_text(question['questionString'])
            else:
                raise NullArgument('questionString')

            if 'firstAngle' in question:
                form.set_first_angle_projection(question['firstAngle'])

            # files = request.FILES
            files = {}
            if 'manip' in files:
                if 'promptName' in question:
                    manip_name = question['promptName']
                else:
                    manip_name = 'A manipulatable'

                # TODO set the manip name to the question['promptName']
                # and find the right choice / ovs to go with it
                if 'rightAnswer' in question:
                    right_answer_sm, right_answer_lg = get_ovs_file_set(files,
                                                                        question['rightAnswer'])
                    form.set_manip(DataInputStream(files['manip']),
                                   DataInputStream(right_answer_sm),
                                   DataInputStream(right_answer_lg),
                                   manip_name)
                else:
                    form.set_manip(DataInputStream(files['manip']),
                                   name=manip_name)

                if not ('choice0small' in files and 'choice0big' in files):
                    raise NullArgument('At least two choice set attribute(s) required for Ortho-3D items.')
                elif not ('choice1small' in files and 'choice1big' in files):
                    raise NullArgument('At least two choice set attribute(s) required for Ortho-3D items.')
                else:
                    choice_files = get_choice_files(files)
                    if len(choice_files.keys()) % 2 != 0:
                        raise NullArgument('Large and small image files')
                    num_files = len(choice_files.keys()) / 2
                    for i in range(0,num_files):
                        # this goes with the code ~20 lines above, where
                        # the right choice files are saved with the manip...
                        # but, regardless, make a choice for each provided
                        # viewset. Trust the consumer to pair things up
                        # properly. Need the choiceId to set the answer
                        if 'rightAnswer' in question and i == int(question['rightAnswer']):
                            # save this as a choice anyways
                            small_file = DataInputStream(choice_files['choice' + str(i) + 'small'])
                            big_file = DataInputStream(choice_files['choice' + str(i) + 'big'])
                        else:
                            small_file = DataInputStream(choice_files['choice' + str(i) + 'small'])
                            big_file = DataInputStream(choice_files['choice' + str(i) + 'big'])
                        if 'choiceNames' in question:
                            name = question['choiceNames'][i]
                        else:
                            name = ''
                        form.set_ortho_choice(small_asset_data=small_file,
                                              large_asset_data=big_file,
                                              name=name)
            else:
                # is a match the ortho manip, so has choice#manip and
                # primary object of viewset
                raise NullArgument('manip file')

        else:
            if 'questionString' in question:
                form.set_text(question['questionString'])
            if 'firstAngle' in question:
                form.set_first_angle_projection(question['firstAngle'])
            # files = request.FILES
            # files = {}
            # if 'manip' in files:
            #     form.set_manip(DataInputStream(files['manip']))

            # TODO: change a choice set
    elif question['type'] == 'question-record-type%3Amulti-choice-edx%40ODL.MIT.EDU':
        if "rerandomize" in question:
            form.add_rerandomize(question['rerandomize'])
        if create:
            expected = ['questionString','choices']
            utilities.verify_keys_present(question, expected)

            should_be_list = ['choices']
            utilities.verify_min_length(question, should_be_list, 2)

            form.set_text(str(question['questionString']))
            # files get set after the form is returned, because
            # need the new_item
            # now manage the choices
            for ind, choice in enumerate(question['choices']):
                if isinstance(choice, dict):
                    form.add_choice(choice.get('text', ''),
                                    choice.get('name', 'Choice ' + str(int(ind) + 1)))
                else:
                    form.add_choice(choice, 'Choice ' + str(int(ind) + 1))
        else:
            if 'questionString' in question:
                form.set_text(str(question['questionString']))
            if 'choices' in question:
                # delete the old choices first
                for current_choice in form.my_osid_object_form._my_map['choices']:
                    form.clear_choice(current_choice)
                # now add the new ones
                for ind, choice in enumerate(question['choices']):
                    if isinstance(choice, dict):
                        form.add_choice(choice.get('text', ''),
                                        choice.get('name', 'Choice ' + str(int(ind) + 1)))
                    else:
                        form.add_choice(choice, 'Choice ' + str(int(ind) + 1))
    elif question['type'] == 'question-record-type%3Afiles-submission%40ODL.MIT.EDU':
        form.set_text(str(question['questionString']))
    elif question['type'] == 'question-record-type%3Anumeric-response-edx%40ODL.MIT.EDU':
        if create:
            form.set_text(str(question['questionString']))
        else:
            if 'questionString' in question:
                form.set_text(str(question['questionString']))
    elif 'qti' in question['type']:
        if 'questionString' in question:
            form.set_text(str(question['questionString']))
        if 'choices' in question:
            for choice in question['choices']:
                if 'id' in choice:
                    form.edit_choice(choice['id'], choice['text'])
                else:
                    form.add_choice(choice['text'])
        if 'inlineRegions' in question:
            for region, region_data in question['inlineRegions'].iteritems():
                for choice in region_data['choices']:
                    if 'id' in choice:
                        form.edit_choice(choice['id'], choice['text'], region)
                    else:
                        form.add_choice(choice['text'], region)
    else:
        raise Unsupported()

    return form

def update_response_form(response, form):
    """
    Put the response data into the form and send it back
    :param response: JSON data from user request
    :param form: responseForm, with methods that match the corresponding answerForm
    :return: updated form
    """
    if response['type'] == 'answer-record-type%3Aresponse-string%40ODL.MIT.EDU':
        if 'responseString' in response:
            form.set_response_string(response['responseString'])
    elif response['type'] == 'answer-record-type%3Alabel-ortho-faces%40ODL.MIT.EDU':
        if 'integerValues' in response:
            if isinstance(response['integerValues'], basestring):
                values = json.loads(response['integerValues'])
            else:
                values = response['integerValues']
            form.set_face_values(front_face_value=values['frontFaceValue'],
                                 side_face_value=values['sideFaceValue'],
                                 top_face_value=values['topFaceValue'])
    elif is_multiple_choice(response) or is_ordered_choice(response):
        try:
            response['choiceIds'] = response.getlist('choiceIds')
        except Exception:
            pass
        if isinstance(response['choiceIds'], list):
            for choice in response['choiceIds']:
                form.add_choice_id(choice)
        else:
            form.add_choice_id(response['choiceIds'])
            # raise InvalidArgument('ChoiceIds should be a list.')
    elif is_file_submission(response):
        try:
            for file_label, file_data in response['files'].iteritems():
                data_package = DataInputStream(file_data)
                data_package.name = file_label  # assumption ..
                extension = file_label.split('.')[-1]
                ac_genus_type = Type(identifier=extension,
                                     namespace='asset-content-genus-type',
                                     authority='ODL.MIT.EDU')
                label = file_label.replace('.', '_')
                try:
                    form.add_file(data_package, label)
                except AttributeError:
                    form.set_file(asset_data=data_package,
                                  asset_name=label,
                                  asset_content_type=ac_genus_type)
                    break
        except KeyError:
            pass  # perhaps no file passed in?
    elif is_short_answer(response):
        form.set_text(response['text'])
    elif response['type'] == 'answer-record-type%3Anumeric-response-edx%40ODL.MIT.EDU':
        if 'decimalValue' in response:
            form.set_decimal_value(float(response['decimalValue']))
        if 'tolerance' in response:
            form.set_tolerance_value(float(response['tolerance']))
    elif is_inline_choice(response):
        for inline_region, data in response['inlineRegions'].iteritems():
            form.add_inline_region(inline_region)
            for choice_id in data['choiceIds']:
                form.add_choice_id(choice_id, inline_region)
    elif is_numeric_response(response):
        region = [k for k in response.keys()if k != 'type'][0]
        try:
            form.add_integer_value(int(response[region]), region)
        except ValueError:
            try:
                form.add_decimal_value(float(response[region]), region)
            except ValueError:
                form.set_text(str(response[region]))
    else:
        raise Unsupported()
    return form

def validate_response(response, answers):
    correct = False
    # for longer submissions / multi-answer questions, need to make
    # sure that all of them match...
    if is_file_submission(response) or is_short_answer(response) or is_survey(response):
        return True  # always say True because the file was accepted

    submission = get_response_submissions(response)

    if is_multiple_choice(response) or is_ordered_choice(response):
        right_answers = [a for a in answers
                         if is_right_answer(a)]
        for answer in right_answers:
            num_right = 0
            num_total = answer.get_choice_ids().available()
            if len(submission) == num_total:
                for index, choice_id in enumerate(answer.get_choice_ids()):
                    if is_ordered_choice(response):
                        if str(choice_id) == submission[index]:  # order matters
                            num_right += 1
                    else:
                        if str(choice_id) in submission:  # order doesn't matter
                            num_right += 1
                if num_right == num_total and len(submission) == num_total:
                    correct = True
    elif is_inline_choice(response):
        correct = evaluate_inline_choice(answers, submission)
    elif is_numeric_response(response):
        right_answers = [a for a in answers
                         if is_right_answer(a)]

        for answer in right_answers:
            correct = answer.is_match(submission)
            break  # only take the first right answer for now
    else:
        for answer in answers:
            ans_type = answer.object_map['recordTypeIds'][0]
            if ans_type == 'answer-record-type%3Alabel-ortho-faces%40ODL.MIT.EDU':
                if isinstance(submission, basestring):
                    submission = json.loads(submission)
                if (int(answer.get_front_face_value()) == int(submission['frontFaceValue']) and
                    int(answer.get_side_face_value()) == int(submission['sideFaceValue']) and
                    int(answer.get_top_face_value()) == int(submission['topFaceValue'])):
                    correct = True
                    break
            elif (ans_type == 'answer-record-type%3Amulti-choice-ortho%40ODL.MIT.EDU' or
                  ans_type == 'answer-record-type%3Amulti-choice-edx%40ODL.MIT.EDU'):
                if not isinstance(submission, list):
                    raise InvalidArgument('ChoiceIds should be a list, in a student response.')
                if len(submission) == 1:
                    if answer.get_choice_ids()[0] == submission[0]:
                        correct = True
                        break
            elif ans_type == 'answer-record-type%3Anumeric-response-edx%40ODL.MIT.EDU':
                expected = answer.get_decimal()
                tolerance = answer.get_tolerance()
                if (expected - tolerance) <= submission <= (expected + tolerance):
                    correct = True
                    break
    return correct
