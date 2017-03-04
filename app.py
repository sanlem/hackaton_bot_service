from collections import OrderedDict
import tornado.web
import asyncio
import logging
# import pickle
from tornado.options import options
from tornado.httpserver import HTTPServer

import settings
from urls import urlpatterns
from bots.faqbot import ChatBot

logger = logging.getLogger(__name__)


class Application(tornado.web.Application):
    def __init__(self, io_loop):
        tornado.ioloop.IOLoop.configure('tornado.platform.asyncio.AsyncIOMainLoop')
        self.loop = io_loop
        self.bot_data = io_loop.run_until_complete(self.fetch_bots_data())
        self.bot = ChatBot('bot1', self.bot_data)
        # load synonyms
        # self.synonyms = pickle.load(open('./utils/data/pickled_synonims.txt', 'rb'))

        super().__init__(urlpatterns, debug=True)

    async def fetch_bots_data(self):
        data = {
            'name': 'bot1',
            'faqs': OrderedDict({
                'привет': 'ну здравствуй',
                'пока': 'проходи не задерживайся проходи не задерживайся проходи не задерживайся',
                'пидор': 'я не пишу фронтенд'
            })
        }
        return data


if __name__ == '__main__':
    loop = asyncio.get_event_loop()
    app = Application(loop)

    server = HTTPServer(app)
    server.bind(port=options.port)
    server.start(1)
    logger.info('Server started at port {}...'.format(options.port))
    loop.run_forever()
