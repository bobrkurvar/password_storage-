from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker
from sqlalchemy import select, update, delete
import logging


log = logging.getLogger(__name__)

class Crud:
    def __init__(self, url):
        self._engine = create_async_engine(url)
        self._session = async_sessionmaker(self._engine)

    async def create(self, model, **kwargs):
        async with self._session.begin() as session:
            tup = model(**kwargs)
            session.add(tup)
            return tup.id

    async def delete(self, model, ident = None, ident_val = None):
        async with self._session.begin() as session:
            if ident:
                for_remove = await session.get(model, ident)
                await session.delete(for_remove)
                return getattr(for_remove, ident)
            else:
                await session.execute(delete(model))


    async def update(self, model, ident: str, ident_val: int, **kwargs):
        async with self._session.begin() as session:
            query = update(model).where(getattr(model, ident) == ident_val).values(**kwargs)
            await session.execute(query)

    async def read(self, model, ident: str | None = None, ident_val: int | None = None, limit: int | None = None, offset: int | None = None,
                   order_by: str | None = None):
        async with self._session.begin() as session:
            query = select(model)
            if ident:
                query = query.where(getattr(model, ident) == ident_val)
            if order_by:
                log.debug('сортировка по %s', order_by)
                query = query.order_by(getattr(model, order_by))
            if offset:
                query = query.offset(offset)
            if limit:
                query = query.limit(limit)
            res = (await session.execute(query)).scalars()
            return [r.model_dump() for r in res]

    async def close_and_dispose(self):
        await self._engine.dispose()


