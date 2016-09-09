import functools
import json
import traceback
import web

from urllib import quote

from dlkit.mongo import types

from dlkit_edx import PROXY_SESSION, RUNTIME
from dlkit_edx.errors import PermissionDenied, InvalidArgument, IllegalState, NotFound,\
    OperationFailed, Unsupported
from dlkit_edx.primitives import IntitializableLocale
from dlkit_edx.primordium import Id, Type, DisplayText
from dlkit_edx.proxy_example import TestRequest

DEFAULT_LANGUAGE_TYPE = Type(**types.Language().get_type_data('DEFAULT'))
DEFAULT_SCRIPT_TYPE = Type(**types.Script().get_type_data('DEFAULT'))
DEFAULT_FORMAT_TYPE = Type(**types.Format().get_type_data('DEFAULT'))


CORS_HEADERS = "Content-Type,Authorization,X-Api-Proxy,X-Api-Key,request-line,X-Api-Locale"


class BaseClass:
    def OPTIONS(self, *args, **kwargs):
        # https://www.youtube.com/watch?v=gZelOtYjYv8
        web.header("Access-Control-Allow-Origin", "*")
        web.header("Access-Control-Allow-Credentials", "true")
        web.header("Access-Control-Allow-Headers", CORS_HEADERS)
        web.header("Access-Control-Allow-Methods", "GET, POST, OPTIONS, PUT, DELETE")
        web.header("Access-Control-Max-Age", "1728000")
        return

    @staticmethod
    def data():
        try:
            return json.loads(web.data())
        except (ValueError, TypeError):
            return {}

def create_display_text(text_string, language_code=None):
    if language_code is None:
        return DisplayText(display_text_map={
            'text': text_string,
            'languageTypeId': str(DEFAULT_LANGUAGE_TYPE),
            'formatTypeId': str(DEFAULT_FORMAT_TYPE),
            'scriptTypeId': str(DEFAULT_SCRIPT_TYPE)
        })
    else:
        language_code = language_code.lower()
        if language_code in ['en', 'hi', 'te']:
            if language_code == 'en':
                language_code = 'ENG'
                script_code = 'LATN'
            elif language_code == 'hi':
                language_code = 'HIN'
                script_code = 'DEVA'
            elif language_code == 'te':
                language_code = 'TEL'
                script_code = 'TELU'
            locale = IntitializableLocale(language_type_identifier=language_code,
                                          script_type_identifier=script_code)
            language_type_id = locale.language_type
            script_type_id = locale.script_type
        else:
            language_type_id = DEFAULT_LANGUAGE_TYPE
            script_type_id = DEFAULT_SCRIPT_TYPE

        return DisplayText(display_text_map={
            'text': text_string,
            'languageTypeId': str(language_type_id),
            'formatTypeId': str(DEFAULT_FORMAT_TYPE),
            'scriptTypeId': str(script_type_id)
        })

def format_response_mit_type(func):
    """wrap original response in a {"format": "MIT-CLIx-OEA", "data": "<foo>"} object
    ASSUMES that this is wrapped around format_response, like

      @utilities.format_response
      @utilities.format_response_mit_type
      def GET(self, bank_id, taken_id):

    """
    @functools.wraps(func)
    def wrapper(self, *args):
        from assessment_utilities import get_assessment_manager
        results = func(self, *args)

        response = {
            "format": "MIT-CLIx-OEA",
            "data": json.loads(results)  # return an object
        }

        # inject the offered N of M also, if available
        if (len(args) == 2 and
                args[0].startswith('assessment.Bank') and
                args[1].startswith('assessment.AssessmentTaken')):
            am = get_assessment_manager()
            bank = am.get_bank(clean_id(args[0]))
            taken = bank.get_assessment_taken(clean_id(args[1]))
            offered = bank.get_assessment_offered(clean_id(taken.object_map['assessmentOfferedId']))
            offered_map = offered.object_map
            if 'nOfM' in offered_map:
                response.update({
                    'nOfM': offered_map['nOfM']
                })
        return response
    return wrapper

def format_response(func):
    """set json header and convert response to json string"""
    @functools.wraps(func)
    def wrapper(self, *args):
        results = func(self, *args)
        web.header('Content-type', 'application/json')
        web.header("Access-Control-Allow-Origin", "*")
        web.header("Access-Control-Allow-Credentials", "true")
        web.header("Access-Control-Allow-Headers", CORS_HEADERS)
        web.header("Access-Control-Allow-Methods", "GET, POST, OPTIONS, PUT, DELETE")
        web.header("Access-Control-Max-Age", "1728000")
        if isinstance(results, dict):
            return json.dumps(results)
        else:
            return results
    return wrapper

def format_xml_response(func):
    """set json header and convert response to json string"""
    @functools.wraps(func)
    def wrapper(self, *args):
        results = func(self, *args)
        web.header('Content-type', 'application/xml')
        web.header("Access-Control-Allow-Origin", "*")
        web.header("Access-Control-Allow-Credentials", "true")
        web.header("Access-Control-Allow-Headers", CORS_HEADERS)
        web.header("Access-Control-Allow-Methods", "GET, POST, OPTIONS, PUT, DELETE")
        web.header("Access-Control-Max-Age", "1728000")
        if isinstance(results, dict):
            return json.dumps(results)
        else:
            return results
    return wrapper

