from aiogram import Router
from . import command_core

main_router = Router()
main_router.include_router(command_core.router)