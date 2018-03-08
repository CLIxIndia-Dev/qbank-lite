#!/bin/sh

import os
import sys
import web

from assessment import assessment
from logging_ import logging_
from repository import repository
import utilities

from web.wsgiserver import CherryPyWSGIServer

# http://pythonhosted.org/PyInstaller/runtime-information.html#run-time-information
if getattr(sys, 'frozen', False):
    ABS_PATH = os.path.dirname(sys.executable)
else:
    PROJECT_PATH = os.path.dirname(os.path.abspath(__file__))
    ABS_PATH = '{0}/qbank-lite'.format(os.path.abspath(os.path.join(PROJECT_PATH, os.pardir)))

CherryPyWSGIServer.ssl_certificate_chain = ''
try:
    CherryPyWSGIServer.ssl_certificate = "{0}/unplatform/unplatform.cert.dummy.pem".format(sys._MEIPASS)
    CherryPyWSGIServer.ssl_private_key = "{0}/unplatform/unplatform.key.dummy.pem".format(sys._MEIPASS)
except AttributeError:
    CherryPyWSGIServer.ssl_certificate = "{0}/unplatform/unplatform.cert.dummy.pem".format(ABS_PATH)
    CherryPyWSGIServer.ssl_private_key = "{0}/unplatform/unplatform.key.dummy.pem".format(ABS_PATH)


web.config.debug = False

urls = (
    '/api/v1/assessment', assessment.app_assessment,
    '/api/v1/logging', logging_.app_logging,
    '/api/v1/repository', repository.app_repository,
    '/test', 'video_test',
    '/datastore_path', 'bootloader_storage_path',
    '/version', 'version',
    '/(.*)', 'index'
)
app = web.application(urls, locals())


class bootloader_storage_path:
    def GET(self):
        return ABS_PATH


class index:
    def GET(self, path=None):
        return 'Trying to GET: {0}'.format(path)


class version:
    def GET(self):
        return '3.16.2'


class video_test:
    def GET(self):
        test_file = '{0}/static/video_test.html'.format(ABS_PATH)
        yield open(test_file, 'rb').read()

################################################
# INITIALIZER
################################################


def is_test():
    if 'WEBPY_ENV' in os.environ:
        return os.environ['WEBPY_ENV'] == 'test'
    return False


if (not is_test()) and __name__ == "__main__":
    app.run()
