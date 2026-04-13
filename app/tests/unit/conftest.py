import logging

import pytest

from app.infra.tokens import TokensManager
from core.logger import setup_logging
from app.tests.fakes import FakeCRUD, FakeRedis

setup_logging()
log = logging.getLogger(__name__)


@pytest.fixture
def tokens_manager():
    return TokensManager()


@pytest.fixture
def redis_service():
    return FakeRedis()


@pytest.fixture
def manager():
    return FakeCRUD()
