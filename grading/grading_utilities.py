import inflection
import web
import utilities

from dlkit.json_ import types
from dlkit.runtime import PROXY_SESSION, RUNTIME
from dlkit.runtime.errors import InvalidArgument
from dlkit.runtime.primitives import InitializableLocale
from dlkit.runtime.primordium import Type
from dlkit.runtime.proxy_example import SimpleRequest

DEFAULT_LANGUAGE_TYPE = Type(**types.Language().get_type_data('DEFAULT'))
DEFAULT_SCRIPT_TYPE = Type(**types.Script().get_type_data('DEFAULT'))
DEFAULT_FORMAT_TYPE = Type(**types.Format().get_type_data('DEFAULT'))


def add_grades_to_grade_system(gradebook, grade_system, data):
    try:
        attrs_to_check = ['inputScoreStartRange', 'inputScoreEndRange', 'outputScore',
                          'name', 'description']
        for grade in data['grades']:
            form = gradebook.get_grade_form_for_create(grade_system.ident, [])
            for attr in attrs_to_check:
                if attr in grade:
                    if attr in ['inputScoreStartRange', 'inputScoreEndRange', 'outputScore']:
                        val = float(grade[attr])
                        getattr(form, 'set_' + inflection.underscore(attr))(val)
                    else:
                        val = str(grade[attr])
                        if attr == 'name':
                            form.display_name = val
                        else:
                            form.description = val
            gradebook.create_grade(form)
    except KeyError as ex:
        raise InvalidArgument('"{}" expected in grade object.'.format(str(ex.args[0])))


def check_grade_inputs(data):
    utilities.verify_keys_present(data, 'grades')
    if not isinstance(data['grades'], list):
        raise InvalidArgument('Grades must be a list of objects.')


def check_numeric_score_inputs(data):
    expected_score_inputs = ['highestNumericScore', 'lowestNumericScore', 'numericScoreIncrement']
    utilities.verify_keys_present(data, expected_score_inputs)


def validate_score_and_grades_against_system(grade_system, data):
    if grade_system.is_based_on_grades() and 'score' in data:
        raise InvalidArgument('You cannot set a numeric score when using a grade-based system.')
    if not grade_system.is_based_on_grades() and 'grade' in data:
        raise InvalidArgument('You cannot set a grade when using a numeric score-based system.')


def validate_grade_system_exists(gradebook, grade_system_id):
    gradebook.get_grade_system(grade_system_id)

def get_grading_manager():
    condition = PROXY_SESSION.get_proxy_condition()
    dummy_request = SimpleRequest(username=web.ctx.env.get('HTTP_X_API_PROXY', 'student@tiss.edu'),
                                  authenticated=True)
    condition.set_http_request(dummy_request)

    if 'HTTP_X_API_LOCALE' in web.ctx.env:
        language_code = web.ctx.env['HTTP_X_API_LOCALE'].lower()
        if language_code in ['en', 'hi', 'te']:
            if language_code == 'en':
                language_code = 'ENG'
                script_code = 'LATN'
            elif language_code == 'hi':
                language_code = 'HIN'
                script_code = 'DEVA'
            else:
                language_code = 'TEL'
                script_code = 'TELU'
        else:
            language_code = DEFAULT_LANGUAGE_TYPE.identifier
            script_code = DEFAULT_SCRIPT_TYPE.identifier

        locale = InitializableLocale(language_type_identifier=language_code,
                                     script_type_identifier=script_code)

        condition.set_locale(locale)

    proxy = PROXY_SESSION.get_proxy(condition)
    return RUNTIME.get_service_manager('GRADING',
                                       proxy=proxy)

