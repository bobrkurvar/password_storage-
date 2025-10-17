import asyncio
import db.models as md
from db import get_db_manager

class DataInit:
    """
    Класс содержащий информацию и методы для заполнения таблиц
    сопоставления roles и actions
    """
    def __init__(self):
        self.actions = ['read', 'update', 'create', 'delete']
        self.role = ['admin', 'user', 'moderator']
        self.manager = get_db_manager()

    async def generate(self):
