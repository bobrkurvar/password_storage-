from aiogram import Router
from . import command_core, user, account
from aiogram.utils.callback_answer import CallbackAnswerMiddleware
from bot.utils.middleware import DeleteUsersMessageMiddleware, AuthMiddleware

main_router = Router()
account.router.callback_query.outer_middleware(AuthMiddleware())
main_router.include_routers(command_core.router, user.router, account.router)

main_router.callback_query.outer_middleware(CallbackAnswerMiddleware())
main_router.message.outer_middleware(DeleteUsersMessageMiddleware())