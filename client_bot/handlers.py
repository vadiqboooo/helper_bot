from aiogram import Router, F
from aiogram.filters import Command
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from client_bot.keyboards import (
    get_main_menu_keyboard,
    get_homework_list_keyboard,
    get_homework_detail_keyboard,
    get_tasks_list_keyboard,
    get_task_actions_keyboard,
    get_back_to_task_keyboard,
    get_feedback_keyboard
)
from api.api_client import KompegeAPI
from api.openrouter_client import get_openrouter_client
from backend.crud import SolutionCRUD, HintCRUD, HomeworkCRUD
import html as html_lib

router = Router()


class CodeSubmission(StatesGroup):
    """Состояния для отправки кода"""
    waiting_for_code = State()


@router.message(Command("start"))
async def cmd_start(message: Message, is_admin: bool = False):
    """Обработчик команды /start"""
    text = "👋 Добро пожаловать!\n\n" \
           "Я помогу вам с домашними заданиями по информатике.\n"

    if is_admin:
        text += "\n🔧 Вы - администратор. Используйте /admin для управления решениями.\n"

    text += "\nВыберите действие:"

    await message.answer(
        text,
        reply_markup=get_main_menu_keyboard()
    )


@router.callback_query(F.data == "main_menu")
async def show_main_menu(callback: CallbackQuery):
    """Показать главное меню"""
    await callback.message.edit_text(
        "👋 Добро пожаловать!\n\n"
        "Я помогу вам с домашними заданиями по информатике.\n"
        "Выберите действие:",
        reply_markup=get_main_menu_keyboard()
    )
    await callback.answer()


@router.callback_query(F.data == "homework_list")
async def show_homework_list(callback: CallbackQuery):
    """Показать список домашних работ"""
    # Получаем активные домашние работы из БД
    hw_list = HomeworkCRUD.get_active_homeworks()
    homeworks = []

    for hw in hw_list:
        description = hw.title or KompegeAPI.get_description(hw.kim)
        homeworks.append((hw.kim, description))

    if not homeworks:
        await callback.message.edit_text(
            "❌ Нет доступных домашних работ",
            reply_markup=get_main_menu_keyboard()
        )
    else:
        await callback.message.edit_text(
            "📚 Доступные домашние работы:",
            reply_markup=get_homework_list_keyboard(homeworks)
        )

    await callback.answer()


@router.callback_query(F.data.startswith("homework_") & ~F.data.startswith("homework_list"))
async def show_homework_detail(callback: CallbackQuery):
    """Показать детали конкретной домашней работы"""
    kim = int(callback.data.split("_")[1])

    description = KompegeAPI.get_description(kim)
    tasks = KompegeAPI.get_tasks(kim)

    text = (
        f"📚 <b>{description}</b>\n\n"
        f"🆔 КИМ: <code>{kim}</code>\n"
        f"📝 Количество заданий: {len(tasks)}\n\n"
        f"Выберите действие:"
    )

    await callback.message.edit_text(
        text,
        reply_markup=get_homework_detail_keyboard(kim),
        parse_mode="HTML"
    )
    await callback.answer()


@router.callback_query(F.data.startswith("hints_"))
async def show_tasks_list(callback: CallbackQuery):
    """Показать список заданий для получения подсказок"""
    kim = int(callback.data.split("_")[1])

    tasks = KompegeAPI.get_tasks(kim)

    if not tasks:
        await callback.answer("❌ Не удалось загрузить задания", show_alert=True)
        return

    description = KompegeAPI.get_description(kim)

    text = (
        f"💡 Подсказки для: <b>{description}</b>\n\n"
        f"Выберите задание:"
    )

    await callback.message.edit_text(
        text,
        reply_markup=get_tasks_list_keyboard(kim, tasks),
        parse_mode="HTML"
    )
    await callback.answer()


@router.callback_query(F.data.startswith("task_"))
async def show_task_detail(callback: CallbackQuery):
    """Показать детали задания"""
    parts = callback.data.split("_")
    kim = int(parts[1])
    task_id = int(parts[2])

    tasks = KompegeAPI.get_tasks(kim)
    task = next((t for t in tasks if t.get('taskId') == task_id), None)

    if not task:
        await callback.answer("❌ Задание не найдено", show_alert=True)
        return

    text = (
        f"📋 <b>Задание #{task_id}</b>\n\n"
        f"Выберите действие:"
    )

    await callback.message.edit_text(
        text,
        reply_markup=get_task_actions_keyboard(kim, task_id),
        parse_mode="HTML"
    )
    await callback.answer()


