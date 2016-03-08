import web

urls = (
    '/api/v1/assessment/banks/', 'banks'
)

class banks:
    def GET(self):
        return "foo"


if __name__ == "__main__":
    app = web.application(urls, globals())
    app.run()
