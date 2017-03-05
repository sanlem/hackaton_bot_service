from tornado.httpclient import HTTPRequest
from tornado.escape import json_decode, json_encode, url_escape
import datetime
import logging


logger = logging.getLogger(__name__)


class TelegramAPIWrapper:
    def __init__(self, client):
        self.client = client

    async def send_guide_item(self, response, answers, conversation_id,
                              token='340724340:AAGqk-5O_EMn4nlQvLKBAhPQ0hYUv2SmJHQ'):
        logger.info('Sending guide item...')
        base_url = 'https://api.telegram.org/bot%s/{}' % token
        body = {
            "chat_id": conversation_id,
            "text": response,
            "reply_markup": {
                "inline_keyboard": [
                    [{
                        "text": answer['value'],
                        "callback_data": str(answer['next'])
                    }]
                    for answer in answers
                    ]
            }
        }

        params = {
            "url": base_url.format("sendMessage"),
            "method": "POST",
            "headers": {"Content-Type": "application/json"},
            "validate_cert": False,
            "body": json_encode(body),
        }
        request = HTTPRequest(**params)
        response = await self.client.fetch(request, raise_error=False)
        logger.info('Sending guide item response: {}'.format(response.body))

    async def send_guides(self, conversation_id, guides,
                          token='340724340:AAGqk-5O_EMn4nlQvLKBAhPQ0hYUv2SmJHQ'):
        base_url = 'https://api.telegram.org/bot%s/{}' % token
        print(guides)
        body = {
            "chat_id": conversation_id,
            "text": "Также можете посмотреть следуюшие гайды:",
            "reply_markup": {
                "inline_keyboard": [
                    [{
                        "text": guide['guide_name'],
                        "callback_data": 'g' + str(i)
                    }]
                    for i, guide in enumerate(guides)
                    ]
            }
        }

        params = {
            "url": base_url.format("sendMessage"),
            "method": "POST",
            "headers": {"Content-Type": "application/json"},
            "validate_cert": False,
            "body": json_encode(body),
        }
        request = HTTPRequest(**params)
        response = await self.client.fetch(request, raise_error=False)
        logger.info('Send guides response: {}'.format(response.body))

    async def send(self, conversation_id, message,
                   message_type, token='340724340:AAGqk-5O_EMn4nlQvLKBAhPQ0hYUv2SmJHQ'):
        base_url = 'https://api.telegram.org/bot%s/{}' % token
        body = {
            "chat_id": conversation_id,
        }
        print(message)
        if message_type == 'answer':
            body['text'] = message
        elif message_type == 'questions':
            body.update({
                "text": "Возможно, Вы имели в виду что-нибудь из етого?",
                "reply_markup": {
                    "inline_keyboard": [
                        [{
                            "text": qa,
                            "callback_data": str(i)
                        }]
                        for i, qa in enumerate(message)
                        ]
                }
            })

        params = {
            "url": base_url.format("sendMessage"),
            "method": "POST",
            "headers": {"Content-Type": "application/json"},
            "validate_cert": False,
            "body": json_encode(body),
        }
        request = HTTPRequest(**params)
        response = await self.client.fetch(request, raise_error=False)

"""
Set Telegram webhook
curl -X POST -H "Cache-Control: no-cache" -H "Content-Type: application/x-www-form-urlencoded" -d 'url=https://faq-bureaucracy.in.ua:8443/telegram/' 'https://api.telegram.org/bot340724340:AAGqk-5O_EMn4nlQvLKBAhPQ0hYUv2SmJHQ/setWebhook'
"""
