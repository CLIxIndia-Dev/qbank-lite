#!/bin/sh

import os
import sys
import web

import assessment
import logging_
import repository

from waitress import serve


def is_test():
    if 'WEBPY_ENV' in os.environ:
        return os.environ['WEBPY_ENV'] == 'test'
    return False


# http://pythonhosted.org/PyInstaller/runtime-information.html#run-time-information
if getattr(sys, 'frozen', False):
    ABS_PATH = os.path.dirname(sys.argv[0])
else:
    PROJECT_PATH = os.path.dirname(os.path.abspath(__file__))
    # hack to get runtime working on ubuntu-based version,
    # because pyinstaller doesn't create a "bundle" in linux ...
    # so BOOTLOADER = False
    # because otherwise it reports just /var/www as the runtime path ...
    # and we don't want to add webapps/ to the configs.py file,
    # otherwise that breaks on local-Windows versions (because
    # the saved file paths in Assets.json shows "url": "webapps/CLIx/datastore"
    # when we only need "url": "CLIx/datastore") ...
    if (not is_test() and
            'linux' in sys.platform):
        PROJECT_PATH = '{0}/webapps'.format(PROJECT_PATH)
    ABS_PATH = '{0}/qbank-lite'.format(os.path.abspath(os.path.join(PROJECT_PATH, os.pardir)))

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
    def GET(self, path):
        return "Trying to GET {}".format(path)

class version:
    def GET(self):
        return '0.69'

class video_test:
    def GET(self):
        test_file = '{0}/static/index.html'.format(ABS_PATH)
        yield open(test_file, 'r').read()

################################################
# INITIALIZER
################################################


if (not is_test()) and __name__ == "__main__":
    serve(app.wsgifunc(), port=8091)
