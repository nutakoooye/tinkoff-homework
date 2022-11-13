import re
import json
from tvmaze.tv_program import get_tv_program
from tvmaze.tv_program_model import TVProgram
from database_tools import FavoritesDB
from tg_api import TelegramAPI


START_MESSAGE = """
Hi, I'm a TV show search bot, just try
to send me the name of the TV show to see!
/help - to learn more
"""
HELP_MESSAGE = """
<strong>That's all I know how to do:</strong>\n
<b>add to favorites</b> - Press the button under TV show
<b>view favorites programs</b> - /favorites command
<b>delete favorites</b> - Click on the command next to the entry in favorites
"""
BOT_COMMANDS = [
    {"command": "/start", "description": "Start bot"},
    {"command": "/help", "description": "Get help"},
    {"command": "/favorites", "description": "Give all your favorite shows"},
]


class Bot:
    def __init__(self, token: str):
        self.offset: int = 0
        self.api = TelegramAPI(token)
        self.favorites_db = FavoritesDB()
        self.set_commands()

    def set_commands(self):
        self.api.send_bot_commands(json.dumps(BOT_COMMANDS))

    @staticmethod
    def delete_html_tags(text: str) -> str:
        to_clean = re.compile('<.*?>')
        cleantext = re.sub(to_clean, '', text)
        return cleantext

    def generate_text_message(self, program: TVProgram) -> str:
        summary = self.delete_html_tags(program.summary)
        message = (
            f"<b>{program.name}</b>\n"
            + f"(<i>{program.network.name}</i> - "
            + f"{program.network.country.name})\n"
            + summary[0:900]
        )
        # summary[0:900] because Telegram received max 1024 caption chars
        return message

    def send_tv_program(self, chat_id: int, name_tv_program: str):
        try:
            tv_program = get_tv_program(name_tv_program)
            message = self.generate_text_message(tv_program)
            image_url = tv_program.image.medium
            self.api.send_photo_text_button(
                chat_id, message, image_url, tv_program.name
            )
        except ValueError:
            self.api.send_text_mess(chat_id, "Program not found")

    def send_start_message(self, chat_id: int):
        message = START_MESSAGE
        self.api.send_text_mess(chat_id, message)

    def send_help_message(self, chat_id: int):
        message = HELP_MESSAGE
        self.api.send_text_mess(chat_id, message)

    def send_favorites(self, chat_id: int, user_id: int):
        favorites = self.favorites_db.get_favorites(user_id)
        message_list = []
        for record in favorites:
            message_list.append(f"{record[1]} /delete{record[0]}")
        if message_list:
            message = "\n".join(message_list)
        else:
            message = "favorites is empty("
        self.api.send_text_mess(chat_id, message)

    def add_to_favorites(self, callback_query: dict):
        program_name = callback_query["data"]
        user_id = callback_query["from"]["id"]
        self.favorites_db.add_program(program_name, user_id)

        callback_id = str(callback_query["id"])
        callback_text = "Tv show added to favorites"
        self.api.send_answer_callback(callback_id, callback_text)

    def del_from_favorites(self, chat_id: int, command: str):
        try:
            program_id = int(command[7:])
            program_id = int(program_id)
            self.favorites_db.del_program(program_id)
            message = f"Program with id = {program_id} is deleted"
        except ValueError:
            message = "Invalid command"
        self.api.send_text_mess(chat_id, message)

    def execute_command(self, chat_id: int, user_id: int, command: str):
        if command == "/help":
            self.send_help_message(chat_id)
        elif command == "/start":
            self.send_start_message(chat_id)
        elif command == "/favorites":
            self.send_favorites(chat_id, user_id)
        elif command.startswith("/delete"):
            self.del_from_favorites(chat_id, command)
        else:
            self.api.send_text_mess(chat_id, "Invalid command")

    def reply_to_user(self, message):
        chat_id = message['chat']['id']

        if 'text' in message:
            text_message = message['text']

            if text_message.startswith("/"):
                user_id = message['from']['id']
                self.execute_command(chat_id, user_id, text_message)
            else:
                self.send_tv_program(chat_id, text_message)
        else:
            self.api.send_text_mess(chat_id, "Bot takes only text messages")

    def update_offset(self, updates):
        if updates:
            last_update = updates[-1]
            self.offset = last_update["update_id"] + 1

    def skip_updates(self):
        """skipping calls to the bot while it was turned off"""
        updates = self.api.get_updates(offset=self.offset)
        if updates:
            last_update = updates[-1]
            self.offset = last_update["update_id"]

    def start(self):
        self.skip_updates()
        while True:
            updates = self.api.get_updates(offset=self.offset)

            for update in updates:
                if 'message' in update:
                    message = update["message"]
                    self.reply_to_user(message)
                elif "callback_query" in update:
                    callback_query = update["callback_query"]
                    self.add_to_favorites(callback_query)

            self.update_offset(updates)
