from typing import Callable, Dict, Any, Awaitable
from aiogram import BaseMiddleware
from aiogram.types import Message, CallbackQuery
from client_bot.config import ADMIN_ID


class AdminCheckMiddleware(BaseMiddleware):
    """Middleware для проверки прав администратора"""

    async def __call__(
        self,
        handler: Callable[[Message | CallbackQuery, Dict[str, Any]], Awaitable[Any]],
        event: Message | CallbackQuery,
        data: Dict[str, Any]
    ) -> Any:
        # Добавляем флаг is_admin в данные
        user_id = event.from_user.id
        data['is_admin'] = user_id == ADMIN_ID

        return await handler(event, data)


def admin_only(func):
    """Декоратор для обработчиков доступных только администратору"""
    async def wrapper(event: Message | CallbackQuery, *args, **kwargs):
        user_id = event.from_user.id

        if user_id != ADMIN_ID:
            if isinstance(event, Message):
                await event.answer("❌ У вас нет доступа к этой команде")
            else:
                await event.answer("❌ У вас нет доступа к этой функции", show_alert=True)
            return

        return await func(event, *args, **kwargs)

    return wrapper
