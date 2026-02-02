from aiogram import Router, F
from aiogram.filters import Command
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from client_bot.middlewares import admin_only
from client_bot.keyboards_admin import (
    get_admin_menu_keyboard,
    get_admin_solutions_list_keyboard,
    get_admin_solution_actions_keyboard,
    get_cancel_keyboard,
    get_confirm_delete_keyboard,
    get_homeworks_list_keyboard,
    get_homework_actions_keyboard,
    get_confirm_hw_delete_keyboard
)
from backend.crud import SolutionCRUD, HintCRUD, HomeworkCRUD
from client_bot.config import ADMIN_ID
from datetime import datetime

router = Router()


class AddSolutionStates(StatesGroup):
    """Состояния для добавления решения"""
    waiting_for_task_id = State()
    waiting_for_solution = State()
    waiting_for_comment = State()


class SearchSolutionStates(StatesGroup):
    """Состояния для поиска решения"""
    waiting_for_task_id = State()


@router.message(Command("admin"))
@admin_only
async def cmd_admin(message: Message, **kwargs):
    """Открыть админ-панель"""
    await message.answer(
        "🔧 <b>Панель администратора</b>\n\n"
        "Управление эталонными решениями:",
        reply_markup=get_admin_menu_keyboard(),
        parse_mode="HTML"
    )


@router.callback_query(F.data == "admin_menu")
@admin_only
async def show_admin_menu(callback: CallbackQuery, state: FSMContext, **kwargs):
    """Показать админ-меню"""
    await state.clear()

    await callback.message.edit_text(
        "🔧 <b>Панель администратора</b>\n\n"
        "Управление эталонными решениями:",
        reply_markup=get_admin_menu_keyboard(),
        parse_mode="HTML"
    )
    await callback.answer()


@router.callback_query(F.data == "admin_add_solution")
@admin_only
async def start_add_solution(callback: CallbackQuery, state: FSMContext, **kwargs):
    """Начать процесс добавления решения"""
    await state.set_state(AddSolutionStates.waiting_for_task_id)

    await callback.message.edit_text(
        "➕ <b>Добавление решения</b>\n\n"
        "Шаг 1/3: Введите Task ID задачи:",
        reply_markup=get_cancel_keyboard(),
        parse_mode="HTML"
    )
    await callback.answer()


@router.message(AddSolutionStates.waiting_for_task_id)
@admin_only
async def process_task_id(message: Message, state: FSMContext, **kwargs):
    """Обработать Task ID"""
    try:
        task_id = int(message.text.strip())
        await state.update_data(task_id=task_id)
        await state.set_state(AddSolutionStates.waiting_for_solution)

        await message.answer(
            f"✅ Task ID: <code>{task_id}</code>\n\n"
            "Шаг 2/3: Отправьте текст решения (код):",
            reply_markup=get_cancel_keyboard(),
            parse_mode="HTML"
        )
    except ValueError:
        await message.answer(
            "❌ Неверный формат. Введите числовой Task ID:",
            reply_markup=get_cancel_keyboard()
        )


@router.message(AddSolutionStates.waiting_for_solution)
@admin_only
async def process_solution(message: Message, state: FSMContext, **kwargs):
    """Обработать текст решения"""
    solution = message.text

    await state.update_data(solution=solution)
    await state.set_state(AddSolutionStates.waiting_for_comment)

    await message.answer(
        f"✅ Решение получено ({len(solution)} символов)\n\n"
        "Шаг 3/3: Введите комментарий к решению\n"
        "или отправьте '-' для пропуска:",
        reply_markup=get_cancel_keyboard(),
        parse_mode="HTML"
    )


@router.message(AddSolutionStates.waiting_for_comment)
@admin_only
async def process_comment(message: Message, state: FSMContext, **kwargs):
    """Обработать комментарий и сохранить решение"""
    comment = message.text.strip()

    if comment == '-':
        comment = None

    data = await state.get_data()
    task_id = data['task_id']
    solution = data['solution']

    # Сохранение в БД
    result = SolutionCRUD.add_solution(task_id, solution, comment)

    await state.clear()

    text = (
        "✅ <b>Решение успешно добавлено!</b>\n\n"
        f"🆔 ID решения: <code>{result.id}</code>\n"
        f"📝 Task ID: <code>{task_id}</code>\n"
        f"📊 Длина: {len(solution)} символов\n"
    )

    if comment:
        text += f"💬 Комментарий: {comment}\n"

    await message.answer(
        text,
        reply_markup=get_admin_menu_keyboard(),
        parse_mode="HTML"
    )


