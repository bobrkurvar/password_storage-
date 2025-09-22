import logging
from db.exceptions import NotFoundError, AlreadyExistsError

log = logging.getLogger(__name__)

class FakeCrud:
    storage = None
    def __init__(self):
        if not self.__class__.storage:
            self.__class__.storage = []

    async def read(self, model = None, ident: str | None = None, ident_val = None):
        if ident is None:
            if ident_val is None:
                res = self.__class__.storage
            else:
                log.debug('Чтение fake_db по id: %s', ident_val)
                res = [i for i in self.__class__.storage if i['id'] == ident_val]
        else:
            res = [i for i in self.__class__.storage if i[ident] == ident_val]

        if res:
            log.debug('result fake_crud: %s', res)
            return res if len(res) > 1 else res[0]
        else:
            name = model.__name__ if model else self.__class__.__name__
            raise NotFoundError(name, ident, ident_val)

    async def create(self, model = None, primary: str = 'id', **entity):
        if any(i[primary] == entity[primary] for i in self.__class__.storage):
            name = model.__name__ if model else self.__class__.__name__
            raise AlreadyExistsError(name, field = primary, value = entity[primary])
        log.debug('ФЭК СОЗДАНИЕ %s', entity)
        self.__class__.storage.append(entity)
        return entity

    async def delete(self, model = None, ident: str = 'id', ident_val = None):
        name = model.__name__ if model else self.__class__.__name__
        if ident_val is None:
            log.debug('ФЭК УДАЛЕНИЕ ВСЕХ ПОЛЬЗОВАТЕЛЕЙ')
            if not self.__class__.storage:
                raise NotFoundError(name)
            self.__class__.storage = None
            log.debug('ВСЕ ПОЛЬЗОВАТЕЛИ УДАЛЕНЫ')
        else:
            log.debug('ФЭК УДАЛЕНИЕ ПО %s = %s', ident, ident_val)
            flag = True
            for i in self.__class__.storage:
                if i[ident] == ident_val:
                    if flag: flag = False
                    res = i
                    self.__class__.storage.pop(self.__class__.storage.index(i))
                    log.debug('УДАЛЁН %s с %s', res, ident)
                    if ident == 'id':
                        return res
            if flag:
                raise NotFoundError(name, ident, ident_val)
            log.debug('ПОЛЬЗОВАТЕЛИ  ПО %s = %s УДАЛЕНЫ, CLASS.STORAGE: %s', ident, ident_val, self.__class__.storage)

    def clear(self):
        self.__class__.storage = None
