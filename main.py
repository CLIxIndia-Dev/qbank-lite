#!/bin/sh

import os
import sys
import web

import assessment
import logging_
import repository

# from waitress import serve

# import cherrypy

#from web.wsgiserver import CherryPyWSGIServer

# http://pythonhosted.org/PyInstaller/runtime-information.html#run-time-information
if getattr(sys, 'frozen', False):
    ABS_PATH = os.path.dirname(sys.argv[0])
else:
    PROJECT_PATH = os.path.dirname(os.path.abspath(__file__))
    ABS_PATH = '{0}/qbank-lite'.format(os.path.abspath(os.path.join(PROJECT_PATH, os.pardir)))

#CherryPyWSGIServer.ssl_certificate = "{0}/unplatform/unplatform.cert.dummy.pem".format(ABS_PATH)
#CherryPyWSGIServer.ssl_private_key = "{0}/unplatform/unplatform.key.dummy.pem".format(ABS_PATH)

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
        return '0.43'

class video_test:
    def GET(self):
        test_file = '{0}/static/index.html'.format(ABS_PATH)
        yield open(test_file, 'r').read()

################################################
# INITIALIZER
################################################
application = app.wsgifunc()