@router.callback_query(F.data == "admin_cancel")
@admin_only
async def cancel_admin_action(callback: CallbackQuery, state: FSMContext, **kwargs):
    """Отменить действие администратора"""
    await state.clear()

    await callback.message.edit_text(
        "❌ Действие отменено",
        reply_markup=get_admin_menu_keyboard()
    )
    await callback.answer()


@router.callback_query(F.data == "admin_list_solutions")
@admin_only
async def list_all_solutions(callback: CallbackQuery, **kwargs):
    """Показать все решения"""
    solutions = SolutionCRUD.get_all_solutions()

    if not solutions:
        await callback.message.edit_text(
            "📋 <b>Список решений</b>\n\n"
            "❌ В базе нет решений",
            reply_markup=get_admin_menu_keyboard(),
            parse_mode="HTML"
        )
        await callback.answer()
        return

    await callback.message.edit_text(
        f"📋 <b>Список решений</b>\n\n"
        f"Всего: {len(solutions)}\n\n"
        f"Выберите решение:",
        reply_markup=get_admin_solutions_list_keyboard(solutions),
        parse_mode="HTML"
    )
    await callback.answer()


@router.callback_query(F.data.startswith("admin_list_page_"))
@admin_only
async def navigate_solutions_list(callback: CallbackQuery, **kwargs):
    """Навигация по страницам списка решений"""
    page = int(callback.data.split("_")[-1])
    solutions = SolutionCRUD.get_all_solutions()

    await callback.message.edit_text(
        f"📋 <b>Список решений</b>\n\n"
        f"Всего: {len(solutions)}\n"
        f"Страница: {page + 1}\n\n"
        f"Выберите решение:",
        reply_markup=get_admin_solutions_list_keyboard(solutions, page),
        parse_mode="HTML"
    )
    await callback.answer()


@router.callback_query(F.data.startswith("admin_view_solution_"))
@admin_only
async def view_solution_admin(callback: CallbackQuery, **kwargs):
    """Просмотр решения с действиями администратора"""
    solution_id = int(callback.data.split("_")[-1])
    solution = SolutionCRUD.get_solution_by_id(solution_id)

    if not solution:
        await callback.answer("❌ Решение не найдено", show_alert=True)
        return

    text = (
        f"📝 <b>Решение #{solution.id}</b>\n\n"
        f"🆔 Task ID: <code>{solution.task_id}</code>\n"
        f"📅 Создано: {solution.created_at.strftime('%d.%m.%Y %H:%M')}\n"
    )

    if solution.comment:
        text += f"💬 Комментарий: <i>{solution.comment}</i>\n"

    text += f"\n📄 <b>Решение:</b>\n<pre>{solution.solution}</pre>"

    # Ограничение длины сообщения
    if len(text) > 4000:
        text = text[:3900] + "\n\n... (слишком длинное)</pre>"

    await callback.message.edit_text(
        text,
        reply_markup=get_admin_solution_actions_keyboard(solution_id),
        parse_mode="HTML"
    )
    await callback.answer()


@router.callback_query(F.data.startswith("admin_delete_"))
@admin_only
async def confirm_delete_solution(callback: CallbackQuery, **kwargs):
    """Подтверждение удаления решения"""
    solution_id = int(callback.data.split("_")[-1])
    solution = SolutionCRUD.get_solution_by_id(solution_id)

    if not solution:
        await callback.answer("❌ Решение не найдено", show_alert=True)
        return

    text = (
        f"⚠️ <b>Подтверждение удаления</b>\n\n"
        f"Вы действительно хотите удалить решение?\n\n"
        f"🆔 ID: {solution.id}\n"
        f"📝 Task ID: {solution.task_id}\n"
    )

    if solution.comment:
        text += f"💬 {solution.comment}\n"

    await callback.message.edit_text(
        text,
        reply_markup=get_confirm_delete_keyboard(solution_id),
        parse_mode="HTML"
    )
    await callback.answer()


