from dlkit_edx import PROXY_SESSION, RUNTIME
from dlkit_edx.proxy_example import TestRequest


def get_logging_manager(session, env):
    if 'HTTP_X_API_PROXY' in env:
        condition = PROXY_SESSION.get_proxy_condition()
        dummy_request = TestRequest(username=env.get('HTTP_X_API_PROXY', 'student@tiss.edu'),
                                    authenticated=True)
        condition.set_http_request(dummy_request)
        proxy = PROXY_SESSION.get_proxy(condition)
        return RUNTIME.get_service_manager('LOGGING',
                                           proxy=proxy)
    else:
        return session._initializer['logm']
