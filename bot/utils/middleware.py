import logging
from typing import Any, Awaitable, Callable

from aiogram import BaseMiddleware
from aiogram.types import CallbackQuery, Message, TelegramObject

from bot.lexicon import phrases
from bot.utils.keyboards import get_inline_kb

log = logging.getLogger(__name__)


class AuthMiddleware(BaseMiddleware):
    async def __call__(
        self,
        handler: Callable[[CallbackQuery, dict[str, Any]], Awaitable[Any]],
        event: CallbackQuery,
        data: dict[str, Any],
    ):
        state, ext_api_manager = data.get("state"), data.get("ext_api_manager")
        access_token = await state.storage.get_token(state.key, "access_token")
        if not access_token:
            log.info("access token не существует")
            refresh_token = await state.storage.get_token(state.key, "refresh_token")
            access_time = 900
            if refresh_token:
                log.info("refresh token существует")
                refresh_time = 86400 * 7
                tokens = await ext_api_manager.refresh(refresh_token)
                await state.storage.set_token(
                    state.key,
                    token_name="access_token",
                    token_value=tokens.get("access_token"),
                    ttl=access_time,
                )
                await state.storage.set_token(
                    state.key,
                    token_name="refresh_token",
                    token_value=tokens.get("refresh_token"),
                    ttl=refresh_time,
                )
                return await handler(event, data)
            else:
                log.info("refresh token не существует")
                buttons = ("SIGN IN", "SIGN UP")
                kb = get_inline_kb(*buttons)
                await event.message.edit_text(text=phrases.start, reply_markup=kb)
        else:
            log.info("access token существует")
            return await handler(event, data)


class DeleteUsersMessageMiddleware(BaseMiddleware):
    async def __call__(
        self,
        handler: Callable[[Message, dict[str, Any]], Awaitable[Any]],
        event: Message,
        data: dict[str, Any],
    ):
        result = await handler(event, data)
        await event.delete()
        return result


class FetchUserInfo(BaseMiddleware):
    async def __call__(
        self,
        handler: Callable[[TelegramObject, dict[str, Any]], Awaitable[Any]],
        event: TelegramObject,
        data: dict[str, Any],
    ):
        state, ext_api_manager = data.get("state"), data.get("ext_api_manager")
        user_salt = (await state.get_data()).get("user_salt", None)
        if user_salt is None:
            user = await ext_api_manager.read("user", ident=event.from_user.id)
            log.debug("User: %s", user)
            if user is not None:
                user_salt = user.get("salt")
                await state.update_data(user_salt=user_salt)
        result = await handler(event, data)
        return result
