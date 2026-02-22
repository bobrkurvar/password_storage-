from bot.services.exceptions import UnauthorizedError, UnlockStorageError


class HttpClient:
    def __init__(self, registration=True):
        self.registration = registration

    async def auth(self, *args, **kwargs):
        raise UnauthorizedError(self.registration)

    async def create_account(self, *args, **kwargs):
        raise UnlockStorageError()

    async def master_key(self, *args, **kwargs):
        raise UnauthorizedError