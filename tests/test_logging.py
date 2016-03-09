import os
import json
import shutil

from copy import deepcopy

from dlkit_edx.primordium import Id, Type
from nose.tools import *
from paste.fixture import TestApp, AppError
from records.registry import LOG_ENTRY_RECORD_TYPES
from unittest import TestCase

from dlkit_edx import PROXY_SESSION, RUNTIME
from dlkit_edx.proxy_example import TestRequest
from dlkit_edx.utilities import impl_key_dict
import dlkit_edx.configs


PROJECT_PATH = os.path.dirname(os.path.abspath(__file__))
ABS_PATH = os.path.abspath(os.path.join(PROJECT_PATH, os.pardir))
TEST_DATA_STORE = ABS_PATH + '/test_datastore'

TEXT_BLOB_RECORD_TYPE = Type(**LOG_ENTRY_RECORD_TYPES['text-blob'])

def configure_dlkit():
    dlkit_edx.configs.FILESYSTEM_1 = {
        'id': 'filesystem_configuration_1',
        'displayName': 'Filesystem Configuration',
        'description': 'Configuration for Filesystem Implementation',
        'parameters': {
            'implKey': impl_key_dict('filesystem'),
            'dataStorePath': {
                'syntax': 'STRING',
                'displayName': 'Path to local filesystem datastore',
                'description': 'Filesystem path for setting the MongoClient host.',
                'values': [
                    {'value': TEST_DATA_STORE, 'priority': 1}
                ]
            },
            'recordsRegistry': {
                'syntax': 'STRING',
                'displayName': 'Python path to the extension records registry file',
                'description': 'dot-separated path to the extension records registry file',
                'values': [
                    {'value': 'records.registry', 'priority': 1}
                ]
            },
        }
    }

configure_dlkit()

from main import app


def create_test_bank():
    am = get_managers()['am']
    form = am.get_bank_form_for_create([])
    form.display_name = 'an assessment bank'
    form.description = 'for testing with'
    return am.create_bank(form)

def get_managers():
    managers = [('am', 'ASSESSMENT'),
                ('logm', 'LOGGING')]
    results = {}
    for manager in managers:
        nickname = manager[0]
        service_name = manager[1]
        condition = PROXY_SESSION.get_proxy_condition()
        dummy_request = TestRequest(username='student@tiss.edu', authenticated=True)
        condition.set_http_request(dummy_request)
        proxy = PROXY_SESSION.get_proxy(condition)
        results[nickname] = RUNTIME.get_service_manager(service_name,
                                                        proxy=proxy)
    return results


class BaseTestCase(TestCase):
    """
    """
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
        configure_dlkit()
        middleware = []
        self.app = TestApp(app.wsgifunc(*middleware))
        self.url = '/api/v1/logging'

        if not os.path.isdir(TEST_DATA_STORE):
            os.makedirs(TEST_DATA_STORE)
        shutil.rmtree(TEST_DATA_STORE)

    def setup_entry(self, log_id, data):
        logm = get_managers()['logm']

        log = logm.get_log(log_id)

        form = log.get_log_entry_form_for_create([TEXT_BLOB_RECORD_TYPE])
        form.set_text(data)

        new_entry = log.create_log_entry(form)

        return new_entry

    def tearDown(self):
        shutil.rmtree(TEST_DATA_STORE)


class BasicServiceTests(BaseTestCase):
    """Test the views for getting the basic service calls

    """
    def setUp(self):
        super(BasicServiceTests, self).setUp()

    def tearDown(self):
        super(BasicServiceTests, self).tearDown()

    def test_users_can_get_list_of_logs(self):
        url = self.url + '/logs'
        req = self.app.get(url)
        self.ok(req)
        self.message(req, '[]')


