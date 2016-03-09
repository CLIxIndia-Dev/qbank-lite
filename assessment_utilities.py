import json

from dlkit_edx.errors import InvalidArgument, Unsupported, NotFound
from dlkit_edx.primordium import Duration, DateTime, Id, Type,\
    DataInputStream

from inflection import underscore

from records.registry import ASSESSMENT_OFFERED_RECORD_TYPES,\
    ANSWER_GENUS_TYPES, ANSWER_RECORD_TYPES

import utilities

REVIEWABLE_OFFERED = Type(**ASSESSMENT_OFFERED_RECORD_TYPES['review-options'])


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

def find_answer_in_answers(ans_id, ans_list):
    for ans in ans_list:
        if ans.ident == ans_id:
            return ans
    return None

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
    except NotFound:
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
    elif is_multiple_choice(response):
        if isinstance(response, dict):
            submission = response['choiceIds']
        else:
            submission = response.getlist('choiceIds')
    elif response['type'] == 'answer-record-type%3Anumeric-response-edx%40ODL.MIT.EDU':
        submission = float(response['decimalValue'])
    else:
        raise Unsupported
    return submission

def is_multiple_choice(response):
    return any(mc in response['type'] for mc in ['multi-choice-ortho', 'multi-choice-edx'])

def is_right_answer(answer):
    return (answer.genus_type == Type(**ANSWER_GENUS_TYPES['right-answer']) or
            str(answer.genus_type).lower() == 'genustype%3adefault%40dlkit.mit.edu')

def set_answer_form_genus_and_feedback(answer, answer_form):
    """answer is a dictionary"""
    if 'genus' in answer:
        answer_form.genus_type = Type(answer['genus'])
        if answer['genus'] == str(Type(**ANSWER_GENUS_TYPES['wrong-answer'])):
            if 'feedback' in answer:
                answer_form._init_record(str(Type(**ANSWER_RECORD_TYPES['answer-with-feedback'])))
                answer_form.set_feedback(str(answer['feedback']))
            if 'confusedLearningObjectiveIds' in answer:
                if not isinstance(answer['confusedLearningObjectiveIds'], list):
                    los = [answer['confusedLearningObjectiveIds']]
                else:
                    los = answer['confusedLearningObjectiveIds']
                answer_form.set_confused_learning_objective_ids(los)
    else:
        # default is correct answer, if not supplied
        answer_form.set_genus_type(Type(**ANSWER_GENUS_TYPES['right-answer']))
        try:
            # remove the feedback components
            del answer_form._my_map['texts']['feedback']
            del answer_form._my_map['recordTypeIds'][str(Type(**ANSWER_RECORD_TYPES['answer-with-feedback']))]
        except KeyError:
            pass
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
                                                                        [REVIEWABLE_OFFERED])
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

        new_offering = execute(offering_form)
        return_data.append(new_offering)
    return return_data

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
    elif (response['type'] == 'answer-record-type%3Amulti-choice-ortho%40ODL.MIT.EDU' or
          response['type'] == 'answer-record-type%3Amulti-choice-edx%40ODL.MIT.EDU'):
        try:
            response['choiceIds'] = response.getlist('choiceIds')
        except Exception:
            pass
        if isinstance(response['choiceIds'], list):
            for choice in response['choiceIds']:
                form.add_choice_id(choice)
        else:
            raise InvalidArgument('ChoiceIds should be a list.')
    elif response['type'] == 'answer-record-type%3Afiles-submission%40ODL.MIT.EDU':
        for file_label, file_data in response['files'].iteritems():
            form.add_file(DataInputStream(file_data), file_label)
    elif response['type'] == 'answer-record-type%3Anumeric-response-edx%40ODL.MIT.EDU':
        if 'decimalValue' in response:
            form.set_decimal_value(float(response['decimalValue']))
        if 'tolerance' in response:
            form.set_tolerance_value(float(response['tolerance']))
    else:
        raise Unsupported()
    return form

def validate_response(response, answers):
    correct = False
    # for longer submissions / multi-answer questions, need to make
    # sure that all of them match...
    if response['type'] == 'answer-record-type%3Afiles-submission%40ODL.MIT.EDU':
        return True  # always say True because the file was accepted

    submission = get_response_submissions(response)

    if is_multiple_choice(response):
        right_answers = [a for a in answers
                         if is_right_answer(a)]
        num_total = len(right_answers)

        if num_total != len(submission):
            pass
        else:
            num_right = 0
            for answer in right_answers:
                if answer.get_choice_ids()[0] in submission:
                    num_right += 1
                else:
                    break
            if num_right == num_total:
                correct = True
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
