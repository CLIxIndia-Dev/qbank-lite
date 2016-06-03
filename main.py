import os
import web

import assessment
import logging_
import repository

from waitress import serve

web.config.debug = False

urls = (
    '/api/v1/assessment', assessment.app_assessment,
    '/api/v1/logging', logging_.app_logging,
    '/api/v1/repository', repository.app_repository,
    '/test', 'video_test',
    '/(.*)', 'index'
)

app = web.application(urls, locals())

class index:
    def GET(self, path):
        return "Trying to GET {}".format(path)

class video_test:
    def GET(self):
        yield open('static/index.html', 'r').read()

################################################
# INITIALIZER
################################################

def is_test():
    if 'WEBPY_ENV' in os.environ:
        return os.environ['WEBPY_ENV'] == 'test'
    return False

if (not is_test()) and __name__ == "__main__":
    serve(app.wsgifunc(), port=8091)
