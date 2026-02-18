import asyncio
import logging

from app.adapters.crud import get_db_manager
from app.domain import Admin, AlreadyExistsError

log = logging.getLogger(__name__)
manager = get_db_manager()
_ADMINS = [1295347345]


async def add_admins():
    for admin in _ADMINS:
        try:
            manager.connect()
            await manager.create(Admin, id=admin)
        except AlreadyExistsError:
            log.debug("admins %s already exists", admin)


if __name__ == "__main__":
    log.debug("старт добавления админов")
    asyncio.run(add_admins())
    log.debug("конец")
