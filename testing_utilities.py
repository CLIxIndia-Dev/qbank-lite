import envoy
import json
import os
import re
import shutil
from unittest import TestCase

from bs4 import Tag, BeautifulSoup
from paste.fixture import TestApp

from authorization.authorization_utilities import create_function_id, create_qualifier_id, create_agent_id

# Note that changing the runtime configs works with testing, but
# trying to change dlkit_configs.configs does not...
import dlkit.runtime.configs
from dlkit.runtime import PROXY_SESSION, RUNTIME
from dlkit.runtime.primordium import Type
from dlkit.runtime.proxy_example import SimpleRequest
from dlkit.runtime.utilities import impl_key_dict
from dlkit.records.registry import LOG_ENTRY_RECORD_TYPES

from urllib import unquote

from main import app


# PROJECT_PATH = os.path.dirname(os.path.abspath(__file__))
# ABS_PATH = os.path.abspath(os.path.join(PROJECT_PATH, os.pardir))
TEST_DATA_STORE_PATH = 'test_datastore'
TEST_STUDENT_RESPONSE_DATA_STORE_PATH = 'test_datastore/studentResponseFiles'
TEST_FIXTURES_PATH = 'tests/fixtures'

TEXT_BLOB_RECORD_TYPE = Type(**LOG_ENTRY_RECORD_TYPES['text-blob'])

BOOTSTRAP_VAULT_GENUS = Type(**{
    'identifier': 'bootstrap-vault',
    'namespace': 'authorization.Vault',
    'authority': 'ODL.MIT.EDU'
})

BASE_IDENTIFIERS = ['ROOT', 24 * '0']

SUPER_USER_AUTHZ_GENUS = Type(**{
    'identifier': 'super-user-authz',
    'namespace': 'authorization.Authorization',
    'authority': 'ODL.MIT.EDU'
})

BASE_AUTHORIZATIONS = (
    ('assessment.Bank', 'lookup', 'assessment.Bank'),
    ('authorization.Vault', 'lookup', 'authorization.Vault'),
    ('commenting.Book', 'lookup', 'commenting.Book'),
    ('hierarchy.Hierarchy', 'lookup', 'hierarchy.Hierarchy'),
    ('learning.ObjectiveBank', 'lookup', 'learning.ObjectiveBank'),
    ('repository.Repository', 'lookup', 'repository.Repository'),
    ('resource.Bin', 'lookup', 'resource.Bin'),
)

SUPER_USER_FUNCTIONS = (
    ('create', 'authorization.Authorization'),
    ('delete', 'authorization.Authorization'),
    ('lookup', 'authorization.Authorization'),
    ('search', 'authorization.Authorization'),
    ('create', 'authorization.Vault'),
    ('delete', 'authorization.Vault'),
    ('search', 'authorization.Vault'),
)

PROXY_USER_FUNCTIONS = (
    ('proxy', 'users.Proxy'),
)

