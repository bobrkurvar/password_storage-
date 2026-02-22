from bot.services.exceptions import UnauthorizedError, UnlockStorageError


class HttpClient:
    def __init__(self, registration=True, password=False):
        self.registration = registration
        self.password = password

    async def auth(self, *args, **kwargs):
        raise UnauthorizedError(self.registration)

    async def create_account(self, *args, **kwargs):
        raise UnlockStorageError(self.password)
