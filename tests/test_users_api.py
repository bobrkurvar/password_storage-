import logging

import pytest
import pytest_asyncio
from httpx import ASGITransport, AsyncClient

from db import get_db_manager
from main_app import app
from tests.fakes import FakeCrud

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


@pytest_asyncio.fixture
async def fake_manager_with_user(fake_manager):
    await fake_manager.create(model="User", id=1111, username="Alice", password="asdf")
    return fake_manager


@pytest.mark.asyncio
@pytest.mark.parametrize(
    "id_, username, password",
    [
        (1111, "Alice", "asdf"),
        (33333, "Charlie", "sdfsdf"),
    ],
)
async def test_create_user_success(id_, username, password, fake_manager, async_client):
    log.info("Storage Before: %s", fake_manager.storage)
    response = await async_client.post(
        "/user", json={"id": id_, "username": username, "password": password}
    )
    data = response.json()
    log.info("Data: %s", data)
    log.info("Storage After: %s", fake_manager.storage)
    assert response.status_code == 201
    assert data["username"] == username
    assert data["id"] == id_
    assert any(i["id"] == id_ for i in fake_manager.__class__.storage.get("User"))


@pytest.mark.asyncio
async def test_create_user_duplicate_error(fake_manager_with_user, async_client):
    log.debug("FAKE STORAGE: %s", fake_manager_with_user.__class__.storage)
    response = await async_client.post(
        "/user", json={"id": 1111, "username": "Alice", "password": "asdf"}
    )
    data = response.json()
    log.debug("DATA %s", data)
    assert response.status_code == 409
    assert data["code"] == 409
    assert data["detail"] == "Запись с id = 1111 в таблице User уже существует"
    assert (
        sum(
            1
            for u in fake_manager_with_user.__class__.storage.get("User")
            if u["id"] == 1111
        )
        == 1
    )


@pytest.mark.asyncio
async def test_delete_user_by_id_success(fake_manager_with_user, async_client):
    log.debug("FAKE_MANAGER STORAGE: %s", fake_manager_with_user.__class__.storage)
    response = await async_client.delete(f"/user/{1111}")
    data = response.json()
    assert response.status_code == 200
    assert data["id"] == 1111
    assert data["username"] == "Alice"


@pytest.mark.asyncio
@pytest.mark.parametrize(
    "id_, username, password",
    [
        (1111, "Alice", "asdf"),
        (33333, "Charlie", "sdfsdf"),
    ],
)
async def test_delete_user_by_id_not_exists_entity_error(
    id_, username, password, fake_manager, async_client
):
    log.debug("FAKE_MANAGER STORAGE: %s", fake_manager.storage)
    response = await async_client.delete(f"/user/{id_}")
    data = response.json()
    assert response.status_code == 404
    assert data["code"] == 404
