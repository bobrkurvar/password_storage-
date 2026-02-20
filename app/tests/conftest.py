import pytest
from app.services.tokens import create_access_token, create_refresh_token
from datetime import timedelta
from core.logger import setup_logging
import logging
from .fakes import FakeRedis, FakeCRUD, FakeStorage, Table
from app.domain import Role, User

setup_logging()
log = logging.getLogger(__name__)

@pytest.fixture
def get_tokens():
    def token_factory(
            access_data: dict | None = None,
            refresh_data: dict | None = None,
            time_life: timedelta | None = None
    ):
        access_data = {} if access_data is None else access_data
        access_token = create_access_token(access_data, time_life)
        refresh_data = {} if refresh_data is None else refresh_data
        refresh_token = create_refresh_token(refresh_data, time_life)
        return access_token, refresh_token
    return token_factory

@pytest.fixture
def fake_redis():
    return FakeRedis()

@pytest.fixture
def storage():
    storage = FakeStorage()

    storage.register_tables(
        [
            Table(
                name=User,
                columns=["id", "username", "password", "salt"],
                defaults={"id": 1},
            ),
            Table(
                name=Role,
                columns=["name"],
                rows = [{"name": "admin"}]
            )
        ]
    )

    return storage


@pytest.fixture
def fake_db(storage):
    return FakeCRUD(storage)