@router.callback_query(F.data.startswith("admin_confirm_delete_"))
@admin_only
async def delete_solution(callback: CallbackQuery, **kwargs):
    """Удалить решение"""
    solution_id = int(callback.data.split("_")[-1])

    if SolutionCRUD.delete_solution(solution_id):
        await callback.message.edit_text(
            "✅ <b>Решение удалено</b>",
            reply_markup=get_admin_menu_keyboard(),
            parse_mode="HTML"
        )
        await callback.answer("Решение удалено")
    else:
        await callback.answer("❌ Ошибка удаления", show_alert=True)


@router.callback_query(F.data == "admin_search_solutions")
@admin_only
async def start_search_solutions(callback: CallbackQuery, state: FSMContext, **kwargs):
    """Начать поиск решений по Task ID"""
    await state.set_state(SearchSolutionStates.waiting_for_task_id)

    await callback.message.edit_text(
        "🔍 <b>Поиск решений</b>\n\n"
        "Введите Task ID для поиска:",
        reply_markup=get_cancel_keyboard(),
        parse_mode="HTML"
    )
    await callback.answer()


@router.message(SearchSolutionStates.waiting_for_task_id)
@admin_only
async def process_search_task_id(message: Message, state: FSMContext, **kwargs):
    """Обработать поиск по Task ID"""
    try:
        task_id = int(message.text.strip())
        solutions = SolutionCRUD.get_solutions_by_task_id(task_id)

        await state.clear()

        if not solutions:
            await message.answer(
                f"❌ Для задачи <code>{task_id}</code> не найдено решений",
                reply_markup=get_admin_menu_keyboard(),
                parse_mode="HTML"
            )
            return

        text = (
            f"🔍 <b>Результаты поиска</b>\n\n"
            f"Task ID: <code>{task_id}</code>\n"
            f"Найдено решений: {len(solutions)}\n\n"
        )

        for idx, sol in enumerate(solutions, 1):
            comment = sol.comment[:30] + "..." if sol.comment and len(sol.comment) > 30 else sol.comment or "Без комментария"
            text += f"{idx}. ID: {sol.id} | {comment}\n"

        await message.answer(
            text,
            reply_markup=get_admin_solutions_list_keyboard(solutions),
            parse_mode="HTML"
        )

    except ValueError:
        await message.answer(
            "❌ Неверный формат. Введите числовой Task ID:",
            reply_markup=get_cancel_keyboard()
        )

@router.callback_query(F.data == "admin_view_hints")
@admin_only
async def view_user_hints(callback: CallbackQuery, **kwargs):
    """Просмотр последних подсказок пользователей"""
    # Получаем последние 10 подсказок из БД
    try:
        # Получаем все подсказки и группируем по пользователям
        from backend.database import get_db, Hint
        db = get_db()

        try:
            # Получаем последние 10 подсказок
            hints = db.query(Hint).order_by(Hint.created_at.desc()).limit(10).all()

            if not hints:
                await callback.message.edit_text(
                    "📊 <b>Подсказки пользователей</b>\n\n"
                    "Пока нет ни одной подсказки.",
                    reply_markup=get_admin_menu_keyboard(),
                    parse_mode="HTML"
                )
                await callback.answer()
                return

            text = "💡 <b>Последние 10 подсказок:</b>\n\n"

            for idx, hint in enumerate(hints, 1):
                # Форматируем дату
                date_str = hint.created_at.strftime("%d.%m %H:%M")

                # Тип подсказки
                hint_type_emoji = "🎯" if hint.hint_type == "start" else "🔍"
                hint_type_text = "Начало" if hint.hint_type == "start" else "Анализ"

                # Оценка
                if hint.was_helpful is None:
                    helpful_emoji = "⏳"
                elif hint.was_helpful:
                    helpful_emoji = "✅"
                else:
                    helpful_emoji = "❌"

                # Текст подсказки (первые 50 символов)
                hint_preview = hint.hint_text[:50] + "..." if len(hint.hint_text) > 50 else hint.hint_text

                text += (
                    f"{idx}. {hint_type_emoji} <b>{hint_type_text}</b> | Task {hint.task_id}\n"
                    f"   👤 User ID: <code>{hint.user_id}</code>\n"
                    f"   📅 {date_str} | {helpful_emoji}\n"
                    f"   💬 {hint_preview}\n\n"
                )

            await callback.message.edit_text(
                text,
                reply_markup=get_admin_menu_keyboard(),
                parse_mode="HTML"
            )
        finally:
            db.close()

    except Exception as e:
        print(f"Error viewing hints: {e}")
        await callback.message.edit_text(
            "❌ Ошибка при загрузке подсказок.",
            reply_markup=get_admin_menu_keyboard(),
            parse_mode="HTML"
        )

    await callback.answer()


