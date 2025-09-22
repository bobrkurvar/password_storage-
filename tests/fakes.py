import logging
from db.exceptions import NotFoundError, AlreadyExistsError
from app.exceptions.custom_errors import UnauthorizedError
from datetime import timedelta, datetime, timezone
import jwt
from core import conf

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

# class LoginBarer:
#     def __init__(self, secret_key: str, algorithm: str):
#         self.secret_key = secret_key
#         self.algorithm = algorithm
#
#     def create_access_token(self, data: dict, expires_delta: timedelta = None) -> str:
#         to_encode = data.copy()
#         expire = (
#             datetime.now(timezone.utc) + expires_delta
#             if expires_delta
#             else datetime.now(timezone.utc) + timedelta(minutes=15)
#         )
#         to_encode.update({"exp": expire})
#         return jwt.encode(to_encode, self.secret_key, self.algorithm)
#

def create_token(data: dict, expires_delta: timedelta = None) -> str:
    to_encode = data.copy()
    secret_key = conf.secret_key
    algorithm = conf.algorithm
    expire = (
        datetime.now(timezone.utc) + expires_delta
        if expires_delta
        else datetime.now(timezone.utc) + timedelta(minutes=15)
    )
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, secret_key, algorithm)

def get_fake_user_from_token(token: str):
    try:
        log.debug("FAKE GET_USER_FROM_TOKEN")
        secret_key = conf.secret_key
        algorithm = conf.algorithm
        payload = jwt.decode(token, secret_key, algorithms=algorithm)
        user_id = payload.get("sub")
        log.debug("FAKE ID: %s", user_id)
        if user_id is None:
            log.debug("user_id is None")
            raise UnauthorizedError(validate=True)
    except jwt.ExpiredSignatureError:
        raise UnauthorizedError(refresh=True)
    except jwt.InvalidTokenError:
        raise UnauthorizedError(validate=True)
    return user_id