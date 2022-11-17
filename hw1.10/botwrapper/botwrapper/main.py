import sys

import tvmazetgbot

bot = tvmazetgbot.Bot(token="5547280874:AAFksFMJuHs7FhfU7Ag0tjVieZGLw8t63MY")
try:
    print("Starting bot")
    bot.start()
except KeyboardInterrupt:
    print("Closing bot")
    sys.exit()
