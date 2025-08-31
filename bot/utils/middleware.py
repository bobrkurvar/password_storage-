from aiogram.types import Message, CallbackQuery
from aiogram import BaseMiddleware
from typing import Callable, Any, Awaitable
from bot.utils.keyboards import get_inline_kb
from bot.lexicon import phrases
import logging


log = logging.getLogger(__name__)

class AuthMiddleware(BaseMiddleware):
    async def __call__(self,
                       handler: Callable[[CallbackQuery, dict[str, Any]], Awaitable[Any]],
                       event: CallbackQuery,
                       data: dict[str, Any]):
        state, ext_api_manager = data.get('state'), data.get('ext_api_manager')
        state_data = await state.get_data()
        access_token = state_data.get('access_token')
        if not access_token:
            log.info('access token не существует')
            refresh_token = state_data.get('refresh_token')
            if refresh_token:
                log.info('refresh token существует')
                tokens = await ext_api_manager.refresh(refresh_token)
                data.update(access_token=tokens.get('access_token'), refresh_token=tokens.get('refresh_token'))
                await state.set_state(state_data)
                return await handler(event, data)
            else:
                log.info('refresh token не существует')
                buttons = ('SIGN IN', 'SIGN UP')
                kb = get_inline_kb(*buttons)
                await event.message.edit_text(text=phrases.start, reply_markup=kb)
        else:
            log.info('access token существует')
            return await handler(event, data)

class DeleteUsersMessageMiddleware(BaseMiddleware):
    async def __call__(self,
                       handler: Callable[[Message, dict[str, Any]], Awaitable[Any]],
                       event: Message,
                       data: dict[str, Any]):
        result = await handler(event, data)
        await event.delete()
        return result