def allow_cors(func):
    """set cors headers"""
    @functools.wraps(func)
    def wrapper(self, *args):
        results = func(self, *args)
        web.header("Access-Control-Allow-Origin", "*")
        web.header("Access-Control-Allow-Credentials", "true")
        web.header("Access-Control-Allow-Headers", CORS_HEADERS)
        web.header("Access-Control-Allow-Methods", "GET, POST, OPTIONS, PUT, DELETE")
        web.header("Access-Control-Max-Age", "1728000")
        return results
    return wrapper

def activate_managers(session, username='student@tiss.edu'):
    """
    Create initial managers and store them in the session
    """
    managers = [('am', 'ASSESSMENT'),
                ('logm', 'LOGGING'),
                ('rm', 'REPOSITORY')]

    for manager in managers:
        nickname = manager[0]
        service_name = manager[1]

        condition = PROXY_SESSION.get_proxy_condition()
        dummy_request = TestRequest(username=username, authenticated=True)
        condition.set_http_request(dummy_request)
        proxy = PROXY_SESSION.get_proxy(condition)
        session._initializer[nickname] = RUNTIME.get_service_manager(service_name,
                                                                     proxy=proxy)
    return session

def clean_id(_id):
    """
    Django seems to un-url-safe the IDs passed in to the rest framework views,
    so we need to url-safe them, then convert them to OSID IDs
    """
    if _id.find('@') >= 0:
        return Id(quote(_id))
    else:
        return Id(_id)

def construct_qti_id(qti_id, namespace='assessment.Item'):
    return Id(identifier=qti_id,
              namespace=namespace,
              authority='QTI.IMS.COM')

def convert_dl_object(obj):
    """
    convert a DLKit object into a "real" json-able object
    """
    try:
        #return json.loads(json.loads(json.dumps(obj, cls=DLEncoder)))
        return json.dumps(obj.object_map)
    except:
        return json.dumps(obj)

def extract_items(item_list):
    try:
        if item_list.available() > 0:
            # so we don't list the items because it's a generator
            try:
                orig_list = list(item_list)
                results = []
                for item in orig_list:
                    try:
                        results.append(item.object_map)
                    except AttributeError:
                        # Hierarchy Nodes do not have .object_map
                        results.append(item.get_node_map())
                    except Exception: # yes, this is overly broad and violets PEP8
                        # but we are suppressing all errors that might happen
                        # due to bad items
                        pass
                return json.dumps(results)
            except OperationFailed:
                return json.dumps([i.object_map for i in item_list])
        else:
            return json.dumps([])
    except AttributeError:
        if len(item_list) > 0:
            return json.dumps([i.object_map for i in item_list])
        return json.dumps([])

def handle_exceptions(ex):
    print traceback.format_exc(10)
    if isinstance(ex, PermissionDenied):
        web.message = 'Permission Denied'
        raise web.Forbidden()
    elif isinstance(ex, IllegalState):
        web.message = 'IllegalState {}'.format(str(ex))
        raise web.NotAcceptable()
    else:
        web.message = 'Bad request {}'.format(ex)
        raise web.NotFound()

def set_form_basics(form, data):
    def _grab_first_match(keys):
        # filtered = {k:v for k, v in data.iteritems() if k in keys}
        # return filtered[filtered.keys()[0]]
        return data[set(keys).intersection(data.keys()).pop()]

    name_keys = ['name', 'displayName', 'displayname', 'display_name']
    description_keys = ['desc', 'description']
    genus_keys = ['genus', 'genusTypeId', 'genusType', 'genus_type_id', 'genus_type']

    if any(_name in data for _name in name_keys):
        form.display_name = _grab_first_match(name_keys)

    if any(_desc in data for _desc in description_keys):
        form.description = _grab_first_match(description_keys)

    if any(_genus in data for _genus in genus_keys):
        form.set_genus_type(Type(_grab_first_match(genus_keys)))

    return form

def verify_at_least_one_key_present(_data, _keys_list):
    """
    at least one of the keys is present
    """
    present = False

    for key in _keys_list:
        if key in _data:
            present = True

    if not present:
        raise KeyError('At least one of the following must be passed in: ' + json.dumps(_keys_list))

def verify_keys_present(my_dict, list_of_keys):
    if not isinstance(list_of_keys, list):
        list_of_keys = [list_of_keys]
    for key in list_of_keys:
        if key not in my_dict:
            raise KeyError('"' + key + '" required in input parameters but not provided.')

def verify_min_length(my_dict, list_of_keys, expected_len):
    for key in list_of_keys:
        if not isinstance(my_dict[key], list):
            raise TypeError('"' + key + '" is not a list.')
        else:
            if len(my_dict[key]) < int(expected_len):
                raise TypeError('"' + key + '" is shorter than ' + str(expected_len) + '.')

