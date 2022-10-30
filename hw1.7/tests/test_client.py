import json
import os
from unittest import TestCase
from unittest.mock import patch
from tvmaze.tv_program_model import TVProgram
from client import Bot


class TestTelegramBot(TestCase):
    def setUp(self):
        self.bot = Bot("3jn4k54534n5l2k4nrt")

    @classmethod
    def tearDownClass(cls) -> None:
        os.remove("sqlite.db")
        os.rmdir("./.tv_program_cache")

    @patch("tg_api.TelegramAPI.send_bot_commands")
    def test_set_commands(self, request_mock):
        self.bot.set_commands()
        bot_commands = [
            {"command": "/start", "description": "Start bot"},
            {"command": "/help", "description": "Get help"},
            {
                "command": "/favorites",
                "description": "Give all your favorite shows",
            },
        ]
        request_mock.assert_called_with(json.dumps(bot_commands))

    def test_delete_html_tags(self):
        test_str = "<p><ul><li>1</li><li>2</li></ul><p>"
        expected_result = "12"
        result = self.bot.delete_html_tags(test_str)
        self.assertEqual(result, expected_result)

    def test_generate_text_message(self):
        tv_program_dict = {
            "name": "Name",
            "network": None,
            "image": None,
            "summary": None,
        }
        tv_program = TVProgram(**tv_program_dict)
        expected_result = (
            "<b>Name</b>\n"
            "(<i>Undefined network</i> - Undefined Country)\n"
            "Summary is missing("
        )
        result = self.bot.generate_text_message(tv_program)
        self.assertEqual(result, expected_result)
