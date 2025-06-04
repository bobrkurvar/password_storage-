from aiogram import Bot, Dispatcher
import asyncio
from core import conf
from bot.handlers import main_router

async def main():
    token = conf.BOT_TOKEN
    bot = Bot(token=token)
    dp = Dispatcher()
    dp.include_router(main_router)
    await dp.start_polling(bot)
if __name__ == '__main__':
    asyncio.run(main())
