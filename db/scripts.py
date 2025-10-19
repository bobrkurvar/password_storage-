import asyncio
import db.models as md
from db import get_db_manager
from sqlalchemy import select
import logging

log = logging.getLogger(__name__)

class DataInit:
    """
    Класс содержащий информацию и методы для заполнения таблиц
    сопоставления roles и actions
    """
    def __init__(self):
        self.actions = ['read', 'update', 'create', 'delete']
        self.roles = ['admin', 'user', 'moderator']

    async def generate(self, out_session):
        log.debug("out_session: %s", out_session)
        roles_in_db = await out_session.execute(select(md.Roles))
        actions_in_db = await out_session.execute(select(md.Actions))
        for role in self.roles:
            role_obj = md.Roles(role_name=role)
            if role_obj not in roles_in_db:
                out_session.add(role_obj)
        for action in self.actions:
            action_obj = md.Actions(action_name=action)
            if action_obj not in actions_in_db:
                out_session.add(action_obj)

if __name__ == "__main__":
    async def main():

        initializer = DataInit()
    asyncio.run(main())