@router.callback_query(F.data.startswith("hint_start_"))
async def show_hint_start(callback: CallbackQuery):
    """Показать подсказку как начать задание"""
    parts = callback.data.split("_")
    kim = int(parts[2])
    task_id = int(parts[3])

    # Получаем задачу
    tasks = KompegeAPI.get_tasks(kim)
    task = next((t for t in tasks if t.get('taskId') == task_id), None)

    if not task:
        await callback.answer("❌ Задача не найдена", show_alert=True)
        return

    # Проверяем наличие эталонных решений
    if not SolutionCRUD.count_solutions_by_task(task_id):
        hint = (
            "💡 <b>Подсказка для начала:</b>\n\n"
            "1. Внимательно прочитайте условие задачи\n"
            "2. Определите входные и выходные данные\n"
            "3. Продумайте алгоритм решения\n"
            "4. Начните с простого примера\n"
            "5. Напишите код пошагово\n\n"
            "Если нужна помощь с кодом - отправьте его для проверки!"
        )
    else:
        # Показываем индикатор загрузки
        await callback.answer("⏳ Генерирую подсказку...")

        # Получаем текст задачи и очищаем HTML
        task_text = html_lib.unescape(task.get('text', ''))

        # Генерируем подсказку через LLM
        try:
            client = get_openrouter_client()
            hint_text = client.generate_start_hint(task_id, task_text)

            # Сохраняем подсказку в БД
            try:
                HintCRUD.add_hint(
                    user_id=callback.from_user.id,
                    task_id=task_id,
                    hint_text=hint_text,
                    hint_type='start'
                )
            except Exception as db_error:
                print(f"DB Error saving hint: {db_error}")

            hint = f"💡 <b>Подсказка для начала:</b>\n\n{hint_text}"
        except Exception as e:
            print(f"LLM Error: {e}")
            hint = (
                "💡 <b>Подсказка для начала:</b>\n\n"
                "1. Внимательно прочитайте условие задачи\n"
                "2. Определите входные и выходные данные\n"
                "3. Продумайте алгоритм решения\n"
                "4. Начните с простого примера\n"
                "5. Напишите код пошагово\n\n"
                "Если нужна помощь с кодом - отправьте его для проверки!"
            )

    await callback.message.edit_text(
        hint,
        reply_markup=get_feedback_keyboard(kim, task_id),
        parse_mode="HTML"
    )
    await callback.answer()


@router.callback_query(F.data.startswith("submit_code_"))
async def request_code_submission(callback: CallbackQuery, state: FSMContext):
    """Запросить отправку кода для проверки"""
    parts = callback.data.split("_")
    kim = int(parts[2])
    task_id = int(parts[3])

    await state.set_state(CodeSubmission.waiting_for_code)
    await state.update_data(kim=kim, task_id=task_id)

    await callback.message.edit_text(
        "📝 <b>Отправка кода</b>\n\n"
        "Отправьте ваш код следующим сообщением.\n"
        "Я проанализирую его и дам подсказки.\n\n"
        "Для отмены отправьте /cancel",
        parse_mode="HTML"
    )
    await callback.answer()


@router.message(CodeSubmission.waiting_for_code, Command("cancel"))
async def cancel_code_submission(message: Message, state: FSMContext):
    """Отменить отправку кода"""
    await state.clear()
    await message.answer(
        "❌ Отправка кода отменена",
        reply_markup=get_main_menu_keyboard()
    )


