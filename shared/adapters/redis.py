import json
import logging

from redis.asyncio import ConnectionError, Redis

from core import conf

log = logging.getLogger(__name__)



class RedisClient:
    def __init__(self):
        self.redis = None

    async def init_redis(self) -> Redis | None:
        if self.redis:
            return self.redis
        redis = Redis(host=conf.redis_host)
        try:
            await redis.ping()
            self.redis = redis
            return redis
        except ConnectionError:
            log.debug("У объекта redis закрылось соединение")
            try:
                await redis.close()
                await redis.connection_pool.disconnect()
            except Exception:
                pass

    async def close_redis(self):
        try:
            await self.redis.close()
            await self.redis.connection_pool.disconnect()
        except Exception:
            pass


_redis_client: RedisClient | None = None

def get_redis_client() -> RedisClient:
    global _redis_client
    if _redis_client is None:
        _redis_client = RedisClient()
    return _redis_client


class RedisService:
    def __init__(self, redis=None, prefix: str = ""):
        self.prefix = prefix
        self.redis = redis

    def init_conn(self, redis):
        self.redis = redis

    async def set(
        self,
        key: str,
        value,
        ttl: int | None = None,
    ) -> None:
        key = f"{self.prefix}:{key}"
        await self.redis.set(
            key,
            json.dumps(value),
            ex=ttl,
        )

    async def get(self, key: str):
        key = f"{self.prefix}:{key}"
        value = await self.redis.get(key)
        return json.loads(value) if value else None

    async def delete(self, key: str) -> None:
        key = f"{self.prefix}:{key}"
        await self.redis.delete(key)

    async def pop(self, key: str):
        value = await self.get(key)
        await self.delete(key)
        return value

    async def exists(self, key: str) -> bool:
        key = f"{self.prefix}:{key}"
        return bool(await self.redis.exists(key))

    async def incr(self, key: str) -> int:
        key = f"{self.prefix}:{key}"
        return await self.redis.incr(key)

    async def expire(self, key: str, ttl: int):
        key = f"{self.prefix}:{key}"
        await self.redis.expire(key, ttl)




