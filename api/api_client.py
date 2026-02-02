import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import requests
from typing import Dict, List, Optional
from client_bot.config import KOMPEGE_API_URL


class KompegeAPI:
    """Клиент для работы с API kompege.ru"""

    @staticmethod
    def get_homework_data(kim: int) -> Optional[Dict]:
        """
        Получает данные о домашней работе по KIM

        Args:
            kim: ID варианта (KIM)

        Returns:
            Словарь с данными или None в случае ошибки
        """
        try:
            url = f"{KOMPEGE_API_URL}{kim}"
            response = requests.get(url, timeout=10)
            response.raise_for_status()
            return response.json()
        except requests.RequestException as e:
            print(f"Ошибка при получении данных для KIM {kim}: {e}")
            return None

    @staticmethod
    def get_tasks(kim: int) -> List[Dict]:
        """
        Получает список задач для домашней работы

        Args:
            kim: ID варианта (KIM)

        Returns:
            Список задач
        """
        data = KompegeAPI.get_homework_data(kim)
        if data:
            return data.get('tasks', [])
        return []

    @staticmethod
    def get_description(kim: int) -> str:
        """
        Получает описание домашней работы

        Args:
            kim: ID варианта (KIM)

        Returns:
            Описание работы
        """
        data = KompegeAPI.get_homework_data(kim)
        if data:
            return data.get('description', f'Домашняя работа {kim}')
        return f'Домашняя работа {kim}'
