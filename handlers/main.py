import logging
from tornado.web import RequestHandler
from tornado.escape import json_decode
from messengers.telegram import TelegramAPIWrapper


logger = logging.getLogger(__name__)


class MainHandler(RequestHandler):
    async def get(self, *args, **kwargs):
        message = self.get_argument('q', None)
        if message is not None:
            a = self.application.bot.respond_faq(message)
            print(a)
        self.write('Hello world')


class TelegramHandler(RequestHandler):
    CONTEXT = {}
    CACHE = {}

    def check_xsrf_cookie(self):
        # disable XSRF checking for this handler
        pass

    async def post(self, *args, **kwargs):
        self.set_status(200)
        self.finish()
        telegram = self.application.telegram
        data = json_decode(self.request.body)
        logger.info('Got message from telegram: {}'.format(data))
        response = None
        if 'callback_query' not in data:
            conversation_id = data['message']['chat']['id']
        else:
            conversation_id = data['callback_query']['message']['chat']['id']

        if conversation_id in self.CONTEXT:
            context = self.CONTEXT[conversation_id]
        else:
            context = {
                'state': 'main'
            }
            self.CONTEXT[conversation_id] = context

        if context['state'] == 'main':

            if 'callback_query' not in data:
                message = data['message']['text']
                response = self.application.bot.respond_faq(message)

                message_type = 'answer' if type(response) in [tuple, str] else 'questions'
                if message_type == 'questions':
                    # save to cache
                    self.CACHE[conversation_id] = list(response.values())
                else:
                    if conversation_id in self.CACHE:
                        self.CACHE.pop(conversation_id)

            else:
                message = data['callback_query']['data']
                index = int(message)

                cached = self.CACHE.get(conversation_id, None)
                if cached is not None:
                    response = cached[index]
                    message_type = 'answer'
            if response is not None:
                await telegram.send(conversation_id, response, message_type)
