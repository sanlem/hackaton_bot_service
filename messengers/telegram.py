from tornado.httpclient import HTTPRequest
from tornado.escape import json_decode, json_encode, url_escape
import datetime


class TelegramAPIWrapper:
    def __init__(self, client):
        self.client = client

    async def send(self, conversation_id, message,
                   message_type, token):
        base_url = 'https://api.telegram.org/bot%s/{}' % token
        body = {
            "chat_id": conversation_id,
        }
        if message_type == 'answer':
            body['text'] = message
        elif message_type == 'questions':
            # body['text'] = "\n".join(["{}. {}".format(i, data['question'])
            #                           for i, data in enumerate(message)])

            body.update({
                "text": "\n".join(["{}. {}".format(i, data['question'])
                                      for i, data in enumerate(message)])
                "reply_markup": {
                    "inline_keyboard": [
                        [{
                            "text": str(i),
                            "callback_data": str(i)
                        }]
                        for i, _ in enumerate(message)
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
        print(response.boяdy)

"""
Set Telegram webhook
curl -X POST -H "Cache-Control: no-cache" -H "Content-Type: application/x-www-form-urlencoded" -d 'url=https://faq-bureaucracy.in.ua:8443/telegram/' 'https://api.telegram.org/bot340724340:AAGqk-5O_EMn4nlQvLKBAhPQ0hYUv2SmJHQ/setWebhook'
"""