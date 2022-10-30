import os
import sys
from dotenv import load_dotenv
from client import Bot


load_dotenv()
TELEGRAM_TOKEN = str(os.getenv('TELEGRAM_TOKEN'))


if __name__ == "__main__":
    tg_bot = Bot(TELEGRAM_TOKEN)
    print("Telegram bot has started")
    try:
        tg_bot.start()
    except KeyboardInterrupt:
        print("Telegram bot stopped working")
        sys.exit(0)
