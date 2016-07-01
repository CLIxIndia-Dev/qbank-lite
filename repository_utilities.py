from dlkit_edx import PROXY_SESSION, RUNTIME
from dlkit_edx.proxy_example import TestRequest


def get_asset_content_by_id(asset, asset_content_id):
    for asset_content in asset.get_asset_contents():
        if str(asset_content_id) == str(asset_content.ident):
            return asset_content
    return None

def get_repository_manager(session, env):
    if 'HTTP_X_API_PROXY' in env:
        condition = PROXY_SESSION.get_proxy_condition()
        dummy_request = TestRequest(username=env.get('HTTP_X_API_PROXY', 'student@tiss.edu'),
                                    authenticated=True)
        condition.set_http_request(dummy_request)
        proxy = PROXY_SESSION.get_proxy(condition)
        return RUNTIME.get_service_manager('REPOSITORY',
                                           proxy=proxy)
    else:
        return session._initializer['rm']
