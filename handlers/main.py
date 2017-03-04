from tornado.web import RequestHandler


class MainHandler(RequestHandler):
    async def get(self, *args, **kwargs):
        message = self.get_argument('q', None)
        if message is not None:
            a = self.application.bots['bot1'].respond_faq(message)
            print(a)
        self.write('Hello world')


class TelegramHandler(RequestHandler):
    def check_xsrf_cookie(self):
        # disable XSRF checking for this handler
        pass

    async def prepare(self):
        """
        Dispatch request to proper bot.
        """
        bot_id = self.path_kwargs['bot_id']
        bot = self.application.bots.get(bot_id, None)
        if bot is not None:
            self.bot = bot
        else:
            self.set_status(200)
            self.finish()

    async def post(self, *args, **kwargs):
        pass
