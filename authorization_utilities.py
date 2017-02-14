from dlkit_runtime.errors import PermissionDenied
from dlkit_runtime.primitives import Id

from utilities import clean_id


def allow_user_to_add_authorizations(vault, username):
    from testing_utilities import create_authz

    qualifiers = ('ROOT', 24 * '0')

    for root_qualifier in qualifiers:
        qualifier_id = create_qualifier_id(root_qualifier,
                                           'authorization.Vault',
                                           authority='ODL.MIT.EDU')
        function_id = create_function_id('lookup', 'authorization.Vault')
        create_authz(vault, create_agent_id(username), function_id, qualifier_id, is_super=True)

    functions = ['create', 'lookup', 'delete', 'update', 'search']
    for function in functions:
        function_id = create_function_id(function, 'authorization.Authorization')

        create_authz(vault, create_agent_id(username), function_id, vault.ident)


def check_authz_on_authz(vault, authorization_id):
    # make sure that someone is not trying to delete
    # a hidden, "super" authorization
    from testing_utilities import SUPER_USER_AUTHZ_GENUS
    querier = vault.get_authorization_query()
    querier.match_id(clean_id(authorization_id), True)
    querier.match_genus_type(SUPER_USER_AUTHZ_GENUS, False)

    if vault.get_authorizations_by_query(querier).available() == 0:
        raise PermissionDenied


def create_agent_id(username, authority='MIT-ODL'):
    return Id(identifier=username,
              namespace='osid.agent.Agent',
              authority=authority)


def create_function_id(function, namespace):
    return Id(identifier=function,
              namespace=namespace,
              authority='ODL.MIT.EDU')


def create_qualifier_id(identifier, namespace, authority='ODL.MIT.EDU'):
    if identifier == 'ROOT':
        authority = 'ODL.MIT.EDU'
    return Id(identifier=identifier,
              namespace=namespace,
              authority=authority)


def create_vault(request):
    from testing_utilities import BOOTSTRAP_VAULT_GENUS
    authzm = request['authzm']
    form = authzm.get_vault_form_for_create([])
    form.display_name = "System Vault"
    form.description = "Created during bootstrapping"
    form.set_genus_type(BOOTSTRAP_VAULT_GENUS)
    return authzm.create_vault(form)


def get_non_super_authz(vault):
    from testing_utilities import SUPER_USER_AUTHZ_GENUS
    querier = vault.get_authorization_query()
    querier.match_genus_type(SUPER_USER_AUTHZ_GENUS, False)
    return vault.get_authorizations_by_query(querier)


def get_vault():
    from testing_utilities import get_super_authz_user_request
    from testing_utilities import BOOTSTRAP_VAULT_GENUS
    request = get_super_authz_user_request()

    authzm = request['authzm']
    vaults = authzm.get_vaults_by_genus_type(BOOTSTRAP_VAULT_GENUS)
    if vaults.available() > 0:
        return vaults.next()
    else:
        return create_vault(request)

# def user_can_proxy(user, proxy_username, request):
#     path = request.path
#     if proxy_username is None:
#         return True
#
#     if proxy_username == user.username:
#         return True
#
#     # check against the catalog
#     aqs = get_authz_query_session()
#     function_id = create_function_id('proxy', 'users.Proxy')
#
#     potential_bank = get_object_bank_from_request(request)
#     if potential_bank is not None:
#         qualifier_id = potential_bank.ident
#     else:
#         request_kwargs = resolve(path)[2]
#         catalog_types = ['bank', 'repository', 'bin', 'gradebook', 'log']
#         if any(['{0}_id'.format(c) in request_kwargs
#                 for c in catalog_types]):
#             catalog_name = [c for c in catalog_types if '{0}_id'.format(c) in request_kwargs][0]
#             # assume first match
#             qualifier_id = clean_id(request_kwargs['{0}_id'.format(catalog_name)])
#         else:
#             qualifier_id = create_qualifier_id('ROOT',
#                                                'users.Proxy',
#                                                authority='ODL.MIT.EDU')
#
#     return aqs.is_authorized(
#         agent_id=create_agent_id(user.username),
#         function_id=function_id,
#         qualifier_id=qualifier_id)

# def user_has_authz(user):
#     aqs = get_authz_query_session()
#
#     querier = aqs.get_authorization_query()
#     querier.match_agent_id(create_agent_id(user.username), True)
#
#     return aqs.get_authorizations_by_query(querier).available() > 0
