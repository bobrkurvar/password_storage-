import logging
from typing import List, Any

from sqlalchemy import delete, join, select, update
from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine

log = logging.getLogger(__name__)


class Crud:
    _engine = None
    _session_factory = None
    def __init__(self, url):
        if self.__class__._engine is None:
            self.__class__._engine = create_async_engine(url)
        if self.__class__._session_factory is None:
            self.__class__._session_factory = async_sessionmaker(self._engine)

    async def create(self, model, seq_data: List[Any], **kwargs):
        async with self._session_factory.begin() as session:
            if seq_data:
                for data in seq_data:
                    tup = model(**data)
                    session.add(tup)
            else:
                tup = model(**kwargs)
                session.add(tup)
            await session.flush()
            return tup.model_dump()

    async def delete(
        self, model, ident: str | None = None, ident_val: int | None = None
    ):
        async with self._session_factory.begin() as session:
            if not (ident is None):
                await session.execute(
                    delete(model).where(getattr(model, ident)) == ident_val
                )
            elif ident is None:
                for_remove = await session.get(model, ident_val)
                await session.delete(for_remove)
                return getattr(for_remove, "id")
            else:
                await session.execute(delete(model))

    async def update(self, model, ident: str, ident_val: int, **kwargs):
        async with self._session_factory.begin() as session:
            query = (
                update(model).where(getattr(model, ident) == ident_val).values(**kwargs)
            )
            await session.execute(query)

    async def read(
        self,
        model,
        ident: str | None = None,
        ident_val: int | None = None,
        limit: int | None = None,
        offset: int | None = None,
        order_by: str | None = None,
        to_join: str | None = None,
    ):
        async with self._session_factory.begin() as session:
            query = select(model)
            if to_join:
                joined_table = getattr(model, to_join)
                query = query.join(joined_table)
            if ident:
                if to_join:
                    query = query.where(
                        getattr(joined_table.property.mapper.class_, ident) == ident_val
                    )
                else:
                    query = query.where(getattr(model, ident) == ident_val)
            if order_by:
                log.debug("сортировка по %s", order_by)
                query = query.order_by(getattr(model, order_by))
            if offset:
                query = query.offset(offset)
            if limit:
                query = query.limit(limit)
            res = (await session.execute(query)).scalars()
            return [r.model_dump() for r in res]

    async def close_and_dispose(self):
        log.debug('подключение к движку %s закрывается', self._engine)
        await self._engine.dispose()
