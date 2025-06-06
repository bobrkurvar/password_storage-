from aiogram import Router
from . import command_core
from . import user

main_router = Router()
main_router.include_router(command_core.router)
main_router.include_router(user.router)