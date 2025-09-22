import logging
import pytest
from httpx import AsyncClient, ASGITransport

from main_app import app
from db import get_db_manager
from db.exceptions import NotFoundError
from .fakes.fake_crud import FakeCrud


log = logging.getLogger(__name__)
_last_test_func = None

@pytest.fixture()
def fake_manager(request):
    global _last_test_func
    manager = FakeCrud()
    app.dependency_overrides[get_db_manager] = lambda: manager
    yield manager
    current_func = request.node.name
    log.debug('CURRENT TEST: %s', current_func)
    if _last_test_func is None:
        _last_test_func = current_func
    elif _last_test_func != current_func:
        log.debug('ТЕСТ: ДО %s ПОСЛЕ %s', _last_test_func, current_func)
        manager.clear()
        _last_test_func = current_func
    app.dependency_overrides.clear()

@pytest.mark.asyncio
@pytest.mark.parametrize(
    "id_, username, password",
    [
        (1111, "Alice", "asdf"),
        (33333, "Charlie", "sdfsdf"),
    ],
)
async def test_create_user_success(id_, username, password, fake_manager):
    transport = ASGITransport(app=app)
    log.info('Storage Before: %s', fake_manager.storage)
    async with AsyncClient(transport=transport, base_url='http://') as ac:
        response = await ac.post('/user', json={'id': id_, 'username': username, 'password': password})

    data = response.json()
    log.info('Data: %s', data)
    log.info('Storage After: %s', fake_manager.storage)
    assert response.status_code == 201
    assert data["username"] == username
    assert data["id"] == id_

@pytest.mark.asyncio
@pytest.mark.parametrize(
    "id_, username, password",
    [
        (1111, "Alice", "asdf"),
        (1111, "Charlie", "sdfsdf"),
    ],
)
async def test_create_user_duplicate_error(id_, username, password, fake_manager):
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url='http://') as ac:
        try:
            log.debug('FAKE STORAGE: %s', fake_manager.storage)
            await fake_manager.read(ident_val = id_)
            response = await ac.post('/user', json={'id': id_, 'username': username, 'password': password})
            data = response.json()
            log.debug('DATA %s', data)
            assert response.status_code == 409
            assert data['code'] == 409
            assert data['detail'] == 'Запись с id = 1111 в таблице User уже существует'
        except NotFoundError:
            response = await ac.post('/user', json={'id': id_, 'username': username, 'password': password})
            data = response.json()
            assert response.status_code == 201
            assert data['id'] == id_
            assert data['username'] == username

@pytest.mark.asyncio
@pytest.mark.parametrize(
    "id_, username, password",
    [
        (1111, "Alice", "asdf"),
        (33333, "Charlie", "sdfsdf"),
    ],
)
async def test_delete_user_by_id_success(id_, username, password, fake_manager):
    await fake_manager.create(id=id_, username=username, password=password)
    log.debug('FAKE_MANAGER STORAGE: %s', fake_manager.storage)
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url='http://') as ac:
        response = await ac.delete(f'/user/{id_}')
    data = response.json()
    assert response.status_code == 200
    assert data['id'] == id_
    assert data['username'] == username

@pytest.mark.asyncio
@pytest.mark.parametrize(
    "id_, username, password",
    [
        (1111, "Alice", "asdf"),
        (33333, "Charlie", "sdfsdf"),
    ],
)
async def test_delete_user_by_id_not_exists_entity_error(id_, username, password, fake_manager):
    log.debug('FAKE_MANAGER STORAGE: %s', fake_manager.storage)
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url='http://') as ac:
        response = await ac.delete(f'/user/{id_}')
    data = response.json()
    assert response.status_code == 404
    assert data['code'] == 404