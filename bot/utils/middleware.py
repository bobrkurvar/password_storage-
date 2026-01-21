import logging
from typing import Any, Awaitable, Callable

from aiogram import BaseMiddleware
from aiogram.types import CallbackQuery, Message, TelegramObject

from bot.lexicon import phrases
from bot.utils.keyboards import get_inline_kb
#from services.bot import check_access_and_refresh_token

log = logging.getLogger(__name__)


class AuthMiddleware(BaseMiddleware):
    async def __call__(
        self,
        handler: Callable[[CallbackQuery, dict[str, Any]], Awaitable[Any]],
        event: CallbackQuery,
        data: dict[str, Any],
    ):
        ext_api_manager = data.get("ext_api_manager")
        has_refresh_or_access = await ext_api_manager.check_tokens(event.from_user.id)
        if not has_refresh_or_access:
            log.info("refresh token не существует")
            buttons = ("SIGN IN", "SIGN UP")
            kb = get_inline_kb(*buttons)
            await event.message.edit_text(text=phrases.start, reply_markup=kb)
        else:
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


# class FetchUserInfo(BaseMiddleware):
#     async def __call__(
#         self,
#         handler: Callable[[TelegramObject, dict[str, Any]], Awaitable[Any]],
#         event: TelegramObject,
#         data: dict[str, Any],
#     ):
#         state, ext_api_manager = data.get("state"), data.get("ext_api_manager")
#         user_salt = (await state.get_data()).get("user_salt", None)
#         if user_salt is None:
#             user = await ext_api_manager.read("user", ident=event.from_user.id)
#             log.debug("User: %s", user)
#             if user is not None:
#                 user_salt = user.get("salt")
#                 await state.update_data(user_salt=user_salt)
#         result = await handler(event, data)
#         return result
#
#
# class FetchAdmins(BaseMiddleware):
#     async def __call__(
#         self,
#         handler: Callable[[TelegramObject, dict[str, Any]], Awaitable[Any]],
#         event: TelegramObject,
#         data: dict[str, Any],
#     ):
#         state, ext_api_manager = data.get("state"), data.get("ext_api_manager")
#         admins = (await state.get_data()).get("admins", None)
#         if admins is None:
#             admins = await ext_api_manager.read(prefix="user/admins")
#             if admins:
#                 admins = [i.get("id") for i in admins]
#         log.debug("admins: %s", admins)
#         await state.update_data(admins=admins)
#         result = await handler(event, data)
#         return result
