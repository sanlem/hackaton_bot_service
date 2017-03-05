import logging
from tornado.web import RequestHandler
from tornado.escape import json_decode


logger = logging.getLogger(__name__)


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

    async def post(self, *args, **kwargs):
        data = json_decode(self.request.body)
        message = data['message']['text']
        logger.info('Got message from telegram: {}'.format(data))
        self.set_status(200)
        self.finish()
