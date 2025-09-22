import logging
import pytest
from httpx import AsyncClient, ASGITransport

from core.security import get_user_from_token
from main_app import app
from db import get_db_manager
#from db.exceptions import NotFoundError
from .fakes import FakeCrud, get_fake_user_from_token, create_token


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

@pytest.fixture()
def fake_user_from_token():
    app.dependency_overrides[get_user_from_token] = get_fake_user_from_token
    yield
    app.dependency_overrides.clear()

@pytest.mark.asyncio
@pytest.mark.parametrize(
    "id_, user_id",
    [
        (1111, 32),
        (33333, 32),
    ],
)
async def test_create_account_unauthorized_error(id_: int, user_id: int, fake_manager: FakeCrud):
    transport = ASGITransport(app=app)
    log.info('Storage Before: %s', fake_manager.__class__.storage)
    async with AsyncClient(transport=transport, base_url='http://') as ac:
        response = await ac.post('/account', json={'id': id_, 'user_id': user_id})
    data = response.json()
    log.info('Data: %s', data)
    log.info('Storage After: %s', fake_manager.__class__.storage)
    assert response.status_code == 401
    assert data['detail'] == "Попытка не аутентифицированного доступа, не валидные учётные данные"
    assert data['code'] == 401


@pytest.mark.asyncio
@pytest.mark.parametrize(
    "id_, user_id",
    [
        (1111, 32),
        (33333, 32),
    ],
)
async def test_create_account_authorized_success(id_: int, user_id: int, fake_manager: FakeCrud):
    transport = ASGITransport(app=app)
    log.info('Storage Before: %s', fake_manager.__class__.storage)
    token = create_token({"sub": id_})
    log.debug("TOKEN: %s", token)
    async with AsyncClient(transport=transport, base_url='http://', headers={"Authorization": f"Bearer {token}"}) as ac:
        response = await ac.post('/account', json={'id': id_, 'user_id': user_id})
    data = response.json()
    log.info('Data: %s', data)
    log.info('Storage After: %s', fake_manager.__class__.storage)
    assert response.status_code == 201
