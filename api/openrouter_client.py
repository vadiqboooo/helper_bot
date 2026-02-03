"""
Клиент для работы с OpenRouter API
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from openai import OpenAI
from typing import Optional
from backend.crud import SolutionCRUD


class OpenRouterClient:
    """Клиент для генерации подсказок через OpenRouter"""

    def __init__(self, api_key: Optional[str] = None):
        """
        Инициализация клиента

        Args:
            api_key: API ключ OpenRouter (если не указан, берется из .env)
        """
        self.api_key = api_key or os.getenv('OPENROUTER_API_KEY')
        self.client = OpenAI(
            base_url="https://openrouter.ai/api/v1",
            api_key=self.api_key,
        )
        # Используем Qwen3 Coder
        self.model = "qwen/qwen3-coder"

    def analyze_code(self, task_id: int, task_description: str, user_code: str) -> str:
        """
        Анализировать код пользователя и дать подсказку

        Args:
            task_id: ID задачи
            task_description: Описание задачи
            user_code: Код пользователя

        Returns:
            Подсказка в одном предложении
        """
        # Получаем эталонное решение из БД
        solutions = SolutionCRUD.get_solutions_by_task_id(task_id)

        if not solutions:
            return "К сожалению, для этой задачи пока нет эталонных решений для анализа."

        # Берем первое решение как эталонное
        correct_code = solutions[0].solution

        # Создаем промпт
        prompt = (
            "Role: You are a helpful senior software engineer mentoring a junior student.\n\n"
            f"Task: The student is trying to solve the following problem: {task_description}\n\n"
            f"Reference Solution (Do not reveal): {correct_code}\n\n"
            f"Student's Code: {user_code}\n\n"
            "Instructions:\n"
            "- Analyze the student's code compared to the reference.\n"
            "- Identify the logic error or syntax error.\n"
            "- Provide a helpful hint in ONE sentence.\n"
            "- CRITICAL: Do NOT write the corrected code. Do NOT give the answer directly. Encourage them to think.\n"
            "- Reply in Russian.\n"
            "- Your response must be ONLY ONE sentence with a hint."
        )

        try:
            response = self.client.chat.completions.create(
                model=self.model,
                max_tokens=150,
                messages=[
                    {"role": "system", "content": "You are a helpful programming tutor. Always reply in Russian."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.7,
            )

            message = response.choices[0].message

            # Получаем ответ (сначала content, потом reasoning если есть)
            hint = message.content or getattr(message, 'reasoning', None) or ""
            hint = hint.strip()

            print(f"[DEBUG] Response: {hint[:200]}...")  # Первые 200 символов

            if not hint:
                return "Не удалось получить ответ от модели. Попробуйте позже."

            return hint

        except Exception as e:
            print(f"OpenRouter API Error: {e}")
            import traceback
            traceback.print_exc()
            return "Произошла ошибка при анализе кода. Попробуйте позже."

    def generate_start_hint(self, task_id: int, task_description: str) -> str:
        """
        Генерировать подсказку как начать задачу

        Args:
            task_id: ID задачи
            task_description: Описание задачи

        Returns:
            Подсказка как начать - описание первой строки решения
        """
        solutions = SolutionCRUD.get_solutions_by_task_id(task_id)

        if not solutions:
            return "К сожалению, для этой задачи пока нет подсказок."

        # Берем первое решение как эталонное
        reference_solution = solutions[0].solution

        # Извлекаем первую строку кода (пропускаем комментарии и пустые строки)
        first_line = ""
        for line in reference_solution.split('\n'):
            line = line.strip()
            if line and not line.startswith('#'):
                first_line = line
                break

        prompt = (
            "Role: You are a helpful programming tutor.\n\n"
            f"Task: {task_description}\n\n"
            f"First line of the reference solution: {first_line}\n\n"
            "Instructions:\n"
            "- Explain in ONE sentence what the first line does\n"
            "- DO NOT write the code itself\n"
            "- Be clear and concise\n"
            "- Reply in Russian\n"
            "- Your response must be ONLY ONE sentence"
        )

        try:
            response = self.client.chat.completions.create(
                model=self.model,
                max_tokens=300,
                messages=[
                    {"role": "system", "content": "You are a helpful programming tutor. Always reply in Russian."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.7,
            )

            message = response.choices[0].message

            # Получаем ответ (сначала content, потом reasoning если есть)
            hint = message.content or getattr(message, 'reasoning', None) or ""
            hint = hint.strip()

            print(f"[DEBUG] Response: {hint[:200]}...")  # Первые 200 символов

            if not hint:
                return "Не удалось получить ответ от модели. Попробуйте позже."

            return hint

        except Exception as e:
            print(f"OpenRouter API Error: {e}")
            import traceback
            traceback.print_exc()
            return "Произошла ошибка при генерации подсказки. Попробуйте позже."


# Глобальный экземпляр клиента
_client = None


def get_openrouter_client() -> OpenRouterClient:
    """Получить глобальный экземпляр клиента OpenRouter"""
    global _client
    if _client is None:
        _client = OpenRouterClient()
    return _client
