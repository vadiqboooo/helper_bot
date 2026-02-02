from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder
from typing import List, Dict


def get_main_menu_keyboard() -> InlineKeyboardMarkup:
    """Главное меню с кнопкой 'Домашняя работа'"""
    keyboard = InlineKeyboardBuilder()
    keyboard.button(
        text="📚 Домашняя работа",
        callback_data="homework_list"
    )
    return keyboard.as_markup()


def get_homework_list_keyboard(homeworks: List[tuple]) -> InlineKeyboardMarkup:
    """
    Клавиатура со списком домашних работ

    Args:
        homeworks: Список кортежей (kim, description)
    """
    keyboard = InlineKeyboardBuilder()

    for kim, description in homeworks:
        keyboard.button(
            text=f"{description} \n КИМ: {kim}",
            callback_data=f"homework_{kim}"
        )

    keyboard.button(
        text="◀️ Назад",
        callback_data="main_menu"
    )

    keyboard.adjust(1)  # По одной кнопке в ряд
    return keyboard.as_markup()


def get_homework_detail_keyboard(kim: int) -> InlineKeyboardMarkup:
    """
    Клавиатура для конкретной домашней работы

    Args:
        kim: ID варианта
    """
    keyboard = InlineKeyboardBuilder()

    keyboard.button(
        text="🔗 Открыть работу",
        url=f"https://kompege.ru/homework?kim={kim}"
    )
    keyboard.button(
        text="💡 Получить подсказку по заданиям",
        callback_data=f"hints_{kim}"
    )
    keyboard.button(
        text="◀️ Назад к списку",
        callback_data="homework_list"
    )

    keyboard.adjust(1)
    return keyboard.as_markup()


def get_tasks_list_keyboard(kim: int, tasks: List[Dict]) -> InlineKeyboardMarkup:
    """
    Клавиатура со списком заданий

    Args:
        kim: ID варианта
        tasks: Список задач
    """
    keyboard = InlineKeyboardBuilder()

    for idx, task in enumerate(tasks, 1):
        task_id = task.get('taskId')
        keyboard.button(
            text=f"Задание #{idx} (ID: {task_id})",
            callback_data=f"task_{kim}_{task_id}"
        )

    keyboard.button(
        text="◀️ Назад к работе",
        callback_data=f"homework_{kim}"
    )

    keyboard.adjust(2)  # По две кнопки в ряд
    return keyboard.as_markup()


def get_task_actions_keyboard(kim: int, task_id: int) -> InlineKeyboardMarkup:
    """
    Клавиатура с действиями для конкретного задания

    Args:
        kim: ID варианта
        task_id: ID задания
    """
    keyboard = InlineKeyboardBuilder()

    keyboard.button(
        text="💡 Как начать?",
        callback_data=f"hint_start_{kim}_{task_id}"
    )
    keyboard.button(
        text="📝 Отправить код для проверки",
        callback_data=f"submit_code_{kim}_{task_id}"
    )
    keyboard.button(
        text="◀️ Назад к заданиям",
        callback_data=f"hints_{kim}"
    )

    keyboard.adjust(1)
    return keyboard.as_markup()


def get_back_to_task_keyboard(kim: int, task_id: int) -> InlineKeyboardMarkup:
    """
    Клавиатура для возврата к заданию

    Args:
        kim: ID варианта
        task_id: ID задания
    """
    keyboard = InlineKeyboardBuilder()

    keyboard.button(
        text="◀️ Назад к заданию",
        callback_data=f"task_{kim}_{task_id}"
    )

    return keyboard.as_markup()


def get_feedback_keyboard(kim: int, task_id: int) -> InlineKeyboardMarkup:
    """
    Клавиатура для обратной связи по подсказке

    Args:
        kim: ID варианта
        task_id: ID задания
    """
    keyboard = InlineKeyboardBuilder()

    keyboard.button(
        text="✅ Помогла",
        callback_data=f"feedback_yes_{kim}_{task_id}"
    )
    keyboard.button(
        text="❌ Не помогла",
        callback_data=f"feedback_no_{kim}_{task_id}"
    )
    keyboard.button(
        text="◀️ Назад к заданию",
        callback_data=f"task_{kim}_{task_id}"
    )

    keyboard.adjust(2, 1)
    return keyboard.as_markup()
