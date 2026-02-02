#!/usr/bin/env python3
"""
Главный файл запуска Telegram бота
"""

import sys
import os

# Добавляем корневую директорию в путь для импортов
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Импортируем и запускаем бота
from client_bot.bot import main
import asyncio

if __name__ == '__main__':
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("Бот остановлен")