@router.callback_query(F.data == "admin_hint_stats")
@admin_only
async def view_hint_stats(callback: CallbackQuery, **kwargs):
    """Просмотр статистики по подсказкам"""
    try:
        # Получаем статистику за последние 7 дней
        stats = HintCRUD.get_hint_stats(days=7)

        # Вычисляем процент полезных подсказок
        if stats['helpful'] + stats['not_helpful'] > 0:
            helpful_percent = round(
                stats['helpful'] / (stats['helpful'] + stats['not_helpful']) * 100,
                1
            )
        else:
            helpful_percent = 0

        text = (
            f"📊 <b>Статистика подсказок</b>\n"
            f"За последние {stats['days']} дней\n\n"
            f"📝 Всего подсказок: <b>{stats['total']}</b>\n"
            f"✅ Полезных: <b>{stats['helpful']}</b>\n"
            f"❌ Не полезных: <b>{stats['not_helpful']}</b>\n"
            f"⏳ Без оценки: <b>{stats['not_rated']}</b>\n\n"
            f"📈 Процент полезных: <b>{helpful_percent}%</b>"
        )

        await callback.message.edit_text(
            text,
            reply_markup=get_admin_menu_keyboard(),
            parse_mode="HTML"
        )
    except Exception as e:
        print(f"Error viewing hint stats: {e}")
        await callback.message.edit_text(
            "❌ Ошибка при загрузке статистики.",
            reply_markup=get_admin_menu_keyboard(),
            parse_mode="HTML"
        )

    await callback.answer()


class AddHomeworkStates(StatesGroup):
    """Состояния для добавления домашней работы"""
    waiting_for_kim = State()
    waiting_for_title = State()


@router.callback_query(F.data == "admin_manage_homeworks")
@admin_only
async def manage_homeworks(callback: CallbackQuery, **kwargs):
    """Управление домашними работами"""
    homeworks = HomeworkCRUD.get_all_homeworks()

    if not homeworks:
        text = "📚 <b>Управление домашними работами</b>\n\nСписок пуст."
    else:
        text = f"📚 <b>Управление домашними работами</b>\n\nВсего: {len(homeworks)}\n\n"
        text += "✅ - активна | 🔒 - закрыта"

    await callback.message.edit_text(
        text,
        reply_markup=get_homeworks_list_keyboard(homeworks),
        parse_mode="HTML"
    )
    await callback.answer()


@router.callback_query(F.data.startswith("admin_hw_view_"))
@admin_only
async def view_homework(callback: CallbackQuery, **kwargs):
    """Просмотр домашней работы"""
    kim = int(callback.data.split("_")[-1])
    homework = HomeworkCRUD.get_homework_by_kim(kim)

    if not homework:
        await callback.answer("❌ Домашняя работа не найдена", show_alert=True)
        return

    status = "✅ Активна" if homework.is_active else "🔒 Закрыта"
    title = homework.title or f"KIM {homework.kim}"

    text = (
        f"📚 <b>{title}</b>\n\n"
        f"KIM: <code>{homework.kim}</code>\n"
        f"Статус: {status}\n"
        f"Создана: {homework.created_at.strftime('%d.%m.%Y %H:%M')}\n\n"
        f"Выберите действие:"
    )

    await callback.message.edit_text(
        text,
        reply_markup=get_homework_actions_keyboard(homework.kim, homework.is_active),
        parse_mode="HTML"
    )
    await callback.answer()


@router.callback_query(F.data.startswith("admin_hw_toggle_"))
@admin_only
async def toggle_homework(callback: CallbackQuery, **kwargs):
    """Переключить статус домашней работы"""
    kim = int(callback.data.split("_")[-1])
    homework = HomeworkCRUD.toggle_homework_status(kim)

    if not homework:
        await callback.answer("❌ Ошибка", show_alert=True)
        return

    status = "открыт" if homework.is_active else "закрыт"
    await callback.answer(f"✅ Доступ {status}", show_alert=True)

    # Обновляем сообщение
    await view_homework(callback)


