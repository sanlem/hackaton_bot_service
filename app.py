import tornado.web
import asyncio
import logging
from tornado.options import options
from tornado.httpserver import HTTPServer

import settings
from urls import urlpatterns

logger = logging.getLogger(__name__)


class Application(tornado.web.Application):
    def __init__(self):
        tornado.ioloop.IOLoop.configure('tornado.platform.asyncio.AsyncIOMainLoop')
        super().__init__(urlpatterns, debug=True)


if __name__ == '__main__':

    app = Application()
    loop = asyncio.get_event_loop()

    server = HTTPServer(app)
    server.bind(port=options.port)
    server.start(1)
    logger.info('Server started at port {}...'.format(options.port))
    loop.run_forever()
