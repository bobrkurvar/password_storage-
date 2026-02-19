from enum import Enum

class RepositoryError(Exception):
    """Базовое исключение репозитория"""

    pass


class NotFoundError(RepositoryError):
    """Не найдена запись в базе"""

    def __init__(self, entity_name, ident: str | None = None, ident_val=None):
        self.entity_name = entity_name
        self.ident = ident
        self.ident_val = ident_val
        if ident and ident_val:
            super().__init__(f"{entity_name} with {ident} = {ident_val} not found")
        else:
            super().__init__(f"{entity_name} not found")


class AlreadyExistsError(RepositoryError):
    """Запись с таким атрибутом уже существует в базе"""

    def __init__(self, model_name: str, constraint: str):
        self.model_name = model_name
        self.constraint = constraint
        super().__init__(f"{model_name} already exists (constraint: {constraint})")


class CustomForeignKeyViolationError(RepositoryError):
    """Ошибка внешнего ключа"""

    def __init__(self, model_name: str, detail: str):
        self.model_name = model_name
        self.detail = detail
        super().__init__(f"Foreign key violation in {model_name}: {detail}")


class UnauthorizedError(Exception):
    def __init__(self, detail: str):
        self.detail = detail
        super().__init__(self.detail)

class InvalidTokenError(UnauthorizedError):
    def __init__(self, token_type: str):
        self.detail = f"Неправильный {token_type} token"
        super().__init__(self.detail)

class InvalidAccessTokenError(InvalidTokenError):
    def __init__(self):
        super().__init__("access")

class InvalidRefreshTokenError(InvalidTokenError):
    def __init__(self):
        super().__init__("refresh")

class TokenExpireError(UnauthorizedError):
    def __init__(self, token_type: str):
        self.detail = f"Время жизни {token_type} token истекло"
        super().__init__(self.detail)

class AccessTokenExpireError(TokenExpireError):
    def __init__(self):
        super().__init__("access")

class RefreshTokenExpireError(TokenExpireError):
    def __init__(self):
        super().__init__("refresh")

class CredentialsValidateError(UnauthorizedError):
    def __init__(self):
        self.detail = "Не правильные учётные данные"
        super().__init__(self.detail)
