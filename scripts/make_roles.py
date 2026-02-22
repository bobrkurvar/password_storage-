import asyncio
import logging

from app.adapters.crud import get_db_manager
from app.domain import AlreadyExistsError, Role

log = logging.getLogger(__name__)
manager = get_db_manager()

_ROLES = ["admin", "user"]


async def add_roles():
    manager.connect()
    for role in _ROLES:
        try:
            await manager.create(Role, role_name=role)
        except AlreadyExistsError:
            log.debug("role %s already exists", role)


if __name__ == "__main__":
    log.debug("старт создания ролей")
    asyncio.run(add_roles())
    log.debug("конец создания ролей")
