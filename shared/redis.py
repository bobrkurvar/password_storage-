from redis.asyncio import Redis

from core import conf

host = conf.redis_host
redis = Redis(host=host)