INSTRUCTOR_FUNCTIONS = (
    ('assessment.Answer', 'lookup', 'assessment.Bank'),
    ('assessment.Answer', 'create', 'assessment.Bank'),
    ('assessment.Answer', 'delete', 'assessment.Bank'),
    ('assessment.Answer', 'update', 'assessment.Bank'),
    ('assessment.Assessment', 'author', 'assessment.Bank'),
    ('assessment.Assessment', 'lookup', 'assessment.Bank'),
    ('assessment.Assessment', 'create', 'assessment.Bank'),
    ('assessment.Assessment', 'delete', 'assessment.Bank'),
    ('assessment.Assessment', 'search', 'assessment.Bank'),
    ('assessment.Assessment', 'update', 'assessment.Bank'),
    ('assessment.Assessment', 'take', 'assessment.Bank'),
    ('assessment.AssessmentBank', 'assign', 'assessment.Bank'),
    ('assessment.AssessmentBank', 'lookup', 'assessment.Bank'),
    ('assessment.AssessmentOffered', 'lookup', 'assessment.Bank'),
    ('assessment.AssessmentOffered', 'create', 'assessment.Bank'),
    ('assessment.AssessmentOffered', 'delete', 'assessment.Bank'),
    ('assessment.AssessmentOffered', 'update', 'assessment.Bank'),
    ('assessment.AssessmentResults', 'access', 'assessment.Bank'),
    ('assessment.AssessmentTaken', 'lookup', 'assessment.Bank'),
    ('assessment.AssessmentTaken', 'create', 'assessment.Bank'),
    ('assessment.AssessmentTaken', 'delete', 'assessment.Bank'),
    ('assessment.AssessmentTaken', 'search', 'assessment.Bank'),
    ('assessment.AssessmentTaken', 'update', 'assessment.Bank'),
    ('assessment.Item', 'alias', 'assessment.Bank'),
    ('assessment.Item', 'lookup', 'assessment.Bank'),
    ('assessment.Item', 'create', 'assessment.Bank'),
    ('assessment.Item', 'delete', 'assessment.Bank'),
    ('assessment.Item', 'update', 'assessment.Bank'),
    ('assessment.Item', 'search', 'assessment.Bank'),
    ('assessment.ItemBank', 'assign', 'assessment.Bank'),
    ('assessment.Question', 'lookup', 'assessment.Bank'),
    ('assessment.Question', 'create', 'assessment.Bank'),
    ('assessment.Question', 'delete', 'assessment.Bank'),
    ('assessment.Question', 'update', 'assessment.Bank'),
    ('assessment.Bank', 'access', 'assessment.Bank'),
    ('assessment.Bank', 'alias', 'assessment.Bank'),
    ('assessment.Bank', 'create', 'assessment.Bank'),
    ('assessment.Bank', 'delete', 'assessment.Bank'),
    ('assessment.Bank', 'modify', 'assessment.Bank'),
    ('assessment.Bank', 'search', 'assessment.Bank'),
    ('assessment.Bank', 'update', 'assessment.Bank'),
    ('assessment_authoring.AssessmentPart', 'lookup', 'assessment.Bank'),
    ('assessment_authoring.AssessmentPart', 'create', 'assessment.Bank'),
    ('assessment_authoring.AssessmentPart', 'delete', 'assessment.Bank'),
    ('assessment_authoring.AssessmentPart', 'update', 'assessment.Bank'),
    ('commenting.Book', 'access', 'commenting.Book'),
    ('commenting.Book', 'create', 'commenting.Book'),
    ('commenting.Book', 'delete', 'commenting.Book'),
    ('commenting.Book', 'modify', 'commenting.Book'),
    ('commenting.Book', 'update', 'commenting.Book'),
    ('commenting.Comment', 'author', 'commenting.Book'),
    ('commenting.Comment', 'lookup', 'commenting.Book'),
    ('commenting.Comment', 'create', 'commenting.Book'),
    ('commenting.Comment', 'delete', 'commenting.Book'),
    ('commenting.Comment', 'update', 'commenting.Book'),
    ('hierarchy.Hierarchy', 'update', 'hierarchy.Hierarchy'),
    ('learning.ObjectiveBank', 'create', 'learning.ObjectiveBank'),
    ('learning.ObjectiveBank', 'delete', 'learning.ObjectiveBank'),
    ('learning.ObjectiveBank', 'update', 'learning.ObjectiveBank'),
    ('learning.Proficiency', 'create', 'learning.ObjectiveBank'),
    ('learning.Proficiency', 'delete', 'learning.ObjectiveBank'),
    ('learning.Proficiency', 'lookup', 'learning.ObjectiveBank'),
    ('learning.Proficiency', 'search', 'learning.ObjectiveBank'),
    ('learning.Proficiency', 'update', 'learning.ObjectiveBank'),
    ('logging.Log', 'lookup', 'logging.Log'),
    ('logging.Log', 'create', 'logging.Log'),
    ('logging.Log', 'delete', 'logging.Log'),
    ('logging.Log', 'update', 'logging.Log'),
    ('logging.LogEntry', 'alias', 'logging.Log'),
    ('logging.LogEntry', 'create', 'logging.Log'),
    ('logging.LogEntry', 'delete', 'logging.Log'),
    ('logging.LogEntry', 'lookup', 'logging.Log'),
    ('logging.LogEntry', 'search', 'logging.Log'),
    ('logging.LogEntry', 'update', 'logging.Log'),
    ('repository.Repository', 'access', 'repository.Repository'),
    ('repository.Repository', 'author', 'repository.Repository'),
    ('repository.Repository', 'create', 'repository.Repository'),
    ('repository.Repository', 'delete', 'repository.Repository'),
    ('repository.Repository', 'modify', 'repository.Repository'),
    ('repository.Repository', 'search', 'repository.Repository'),
    ('repository.Repository', 'update', 'repository.Repository'),
    ('repository.Asset', 'author', 'repository.Repository'),
    ('repository.Asset', 'lookup', 'repository.Repository'),
    ('repository.Asset', 'create', 'repository.Repository'),
    ('repository.Asset', 'delete', 'repository.Repository'),
    ('repository.Asset', 'search', 'repository.Repository'),
    ('repository.Asset', 'update', 'repository.Repository'),
    ('repository.AssetComposition', 'access', 'repository.Repository'),
    ('repository.AssetComposition', 'lookup', 'repository.Repository'),
    ('repository.AssetComposition', 'compose', 'repository.Repository'),
    ('repository.AssetRepository', 'assign', 'repository.Repository'),
    ('repository.AssetRepository', 'lookup', 'repository.Repository'),
    ('repository.Composition', 'author', 'repository.Repository'),
    ('repository.Composition', 'lookup', 'repository.Repository'),
    ('repository.Composition', 'create', 'repository.Repository'),
    ('repository.Composition', 'delete', 'repository.Repository'),
    ('repository.Composition', 'search', 'repository.Repository'),
    ('repository.Composition', 'update', 'repository.Repository'),
    ('resource.Bin', 'access', 'resource.Bin'),
    ('resource.Bin', 'author', 'resource.Bin'),
    ('resource.Bin', 'create', 'resource.Bin'),
    ('resource.Bin', 'delete', 'resource.Bin'),
    ('resource.Bin', 'modify', 'resource.Bin'),
    ('resource.Bin', 'update', 'resource.Bin'),
    ('resource.Resource', 'author', 'resource.Bin'),
    ('resource.Resource', 'lookup', 'resource.Bin'),
    ('resource.Resource', 'create', 'resource.Bin'),
    ('resource.Resource', 'delete', 'resource.Bin'),
    ('resource.Resource', 'search', 'resource.Bin'),
    ('resource.Resource', 'update', 'resource.Bin'),
    ('resource.ResourceAgent', 'assign', 'resource.Bin'),
    ('resource.ResourceAgent', 'delete', 'resource.Bin'),
    ('resource.ResourceAgent', 'lookup', 'resource.Bin'),
    ('grading.Gradebook', 'lookup', 'grading.Gradebook'),
    ('grading.Gradebook', 'create', 'grading.Gradebook'),
    ('grading.Gradebook', 'delete', 'grading.Gradebook'),
    ('grading.Gradebook', 'update', 'grading.Gradebook'),
    ('grading.GradeEntry', 'create', 'grading.Gradebook'),
    ('grading.GradeEntry', 'delete', 'grading.Gradebook'),
    ('grading.GradeEntry', 'lookup', 'grading.Gradebook'),
    ('grading.GradeEntry', 'update', 'grading.Gradebook'),
    ('grading.GradeSystem', 'create', 'grading.Gradebook'),
    ('grading.GradeSystem', 'delete', 'grading.Gradebook'),
    ('grading.GradeSystem', 'lookup', 'grading.Gradebook'),
    ('grading.GradeSystem', 'update', 'grading.Gradebook'),
    ('grading.GradebookColumn', 'create', 'grading.Gradebook'),
    ('grading.GradebookColumn', 'delete', 'grading.Gradebook'),
    ('grading.GradebookColumn', 'lookup', 'grading.Gradebook'),
    ('grading.GradebookColumn', 'update', 'grading.Gradebook'),
)