@router.message(CodeSubmission.waiting_for_code)
async def process_code_submission(message: Message, state: FSMContext):
    """Обработать отправленный код"""
    data = await state.get_data()
    kim = data.get('kim')
    task_id = data.get('task_id')
    code = message.text

    # Получаем задачу
    tasks = KompegeAPI.get_tasks(kim)
    task = next((t for t in tasks if t.get('taskId') == task_id), None)

    if not task:
        await message.answer("❌ Задача не найдена")
        await state.clear()
        return

    # Проверяем наличие эталонных решений
    if not SolutionCRUD.count_solutions_by_task(task_id):
        feedback = (
            "✅ <b>Код получен!</b>\n\n"
            f"📊 Длина кода: {len(code)} символов\n\n"
            "💡 <b>Базовые рекомендации:</b>\n"
            "1. Проверьте граничные случаи\n"
            "2. Убедитесь в правильности типов данных\n"
            "3. Оптимизируйте сложные участки кода\n"
            "4. Добавьте обработку ошибок\n\n"
            "Продолжайте работу над заданием!"
        )
        keyboard = get_task_actions_keyboard(kim, task_id)
    else:
        # Показываем статус
        status_msg = await message.answer("⏳ Анализирую ваш код...")

        # Получаем текст задачи и очищаем HTML
        task_text = html_lib.unescape(task.get('text', ''))

        # Генерируем анализ через LLM
        try:
            client = get_openrouter_client()
            hint = client.analyze_code(task_id, task_text, code)

            # Сохраняем подсказку в БД
            try:
                HintCRUD.add_hint(
                    user_id=message.from_user.id,
                    task_id=task_id,
                    hint_text=hint,
                    hint_type='analyze'
                )
            except Exception as db_error:
                print(f"DB Error saving hint: {db_error}")

            feedback = (
                "🔍 <b>Анализ кода:</b>\n\n"
                f"{hint}\n\n"
                "Попробуйте исправить код и отправьте снова!"
            )
        except Exception as e:
            print(f"LLM Error: {e}")
            feedback = (
                "✅ <b>Код получен!</b>\n\n"
                "❌ Не удалось проанализировать код. Попробуйте позже.\n\n"
                "Продолжайте работу над заданием!"
            )

        keyboard = get_feedback_keyboard(kim, task_id)

        # Удаляем статусное сообщение
        try:
            await status_msg.delete()
        except:
            pass

    await message.answer(
        feedback,
        reply_markup=keyboard,
        parse_mode="HTML"
    )

    await state.clear()


@router.callback_query(F.data.startswith("feedback_yes_"))
async def process_feedback_yes(callback: CallbackQuery):
    """Обработать положительную обратную связь"""
    parts = callback.data.split("_")
    kim = int(parts[2])
    task_id = int(parts[3])

    # Сохраняем положительную оценку подсказки
    try:
        hint = HintCRUD.get_latest_hint_for_user(callback.from_user.id)
        if hint and hint.task_id == task_id:
            HintCRUD.mark_helpful(hint.id, was_helpful=True)
    except Exception as e:
        print(f"DB Error marking hint helpful: {e}")

    await callback.answer("✅ Отлично! Продолжайте в том же духе!", show_alert=True)

    # Возвращаемся к заданию
    text = (
        f"📋 <b>Задание #{task_id}</b>\n\n"
        f"Рады, что подсказка помогла!\n\n"
        f"Выберите действие:"
    )

    await callback.message.edit_text(
        text,
        reply_markup=get_task_actions_keyboard(kim, task_id),
        parse_mode="HTML"
    )


@router.callback_query(F.data.startswith("feedback_no_"))
async def process_feedback_no(callback: CallbackQuery):
    """Обработать отрицательную обратную связь"""
    parts = callback.data.split("_")
    kim = int(parts[2])
    task_id = int(parts[3])

    # Сохраняем отрицательную оценку подсказки
    try:
        hint = HintCRUD.get_latest_hint_for_user(callback.from_user.id)
        if hint and hint.task_id == task_id:
            HintCRUD.mark_helpful(hint.id, was_helpful=False)
    except Exception as e:
        print(f"DB Error marking hint not helpful: {e}")

    await callback.answer(
        "Попробуйте отправить свой код для проверки - мы постараемся помочь точнее!",
        show_alert=True
    )

    # Возвращаемся к заданию
    text = (
        f"📋 <b>Задание #{task_id}</b>\n\n"
        f"Не переживайте! Попробуйте:\n"
        f"1. Отправить свой код для более точной подсказки\n"
        f"2. Перечитать условие задачи\n"
        f"3. Начать с простого примера\n\n"
        f"Выберите действие:"
    )

    await callback.message.edit_text(
        text,
        reply_markup=get_task_actions_keyboard(kim, task_id),
        parse_mode="HTML"
    )
