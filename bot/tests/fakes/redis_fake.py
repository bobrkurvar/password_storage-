class FakeRedis:
    def __init__(self):
        self.storage = {}

    async def set(self, key: str, value, ttl=None):
        self.storage[key] = value

    async def get(self, key: str):
        return self.storage.get(key, None)
