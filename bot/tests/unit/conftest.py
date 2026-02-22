import logging

import pytest

from core.logger import setup_logging

from bot.tests.fakes import FakeRedis, HttpClient

setup_logging()
log = logging.getLogger(__name__)


@pytest.fixture
def fake_redis():
    return FakeRedis()


@pytest.fixture
def get_fake_http_client():
    def fake_http_client(registration=True):
        return HttpClient(registration)

    return fake_http_client
