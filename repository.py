import mimetypes
import os
import sys
import web

from bson.errors import InvalidId

from dlkit_edx.errors import *
from dlkit_edx.primitives import DataInputStream

import repository_utilities as rutils
import utilities


if getattr(sys, 'frozen', False):
    ABS_PATH = os.path.dirname(sys.executable)
else:
    PROJECT_PATH = os.path.dirname(os.path.abspath(__file__))
    ABS_PATH = '{0}/qbank-lite'.format(os.path.abspath(os.path.join(PROJECT_PATH, os.pardir)))


urls = (
    "/repositories/(.*)/assets/(.*)/contents/(.*)", "AssetContentDetails",
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

    GET

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

            return data
        except (PermissionDenied, InvalidId) as ex:
            utilities.handle_exceptions(ex)

    @utilities.format_response
    def POST(self, repository_id):
        try:
            x = web.input(inputFile={})
            rm = rutils.get_repository_manager()
            repository = rm.get_repository(utilities.clean_id(repository_id))
            # get each set of files individually, because
            # we are doing this in memory, so the file pointer changes
            # once we read in a file
            # https://docs.python.org/2/library/zipfile.html

            input_file = x['inputFile'].file
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
            querier = repository.get_asset_query()
            querier.match_display_name(rutils.get_singular_filename(file_name), match=True)
            assets = repository.get_assets_by_query(querier)
            if assets.available() > 0:
                asset = assets.next()
            else:
                asset = rutils.create_asset(repository, file_name)

            # now let's create an asset content for this asset, with the
            # right genus type and file data
            rutils.append_asset_contents(repository, asset, file_name, input_file)
            return utilities.convert_dl_object(repository.get_asset(asset.ident))
        except (PermissionDenied, InvalidId) as ex:
            utilities.handle_exceptions(ex)


class AssetContentDetails(utilities.BaseClass):
    """
    Get asset content details; i.e. return pointer to the file
    api/v2/repository/repositories/<repository_id>/assets/<asset_id>/contents/<content_id>

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
            asset_url = asset_content.get_url()

            # the asset_url is relative, so add in the path
            asset_url = '{0}/{1}'.format(ABS_PATH,
                                         asset_url)

            web.header('Content-Type', mimetypes.guess_type(asset_url))
            web.header('Content-Length', os.path.getsize(asset_url))
            filename = asset_url.split('/')[-1]
            web.header('Content-Disposition', 'inline; filename={0}'.format(filename))

            with open(asset_url, 'rb') as ac_file:
                yield ac_file.read()
        except (PermissionDenied, NotFound, InvalidId) as ex:
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

            input_file = x['inputFile'].file
            file_name = x['inputFile'].filename
            repository = rm.get_repository(utilities.clean_id(repository_id))
            form = repository.get_asset_content_form_for_update(asset_content.ident)

            data = DataInputStream(input_file)
            data.name = file_name

            form.set_genus_type(rutils.get_asset_content_genus_type(file_name))
            form.display_name = file_name

            form.set_data(data)

            repository.update_asset_content(form)
            return utilities.convert_dl_object(repository.get_asset(asset.ident))
        except (PermissionDenied, NotFound, InvalidId) as ex:
            utilities.handle_exceptions(ex)


class AssetDetails(utilities.BaseClass):
    """
    Get asset details for the given repository
    api/v2/repository/repositories/<repository_id>/assets/<asset_id>/

    GET

    """
    @utilities.format_response
    def GET(self, repository_id, asset_id):
        try:
            rm = rutils.get_repository_manager()
            als = rm.get_asset_lookup_session()
            als.use_federated_repository_view()
            data = utilities.convert_dl_object(als.get_asset(utilities.clean_id(asset_id)))
            return data
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