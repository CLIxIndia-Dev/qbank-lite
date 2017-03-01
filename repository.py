import mimetypes
import os
import web
import json

from bson.errors import InvalidId

from dlkit_runtime.errors import *
from dlkit_runtime.primitives import DataInputStream, Type

import repository_utilities as rutils
import utilities


urls = (
    "/repositories/(.*)/assets/(.*)/contents/(.*)/stream", "AssetContentStream",
    "/repositories/(.*)/assets/(.*)/contents/(.*)", "AssetContentDetails",
    "/repositories/(.*)/assets/(.*)/contents", "AssetContentsList",
    "/repositories/(.*)/assets/(.*)", "AssetDetails",
    "/repositories/(.*)/assets", "AssetsList",
    "/repositories/(.*)", "RepositoryDetails",
    "/repositories", "RepositoriesList"
)


class RepositoriesList(utilities.BaseClass):
    """
    List all available repositories.
    api/v2/repository/repositories/

    """
    @utilities.format_response
    def GET(self):
        """
        List all available repositories
        """
        try:
            rm = rutils.get_repository_manager()
            repositories = rm.repositories
            repositories = utilities.extract_items(repositories)
            return repositories
        except (PermissionDenied, InvalidId) as ex:
            utilities.handle_exceptions(ex)


class RepositoryDetails(utilities.BaseClass):
    """
    Shows details for a specific repository. This can be orchestrated with an
    existing assessment bank.
    api/v2/repository/repositories/<repository_id>/

    GET
    """
    @utilities.format_response
    def GET(self, repository_id):
        try:
            rm = rutils.get_repository_manager()
            repository = rm.get_repository(utilities.clean_id(repository_id))
            repository = utilities.convert_dl_object(repository)
            return repository
        except (PermissionDenied, NotFound, InvalidId) as ex:
            utilities.handle_exceptions(ex)


class AssetsList(utilities.BaseClass):
    """
    Return list of assets in the given repository.
    api/v2/repository/repositories/<repository_id>/assets/

    GET, POST

    """
    @utilities.format_response
    def GET(self, repository_id=None):
        try:
            if repository_id is None:
                raise PermissionDenied
            rm = rutils.get_repository_manager()
            repository = rm.get_repository(utilities.clean_id(repository_id))
            assets = repository.get_assets()
            data = utilities.extract_items(assets)

            if 'fullUrls' in web.input():
                data = json.loads(data)
                updated_data = []
                for asset in data:
                    updated_data.append(rutils.update_asset_map_with_content_url(rm, asset))

                data = json.dumps(updated_data)

            return data
        except (PermissionDenied, InvalidId) as ex:
            utilities.handle_exceptions(ex)

    @utilities.format_response
    def POST(self, repository_id):
        try:
            x = web.input(inputFile={})
            rm = rutils.get_repository_manager()
            repository = rm.get_repository(utilities.clean_id(repository_id))
            repository.use_isolated_repository_view()
            # get each set of files individually, because
            # we are doing this in memory, so the file pointer changes
            # once we read in a file
            # https://docs.python.org/2/library/zipfile.html

            params = self.data()
            try:
                input_file = x['inputFile'].file
            except AttributeError:
                form = repository.get_asset_form_for_create([])
                form = utilities.set_form_basics(form, params)
                asset = repository.create_asset(form)
            else:
                # first, let's search the database to see if an asset exists with
                # the file name -- file name will be everything minus the
                # extension and language indicator.
                # for example, for one video there might be four files:
                #   * ee_u1l01a01v01.mov
                #   * ee_u1l01a01v01_en.vtt
                #   * ee_u1l01a01v01_hi.vtt
                #   * ee_u1l01a01v01_te.vtt
                # In this case, the "filename" / asset displayName.text is `ee_u1l01a01v01`.
                # If that already exists, add the input_file as an asset content.
                # If that asset does not exist, create it.
                file_name = x['inputFile'].filename

                if 'createNew' in params.keys() and params['createNew']:
                    asset = rutils.create_asset(repository, file_name)
                else:
                    try:
                        querier = repository.get_asset_query()
                    except (AttributeError, Unimplemented):
                        assets = None
                    else:
                        querier.match_display_name(rutils.get_singular_filename(file_name), match=True)
                        assets = repository.get_assets_by_query(querier)

                    if assets is not None and assets.available() > 0:
                        asset = assets.next()
                    else:
                        asset = rutils.create_asset(repository, file_name)

                # now let's create an asset content for this asset, with the
                # right genus type and file data
                rutils.append_asset_contents(repository, asset, file_name, input_file)

            if 'license' in params.keys() or 'copyright' in params.keys():
                form = repository.get_asset_form_for_update(asset.ident)
                if 'license' in params.keys():
                    form.set_license(params['license'])
                if 'copyright' in params.keys():
                    form.set_copyright(params['copyright'])
                asset = repository.update_asset(form)

            # need to get the updated asset with Contents
            asset = repository.get_asset(asset.ident)
            asset_map = json.loads(utilities.convert_dl_object(asset))
            if 'returnUrl' in web.input().keys():
                asset_map = rutils.update_asset_map_with_content_url(rm, asset_map)

            return json.dumps(asset_map)
        except (PermissionDenied, InvalidId) as ex:
            utilities.handle_exceptions(ex)


