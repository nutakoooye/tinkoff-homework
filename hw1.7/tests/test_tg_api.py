import json
from unittest import TestCase
from unittest.mock import patch
from tg_api import TelegramAPI


class TestTelegramAPI(TestCase):
    def setUp(self):
        self.tg_api = TelegramAPI("3jn4k54534n5l2k4nrt")

    @patch("tg_api.requests.get")
    def test_get_updates(self, mock_request):
        mock_request.return_value.json.return_value = {
            'result': {1: 'update_1'}
        }

        updates = self.tg_api.get_updates(offset=1, timeout=30)
        self.assertEqual(updates, {1: 'update_1'})

        url = 'https://api.telegram.org/bot3jn4k54534n5l2k4nrt/getUpdates'
        mock_request.assert_called_with(
            url, params={'timeout': 30, 'offset': 1}
        )

    @patch("tg_api.requests.post")
    def test_send_text_mess(self, mock_request):
        params = {'chat_id': 10, 'text': "text", 'parse_mode': 'html'}
        self.tg_api.send_text_mess(10, "text")
        url = 'https://api.telegram.org/bot3jn4k54534n5l2k4nrt/sendMessage'
        mock_request.assert_called_with(url, data=params)

    @patch("tg_api.requests.post")
    def test_send_answer_callback(self, mock_request):
        params = {'callback_query_id': 12312, 'text': "text"}
        self.tg_api.send_answer_callback(12312, "text")
        url = 'https://api.telegram.org/bot3jn4k54534n5l2k4nrt/answerCallbackQuery'
        mock_request.assert_called_with(url, data=params)

    @patch("tg_api.requests.post")
    def test_send_photo_text_button(self, mock_request):
        reply_markup = {
            "inline_keyboard": [
                [
                    {
                        "text": "Add to favorites",
                        "callback_data": "callback_data",
                    }
                ]
            ]
        }
        params = {
            'chat_id': "chat_id",
            'photo': "photo_url",
            'caption': "caption",
            'parse_mode': 'html',
            'reply_markup': json.dumps(reply_markup),
        }
        self.tg_api.send_photo_text_button(
            "chat_id", "caption", "photo_url", "callback_data"
        )

        url = 'https://api.telegram.org/bot3jn4k54534n5l2k4nrt/sendPhoto'
        mock_request.assert_called_with(url, data=params)

    @patch("tg_api.requests.post")
    def test_send_bot_commands(self, request_mock):
        params = {
            'commands': """[
            {"command": "/start", "description": start_description},
            {"command": "/help", "description": help_description},
            {"command": "/favorites", "description": favorites_description},
        ]}"""
        }
        self.tg_api.send_bot_commands(params["commands"])
        url = 'https://api.telegram.org/bot3jn4k54534n5l2k4nrt/setMyCommands'
        request_mock.assert_called_with(url, data=params)
