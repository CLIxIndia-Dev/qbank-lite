import json
import web

from bson.errors import InvalidId

from dlkit.primordium.type.primitives import Type
from dlkit.json_ import types
from dlkit_runtime import PROXY_SESSION, RUNTIME
from dlkit_runtime.errors import NotFound
from dlkit_runtime.proxy_example import TestRequest
from dlkit_runtime.primitives import InitializableLocale

from utilities import clean_id

DEFAULT_LANGUAGE_TYPE = Type(**types.Language().get_type_data('DEFAULT'))
DEFAULT_SCRIPT_TYPE = Type(**types.Script().get_type_data('DEFAULT'))
DEFAULT_FORMAT_TYPE = Type(**types.Format().get_type_data('DEFAULT'))


def get_alias_resource_id(resource_name, authority='ODL.MIT.EDU'):
    # Note that this authority must match the config...
    return clean_id('resource.Resource%3A{0}%40{1}'.format(resource_name,
                                                           authority))


def get_or_create_resource_id(catalog, resource_name):
    mgr = get_resource_manager()
    bin_ = mgr.get_bin(catalog.ident)

    authority = 'ODL.MIT.EDU'
    try:
        config = bin_._catalog._runtime.get_configuration()
        parameter_id = clean_id('parameter:authority@json')
        authority = config.get_value_by_parameter(parameter_id).get_string_value()
    except (AttributeError, KeyError, NotFound):
        pass

    resource_alias_id = get_alias_resource_id(resource_name,
                                           authority=authority)
    try:
        # look for an aliased resource
        resource = bin_.get_resource(resource_alias_id)
    except (NotFound, InvalidId):
        form = bin_.get_resource_form_for_create([])
        form.display_name = resource_name
        resource = bin_.create_resource(form)
        bin_.alias_resource(resource.ident, resource_alias_id)

    return resource.ident


def get_resource_manager():
    condition = PROXY_SESSION.get_proxy_condition()
    dummy_request = TestRequest(username=web.ctx.env.get('HTTP_X_API_PROXY', 'student@tiss.edu'),
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
    return RUNTIME.get_service_manager('RESOURCE',
                                       proxy=proxy)


def update_asset_map_with_resource(asset_map):
    original_was_string = False
    if isinstance(asset_map, str):
        asset_map = json.loads(asset_map)
        original_was_string = True

    if 'sourceId' in asset_map and asset_map['sourceId'] != '':
        mgr = get_resource_manager()
        rls = mgr.get_resource_lookup_session()
        rls.use_federated_bin_view()
        resource = rls.get_resource(clean_id(asset_map['sourceId']))
        asset_map['source'] = {
            'text': resource.display_name.text,
            'languageTypeId': str(resource.display_name.language_type),
            'formatTypeId': str(resource.display_name.format_type),
            'scriptTypeId': str(resource.display_name.script_type)
        }

    if original_was_string:
        return json.dumps(asset_map)
    return asset_map