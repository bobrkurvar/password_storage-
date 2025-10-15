from aiogram import Router
from aiogram.utils.callback_answer import CallbackAnswerMiddleware

from bot.utils.middleware import AuthMiddleware, DeleteUsersMessageMiddleware

from . import account, command_core, user

main_router = Router()
account.router.callback_query.middleware(AuthMiddleware())
main_router.include_routers(command_core.router, user.router, account.router)

main_router.callback_query.outer_middleware(CallbackAnswerMiddleware())
main_router.message.outer_middleware(DeleteUsersMessageMiddleware())
