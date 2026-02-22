from bot.services import AuthStage


class AuthError(Exception):
    def __init__(self, status: AuthStage):
        self.status = status
        super().__init__(self)


class UnlockStorageError(Exception):
    def __init__(self, password: bool = False):
        self.password = password
        super().__init__(self)


class UnauthorizedError(Exception):
    def __init__(self, registration: bool = False):
        self.registration = registration
        super().__init__(self)
