from datetime import timedelta

import jwt

from app.services.tokens import create_access_token, create_refresh_token
from core import conf

from app.tests.fakes import FakeCRUD


def get_tokens(
    access_data: dict | None = None,
    refresh_data: dict | None = None,
    time_life: timedelta | None = None,
):
    access_data = {} if access_data is None else access_data
    access_token = create_access_token(access_data, time_life)
    refresh_data = {} if refresh_data is None else refresh_data
    refresh_token = create_refresh_token(refresh_data, time_life)
    return access_token, refresh_token


def add_to_table(crud: FakeCRUD, table, row: dict):
    crud.storage.add(table, **row)


def decode_token(token: str):
    return jwt.decode(token, conf.secret_key, [conf.algorithm])
