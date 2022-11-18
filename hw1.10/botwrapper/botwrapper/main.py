import sys

import tvmazetgbot
token = input("Input the tg bot token: ")
bot = tvmazetgbot.Bot(token)
try:
    print("Starting bot")
    bot.start()
except KeyboardInterrupt:
    print("Closing bot")
    sys.exit()
