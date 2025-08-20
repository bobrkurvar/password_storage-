from aiogram.fsm.state import StatesGroup, State
from aiogram.fsm.storage.base import StorageKey
from aiogram.fsm.storage.redis import RedisStorage

class InputUser(StatesGroup):
    user = State()
    new_password = State()
    password = State()

class InputAccount(StatesGroup):
    name = State()
    password = State()

class CustomRedisStorage(RedisStorage):
    async def set_data(self, key: StorageKey, data: dict) -> None:
        await super().set_data(key, data)

        data_key = f"fsm:{key.user_id}:{key.chat_id}:data"
        if self.state_ttl:
            await self.redis.expire(data_key, self.state_ttl)

    async def set_state(self, key: StorageKey, state: str) -> None:
        await super().set_state(key, state)
        state_key = f"fsm:{key.user_id}:{key.chat_id}:state"
        if self.state_ttl:
            await self.redis.expire(state_key, self.state_ttl)