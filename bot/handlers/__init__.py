from aiogram import Router
from . import command_core, user, account

main_router = Router()
main_router.include_router(command_core.router)
main_router.include_router(user.router)
main_router.include_router(account.router)