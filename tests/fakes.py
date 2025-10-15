import logging
from db.exceptions import AlreadyExistsError, NotFoundError

log = logging.getLogger(__name__)


class FakeCrud:
    storage = {}

    async def read(self, model, ident: str | None = None, ident_val=None):
        name = model if isinstance(model, str) else model.__name__
        cur_storage = self.__class__.storage.get(name, {})
        if ident is None:
            if ident_val is None:
                res = cur_storage
            else:
                log.debug("Чтение fake_db по id: %s", ident_val)
                res = [i for i in cur_storage if i["id"] == ident_val]
        else:
            res = [i for i in cur_storage if i[ident] == ident_val]

        if res:
            if len(res) == 1:
                res = res[0]
            log.debug("FROM READ RETURN: %s", res)
            return res
        else:
            log.debug(f"ПОЛЬЗОВАТЕЛЬ В ФЭКЕ {name} НЕ НАЙДЕН")
            raise NotFoundError(name, ident, ident_val)

    async def create(self, model, primary: str = "id", **entity):
        name = model if isinstance(model, str) else model.__name__
        cur_storage = self.__class__.storage.get(name)
        if cur_storage is None:
            self.__class__.storage.update({name: list()})
            cur_storage = self.__class__.storage.get(name)
        if any(i[primary] == entity[primary] for i in cur_storage):
            raise AlreadyExistsError(name, field=primary, value=entity[primary])
        log.debug("ФЭК СОЗДАНИЕ %s", entity)
        cur_storage.append(entity)
        return entity

    async def delete(self, model=None, ident: str = "id", ident_val=None):
        name = model.__name__ if model else self.__class__.__name__
        cur_storage = self.__class__.storage.get(name, {})
        if ident_val is None:
            log.debug("ФЭК УДАЛЕНИЕ ВСЕХ ПОЛЬЗОВАТЕЛЕЙ")
            if not cur_storage:
                raise NotFoundError(name)
            cur_storage.pop(name)
            log.debug("ВСЕ ПОЛЬЗОВАТЕЛИ УДАЛЕНЫ")
        else:
            log.debug("ФЭК УДАЛЕНИЕ ПО %s = %s", ident, ident_val)
            flag = True
            for i in cur_storage:
                if i[ident] == ident_val:
                    if flag:
                        flag = False
                    res = i
                    cur_storage.pop(cur_storage.index(i))
                    log.debug("УДАЛЁН %s с %s", res, ident)
                    if ident == "id":
                        return res
            if flag:
                raise NotFoundError(name, ident, ident_val)
            log.debug(
                "ПОЛЬЗОВАТЕЛИ  ПО %s = %s УДАЛЕНЫ, CLASS.STORAGE: %s",
                ident,
                ident_val,
                self.__class__.storage,
            )

    def clear(self):
        self.__class__.storage.clear()
