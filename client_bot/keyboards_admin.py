from aiogram.types import InlineKeyboardMarkup
from aiogram.utils.keyboard import InlineKeyboardBuilder
from typing import List
from backend.database import Solution


def get_admin_menu_keyboard() -> InlineKeyboardMarkup:
    """Главное меню администратора"""
    keyboard = InlineKeyboardBuilder()

    keyboard.button(
        text="➕ Добавить решение",
        callback_data="admin_add_solution"
    )
    keyboard.button(
        text="📋 Все решения",
        callback_data="admin_list_solutions"
    )
    keyboard.button(
        text="🔍 Поиск по Task ID",
        callback_data="admin_search_solutions"
    )
    keyboard.button(
        text="💡 Подсказки пользователей",
        callback_data="admin_view_hints"
    )
    keyboard.button(
        text="📊 Статистика подсказок",
        callback_data="admin_hint_stats"
    )
    keyboard.button(
        text="📚 Управление домашними работами",
        callback_data="admin_manage_homeworks"
    )
    keyboard.button(
        text="◀️ Вернуться в бот",
        callback_data="main_menu"
    )

    keyboard.adjust(1)
    return keyboard.as_markup()


def get_admin_solution_actions_keyboard(solution_id: int) -> InlineKeyboardMarkup:
    """Клавиатура действий над решением"""
    keyboard = InlineKeyboardBuilder()

    keyboard.button(
        text="🗑️ Удалить",
        callback_data=f"admin_delete_{solution_id}"
    )
    keyboard.button(
        text="✏️ Редактировать",
        callback_data=f"admin_edit_{solution_id}"
    )
    keyboard.button(
        text="◀️ Назад",
        callback_data="admin_list_solutions"
    )

    keyboard.adjust(2, 1)
    return keyboard.as_markup()


def get_admin_solutions_list_keyboard(solutions: List[Solution], page: int = 0, per_page: int = 5) -> InlineKeyboardMarkup:
    """
    Клавиатура со списком решений для администратора

    Args:
        solutions: Список решений
        page: Номер страницы
        per_page: Количество элементов на странице
    """
    keyboard = InlineKeyboardBuilder()

    start_idx = page * per_page
    end_idx = start_idx + per_page
    page_solutions = solutions[start_idx:end_idx]

    for sol in page_solutions:
        task_id = sol.task_id
        comment_preview = sol.comment[:20] + "..." if sol.comment and len(sol.comment) > 20 else sol.comment or "Без комментария"

        keyboard.button(
            text=f"Task {task_id} | {comment_preview}",
            callback_data=f"admin_view_solution_{sol.id}"
        )

    # Навигация по страницам
    nav_buttons = []
    if page > 0:
        nav_buttons.append({
            "text": "⬅️ Назад",
            "callback_data": f"admin_list_page_{page - 1}"
        })

    if end_idx < len(solutions):
        nav_buttons.append({
            "text": "Вперед ➡️",
            "callback_data": f"admin_list_page_{page + 1}"
        })

    for btn in nav_buttons:
        keyboard.button(text=btn["text"], callback_data=btn["callback_data"])

    keyboard.button(
        text="◀️ В админ-меню",
        callback_data="admin_menu"
    )

    keyboard.adjust(1)
    return keyboard.as_markup()


def get_cancel_keyboard() -> InlineKeyboardMarkup:
    """Клавиатура с кнопкой отмены"""
    keyboard = InlineKeyboardBuilder()

    keyboard.button(
        text="❌ Отменить",
        callback_data="admin_cancel"
    )

    return keyboard.as_markup()


def get_confirm_delete_keyboard(solution_id: int) -> InlineKeyboardMarkup:
    """Клавиатура подтверждения удаления"""
    keyboard = InlineKeyboardBuilder()

    keyboard.button(
        text="✅ Да, удалить",
        callback_data=f"admin_confirm_delete_{solution_id}"
    )
    keyboard.button(
        text="❌ Отмена",
        callback_data=f"admin_view_solution_{solution_id}"
    )

    keyboard.adjust(1)
    return keyboard.as_markup()


def get_homeworks_list_keyboard(homeworks: List) -> InlineKeyboardMarkup:
    """Клавиатура со списком домашних работ"""
    keyboard = InlineKeyboardBuilder()

    for hw in homeworks:
        status_emoji = "✅" if hw.is_active else "🔒"
        title = hw.title or f"KIM {hw.kim}"
        keyboard.button(
            text=f"{status_emoji} {title}",
            callback_data=f"admin_hw_view_{hw.kim}"
        )

    keyboard.button(
        text="➕ Добавить новую работу",
        callback_data="admin_hw_add"
    )
    keyboard.button(
        text="◀️ В админ-меню",
        callback_data="admin_menu"
    )

    keyboard.adjust(1)
    return keyboard.as_markup()


def get_homework_actions_keyboard(kim: int, is_active: bool) -> InlineKeyboardMarkup:
    """Клавиатура действий над домашней работой"""
    keyboard = InlineKeyboardBuilder()

    # Кнопка открыть/закрыть доступ
    if is_active:
        keyboard.button(
            text="🔒 Закрыть доступ",
            callback_data=f"admin_hw_toggle_{kim}"
        )
    else:
        keyboard.button(
            text="✅ Открыть доступ",
            callback_data=f"admin_hw_toggle_{kim}"
        )

    keyboard.button(
        text="🗑️ Удалить",
        callback_data=f"admin_hw_delete_{kim}"
    )
    keyboard.button(
        text="◀️ Назад к списку",
        callback_data="admin_manage_homeworks"
    )

    keyboard.adjust(1)
    return keyboard.as_markup()


def get_confirm_hw_delete_keyboard(kim: int) -> InlineKeyboardMarkup:
    """Клавиатура подтверждения удаления домашней работы"""
    keyboard = InlineKeyboardBuilder()

    keyboard.button(
        text="✅ Да, удалить",
        callback_data=f"admin_hw_confirm_delete_{kim}"
    )
    keyboard.button(
        text="❌ Отмена",
        callback_data=f"admin_hw_view_{kim}"
    )

    keyboard.adjust(1)
    return keyboard.as_markup()
