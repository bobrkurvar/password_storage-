import asyncio
import logging
from contextlib import asynccontextmanager

from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from aiogram.fsm.storage.memory import MemoryStorage

from bot.filters.states import CustomRedisStorage
from bot.handlers import main_router
from core import conf
from shared import ext_api_manager
from shared.redis import get_redis_client

bot = Bot(conf.bot_token, default=DefaultBotProperties(parse_mode=ParseMode.HTML))
log = logging.getLogger(__name__)


@asynccontextmanager
async def init_all():
    redis_client = get_redis_client()
    redis_conn = await redis_client.init_redis()
    if redis_conn:
        storage = CustomRedisStorage(redis=redis_conn, state_ttl=3600)
    else:
        log.error("не удалось поключиться к redis, использую MemoryStorage")
        storage = MemoryStorage()
    dp = Dispatcher(storage=storage)
    await ext_api_manager.connect()
    dp["ext_api_manager"] = ext_api_manager
    dp.include_router(main_router)
    await dp.start_polling(bot)
    log.debug("НАЧАЛО РАБОТА БОТА")

    yield

    if redis_conn:
        await redis_client.close_redis()
    try:
        if ext_api_manager:
            await ext_api_manager.close()
        log.debug("ЗАКРЫТИЕ СОЕДИНЕНИЯ ВНЕШНЕГО API")
    except Exception:
        log.error("ПОДКЛЮЧЕНИЕ НЕ БЫЛО ЗАКРЫТО")


async def main():
    async with init_all():
        pass


if __name__ == "__main__":
    asyncio.run(main())
