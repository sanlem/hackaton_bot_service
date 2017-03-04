from tornado.web import RequestHandler


class MainHandler(RequestHandler):
    async def get(self, *args, **kwargs):
        message = self.get_argument('q', None)
        if message is not None:
            a = self.application.bot.respond_faq(message)
            print(a)
        self.write('Hello world')