class AssetContentStream(utilities.BaseClass):
    """
    Get asset content data stream; i.e. return pointer to the file
    api/v2/repository/repositories/<repository_id>/assets/<asset_id>/contents/<content_id>/stream

    GET

    """
    @utilities.allow_cors
    def GET(self, repository_id, asset_id, content_id):
        try:
            rm = rutils.get_repository_manager()
            als = rm.get_asset_lookup_session()
            als.use_federated_repository_view()
            asset = als.get_asset(utilities.clean_id(asset_id))
            asset_content = rutils.get_asset_content_by_id(asset, utilities.clean_id(content_id))
            asset_content_data = asset_content.get_data()

            filespace_path = ''
            try:
                config = asset._runtime.get_configuration()
                parameter_id = utilities.clean_id('parameter:dataStoreFullPath@mongo')
                filespace_path = config.get_value_by_parameter(parameter_id).get_string_value()
            except (AttributeError, KeyError):
                pass

            # the asset_url is relative, so add in the path
            # asset_url = '{0}/{1}'.format(ABS_PATH,
            #                              asset_url)
            asset_content_path = '{0}/{1}'.format(filespace_path,
                                                  asset_content_data.name)
            web.header('Content-Type', mimetypes.guess_type(asset_content_path)[0])
            web.header('Content-Length', os.path.getsize(asset_content_data.name))
            web.header('Content-Disposition', 'inline; filename={0}'.format(os.path.basename(asset_content_data.name)))

            yield asset_content_data.read()
        except (PermissionDenied, NotFound, InvalidId) as ex:
            utilities.handle_exceptions(ex)


class AssetContentsList(utilities.BaseClass):
    @utilities.format_response
    def GET(self, repository_id, asset_id):
        try:
            rm = rutils.get_repository_manager()
            repository = rm.get_repository(utilities.clean_id(repository_id))
            asset = repository.get_asset(utilities.clean_id(asset_id))
            data = utilities.extract_items(asset.get_asset_contents())

            if 'fullUrls' in self.data():
                data = json.dumps(rutils.update_asset_map_with_content_url(rm, asset.object_map)['assetContents'])

            return data
        except (PermissionDenied, InvalidId) as ex:
            utilities.handle_exceptions(ex)

    @utilities.format_response
    def POST(self, repository_id, asset_id):
        try:
            x = web.input(inputFile={})
            rm = rutils.get_repository_manager()
            repository = rm.get_repository(utilities.clean_id(repository_id))
            repository.use_isolated_repository_view()
            asset = repository.get_asset(utilities.clean_id(asset_id))
            # get each set of files individually, because
            # we are doing this in memory, so the file pointer changes
            # once we read in a file
            # https://docs.python.org/2/library/zipfile.html

            params = self.data()
            try:
                input_file = x['inputFile'].file
            except AttributeError:
                asset_content_type_list = rutils.get_asset_content_records(repository)
                form = repository.get_asset_content_form_for_create(asset.ident,
                                                                    asset_content_type_list)
                form = utilities.set_form_basics(form, params)
                asset_content = repository.create_asset_content(form)
            else:
                file_name = x['inputFile'].filename

                # now let's create an asset content for this asset, with the
                # right genus type and file data. Also set the form basics, if passed in
                updated_asset, asset_content = rutils.append_asset_contents(repository, asset, file_name, input_file, params)

            # need to get the updated asset with Contents
            asset_content_map = json.loads(utilities.convert_dl_object(asset_content))
            if 'fullUrl' in params:
                asset_content_map = rutils.update_asset_map_with_content_url(rm, asset_content_map)

            return json.dumps(asset_content_map)
        except (PermissionDenied, InvalidId) as ex:
            utilities.handle_exceptions(ex)