class LogCrUDTests(BaseTestCase):
    """Test the views for log crud

    """
    def num_logs(self, val):
        logm = get_managers()['logm']

        self.assertEqual(
            logm.logs.available(),
            val
        )

    def setUp(self):
        super(LogCrUDTests, self).setUp()
        # also need a test assessment bank here to do orchestration with
        self.assessment_bank = create_test_bank()
        self.bad_log_id = 'assessment.Bank%3A55203f0be7dde0815228bb41%40ODL.MIT.EDU'
        self.url += '/logs'

    def tearDown(self):
        super(LogCrUDTests, self).tearDown()

    def test_can_create_new_log(self):
        self.num_logs(0)
        payload = {
            'name': 'my new log',
            'description': 'for testing with'
        }
        req = self.app.post(self.url,
                            params=json.dumps(payload),
                            headers={'content-type': 'application/json'})
        self.ok(req)
        log = self.json(req)
        self.assertEqual(
            log['displayName']['text'],
            payload['name']
        )
        self.assertEqual(
            log['description']['text'],
            payload['description']
        )
        self.num_logs(1)

    def test_can_create_orchestrated_log_with_default_attributes(self):
        self.num_logs(0)
        payload = {
            'bankId': str(self.assessment_bank.ident)
        }
        req = self.app.post(self.url,
                            params=json.dumps(payload),
                            headers={'content-type': 'application/json'})
        self.ok(req)
        log = self.json(req)
        self.assertEqual(
            log['displayName']['text'],
            'Orchestrated assessment Log'
        )
        self.assertEqual(
            log['description']['text'],
            'Orchestrated Log for the assessment service'
        )
        self.assertEqual(
            self.assessment_bank.ident.identifier,
            Id(log['id']).identifier
        )
        self.num_logs(1)

    def test_can_create_orchestrated_log_and_set_attributes(self):
        payload = {
            'bankId': str(self.assessment_bank.ident),
            'name': 'my new orchestra',
            'description': 'for my assessment bank'
        }
        req = self.app.post(self.url,
                            params=json.dumps(payload),
                            headers={'content-type': 'application/json'})
        self.ok(req)
        log = self.json(req)
        self.assertEqual(
            log['displayName']['text'],
            payload['name']
        )
        self.assertEqual(
            log['description']['text'],
            payload['description']
        )
        self.assertEqual(
            self.assessment_bank.ident.identifier,
            Id(log['id']).identifier
        )

    def test_missing_parameters_throws_exception_on_create(self):
        self.num_logs(0)

        basic_payload = {
            'name': 'my new log',
            'description': 'for testing with'
        }
        blacklist = ['name', 'description']

        for item in blacklist:
            payload = deepcopy(basic_payload)
            del payload[item]

            self.assertRaises(AppError,
                              self.app.post,
                              self.url,
                              params=json.dumps(payload),
                              headers={'content-type': 'application/json'})

        self.num_logs(0)

    def test_can_get_log_details(self):
        log = self.create_new_log()
        url = self.url + '/' + str(log.ident)
        req = self.app.get(url)
        self.ok(req)
        log_details = self.json(req)

        for attr, val in log.object_map.iteritems():
            self.assertEqual(
                val,
                log_details[attr]
            )

    def test_invalid_log_id_throws_exception(self):
        self.create_new_log()
        url = self.url + '/x'
        self.assertRaises(AppError, self.app.get, url)

    def test_bad_log_id_throws_exception(self):
        self.create_new_log()
        url = self.url + '/' + self.bad_log_id
        self.assertRaises(AppError, self.app.get, url)

    def test_can_delete_log(self):
        self.num_logs(0)
        log = self.create_new_log()

        self.num_logs(1)

        url = self.url + '/' + str(log.ident)
        req = self.app.delete(url)
        self.deleted(req)

        self.num_logs(0)

    def test_trying_to_delete_log_with_log_entries_throws_exception(self):
        self.num_logs(0)

        log = self.create_new_log()
        self.setup_entry(log.ident, 'foo')

        self.num_logs(1)

        url = self.url + '/' + str(log.ident)
        self.assertRaises(AppError, self.app.delete, url)

        self.num_logs(1)

    def test_trying_to_delete_log_with_invalid_id_throws_exception(self):
        self.num_logs(0)

        self.create_new_log()

        self.num_logs(1)

        url = self.url + '/' + self.bad_log_id
        self.assertRaises(AppError, self.app.delete, url)

        self.num_logs(1)

    def test_can_update_log(self):
        self.num_logs(0)

        log = self.create_new_log()

        self.num_logs(1)

        url = self.url + '/' + str(log.ident)

        test_cases = [('name', 'a new name'),
                      ('description', 'foobar')]
        for case in test_cases:
            payload = {
                case[0]: case[1]
            }
            req = self.app.put(url,
                               params=json.dumps(payload),
                               headers={'content-type': 'application/json'})
            self.ok(req)
            updated_log = self.json(req)

            if case[0] == 'name':
                self.assertEqual(
                    updated_log['displayName']['text'],
                    case[1]
                )
            else:
                self.assertEqual(
                    updated_log['description']['text'],
                    case[1]
                )

        self.num_logs(1)

    def test_update_with_invalid_id_throws_exception(self):
        self.num_logs(0)

        self.create_new_log()

        self.num_logs(1)

        url = self.url + '/' + self.bad_log_id

        test_cases = [('name', 'a new name'),
                      ('description', 'foobar')]
        for case in test_cases:
            payload = {
                case[0]: case[1]
            }
            self.assertRaises(AppError,
                              self.app.put,
                              url,
                              params=json.dumps(payload),
                              headers={'content-type': 'application/json'})

        self.num_logs(1)

    def test_update_with_no_params_throws_exception(self):
        self.num_logs(0)

        log = self.create_new_log()

        self.num_logs(1)

        url = self.url + '/' + str(log.ident)

        test_cases = [('foo', 'bar'),
                      ('bankId', 'foobar')]
        for case in test_cases:
            payload = {
                case[0]: case[1]
            }
            self.assertRaises(AppError,
                              self.app.put,
                              url,
                              params=json.dumps(payload),
                              headers={'content-type': 'application/json'})

        self.num_logs(1)
        req = self.app.get(url)
        log_fresh = self.json(req)

        log_map = log.object_map
        params_to_test = ['id', 'displayName', 'description']
        for param in params_to_test:
            self.assertEqual(
                log_map[param],
                log_fresh[param]
            )