STUDENT_FUNCTIONS = (
    ('assessment.AssessmentTaken', 'create', 'assessment.Bank'),
    ('assessment.AssessmentTaken', 'lookup', 'assessment.Bank'),
    ('assessment.Assessment', 'take', 'assessment.Bank'),
    ('commenting.Comment', 'lookup', 'commenting.Book'),
    ('repository.Asset', 'create', 'repository.Repository'),
    ('repository.Asset', 'delete', 'repository.Repository'),
    ('repository.Asset', 'lookup', 'repository.Repository'),
    ('repository.Asset', 'search', 'repository.Repository'),
    ('resource.Resource', 'lookup', 'resource.Bin'),
)

SUBPACKAGES = (
    ('assessment_authoring', 'assessment'),
)


def configure_dlkit():
    dlkit.runtime.configs.SERVICE = {
        'id': 'dlkit_runtime_bootstrap_configuration',
        'displayName': 'DLKit Runtime Bootstrap Configuration',
        'description': 'Bootstrap Configuration for DLKit Runtime',
        'parameters': {
            'implKey': impl_key_dict('service'),
            'assessmentProviderImpl': {
                'syntax': 'STRING',
                'displayName': 'Assessment Provider Implementation',
                'description': 'Implementation for assessment service provider',
                'values': [
                    {'value': 'TEST_AUTHZ_ADAPTER_1', 'priority': 1}
                ]
            },
            'loggingProviderImpl': {
                'syntax': 'STRING',
                'displayName': 'Logging Provider Implementation',
                'description': 'Implementation for logging service provider',
                'values': [
                    {'value': 'TEST_AUTHZ_ADAPTER_1', 'priority': 1}
                ]
            },
            'repositoryProviderImpl': {
                'syntax': 'STRING',
                'displayName': 'Repository Provider Implementation',
                'description': 'Implementation for repository service provider',
                'values': [
                    {'value': 'TEST_AUTHZ_ADAPTER_1', 'priority': 1}
                ]
            },
            'learningProviderImpl': {
                'syntax': 'STRING',
                'displayName': 'Learning Provider Implementation',
                'description': 'Implementation for learning service provider',
                'values': [
                    {'value': 'TEST_AUTHZ_ADAPTER_1', 'priority': 1}
                ]
            },
            'hierarchyProviderImpl': {
                'syntax': 'STRING',
                'displayName': 'Hierarchy Provider Implementation',
                'description': 'Implementation for hierarchy service provider',
                'values': [
                    {'value': 'TEST_AUTHZ_ADAPTER_1', 'priority': 1}
                ]
            },
            'resourceProviderImpl': {
                'syntax': 'STRING',
                'displayName': 'Resource Provider Implementation',
                'description': 'Implementation for resource service provider',
                'values': [
                    {'value': 'TEST_AUTHZ_ADAPTER_1', 'priority': 1}
                ]
            },
            'authorizationProviderImpl': {
                'syntax': 'STRING',
                'displayName': 'Authorization Provider Implementation',
                'description': 'Implementation for authorization service provider',
                'values': [
                    {'value': 'TEST_AUTHZ_ADAPTER_1', 'priority': 1}
                ]
            },
        }
    }

