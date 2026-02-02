from aiogram.types import InlineKeyboardMarkup
from aiogram.utils.keyboard import InlineKeyboardBuilder
from typing import List
from database import Solution


def get_solutions_list_keyboard(kim: int, task_id: int, solutions: List[Solution]) -> InlineKeyboardMarkup:
    """
    Клавиатура со списком эталонных решений

    Args:
        kim: ID варианта
        task_id: ID задания
        solutions: Список решений
    """
    keyboard = InlineKeyboardBuilder()

    for idx, solution in enumerate(solutions, 1):
        comment_preview = ""
        if solution.comment:
            comment_preview = f" - {solution.comment[:20]}..."

        keyboard.button(
            text=f"Решение #{idx}{comment_preview}",
            callback_data=f"view_solution_{kim}_{task_id}_{solution.id}"
        )

    keyboard.button(
        text="◀️ Назад к заданию",
        callback_data=f"task_{kim}_{task_id}"
    )

    keyboard.adjust(1)
    return keyboard.as_markup()


def get_solution_view_keyboard(kim: int, task_id: int, solution_id: int,
                                total_solutions: int, current_index: int) -> InlineKeyboardMarkup:
    """
    Клавиатура для просмотра конкретного решения

    Args:
        kim: ID варианта
        task_id: ID задания
        solution_id: ID решения
        total_solutions: Общее количество решений
        current_index: Текущий индекс решения (начиная с 1)
    """
    keyboard = InlineKeyboardBuilder()

    # Навигация между решениями если их несколько
    if total_solutions > 1:
        nav_buttons = []

        if current_index > 1:
            nav_buttons.append({
                "text": "⬅️ Предыдущее",
                "callback_data": f"nav_solution_{kim}_{task_id}_{current_index - 1}"
            })

        if current_index < total_solutions:
            nav_buttons.append({
                "text": "Следующее ➡️",
                "callback_data": f"nav_solution_{kim}_{task_id}_{current_index + 1}"
            })

        for btn in nav_buttons:
            keyboard.button(text=btn["text"], callback_data=btn["callback_data"])

    keyboard.button(
        text="◀️ К списку решений",
        callback_data=f"solutions_{kim}_{task_id}"
    )

    keyboard.adjust(2 if total_solutions > 1 else 1)
    return keyboard.as_markup()
