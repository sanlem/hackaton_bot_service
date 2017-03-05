import logging
from tornado.web import RequestHandler
from tornado.escape import json_decode
from bots.machine import Machine


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

                guides = self.application.bot.respond_guides(message)
                logger.info('Guides: {}'.format(guides))
                logger.info('FAQS: {}'.format(response))
                if guides is not None and response != self.application.bot.default_answer:
                    logger.info('Sending both guides and faqs')
                    await telegram.send(conversation_id, response, message_type)
                    await telegram.send_guides(conversation_id, guides)
                elif guides is not None:
                    logger.info('Sending only guides')
                    await telegram.send_guides(conversation_id, guides)
                else:
                    logger.info('Sending only faqs')
                    await telegram.send(conversation_id, response, message_type)
            else:
                message = data['callback_query']['data']
                if message[0] != 'g':
                    index = int(message)
                    logger.info('Responding to question from cache...')
                    cached = self.CACHE.get(conversation_id, None)
                    if cached is not None:
                        response = cached[index]
                        message_type = 'answer'
                        await telegram.send(conversation_id, response, message_type)
                else:
                    # guide was selected
                    index = int(message[1:])
                    guide = self.application.bot_data['guides'][index]
                    machine = Machine(guide)
                    self.CONTEXT[conversation_id].update({
                        'state': 'guide',
                        'machine': machine
                    })
                    response = machine.current_question['description']
                    answers = machine.current_question['answers']
                    await telegram.send_guide_item(response, answers, conversation_id)
        else:
            if 'callback_query' in data:
                machine = self.CONTEXT[conversation_id]['machine']
                resp = machine.next_state(data['callback_query']['data'])
                if resp.get('answers', None) is None:
                    self.CONTEXT[conversation_id].update({
                        'state': 'main',
                        'machine': None
                    })
                    logger.info('Last guide item data: {}'.format(resp))
                    await telegram.send(conversation_id, resp['description'], 'answer')
                else:
                    await telegram.send_guide_item(resp['description'], resp['answers'], conversation_id)
