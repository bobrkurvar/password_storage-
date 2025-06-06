from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker
from sqlalchemy import select, update
from sqlalchemy.exc import IntegrityError, SQLAlchemyError
from web.exceptions import CustomDbException
from functools import wraps
import logging

log = logging.getLogger('app.db')

def handle_db_operation(func):
    @wraps(func)
    async def wrapper(self, model, *args, **kwargs):
        try:
            return await func(self, model, *args, **kwargs)
        except IntegrityError as err:
            raise CustomDbException(message='данный пользователь уже создан',
                                  detail=' '.join(err.detail), status_code=200)
        except SQLAlchemyError:
            raise CustomDbException(message='ошибка на сторорне быза данных', detail='ошибка на сторорне быза данных',
                                  status_code=500)
    return wrapper

class Crud:
    def __init__(self, url):
        self._engine = create_async_engine(url)
        self._session = async_sessionmaker(self._engine)

    @handle_db_operation
    async def create(self, model, **kwargs):
        async with self._session.begin() as session:
            tup = model(**kwargs)
            session.add(tup)
            return tup.id

    @handle_db_operation
    async def delete(self, model, ident):
        async with self._session.begin() as session:
            for_remove = await session.get(model, ident)
            await session.delete(for_remove)

    @handle_db_operation
    async def update(self, model, ident: str, ident_val: int, **kwargs):
        async with self._session.begin() as session:
            query = update(model).where(getattr(model, ident) == ident_val).values(**kwargs)
            await session.execute(query)

    @handle_db_operation
    async def read(self, model, limit: int, offset: int | None = None, **ident):
        async with self._session.begin() as session:
            query = select(model)
            for key, val in ident:
                if hasattr(model, key):
                    query = query.filter(getattr(model, key) == val)
            if limit:
                query = query.limit(limit)
            if offset:
                query = query.offset(offset)
            res = (await session.execute(query)).scalars()
            return [r.to_dict() for r in res]

    async def close_and_dispose(self):
        await self._engine.dispose()

if __name__ == "__main__":
    import asyncio
    from bot.utils import ext_api_manager
    async def main():
        await ext_api_manager.connect()
        todos = list(await ext_api_manager.read(prefix='todo', ident='doer_id', ident_val=1295347345, limit=3, offset=3))
        print(todos)
    asyncio.run(main())

