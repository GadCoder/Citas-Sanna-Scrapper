import os

import requests
from dotenv import load_dotenv


load_dotenv()


BOT_TOKEN = os.getenv("BOT_TOKEN")
CHAT_ID = os.getenv("CHAT_ID")


def send_telegram_message(message: str):
    send_text = 'https://api.telegram.org/bot' + BOT_TOKEN + \
        '/sendMessage?chat_id=' + CHAT_ID + '&parse_mode=Markdown&text=' + message
    requests.get(send_text)