# Need to do this before importing `app`
# so that the "new" configuration takes. For some reason
# with this testing setup, there is no way to modify
# the settings file post-facto, like with Django
configure_dlkit()


def create_authz(vault, agent, function, qualifier, is_super=False, end_date=None):
    form = vault.get_authorization_form_for_create_for_agent(agent, function, qualifier, [])

    if is_super:
        form.set_genus_type(SUPER_USER_AUTHZ_GENUS)

    if end_date is not None:
        form.set_end_date(end_date)

    return vault.create_authorization(form)


def create_super_authz_authorizations(vault):
    req = get_super_authz_user_request()
    authzm = req['authzm']

    agent_id = authzm.effective_agent_id

    for function_tuple in SUPER_USER_FUNCTIONS:
        function = create_function_id(function_tuple[0],
                                      function_tuple[1])

        create_authz(vault, agent_id, function, vault.ident, is_super=True)


def create_user_authorizations(vault, username="student@tiss.edu", new_catalogs=[]):
    identifiers = BASE_IDENTIFIERS + new_catalogs
    for identifier in identifiers:
        for function_list in [BASE_AUTHORIZATIONS, INSTRUCTOR_FUNCTIONS]:
            for function_tuple in function_list:
                namespace = function_tuple[0]
                function = function_tuple[1]
                catalog = function_tuple[2]

                function_id = create_function_id(function, namespace)
                qualifier_id = create_qualifier_id(identifier, catalog)
                agent_id = create_agent_id(username)
                # print "adding authz: {0}, {1}, {2}".format(str(agent_id), str(function_id), str(qualifier_id))
                create_authz(vault, agent_id, function_id, qualifier_id)

