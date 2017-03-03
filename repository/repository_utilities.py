import os
import web

from dlkit.primordium.id.primitives import Id
from dlkit.primordium.transport.objects import DataInputStream
from dlkit.primordium.type.primitives import Type
from dlkit.mongo import types

from dlkit_runtime import PROXY_SESSION, RUNTIME
from dlkit_runtime.errors import NotFound
from dlkit_runtime.primitives import InitializableLocale
from dlkit_runtime.proxy_example import TestRequest

from records import registry

import utilities

DEFAULT_LANGUAGE_TYPE = Type(**types.Language().get_type_data('DEFAULT'))
DEFAULT_SCRIPT_TYPE = Type(**types.Script().get_type_data('DEFAULT'))
DEFAULT_FORMAT_TYPE = Type(**types.Format().get_type_data('DEFAULT'))

IMAGE_ASSET_GENUS_TYPE = Type(**registry.ASSET_GENUS_TYPES['image'])
JPG_ASSET_CONTENT_GENUS_TYPE = Type(**registry.ASSET_CONTENT_GENUS_TYPES['jpg'])
GENERIC_ASSET_CONTENT_GENUS_TYPE = Type(**registry.ASSET_CONTENT_GENUS_TYPES['generic'])
MP3_ASSET_CONTENT_GENUS_TYPE = Type(**registry.ASSET_CONTENT_GENUS_TYPES['mp3'])
PNG_ASSET_CONTENT_GENUS_TYPE = Type(**registry.ASSET_CONTENT_GENUS_TYPES['png'])
SVG_ASSET_CONTENT_GENUS_TYPE = Type(**registry.ASSET_CONTENT_GENUS_TYPES['svg'])
WAV_ASSET_CONTENT_GENUS_TYPE = Type(**registry.ASSET_CONTENT_GENUS_TYPES['wav'])
MULTI_LANGUAGE_ASSET_CONTENT = Type(**registry.ASSET_CONTENT_RECORD_TYPES['multi-language'])


def append_asset_contents(repo, asset, file_name, file_data, basics=None):
    asset_content_type_list = get_asset_content_records(repo)

    acfc = repo.get_asset_content_form_for_create(asset.ident,
                                                  asset_content_type_list)
    acfc.set_genus_type(get_asset_content_genus_type(file_name))

    try:
        acfc.add_display_name(utilities.create_display_text(file_name))
    except AttributeError:
        acfc.display_name = file_name

    data = DataInputStream(file_data)
    data.name = file_name

    acfc.set_data(data)

    if basics is not None:
        acfc = utilities.set_form_basics(acfc, basics)

    ac = repo.create_asset_content(acfc)

    # really stupid, but set the data again, because for filesystem impl
    # the ID above will be off by one-ish -- we need it to match the
    # AssetContent ID, so re-set it.
    # have to set it above so that the filesystem adapter kicks in on update
    data.seek(0)
    acfu = repo.get_asset_content_form_for_update(ac.ident)
    acfu.set_data(data)
    repo.update_asset_content(acfu)

    return repo.get_asset(asset.ident), ac


def convert_ac_name_to_label(asset_content):
    return asset_content.display_name.text.replace('.', '_')


def create_asset(repo, file_name):
    afc = repo.get_asset_form_for_create([])
    afc.set_display_name(get_singular_filename(file_name))
    afc.set_description('File uploaded from a script')
    return repo.create_asset(afc)


def get_asset_content_by_id(asset, asset_content_id):
    for asset_content in asset.get_asset_contents():
        if str(asset_content_id) == str(asset_content.ident):
            return asset_content
    return None


def get_asset_content_records(repo):
    asset_content_type_list = [MULTI_LANGUAGE_ASSET_CONTENT]
    try:
        config = repo._osid_object._runtime.get_configuration()
        parameter_id = Id('parameter:assetContentRecordTypeForFiles@filesystem')
        asset_content_type_list.append(
            config.get_value_by_parameter(parameter_id).get_type_value())
    except (AttributeError, KeyError, NotFound):
        pass
    return asset_content_type_list


def get_asset_content_genus_type(file_name):
    extension = get_file_extension(file_name).lower()
    if 'png' in extension:
        ac_genus_type = PNG_ASSET_CONTENT_GENUS_TYPE
    elif 'jpg' in extension or 'jpeg' in extension:
        ac_genus_type = JPG_ASSET_CONTENT_GENUS_TYPE
    elif 'svg' in extension:
        ac_genus_type = SVG_ASSET_CONTENT_GENUS_TYPE
    elif 'mp3' in extension:
        ac_genus_type = MP3_ASSET_CONTENT_GENUS_TYPE
    elif 'wav' in extension:
        ac_genus_type = WAV_ASSET_CONTENT_GENUS_TYPE
    else:
        # since this is used for the extension, let's derive it
        # more gracefully
        ac_genus_type = Type(identifier=extension,
                             namespace='asset-content-genus-type',
                             authority='ODL.MIT.EDU')
        # ac_genus_type = GENERIC_ASSET_CONTENT_GENUS_TYPE
    return ac_genus_type


def get_file_extension(file_name):
    return os.path.splitext(os.path.basename(file_name))[-1].replace('.', '')


def get_repository_manager():
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
    return RUNTIME.get_service_manager('REPOSITORY',
                                       proxy=proxy)


def get_singular_filename(file_name):
    file_name = file_name.replace('-', '_')  # just to handle both cases
    extension = get_file_extension(file_name).lower()
    if extension == 'vtt':
        return '_'.join(file_name.split('_')[0:-1])
    else:
        return file_name.split('.')[0]


def match_asset_content_by_name(asset_content_list, name):
    for asset_content in asset_content_list:
        if asset_content.display_name.text == name:
            return asset_content
    return None


def update_asset_map_with_content_url(rm, asset_map):
    # because we've appended the asset content lookup methods to asset lookup session
    acls = rm.get_asset_lookup_session()
    acls.use_federated_repository_view()
    if 'assetContents' in asset_map:
        for index, asset_content in enumerate(asset_map['assetContents']):
            ac = acls.get_asset_content(utilities.clean_id(asset_content['id']))
            asset_map['assetContents'][index]['url'] = ac.get_url()
    else:
        # for an assetContent
        ac = acls.get_asset_content(utilities.clean_id(asset_map['id']))
        asset_map['url'] = ac.get_url()
    return asset_map
