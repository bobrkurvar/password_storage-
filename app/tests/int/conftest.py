import logging

import pytest
from alembic import command
from alembic.config import Config
from sqlalchemy import text

from app.adapters.crud import get_db_manager
from core import conf


log = logging.getLogger(__name__)



@pytest.fixture
async def manager(request):
    manager = get_db_manager(test=True)
    manager.connect()
    yield manager
    engine = manager._engine
    async with engine.begin() as conn:
        await conn.execute(
            text(
            """
                TRUNCATE
                    users,
                    accounts,
                    params,
                    roles,
                    users_roles,
                    admins,
    
                RESTART IDENTITY CASCADE;
            """
            )
        )
    await manager.close_and_dispose()



@pytest.fixture(scope="session", autouse=True)
def migrate_test_db(request):
    """
    Автоматически применяет все миграции к тестовой БД
    только если тест помечен как интеграционный.
    """
    log.debug("INTERGRATION MIGRATIONS TO %s", conf.test_db_url)
    if not any(
            "integration" in marker.name
            for item in request.session.items
            for marker in item.iter_markers()
    ):
        yield
        return
    alembic_cfg = Config("alembic.ini")
    alembic_cfg.set_main_option("sqlalchemy.url", conf.test_db_url)
    command.upgrade(alembic_cfg, "head")
    yield