# def create_authz_superuser():
#     original_config = open_up_services_config()
#
#     req = get_super_authz_user_request()
#     authzm = get_session_data(req, 'authzm')
#     vault = create_vault(req)
#
#     create_base_authorizations(vault, authzm.effective_agent_id, is_super=True)
#     create_super_authz_authorizations(vault)
#
#     restore_services_config(original_config)


def create_new_bank():
    # from authorization_utilities import get_vault
    am = get_managers()['am']
    form = am.get_bank_form_for_create([])
    form.display_name = 'an assessment bank'
    form.description = 'for testing with'
    new_bank = am .create_bank(form)

    # from nose.tools import set_trace
    # set_trace()
    # create_user_authorizations(get_vault(),
    #                            username='clix-authz%40tiss.edu',
    #                            new_catalogs=[new_bank.ident.identifier])

    return new_bank


def create_test_repository():
    from authorization.authorization_utilities import get_vault
    rm = get_managers()['rm']
    form = rm.get_repository_form_for_create([])
    form.display_name = 'a repository'
    form.description = 'for testing with'
    # return rm.create_repository(form)
    new_repo = rm.create_repository(form)

    # from nose.tools import set_trace
    # set_trace()
    # create_super_authz_authorizations(get_vault())
    #
    create_user_authorizations(get_vault(),
                               username="student@tiss.edu",
                               new_catalogs=[new_repo.ident.identifier])
    create_user_authorizations(get_vault(), new_catalogs=[new_repo.ident.identifier])

    return new_repo

# don't use test in the name, otherwise the nose test runner thinks this is a test


def get_fixture_bank():
    # from authorization_utilities import get_vault
    am = get_managers()['am']
    fixture_repo = get_fixture_repository()
    return am.get_bank(fixture_repo.ident)

# don't use test in the name, otherwise the nose test runner thinks this is a test


def get_fixture_repository():
    # from authorization_utilities import get_vault
    rm = get_managers()['rm']
    return rm.get_repositories().next()


def get_super_authz_user_request():
    try:
        import settings
    except ImportError:
        authz_user = os.environ.get('AUTHZ_USER')
    else:
        authz_user = settings.AUTHZ_USER
    return get_managers(username=authz_user)


def get_managers(username='student@tiss.edu'):
    managers = [('am', 'ASSESSMENT'),
                ('authzm', 'AUTHORIZATION'),
                ('logm', 'LOGGING'),
                ('rm', 'REPOSITORY')]
    results = {}
    for manager in managers:
        nickname = manager[0]
        service_name = manager[1]
        condition = PROXY_SESSION.get_proxy_condition()
        dummy_request = SimpleRequest(username=username, authenticated=True)
        condition.set_http_request(dummy_request)
        proxy = PROXY_SESSION.get_proxy(condition)
        results[nickname] = RUNTIME.get_service_manager(service_name,
                                                        proxy=proxy)

    return results


def get_valid_contents(tag):
    return [c for c in tag.contents if isinstance(c, Tag) or c.string.strip() != ""]


def update_soup_with_url(text, asset_content):
    soup = BeautifulSoup(u'<wrapper>{0}</wrapper>'.format(text), 'xml')
    media_regex = re.compile('(AssetContent:)')

    media_file_elements = soup.find_all(src=media_regex)
    media_file_elements += soup.find_all(data=media_regex)
    for media_file_element in media_file_elements:
        if 'src' in media_file_element.attrs:
            media_key = 'src'
        else:
            media_key = 'data'

        media_file_element[media_key] = asset_content.get_url()

    return soup.wrapper.renderContents()