@router.callback_query(F.data.startswith("admin_hw_delete_"))
@admin_only
async def delete_homework_confirm(callback: CallbackQuery, **kwargs):
    """Подтверждение удаления домашней работы"""
    kim = int(callback.data.split("_")[-1])
    homework = HomeworkCRUD.get_homework_by_kim(kim)

    if not homework:
        await callback.answer("❌ Домашняя работа не найдена", show_alert=True)
        return

    title = homework.title or f"KIM {homework.kim}"

    text = (
        f"⚠️ <b>Подтверждение удаления</b>\n\n"
        f"Вы уверены, что хотите удалить:\n"
        f"<b>{title}</b> (KIM: {homework.kim})?"
    )

    await callback.message.edit_text(
        text,
        reply_markup=get_confirm_hw_delete_keyboard(kim),
        parse_mode="HTML"
    )
    await callback.answer()


@router.callback_query(F.data.startswith("admin_hw_confirm_delete_"))
@admin_only
async def delete_homework(callback: CallbackQuery, **kwargs):
    """Удалить домашнюю работу"""
    kim = int(callback.data.split("_")[-1])

    if HomeworkCRUD.delete_homework(kim):
        await callback.answer("✅ Домашняя работа удалена", show_alert=True)
        await manage_homeworks(callback)
    else:
        await callback.answer("❌ Ошибка при удалении", show_alert=True)


@router.callback_query(F.data == "admin_hw_add")
@admin_only
async def add_homework_start(callback: CallbackQuery, state: FSMContext, **kwargs):
    """Начать добавление домашней работы"""
    await state.set_state(AddHomeworkStates.waiting_for_kim)

    await callback.message.edit_text(
        "➕ <b>Добавление домашней работы</b>\n\n"
        "Введите KIM (ID варианта):",
        reply_markup=get_cancel_keyboard(),
        parse_mode="HTML"
    )
    await callback.answer()


@router.message(AddHomeworkStates.waiting_for_kim)
async def add_homework_kim(message: Message, state: FSMContext):
    """Получить KIM для новой домашней работы"""
    try:
        kim = int(message.text)

        # Проверяем, не существует ли уже
        if HomeworkCRUD.get_homework_by_kim(kim):
            await message.answer(
                "❌ Домашняя работа с таким KIM уже существует!",
                reply_markup=get_cancel_keyboard()
            )
            return

        await state.update_data(kim=kim)
        await state.set_state(AddHomeworkStates.waiting_for_title)

        await message.answer(
            "Введите название работы (или отправьте /skip для пропуска):",
            reply_markup=get_cancel_keyboard()
        )

    except ValueError:
        await message.answer(
            "❌ Неверный формат. Введите числовой KIM:",
            reply_markup=get_cancel_keyboard()
        )


@router.message(AddHomeworkStates.waiting_for_title, Command("skip"))
async def add_homework_skip_title(message: Message, state: FSMContext):
    """Пропустить название"""
    data = await state.get_data()
    kim = data.get('kim')

    # Создаем домашнюю работу без названия
    homework = HomeworkCRUD.add_homework(kim=kim, is_active=True)

    await state.clear()

    await message.answer(
        f"✅ Домашняя работа добавлена!\n\n"
        f"KIM: {homework.kim}\n"
        f"Статус: ✅ Активна",
        reply_markup=get_admin_menu_keyboard(),
        parse_mode="HTML"
    )


@router.message(AddHomeworkStates.waiting_for_title)
async def add_homework_title(message: Message, state: FSMContext):
    """Получить название для новой домашней работы"""
    data = await state.get_data()
    kim = data.get('kim')
    title = message.text

    # Создаем домашнюю работу
    homework = HomeworkCRUD.add_homework(kim=kim, title=title, is_active=True)

    await state.clear()

    await message.answer(
        f"✅ Домашняя работа добавлена!\n\n"
        f"Название: {homework.title}\n"
        f"KIM: {homework.kim}\n"
        f"Статус: ✅ Активна",
        reply_markup=get_admin_menu_keyboard(),
        parse_mode="HTML"
    )


@router.callback_query(F.data == "admin_cancel", AddHomeworkStates)
@admin_only
async def cancel_add_homework(callback: CallbackQuery, state: FSMContext, **kwargs):
    """Отменить добавление домашней работы"""
    await state.clear()
    await manage_homeworks(callback)
