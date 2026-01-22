import logging
from repo import get_db_manager
import asyncio
from domain.user import Role

log = logging.getLogger(__name__)
manager = get_db_manager()

async def add_roles():
    await manager.create(Role, [{"role_name": "admin"}, {"role_name": "user"}])

if __name__ == "__main__":
    log.debug("старт создания ролей")
    asyncio.run(add_roles())
    log.debug("конец создания ролей")