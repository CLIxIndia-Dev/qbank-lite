import os
import web

from dlkit_edx.errors import *

import repository_utilities as rutils
import utilities


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
            repositories = session._initializer['rm'].repositories
            repositories = utilities.extract_items(repositories)
            return repositories
        except PermissionDenied as ex:
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
            repository = session._initializer['rm'].get_repository(utilities.clean_id(repository_id))
            repository = utilities.convert_dl_object(repository)
            return repository
        except (PermissionDenied, NotFound) as ex:
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

            repository = session._initializer['rm'].get_repository(utilities.clean_id(repository_id))
            assets = repository.get_assets()
            data = utilities.extract_items(assets)

            return data
        except PermissionDenied as ex:
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
            repository = session._initializer['rm'].get_repository(utilities.clean_id(repository_id))
            asset = repository.get_asset(utilities.clean_id(asset_id))
            asset_content = rutils.get_asset_content_by_id(asset, utilities.clean_id(content_id))
            web.header('Content-Length', os.path.getsize(asset_content.get_url()))
            filename = asset_content.get_url().split('/')[-1]
            web.header('Content-Disposition', 'inline; filename={0}'.format(filename))

            with open(asset_content.get_url(), 'r') as ac_file:
                yield ac_file.read()
        except (PermissionDenied, NotFound) as ex:
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
            repository = session._initializer['rm'].get_repository(utilities.clean_id(repository_id))
            data = utilities.convert_dl_object(repository.get_asset(utilities.clean_id(asset_id)))
            return data
        except (PermissionDenied, NotFound) as ex:
            utilities.handle_exceptions(ex)

app_repository = web.application(urls, locals())
session = utilities.activate_managers(web.session.Session(app_repository,
                                      web.session.DiskStore('sessions'),
                                      initializer={
                                          'am': None,
                                          'logm': None,
                                          'rm': None
                                      }))