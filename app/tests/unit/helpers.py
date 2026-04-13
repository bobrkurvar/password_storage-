import jwt

from app.infra.tokens import TokensManager
from core import conf


def get_tokens(
    access_data: dict | None = None,
    refresh_data: dict | None = None,
):
    token_manager = TokensManager()
    access_data = {} if access_data is None else access_data
    access_token = token_manager.create_access_token(access_data)
    refresh_data = {} if refresh_data is None else refresh_data
    refresh_token = token_manager.create_refresh_token(refresh_data)
    return access_token, refresh_token


def decode_token(token: str):
    return jwt.decode(token, conf.secret_key, [conf.algorithm])
