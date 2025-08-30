from core import conf
import logging
from aiogram.client.default import DefaultBotProperties
from aiogram import Bot, Dispatcher
from redis.asyncio import Redis
from aiogram.enums import ParseMode
from bot.handlers import main_router
from aiogram.fsm.storage.memory import MemoryStorage
from bot.filters.states import CustomRedisStorage
import asyncio
from utils import ext_api_manager
from redis import exceptions

bot = Bot(conf.bot_token, default=DefaultBotProperties(parse_mode=ParseMode.HTML))
log = logging.getLogger(__name__)

async def main():
    try:
        try:
            host = conf.redis_host
            redis = Redis(host=host)
            await redis.ping()
            storage = CustomRedisStorage(redis=redis, state_ttl=3600)
        except exceptions.ConnectionError:
            log.error('не удалось поключиться к redis, использую MemoryStorage')
            storage = MemoryStorage()
        dp = Dispatcher(storage=storage)
        await ext_api_manager.connect()
        dp['ext_api_manager'] = ext_api_manager
        dp.include_router(main_router)
        await dp.start_polling(bot)
        log.debug('НАЧАЛО РАБОТА БОТА')
    finally:
        try:
            if ext_api_manager:
                await ext_api_manager.close()
            log.debug('ЗАКРЫТИЕ СОЕДИНЕНИЯ ВНЕШНЕГО API')
        except Exception:
            log.error('ПОДКЛЮЧЕНИЕ НЕ БЫЛО ЗАКРЫТО')

if __name__ == "__main__":
    asyncio.run(main())