import functools
import json
import traceback
import web

from urllib import quote

from dlkit_edx import PROXY_SESSION, RUNTIME
from dlkit_edx.errors import PermissionDenied, InvalidArgument, IllegalState, NotFound
from dlkit_edx.primordium import Id, Type
from dlkit_edx.proxy_example import TestRequest


class BaseClass:
    @staticmethod
    def data():
        try:
            return json.loads(web.data())
        except (ValueError, TypeError):
            return {}


def format_response(func):
    """set json header and convert response to json string"""
    @functools.wraps(func)
    def wrapper(self, *args):
        results = func(self, *args)
        web.header('Content-type', 'application/json')
        if isinstance(results, dict):
            return json.dumps(results)
        else:
            return results
    return wrapper



def activate_managers(session):
    """
    Create initial managers and store them in the session
    """
    managers = [('am', 'ASSESSMENT'),
                ('logm', 'LOGGING')]

    for manager in managers:
        nickname = manager[0]
        service_name = manager[1]
        if not hasattr(session, nickname):
            condition = PROXY_SESSION.get_proxy_condition()
            dummy_request = TestRequest(username='student@tiss.edu', authenticated=True)
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
        web.message = 'IllegalState {}'.format(ex)
        raise web.NotAcceptable()
    else:
        web.message = 'Bad request {}'.format(ex)
        raise web.NotAcceptable()

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

