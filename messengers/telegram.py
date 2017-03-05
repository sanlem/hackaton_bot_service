from tornado.httpclient import HTTPRequest
from tornado.escape import json_decode, json_encode, url_escape
import datetime


class TelegramAPIWrapper:
    def __init__(self, client):
        self.client = client

    async def send(self, conversation_id, message,
                   message_type, token='340724340:AAGqk-5O_EMn4nlQvLKBAhPQ0hYUv2SmJHQ'):
        base_url = 'https://api.telegram.org/bot%s/{}' % token
        body = {
            "chat_id": conversation_id,
        }
        if message_type == 'answer':
            body['text'] = message
        elif message_type == 'questions':
            body.update({
                "text": "Возможно, Ві имели в виду что-нибудь из етого?",
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
