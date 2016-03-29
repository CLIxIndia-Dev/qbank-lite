import os
import web

import assessment
import logging_

from waitress import serve

web.config.debug = False

web.config.handler_parameters = {
    'file_dir': 'C:\CLIx\qbank\sessions'
}

urls = (
    '/api/v1/assessment', assessment.app_assessment,
    '/api/v1/logging', logging_.app_logging,
    '/(.*)', 'index'
)

app = web.application(urls, locals())

class index:
    def GET(self, path):
        return "Trying to GET {}".format(path)

################################################
# INITIALIZER
################################################

def is_test():
    if 'WEBPY_ENV' in os.environ:
        return os.environ['WEBPY_ENV'] == 'test'
    return False

if (not is_test()) and __name__ == "__main__":
    serve(app.wsgifunc(), port=8091)
