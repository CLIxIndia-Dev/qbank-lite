import os
import sys
import web

import assessment
import logging_
import repository

# from waitress import serve

# import cherrypy

from web.wsgiserver import CherryPyWSGIServer

# http://pythonhosted.org/PyInstaller/runtime-information.html#run-time-information
if getattr(sys, 'frozen', False):
    ABS_PATH = os.path.dirname(sys.argv[0])
else:
    PROJECT_PATH = os.path.dirname(os.path.abspath(__file__))
    ABS_PATH = '{0}/qbank-lite'.format(os.path.abspath(os.path.join(PROJECT_PATH, os.pardir)))

CherryPyWSGIServer.ssl_certificate = "{0}/unplatform/unplatform.cert.dummy.pem".format(ABS_PATH)
CherryPyWSGIServer.ssl_private_key = "{0}/unplatform/unplatform.key.dummy.pem".format(ABS_PATH)

web.config.debug = False

urls = (
    '/api/v1/assessment', assessment.app_assessment,
    '/api/v1/logging', logging_.app_logging,
    '/api/v1/repository', repository.app_repository,
    '/test', 'video_test',
    '/datastore_path', 'bootloader_storage_path',
    '/(.*)', 'index'
)
app = web.application(urls, locals())

class bootloader_storage_path:
    def GET(self):
        return ABS_PATH

class index:
    def GET(self, path):
        return "Trying to GET {}".format(path)

class video_test:
    def GET(self):
        test_file = '{0}/static/index.html'.format(ABS_PATH)
        yield open(test_file, 'r').read()

################################################
# INITIALIZER
################################################

def is_test():
    if 'WEBPY_ENV' in os.environ:
        return os.environ['WEBPY_ENV'] == 'test'
    return False

if (not is_test()) and __name__ == "__main__":
    # serve(app.wsgifunc(), port=8091)

    app.run()

    # cherrypy.tree.mount(app)
    #
    # cherrypy.server.unsubscribe()
    #
    # server1 = cherrypy._cpserver.Server()
    # server1.socket_port=9443
    # server1._socket_host='0.0.0.0'
    # server1.thread_pool=30
    # server1.ssl_module = 'pyopenssl'
    # server1.ssl_certificate = "{0}/unplatform/unplatform.cert.dummy.pem".format(ABS_PATH)
    # server1.ssl_private_key = "{0}/unplatform/unplatform.key.dummy.pem".format(ABS_PATH)
    # # server1.ssl_certificate_chain = '/home/ubuntu/gd_bundle.crt'
    # server1.subscribe()
    #
    # server2 = cherrypy._cpserver.Server()
    # server2.socket_port=9080
    # server2._socket_host="0.0.0.0"
    # server2.thread_pool=30
    # server2.subscribe()
    #
    # cherrypy.engine.start()
    # cherrypy.engine.block()