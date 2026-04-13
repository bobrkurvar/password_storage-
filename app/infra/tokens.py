import logging
from datetime import datetime, timedelta, timezone
import jwt
from app.domain.exceptions import InvalidRefreshTokenError, RefreshTokenExpireError
from core import conf

log = logging.getLogger(__name__)
secret_key = conf.secret_key
algorithm = conf.algorithm


class TokensManager:
    def __init__(self):
        self._access_token_life_time = timedelta(minutes=15)
        self._refresh_token_life_time = timedelta(minutes=15)

    @property
    def access_token_lifetime(self):
        return datetime.now(timezone.utc) + self._access_token_life_time

    @property
    def refresh_token_lifetime(self):
        return datetime.now(timezone.utc) + self._refresh_token_life_time

    def create_access_token(self, data: dict) -> str:
        to_encode = data.copy()
        to_encode.update({"exp": self.access_token_lifetime, "type": "access"})
        return jwt.encode(to_encode, secret_key, algorithm)

    def create_refresh_token(self, data: dict) -> str:
        to_encode = data.copy()
        to_encode.update({"exp": self.refresh_token_lifetime, "type":"refresh"})
        return jwt.encode(to_encode, secret_key, algorithm=algorithm)

    @staticmethod
    def get_payload(token):
        return jwt.decode(token, conf.secret_key, algorithms=conf.algorithm)

    @staticmethod
    def check_refresh_token(refresh_token: str, my_id: int):
        try:
            payload = jwt.decode(refresh_token, secret_key, algorithms=[algorithm])
        except jwt.ExpiredSignatureError:
            raise RefreshTokenExpireError
        except jwt.InvalidTokenError as exc:
            log.exception("ошибка декодирования refresh токена")
            raise InvalidRefreshTokenError from exc
        if payload.get("type") != "refresh":
            raise InvalidRefreshTokenError
        if payload.get("sub") != str(my_id):
            raise InvalidRefreshTokenError

