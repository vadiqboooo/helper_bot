import os
from dotenv import load_dotenv

load_dotenv()

BOT_TOKEN = os.getenv('BOT_TOKEN', '0')
KOMPEGE_API_URL = 'https://kompege.ru/api/v1/variant/kim/'
KOMPEGE_HOMEWORK_URL = 'https://kompege.ru/homework?kim='


# ID администратора (ваш Telegram ID)
# Чтобы узнать свой ID, напишите боту @userinfobot
ADMIN_ID = int(os.getenv('ADMIN_ID', '0'))  # Замените на ваш ID

# DashScope API ключ для Qwen LLM
DASHSCOPE_API_KEY = os.getenv('DASHSCOPE_API_KEY', '')
