from nose.tools import set_trace

from testing_utilities import BaseTestCase


class BaseMainTestCase(BaseTestCase):
    def setUp(self):
        super(BaseMainTestCase, self).setUp()

    def tearDown(self):
        # don't teardown again here, because the BaseTestCase tearDown
        # will try to remove the test_datastore directory,
        # but that isn't re-created automatically with these tests
        # super(BaseMainTestCase, self).tearDown()
        pass


class BasicServiceTests(BaseMainTestCase):
    """Test the views for getting the basic service calls

    """
    def setUp(self):
        super(BasicServiceTests, self).setUp()

    def tearDown(self):
        super(BasicServiceTests, self).tearDown()

    def test_users_can_get_index_page(self):
        url = '/'
        req = self.app.get(url)
        self.ok(req)
        # TODO: make this match something in the login screen
        # self.message(req, '')


class ModuleDirectoryListingTests(BaseMainTestCase):
    """Test the views for the GET modules endpoint

    """
    def setUp(self):
        super(ModuleDirectoryListingTests, self).setUp()
        self.url = '/modules_list'

    def tearDown(self):
        super(ModuleDirectoryListingTests, self).tearDown()

    def test_can_get_modules_listing(self):
        req = self.app.get(self.url)
        self.ok(req)
        data = self.json(req)
        # self.assertTrue(len(data) > 0)
