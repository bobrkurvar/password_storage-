import logging
import asyncio
from repo import get_db_manager
from domain.user import Admin

log = logging.getLogger(__name__)
manager = get_db_manager()
admins = [1295347345]

async def add_admins():
    admins_ids = [{"id": admin} for admin in admins]
    await manager.create(Admin, admins_ids)


if __name__ == "__main__":
    log.debug("старт добавления админов")
    asyncio.run(add_admins())
    log.debug("конец")
