import logging

from sqlalchemy import select

from db import get_db_manager
from db.models import Actions, Roles

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

    async def seed(self):
        async with self.manager._session_factory.begin() as session:
            roles_in_db = await session.execute(select(Roles))
            actions_in_db = await session.execute(select(Actions))
            for role in self.roles:
                role_obj = Roles(role_name=role)
                if role_obj not in roles_in_db:
                    session.add(role_obj)
            for action in self.actions:
                action_obj = Actions(action_name=action)
                if action_obj not in actions_in_db:
                    session.add(action_obj)


if __name__ == "__main__":
    import asyncio

    async def main():
        initializer = DataInit()
        await initializer.seed()

    asyncio.run(main())
