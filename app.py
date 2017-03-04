from collections import OrderedDict
import tornado.web
import asyncio
import logging
import openpyxl
# import pickle
from tornado.options import options
from tornado.httpserver import HTTPServer
from tornado.httpclient import HTTPClient, AsyncHTTPClient

import settings
from urls import urlpatterns
from bots.faqbot import ChatBot

logger = logging.getLogger(__name__)


class Application(tornado.web.Application):
    def __init__(self, io_loop):
        tornado.ioloop.IOLoop.configure('tornado.platform.asyncio.AsyncIOMainLoop')
        self.loop = io_loop
        self.bot_data = io_loop.run_until_complete(self.fetch_bots_data())
        self.bot_data = {'faqs': self.parse_xl('./FAQ.EStaff.xlsx')}
        self.bots = {'bot1': ChatBot('bot1', self.bot_data)}

        AsyncHTTPClient.configure("tornado.curl_httpclient.CurlAsyncHTTPClient")
        self.async_http_client = AsyncHTTPClient()
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

    @staticmethod
    def parse_xl(filename):
        wb = openpyxl.load_workbook(filename)
        sheet_names = wb.get_sheet_names()
        worksheet = wb.get_sheet_by_name(sheet_names[0])
        data = list(worksheet.values)
        question_data = OrderedDict()

        for row in data:
            question, answer = row
            question_data[question] = answer

        return question_data


if __name__ == '__main__':
    loop = asyncio.get_event_loop()
    app = Application(loop)

    # server = HTTPServer(app)
    server = tornado.httpserver.HTTPServer(app, ssl_options={
        "certfile": "/etc/letsencrypt/live/faq-bureaucracy.in.ua/fullchain.pem",
        "keyfile": "/etc/letsencrypt/live/faq-bureaucracy.in.ua/privkey.pem",
    })
    server.bind(port=options.port)
    server.start(1)
    logger.info('Server started at port {}...'.format(options.port))
    loop.run_forever()