class LogEntryCrUDTests(BaseTestCase):
    """Test the views for log entries crud

    """
    def num_entries(self, val):
        logm = get_managers()['logm']

        log = logm.get_log(self.log.ident)
        self.assertEqual(
            log.get_log_entries().available(),
            val
        )

    def setUp(self):
        super(LogEntryCrUDTests, self).setUp()
        self.bad_log_id = 'assessment.Bank%3A55203f0be7dde0815228bb41%40bazzim.MIT.EDU'
        self.log = self.create_new_log()
        self.url += '/logs/{0}/logentries'.format(str(self.log.ident))

    def tearDown(self):
        super(LogEntryCrUDTests, self).tearDown()

    def test_can_get_log_entries(self):
        self.num_entries(0)
        self.setup_entry(self.log.ident, 'foo')
        self.num_entries(1)

        req = self.app.get(self.url)
        self.ok(req)
        entries = self.json(req)
        self.assertEqual(
            len(entries),
            1
        )
        self.assertEqual(
            entries[0]['text']['text'],
            'foo'
        )

    def test_can_create_log_entry(self):
        self.num_entries(0)
        payload = {
            'data': json.dumps({"actor": "agentId"})
        }

        req = self.app.post(self.url,
                            params=json.dumps(payload),
                            headers={'content-type': 'application/json'})
        self.ok(req)
        
        data = self.json(req)
        self.assertEqual(
            data['text']['text'],
            payload['data']
        )
        self.num_entries(1)

    def test_creating_log_entry_requires_data_parameter(self):
        self.num_entries(0)

        payload = {
            'foo': json.dumps({"actor": "agentId"})
        }

        self.assertRaises(AppError,
                          self.app.post,
                          self.url,
                          params=json.dumps(payload),
                          headers={'content-type': 'application/json'})

    def test_can_update_log_entry(self):
        self.num_entries(0)
        entry = self.setup_entry(self.log.ident, "foo")

        url = '{0}/{1}'.format(self.url,
                               str(entry.ident))

        test_cases = [
            {'data': json.dumps({"baz": "zim"})}
        ]

        for payload in test_cases:
            req = self.app.put(url,
                               params=json.dumps(payload),
                               headers={'content-type': 'application/json'})
            self.ok(req)

            data = self.json(req)

            self.assertEqual(
                data['id'],
                str(entry.ident)
            )
            key = payload.keys()[0]
            if key == 'data':
                self.assertEqual(
                    data['text']['text'],
                    payload[key]
                )
            else:
                self.assertEqual(
                    data[key],
                    payload[key]
                )

        self.num_entries(1)

    def test_can_delete_log_entry(self):
        self.num_entries(0)
        entry = self.setup_entry(self.log.ident, "foo")

        self.num_entries(1)

        url = '{0}/{1}/'.format(self.url,
                                str(entry.ident))

        req = self.app.delete(url)
        self.deleted(req)

        self.num_entries(0)

