from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
import asyncio
from core import conf, logger
from bot.handlers import main_router
import logging
from bot.utils import ext_api_manager

log = logging
log.basicConfig(level=logging.DEBUG,
                format='[%(asctime)s] #%(levelname)-8s %(filename)s:%(lineno)d - %(name)s - %(message)s')

async def main():
    try:
        token = conf.BOT_TOKEN
        bot = Bot(token=token, default=DefaultBotProperties(parse_mode=ParseMode.HTML))
        dp = Dispatcher()
        await ext_api_manager.connect()
        dp['ext_api_manager'] = ext_api_manager
        dp.include_router(main_router)
        await dp.start_polling(bot)
    finally:
        try:
            log.info('соединение bot.utils.ext_api_manager закрыто')
            await ext_api_manager.close()
        except:
            log.error('не удалось закрыть соединение bot.utils.ext_api_manager')


if __name__ == '__main__':
    asyncio.run(main())
