import asyncio
import logging
from contextlib import asynccontextmanager

from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.fsm.storage.redis import RedisStorage

from bot.handlers import main_router
from bot.http_client import ext_api_manager
from core import conf
from core.logger import setup_logging
from shared.adapters.queue_client import RabbitMQClient
from shared.adapters.redis import get_redis_client, get_redis_service

bot = Bot(conf.bot_token, default=DefaultBotProperties(parse_mode=ParseMode.HTML))
log = logging.getLogger(__name__)


@asynccontextmanager
async def init_all():
    # rmq_client = RabbitMQClient()
    # await rmq_client.connect("logs_queue")
    rmq_client = None
    await setup_logging("bot", rmq_client)
    redis_client = get_redis_client()
    redis_conn = await redis_client.init_redis()
    redis_service = get_redis_service(prefix="front", redis_conn=redis_conn)
    if redis_conn:
        redis_service.init_conn(redis_conn)
        storage = RedisStorage(redis=redis_conn, state_ttl=3600)
    else:
        log.error("не удалось поключиться к redis, использую MemoryStorage для FSM")
        storage = MemoryStorage()
    dp = Dispatcher(storage=storage)
    await ext_api_manager.connect()
    dp["ext_api_manager"] = ext_api_manager
    dp["redis_service"] = redis_service
    dp.include_router(main_router)
    await dp.start_polling(bot)
    log.debug("НАЧАЛО РАБОТА БОТА")

    yield
    # await rmq_client.close()
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
