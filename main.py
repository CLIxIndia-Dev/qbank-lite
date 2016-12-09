#!/bin/sh

import os
import sys
import web

import assessment
import logging_
import repository
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
    '/modules_list', 'modules_list',
    '/', 'index'
)
app = web.application(urls, locals())

def list_dir(root, directory, current_level=0, max_level=3):
    # recursively list the directories under modules. Set limit to 3, given how
    # the epubs are structured, but let's make that an option
    # Tools will show up with an extra level of depth.
    # Sample output:
    # ['modules/English Elementary', 'modules/English Elementary/G9', 'modules/English Elementary/G9/U1',
    #  'modules/Tools', 'modules/Tools/Bio- Mechanic', 'modules/Tools/Open Story',
    #  'modules/Tools/Open Story/css', 'modules/Tools/Open Story/fonts', 'modules/Tools/Physics Video Player',
    #  'modules/Tools/Police Quad', 'modules/Tools/Turtle Blocks']
    sub_dirs = []
    if current_level < max_level:
        for sub_dir in os.listdir('{0}/{1}'.format(root, directory)):
            new_sub_dir = '{0}/{1}'.format(directory, sub_dir)
            full_sub_dir_path = '{0}/{1}'.format(root, new_sub_dir)
            if not sub_dir.startswith('.') and os.path.isdir(full_sub_dir_path):
                sub_dirs.append(new_sub_dir)
                sub_dirs += list_dir(root, new_sub_dir, current_level=current_level+1)
        sub_dirs.sort()
    return sub_dirs

class bootloader_storage_path:
    def GET(self):
        return ABS_PATH

class index:
    def GET(self):
        # render the unplatform v2 front-end
        index_file = '{0}/static/index.html'.format(ABS_PATH)
        yield open(index_file, 'rb').read()

class modules_list:
    @utilities.format_response
    def GET(self):
        # send the entire
        # file structure for /modules in one go, so that the
        # OS doesn't have to be re-walked every time.
        data = list_dir(ABS_PATH, 'modules')
        return data

class version:
    def GET(self):
        return '1.2.0'

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