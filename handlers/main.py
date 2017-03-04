from tornado.web import RequestHandler


class MainHandler(RequestHandler):
    async def get(self, *args, **kwargs):
        self.write('Hello world')
