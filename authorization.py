from bson.errors import InvalidId

from django.template import RequestContext
from django.shortcuts import render_to_response

from rest_framework.response import Response
from rest_framework.permissions import AllowAny

from dlkit_runtime.errors import PermissionDenied, InvalidArgument, IllegalState, NotFound
from dlkit_runtime.primitives import DateTime

from qbank.views import DLKitSessionsManager
from utilities import authorization as authzutils
from utilities import general as gutils
from utilities import resource as resutils
from utilities import testing as testutils


class Documentation(DLKitSessionsManager):
    """
    Shows the user documentation for talking to the RESTful service
    """
    permission_classes = (AllowAny,)

    def get(self, request, format=None):
        return render_to_response('authorization/documentation.html',
                                  {},
                                  RequestContext(request))


class VaultAuthorizationDetails(DLKitSessionsManager):
    """
    Get qualifier details
    api/v2/authorization/authorizations/<authorization_id>/

    GET, DELETE
    DELETE to remove the authorization.
    """
    def delete(self, request, authorization_id, format=None):
        try:
            vault = authzutils.get_vault(request)

            authzutils.check_authz_on_authz(vault, authorization_id)

            vault.delete_authorization(gutils.clean_id(authorization_id))

            return gutils.DeletedResponse()
        except (PermissionDenied, InvalidArgument, IllegalState) as ex:
            gutils.handle_exceptions(ex)

    def get(self, request, authorization_id, format=None):
        try:
            vault = authzutils.get_vault(request)

            authzutils.check_authz_on_authz(vault, authorization_id)

            authorization = vault.get_authorization(gutils.clean_id(authorization_id))
            authorization_map = authorization.object_map

            authorization_map.update({
                '_links': {
                    'self': gutils.build_safe_uri(request),
                }
            })

            return Response(authorization_map)
        except (PermissionDenied, NotFound) as ex:
            gutils.handle_exceptions(ex)


class VaultAuthorizationsList(DLKitSessionsManager):
    """
    Get or add qualifiers to a vault
    api/v2/authorization/authorizations/

    GET, POST
    GET to view current authorizations.
    POST to create a new authorization
      * allowed functions (may depend on the catalog / service):
          assign
          create
          delete
          lookup
          search
          update

    Note that for RESTful calls, you need to set the request header
    'content-type' to 'application/json'

    Example (note the use of double quotes!!):
        To grant a student ability to lookup assessment Items in a specific bank:
       {
         "functionId": "assessment.Item%3Alookup%40ODL.MIT.EDU",
         "qualifierId": "assessment.Bank%3A56f96d10c522067a550e5099%40bazzim.MIT.EDU",
         "agentId": "student@mit.edu"
       }

       To create bulk authorizations:
       {
         "bulk": [
           {
             "functionId": "assessment.Item%3Alookup%40ODL.MIT.EDU",
             "qualifierId": "assessment.Bank%3A56f96d10c522067a550e5099%40bazzim.MIT.EDU",
             "agentId": "student@mit.edu"
           },
           {
             "functionId": "assessment.Item%3Acreate%40ODL.MIT.EDU",
             "qualifierId": "assessment.Bank%3A56f96d10c522067a550e5099%40bazzim.MIT.EDU",
             "agentId": "student@mit.edu"
           }
         ]
       }
    """
    def get(self, request, format=None):
        try:
            vault = authzutils.get_vault(request)
            supported_query_params = ['qualifierId', 'functionId', 'agentId']
            if (len(self.data) > 0 and
                    any(p in self.data for p in supported_query_params)):
                querier = vault.get_authorization_query()

                if 'qualifierId' in self.data:
                    querier.match_qualifier_id(gutils.clean_id(self.data['qualifierId']), True)

                if 'functionId' in self.data:
                    querier.match_function_id(gutils.clean_id(self.data['functionId']), True)

                if 'agentId' in self.data:
                    querier.match_agent_id(resutils.get_agent_id(self.data['agentId']), True)

                querier.match_genus_type(testutils.SUPER_USER_AUTHZ_GENUS, False)
                authorizations = vault.get_authorizations_by_query(querier)
            else:
                authorizations = authzutils.get_non_super_authz(vault)
            data = gutils.extract_items(request, authorizations)

            return Response(data)
        except (PermissionDenied, NotFound) as ex:
            gutils.handle_exceptions(ex)

    def post(self, request, format=None):
        try:
            vault = authzutils.get_vault(request)
            if 'bulk' in self.data:
                data = []
                for authz_tuple in self.data['bulk']:
                    agent_id = resutils.get_agent_id(authz_tuple['agentId'])
                    function_id = gutils.clean_id(authz_tuple['functionId'])
                    qualifier_id = gutils.clean_id(authz_tuple['qualifierId'])
                    end_date = None
                    if 'endDate' in authz_tuple:
                        end_date = DateTime(**authz_tuple['endDate'])
                    data.append(gutils.convert_dl_object(testutils.create_authz(vault,
                                                                                agent_id,
                                                                                function_id,
                                                                                qualifier_id,
                                                                                end_date=end_date)))
            else:
                gutils.verify_keys_present(self.data, ['qualifierId', 'functionId', 'agentId'])

                agent_id = resutils.get_agent_id(self.data['agentId'])
                function_id = gutils.clean_id(self.data['functionId'])
                qualifier_id = gutils.clean_id(self.data['qualifierId'])
                end_date = None
                if 'endDate' in self.data:
                    end_date = DateTime(**self.data['endDate'])
                data = gutils.convert_dl_object(testutils.create_authz(vault,
                                                                       agent_id,
                                                                       function_id,
                                                                       qualifier_id,
                                                                       end_date=end_date))

            gutils.clear_cache()

            return gutils.CreatedResponse(data)
        except (PermissionDenied, InvalidArgument, KeyError) as ex:
            gutils.handle_exceptions(ex)


class AuthorizationService(DLKitSessionsManager):
    """
    List all available authorization services.
    api/v2/authorization/
    """

    def get(self, request, format=None):
        """
        List all available authorization services.
        """
        data = {}
        data = gutils.add_links(request,
                                data,
                                {
                                    'authorizations': 'authorizations/',
                                    'documentation': 'docs/'
                                })
        return Response(data)

