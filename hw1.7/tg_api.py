from typing import Optional

import requests
import json


class TelegramAPI:
    def __init__(self, token: str):
        self.url = f"https://api.telegram.org/bot{token}/"

    def get_updates(self, offset: int, timeout: int = 30) -> dict:
        method = "getUpdates"
        query = {"timeout": timeout, "offset": offset}
        response = requests.get(self.url + method, params=query)
        updates = response.json()["result"]
        return updates

    def send_text_mess(self, chat_id: int, text: str):
        params = {'chat_id': chat_id, 'text': text, 'parse_mode': 'html'}
        method = 'sendMessage'
        response = requests.post(self.url + method, data=params)
        return response

    def send_answer_callback(self, callback_query_id: str, text: str):
        params = {'callback_query_id': callback_query_id, 'text': text}
        method = "answerCallbackQuery"
        response = requests.post(self.url + method, data=params)
        return response

    def send_photo_text_button(
        self,
        chat_id: int,
        caption: str,
        photo_url: Optional[str],
        callback_data: str,
    ):
        reply_markup = {
            "inline_keyboard": [
                [{"text": "Add to favorites", "callback_data": callback_data}]
            ]
        }
        params = {
            'chat_id': chat_id,
            'photo': photo_url,
            'caption': caption,
            'parse_mode': 'html',
            'reply_markup': json.dumps(reply_markup),
        }
        method = 'sendPhoto'
        response = requests.post(self.url + method, data=params)
        return response

    def send_bot_commands(self, commands: str):
        """send commands and description to TG Bot

        :param commands: json serialized str
        :return: Response
        """
        params = {'commands': commands}
        method = 'setMyCommands'
        response = requests.post(self.url + method, data=params)
        return response
