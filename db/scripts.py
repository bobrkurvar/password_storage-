import logging
from contextlib import asynccontextmanager

from sqlalchemy import select
from sqlalchemy.exc import SQLAlchemyError

from db import get_db_manager
from db.models import Actions, AdminUser, Roles

log = logging.getLogger(__name__)


class DataInit:
    """
    Класс содержащий информацию и методы для заполнения таблиц
    сопоставления roles и actions
    """

    def __init__(self):
        self.actions = ["read", "update", "create", "delete"]
        self.roles = ["admin", "user", "moderator"]
        self.manager = get_db_manager()
        self.admins = [1295347345]

    @asynccontextmanager
    async def session_scope(self):
        try:
            async with self.manager._session_factory.begin() as session:
                yield session
        except SQLAlchemyError:
            pass

    async def seed_roles(self):
        async with self.session_scope() as session:
            roles_in_db = await session.execute(select(Roles))
            for role in self.roles:
                role_obj = Roles(role_name=role)
                if role_obj not in roles_in_db:
                    session.add(role_obj)

    async def seed_actions(self):
        async with self.session_scope() as session:
            actions_in_db = await session.execute(select(Actions))
            for action in self.actions:
                action_obj = Actions(action_name=action)
                if action_obj not in actions_in_db:
                    session.add(action_obj)

    async def seed_admins(self):
        async with self.session_scope() as session:
            for admin_id in self.admins:
                admin_obj = AdminUser(id=admin_id)
                session.add(admin_obj)


if __name__ == "__main__":
    import asyncio

    async def main():
        initializer = DataInit()
        await initializer.seed_roles()
        await initializer.seed_actions()
        await initializer.seed_admins()

    asyncio.run(main())
