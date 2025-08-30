from aiogram.fsm.state import StatesGroup, State
from aiogram.fsm.storage.base import StorageKey
from aiogram.fsm.storage.redis import RedisStorage
from typing import Optional

class InputUser(StatesGroup):
    sign_in = State()
    sign_up = State()

class InputAccount(StatesGroup):
    name = State()
    password = State()

class CustomRedisStorage(RedisStorage):
    async def set_data(self, key: StorageKey, data: dict) -> None:
        await super().set_data(key, data)

        data_key = f"fsm:{key.user_id}:{key.chat_id}:data"
        if self.state_ttl:
            await self.redis.expire(data_key, self.state_ttl)

    async def update_data(self, key, data: dict, *, ttl: Optional[int] = None):
        await super().update_data(key, data)
        if ttl is not None:
            data_key = f"fsm:{key.user_id}:{key.chat_id}:data"
            await self.redis.expire(data_key, ttl)

    async def set_state(self, key: StorageKey, state: str) -> None:
        await super().set_state(key, state)
        state_key = f"fsm:{key.user_id}:{key.chat_id}:state"
        if self.state_ttl:
            await self.redis.expire(state_key, self.state_ttl)