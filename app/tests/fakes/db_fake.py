import logging
from copy import deepcopy
from typing import Any
from app.domain import Role, NotFoundError

log = logging.getLogger(__name__)


def join_users_with_roles(new_table, other_table):
    new_table.columns += ["roles"]
    for row in new_table.rows:
        roles_names = [row["name"] for row in other_table.rows]
        row.update(roles_names = roles_names)


class Table:

    def __init__(
        self,
        name,
        columns: list[str],
        rows: list[dict] | None = None,
        defaults: dict[str, Any] | None = None,
    ):
        self.name = name
        self.columns = columns
        self.rows = rows if rows else []
        self.defaults = defaults

    def __add__(self, other):
        new_table = Table(
            name=self.name,
            columns=self.columns.copy(),
            rows=deepcopy(self.rows),
            defaults=self.defaults,
        )
        if other.name is Role:
            join_users_with_roles(new_table, other)

        return new_table


class FakeStorage:

    def __init__(self):
        self.tables: dict[Any, Table] = {}
        self.to_join = {
            "roles": Role
        }

    def register_tables(self, models: list[Table]):
        for model in models:
            self.tables[model.name] = model

    @staticmethod
    def _add_default(table_column, table, columns):
        columns.update(
            {table_column: (table.defaults[table_column] if table.defaults else None)}
        )
        if isinstance(table.defaults[table_column], int):
            table.defaults[table_column] += 1

    def add(self, model, **row) -> tuple[dict, ...] | dict:
        table = self.tables[model]
        for table_column in table.columns:
            if table_column not in row:
                self._add_default(table_column, table, row)
        table.rows.append(row)
        return row

    def read(
        self, model, to_join=None, distinct=None, limit=None, offset=None, **filters
    ) -> tuple[dict, ...]:
        table = self.tables[model]
        if not table.rows:
            return tuple()

        result = []
        if to_join:
            for t in to_join:
                t = self.to_join.get(t, t)
                t = self.tables[t]
                table = table + t

        for row in table.rows:
            if all(row.get(k) == v for k, v in filters.items()):
                result.append(row)

        if distinct:
            if isinstance(distinct, str):
                distinct = (distinct,)
            seen = set()
            unique_result = []
            for row in result:
                key = tuple(row.get(f) for f in distinct)
                if key not in seen:
                    seen.add(key)
                    unique_result.append(row)
            result = unique_result

        if offset:
            result = result[offset:]
        if limit:
            result = result[:limit]

        return tuple(result)

    def update(self, model, filters, **values):
        table = self.tables[model]
        for i in range(len(table.rows)):
            if all(table.rows[i][f] == v for f, v in filters.items()):
                for k, v in values.items():
                    table.rows[i][k] = v

    def delete(self, model, **filters) -> tuple[dict, ...]:
        table = self.tables[model]
        del_res = []
        for i in range(len(table.rows)):
            if all(table.rows[i][f] == v for f, v in filters.items()):
                del_res.append(table.rows[i])
                del table.rows[i]
        if not del_res:
            raise NotFoundError(model, **filters)
        return tuple(del_res)


class FakeCRUD:
    _session_factory = None

    def __init__(self, storage: FakeStorage):
        self.storage = storage

    async def create(self, model, session=None, **columns) -> tuple[dict, ...] | dict:
        return self.storage.add(model, **columns)

    async def read(
        self,
        model,
        session=None,
        to_join=None,
        distinct=None,
        limit=None,
        offset=None,
        **filters,
    ) -> tuple[dict, ...]:
        return self.storage.read(
            model,
            to_join=to_join,
            distinct=distinct,
            limit=limit,
            offset=offset,
            **filters,
        )

    async def update(self, model, filters: dict, session=None, **values):
        return self.storage.update(model, filters, **values)

    async def delete(self, model, session=None, **filters) -> tuple[dict, ...]:
        return self.storage.delete(model, **filters)


class FakeUoW:
    def __init__(self, *args, **kwargs):
        self.committed = False
        self.session = self  # если session нужен, но не используется

    async def __aenter__(self):
        return self

    async def __aexit__(self, exc_type, exc, tb):
        return False

    async def commit(self):
        self.committed = True