class AssetContentDetails(utilities.BaseClass):
    """
    Get asset content details; or edit asset content
    api/v2/repository/repositories/<repository_id>/assets/<asset_id>/contents/<content_id>

    GET, PUT

    """
    @utilities.format_response
    def GET(self, repository_id, asset_id, content_id):
        try:
            rm = rutils.get_repository_manager()
            repository = rm.get_repository(utilities.clean_id(repository_id))
            asset = repository.get_asset(utilities.clean_id(asset_id))
            asset_contents = asset.get_asset_contents()
            data = {}

            for asset_content in asset_contents:
                if str(asset_content.ident) == str(utilities.clean_id(content_id)):
                    data = asset_content.object_map
                    break

            if 'fullUrl' in self.data():
                contents = rutils.update_asset_map_with_content_url(rm, asset.object_map)['assetContents']
                for content in contents:
                    if content['id'] == str(utilities.clean_id(content_id)):
                        data = content
                        break

            return json.dumps(data)
        except (PermissionDenied, InvalidId) as ex:
            utilities.handle_exceptions(ex)

    @utilities.format_response
    def PUT(self, repository_id, asset_id, content_id):
        """ replace the asset content data ... keep the same name (ugh),
        but hacking this in for the Onyx workflow for CLIx.

        They want to author in Onyx with high-res images but then replace
        them with the right-sized images via a script. So we'll enable
        this endpoint and let the script find / replace the right
        asset content.
        """
        try:
            x = web.input(inputFile={})
            rm = rutils.get_repository_manager()
            als = rm.get_asset_lookup_session()
            als.use_federated_repository_view()
            asset = als.get_asset(utilities.clean_id(asset_id))
            asset_content = rutils.get_asset_content_by_id(asset, utilities.clean_id(content_id))

            repository = rm.get_repository(utilities.clean_id(repository_id))
            repository.use_isolated_repository_view()
            form = repository.get_asset_content_form_for_update(asset_content.ident)

            try:
                input_file = x['inputFile'].file
            except AttributeError:
                pass  # no file included
            else:
                file_name = x['inputFile'].filename

                data = DataInputStream(input_file)
                data.name = file_name

                # default, but can be over-ridden by user params
                form.set_genus_type(rutils.get_asset_content_genus_type(file_name))

                try:
                    form.add_display_name(utilities.create_display_text(file_name))
                except AttributeError:
                    form.display_name = file_name

                form.set_data(data)

            params = self.data()
            form = utilities.set_form_basics(form, params)

            repository.update_asset_content(form)
            return utilities.convert_dl_object(repository.get_asset(asset.ident))
        except (PermissionDenied, NotFound, InvalidId) as ex:
            utilities.handle_exceptions(ex)


class AssetDetails(utilities.BaseClass):
    """
    Get asset details for the given repository
    api/v2/repository/repositories/<repository_id>/assets/<asset_id>

    GET

    """
    @utilities.format_response
    def GET(self, repository_id, asset_id):
        try:
            rm = rutils.get_repository_manager()
            als = rm.get_asset_lookup_session()
            als.use_federated_repository_view()
            data = utilities.convert_dl_object(als.get_asset(utilities.clean_id(asset_id)))

            if 'fullUrls' in self.data().keys():
                data = json.loads(data)

                data = rutils.update_asset_map_with_content_url(rm, data)

                data = json.dumps(data)
            return data
        except (PermissionDenied, NotFound, InvalidId) as ex:
            utilities.handle_exceptions(ex)

    @utilities.format_response
    def PUT(self, repository_id, asset_id):
        try:
            rm = rutils.get_repository_manager()
            repo = rm.get_repository(utilities.clean_id(repository_id))
            form = repo.get_asset_form_for_update(utilities.clean_id(asset_id))

            params = self.data()
            form = utilities.set_form_basics(form, params)

            if 'license' in params.keys():
                form.set_license(params['license'])

            if 'copyright' in params.keys():
                form.set_copyright(params['copyright'])

            return utilities.convert_dl_object(repo.update_asset(form))
        except (PermissionDenied, NotFound, InvalidId) as ex:
            utilities.handle_exceptions(ex)

app_repository = web.application(urls, locals())
# session = utilities.activate_managers(web.session.Session(app_repository,
#                                       web.session.DiskStore('sessions'),
#                                       initializer={
#                                           'am': None,
#                                           'logm': None,
#                                           'rm': None
#                                       }))