class BaseTestCase(TestCase):
    @staticmethod
    def _filename(file_object):
        return file_object.name.split('/')[-1]

    @staticmethod
    def _label(text):
        return text.replace('.', '_')

    def code(self, _req, _code):
        self.assertEqual(_req.status, _code)

    def create_new_log(self):
        logm = get_managers()['logm']
        form = logm.get_log_form_for_create([])
        form.display_name = 'my new log'
        form.description = 'for testing with'
        return logm.create_log(form)

    def created(self, _req):
        self.code(_req, 201)

    def deleted(self, _req):
        self.code(_req, 202)

    def json(self, _req):
        return json.loads(_req.body)

    def message(self, _req, _msg):
        self.assertIn(_msg, str(_req.body))

    def ok(self, _req):
        self.assertEqual(_req.status, 200)

    def setUp(self):
        middleware = []
        self.app = TestApp(app.wsgifunc(*middleware))

        envoy.run('mongo test_qbank_lite_assessment --eval "db.dropDatabase()"')
        envoy.run('mongo test_qbank_lite_assessment_authoring --eval "db.dropDatabase()"')
        envoy.run('mongo test_qbank_lite_hierarchy --eval "db.dropDatabase()"')
        envoy.run('mongo test_qbank_lite_authorization --eval "db.dropDatabase()"')
        envoy.run('mongo test_qbank_lite_id --eval "db.dropDatabase()"')
        envoy.run('mongo test_qbank_lite_logging --eval "db.dropDatabase()"')
        envoy.run('mongo test_qbank_lite_relationship --eval "db.dropDatabase()"')
        envoy.run('mongo test_qbank_lite_repository --eval "db.dropDatabase()"')

        envoy.run('mongorestore --db test_qbank_lite_authorization --drop tests/fixtures/test_qbank_lite_authorization')
        envoy.run('mongorestore --db test_qbank_lite_repository --drop tests/fixtures/test_qbank_lite_repository')
        if os.path.isdir(TEST_DATA_STORE_PATH):
            shutil.rmtree(TEST_DATA_STORE_PATH)

        if not os.path.isdir(TEST_DATA_STORE_PATH):
            os.makedirs(TEST_DATA_STORE_PATH)

        # copy over the test fixture data from tests/fixtures
        shutil.copytree('{0}/authorization'.format(TEST_FIXTURES_PATH),
                        '{0}/authorization'.format(TEST_DATA_STORE_PATH))
        # shutil.copytree('{0}/assessment'.format(TEST_FIXTURES_PATH),
        #                 '{0}/assessment'.format(TEST_DATA_STORE_PATH))
        shutil.copytree('{0}/repository'.format(TEST_FIXTURES_PATH),
                        '{0}/repository'.format(TEST_DATA_STORE_PATH))

        self._bank = get_fixture_bank()

    def setup_entry(self, log_id, data):
        logm = get_managers()['logm']

        log = logm.get_log(log_id)

        form = log.get_log_entry_form_for_create([TEXT_BLOB_RECORD_TYPE])
        form.set_text(data)

        new_entry = log.create_log_entry(form)

        return new_entry

    def tearDown(self):
        shutil.rmtree(TEST_DATA_STORE_PATH)
        envoy.run('mongo test_qbank_lite_assessment --eval "db.dropDatabase()"')
        envoy.run('mongo test_qbank_lite_assessment_authoring --eval "db.dropDatabase()"')
        envoy.run('mongo test_qbank_lite_hierarchy --eval "db.dropDatabase()"')
        envoy.run('mongo test_qbank_lite_authorization --eval "db.dropDatabase()"')
        envoy.run('mongo test_qbank_lite_id --eval "db.dropDatabase()"')
        envoy.run('mongo test_qbank_lite_logging --eval "db.dropDatabase()"')
        envoy.run('mongo test_qbank_lite_relationship --eval "db.dropDatabase()"')
        envoy.run('mongo test_qbank_lite_repository --eval "db.dropDatabase()"')

    def upload_media_file(self, file_handle):
        url = '/api/v1/repository/repositories/{0}/assets'.format(unquote(str(self._bank.ident)))
        file_handle.seek(0)
        req = self.app.post(url,
                            upload_files=[('inputFile',
                                           self._filename(file_handle),
                                           file_handle.read())])
        self.ok(req)
        data = self.json(req)
        return data
