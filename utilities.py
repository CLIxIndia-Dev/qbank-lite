import functools
import json
import traceback
import web
import os

from urllib import quote

from dlkit.json_ import types

from dlkit.runtime.errors import PermissionDenied, IllegalState,\
    OperationFailed
from dlkit.runtime.primitives import InitializableLocale
from dlkit.runtime.primordium import Id, Type, DisplayText

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
        # merge web.data() (url params) and web.input() (form)
        form_data = web.input()

        url_data = {}
        try:
            url_data = json.loads(web.data())
        except (ValueError, TypeError):
            pass
        if isinstance(url_data, dict):
            # because might pass in list data, like a list of offereds
            url_data.update(form_data)

        return url_data


def create_agent_id(username, authority='MIT-ODL'):
    return Id(identifier=username,
              namespace='osid.agent.Agent',
              authority=authority)


def create_display_text(text_string, language_code=None):
    if isinstance(text_string, dict):
        return DisplayText(display_text_map=text_string)

    # check the web headers to see if it was included
    header_language_code = web.ctx.env.get('HTTP_X_API_LOCALE', None)

    if language_code is None and header_language_code is not None:
        language_code = header_language_code

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
            locale = convert_two_digit_lang_code_to_locale_object(language_code)
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
        from assessment.assessment_utilities import get_assessment_manager
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
        if isinstance(results, dict) or isinstance(results, list):
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


def clean_id(_id):
    """
    Django seems to un-url-safe the IDs passed in to the rest framework views,
    so we need to url-safe them, then convert them to OSID IDs
    """
    if _id.find('@') >= 0:
        return Id(quote(_id))
    else:
        return Id(_id)


def clean_json(data):
    """return the json object version of the data, assuming it's a JSON string
    Return the original data if an exception is throw
    TypeError is thrown if non-string passed in
    ValueError is thrown if a non-JSON string passed in
    """
    try:
        return json.loads(data)
    except (TypeError, ValueError):
        pass
    return data


def construct_qti_id(qti_id, namespace='assessment.Item'):
    return Id(identifier=qti_id,
              namespace=namespace,
              authority='QTI.IMS.COM')


def convert_dl_object(obj):
    """
    convert a DLKit object into a "real" json-able object
    """
    try:
        # return json.loads(json.loads(json.dumps(obj, cls=DLEncoder)))
        return json.dumps(obj.object_map)
    except:
        return json.dumps(obj)


def convert_two_digit_lang_code_to_locale_object(language_code):
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
        return InitializableLocale(language_type_identifier=language_code,
                                   script_type_identifier=script_code)
    return None


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
                    except Exception:  # yes, this is overly broad and violets PEP8
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
            try:
                return json.dumps([i.object_map for i in item_list])
            except AttributeError:
                return json.dumps(item_list)
        return json.dumps([])


def handle_exceptions(ex):
    message = str(ex)
    if 'WEBENV' in os.environ and os.environ['WEBENV'] == 'test':
        pass
    elif (('WEBENV' in os.environ and os.environ['WEBENV'] == 'development') or
          ('WEBENV' in web.ctx.env and web.ctx.env['WEBENV'] == 'development')):
        message = traceback.format_exc(10)
        print message  # to get this in the server logs
    else:
        pass
        # print traceback.format_exc(10)
    if isinstance(ex, PermissionDenied):
        web.message = 'Permission Denied'
        raise web.Forbidden()
    elif isinstance(ex, IllegalState):
        # Sometimes we try to explain why illegal state, like
        # the assessment still has items, can't delete it.
        # web.message = 'IllegalState {0}'.format(message)
        # raise web.NotAcceptable()
        raise web.InternalError('IllegalState {0}'.format(message))
    else:
        raise web.InternalError(message)


def set_form_basics(form, data):
    def _grab_first_match(keys):
        # filtered = {k:v for k, v in data.iteritems() if k in keys}
        # return filtered[filtered.keys()[0]]
        return data[set(keys).intersection(data.keys()).pop()]

    name_keys = ['name', 'displayName', 'displayname', 'display_name']
    description_keys = ['desc', 'description']
    genus_keys = ['genus', 'genusTypeId', 'genusType', 'genus_type_id', 'genus_type']

    if any(_name in data for _name in name_keys):
        try:
            form.add_display_name(create_display_text(_grab_first_match(name_keys)))
        except AttributeError:
            # to support legacy data
            form.display_name = _grab_first_match(name_keys)

    if 'editName' in data:
        old_name = create_display_text(data['editName'][0])
        new_name = create_display_text(data['editName'][1])
        form.edit_display_name(old_name, new_name)

    if 'removeName' in data:
        old_name = create_display_text(data['removeName'])
        form.clear_display_name(old_name)

    if any(_desc in data for _desc in description_keys):
        try:
            form.add_description(create_display_text(_grab_first_match(description_keys)))
        except AttributeError:
            # to support legacy data
            form.description = _grab_first_match(description_keys)

    if 'editDescription' in data:
        old_description = create_display_text(data['editDescription'][0])
        new_description = create_display_text(data['editDescription'][1])
        form.edit_description(old_description, new_description)

    if 'removeDescription' in data:
        old_description = create_display_text(data['removeDescription'])
        form.clear_description(old_description)

    if any(_genus in data for _genus in genus_keys):
        form.set_genus_type(Type(_grab_first_match(genus_keys)))

    return form


def success():
    return json.dumps({"success": True})


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
