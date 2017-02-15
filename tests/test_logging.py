import json

from copy import deepcopy

from dlkit_runtime.primordium import Id

from paste.fixture import AppError

from urllib import quote

from testing_utilities import BaseTestCase, get_managers, get_fixture_bank


def osid_agent(name):
    return 'osid.agent.Agent%3A{0}%40MIT-ODL'.format(quote(quote(name)))


class BaseLoggingTestCase(BaseTestCase):
    def setUp(self):
        super(BaseLoggingTestCase, self).setUp()
        self.url = '/api/v1/logging'

    def tearDown(self):
        super(BaseLoggingTestCase, self).tearDown()


class BasicServiceTests(BaseLoggingTestCase):
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


class LogCrUDTests(BaseLoggingTestCase):
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
        self.assessment_bank = get_fixture_bank()
        self.bad_log_id = 'assessment.Bank%3A55203f0be7dde0815228bb41%40ODL.MIT.EDU'
        self.url += '/logs'

    def tearDown(self):
        super(LogCrUDTests, self).tearDown()

    def test_can_create_new_log(self):
        self.num_logs(0)
        payload = {
            'name': 'my new log',
            'description': 'for testing with',
            'genusTypeId': 'log-genus-type%3Adefault-log%40ODL.MIT.EDU'
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
        self.ok(req)
        data = self.json(req)
        self.assertTrue(data['success'])

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


class LogEntryCrUDTests(BaseLoggingTestCase):
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
        self.ok(req)
        data = self.json(req)
        self.assertTrue(data)

        self.num_entries(0)


class LoggingTests(BaseLoggingTestCase):
    """Test the logging endpoints with default log

    """

    def setUp(self):
        super(LoggingTests, self).setUp()
        self.url = '/api/v1/logging/genericlog'
        # self.data_dir = '{0}/webapps/CLIx/datastore/logging'.format(ABS_PATH)
        # if os.path.isdir(self.data_dir):
        #     shutil.rmtree(self.data_dir)

    def tearDown(self):
        super(LoggingTests, self).tearDown()
        # if os.path.isdir(self.data_dir):
        #     shutil.rmtree(self.data_dir)

    def test_can_get_log_entries(self):
        payload = {
            'name': 'my new log entry',
            'description': 'for testing with',
            'data': {
                'action': 'pause audio',
                'questionId': 'assessment.Item%3A57b954e0ed849b7a420859dc%40ODL.MIT.EDU',
                'assessmentOfferedId': 'assessment.AssessmentOffered:57bfcc21ed849b11f52fc80a@ODL.MIT.EDU',
                'mediaId': '',
                'mediaTime': 9.142857
            }
        }

        req = self.app.post(self.url,
                            params=json.dumps(payload),
                            headers={'content-type': 'application/json'})

        req = self.app.get(self.url)
        self.ok(req)
        data = self.json(req)
        self.assertEqual(len(data), 1)
        self.assertEqual(data[0]['displayName']['text'], 'my new log entry')
        self.assertEqual(data[0]['description']['text'], 'for testing with')
        self.assertEqual(data[0]['text']['text'], json.dumps(payload['data']))

    def test_can_create_log_entry_with_default_user(self):
        payload = {
            'data': {
                'action': 'pause audio',
                'questionId': 'assessment.Item%3A57b954e0ed849b7a420859dc%40ODL.MIT.EDU',
                'assessmentOfferedId': 'assessment.AssessmentOffered:57bfcc21ed849b11f52fc80a@ODL.MIT.EDU',
                'mediaId': '',
                'mediaTime': 9.142857
            }
        }

        req = self.app.post(self.url,
                            params=json.dumps(payload),
                            headers={'content-type': 'application/json'})
        self.ok(req)
        entry = self.json(req)
        self.assertTrue(
            json.loads(entry['text']['text']) == payload['data'])
        self.assertEqual(
            entry['agentId'],
            osid_agent('student@tiss.edu')
        )

    def test_session_id_passes_through_from_header_if_provided(self):
        payload = {
            'data': {
                'action': 'pause audio',
                'questionId': 'assessment.Item%3A57b954e0ed849b7a420859dc%40ODL.MIT.EDU',
                'assessmentOfferedId': 'assessment.AssessmentOffered:57bfcc21ed849b11f52fc80a@ODL.MIT.EDU',
                'mediaId': '',
                'mediaTime': 9.142857,
                'session_id': 'foo'
            }
        }

        req = self.app.post(self.url,
                            params=json.dumps(payload),
                            headers={'content-type': 'application/json',
                                     'x-api-proxy': 'student@tiss.edu'})
        self.ok(req)
        entry = self.json(req)
        self.assertTrue(
            json.loads(entry['text']['text']) == payload['data'])
        self.assertEqual(
            entry['agentId'],
            osid_agent('student@tiss.edu')
        )
