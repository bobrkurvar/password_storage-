import logging

import pytest
import pytest_asyncio
from httpx import ASGITransport, AsyncClient

from core.security import create_access_token
from db import get_db_manager
from main_app import app

from .fakes import FakeCrud

log = logging.getLogger(__name__)


@pytest_asyncio.fixture
async def async_client():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://") as ac:
        yield ac


@pytest_asyncio.fixture
async def fake_manager():
    manager = FakeCrud()
    app.dependency_overrides[get_db_manager] = lambda: manager
    yield manager
    manager.clear()
    app.dependency_overrides.clear()


@pytest.mark.asyncio
@pytest.mark.parametrize(
    "id_, user_id",
    [
        (1111, 32),
        (33333, 32),
    ],
)
async def test_create_account_unauthorized_error(
    id_: int, user_id: int, fake_manager: FakeCrud, async_client
):
    log.info("Storage Before: %s", fake_manager.__class__.storage)
    response = await async_client.post("/account", json={"id": id_, "user_id": user_id})
    data = response.json()
    log.info("Data: %s", data)
    log.info("Storage After: %s", fake_manager.__class__.storage)
    assert response.status_code == 401
    assert (
        data["detail"]
        == "Попытка не аутентифицированного доступа, не валидные учётные данные"
    )
    assert data["code"] == 401


@pytest.mark.asyncio
@pytest.mark.parametrize(
    "id_, user_id",
    [
        (1111, 31),
        (33333, 32),
    ],
)
async def test_create_account_authorized_success(
    id_: int, user_id: int, fake_manager: FakeCrud, async_client
):
    log.info("Storage Before: %s", fake_manager.__class__.storage)
    token = create_access_token({"sub": str(user_id)})
    response = await async_client.post(
        "/account",
        json={"id": id_, "user_id": user_id},
        headers={"Authorization": f"Bearer {token}"},
    )
    data = response.json()
    log.info("Data: %s", data)
    log.info("Storage After: %s", fake_manager.__class__.storage)
    assert response.status_code == 201
