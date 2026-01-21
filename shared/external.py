import logging
from functools import wraps

from aiohttp import ClientResponseError, ClientSession
from aiohttp.client_exceptions import ClientConnectorError

log = logging.getLogger(__name__)


def handle_ext_api(func):
    @wraps(func)
    async def wrapper(self, *args, **kwargs):
        try:
            return await func(self, *args, **kwargs)
        except ClientConnectorError:
            log.warning("поключение не установлено")

    return wrapper


def add_exception_handler(cls):
    api_methods = ["create", "remove", "read", "update", "login", "refresh"]
    for attr_name in dir(cls):
        attr = getattr(cls, attr_name)
        if attr in api_methods:
            setattr(cls, attr_name, handle_ext_api(attr))
    return cls


@add_exception_handler
class MyExternalApiForBot:
    def __init__(self, url):
        self._url = url
        self._session = None

    async def sign_in(self, user_id: int | None, username: str | None, password: str):
        async with self._session.post(
            self._url + "/user/sign-in", json = {"user_id": user_id, "username": username, "password": password}
        ) as resp:
            try:
                resp.raise_for_status()
                return await resp.json()
            except ClientResponseError:
                return None

    async def sign_up(self, user_id: int | None, username: str | None, password: str):
        async with self._session.post(
            self._url + "/user/sign-up", json = {"user_id": user_id, "username": username, "password": password}
        ) as resp:
            try:
                resp.raise_for_status()
                return await resp.json()
            except ClientResponseError:
                return None

    async def read_user(self, user_id: int):
        headers = {}
        async with self._session.read(
            self._url + f"/user/{user_id}",  headers=headers
        ) as resp:
            try:
                resp.raise_for_status()
                return await resp.json()
            except ClientResponseError:
                return None

    async def create(self, prefix: str, **data):
        try:
            headers = {"Authorization": f"Bearer {data.pop('access_token')}"}
        except KeyError:
            headers = {}
        async with self._session.post(
            self._url + prefix, json=data, headers=headers
        ) as resp:
            try:
                resp.raise_for_status()
                return await resp.json()
            except ClientResponseError:
                return None

    async def remove(self, prefix: str, **data):
        id_ = data.get("ident")
        try:
            headers = {"Authorization": f"Bearer {data.pop('access_token')}"}
        except KeyError:
            headers = {}
        log.debug("ext data: %s", data)
        if (not (id_ is None)) and (len(data) == 1):
            async with self._session.delete(
                self._url + prefix + f"/{id_}", headers=headers
            ):
                pass
        else:
            async with self._session.delete(
                self._url + prefix, params=data, headers=headers
            ):
                pass

    async def read(self, prefix: str, **data):
        id_ = data.get("ident")
        try:
            headers = {"Authorization": f"Bearer {data.pop('access_token')}"}
        except KeyError:
            headers = {}
        try:
            if (not (id_ is None)) and (len(data) == 1):
                async with self._session.get(
                    self._url + prefix + f"/{id_}", headers=headers
                ) as resp:
                    resp.raise_for_status()
                    data = await resp.json()
            else:
                async with self._session.get(
                    self._url + prefix, params=data, headers=headers
                ) as resp:
                    resp.raise_for_status()
                    data = await resp.json()
        except ClientResponseError:
            return None
        return data

    async def update(self, prefix: str, **data):
        ident = data.get("ident")
        if ident is None:
            id_ = data.pop("ident_val", None)
            async with self._session.patch(self._url + prefix + f"/{id_}", data=data):
                pass
        else:
            async with self._session.patch(self._url + prefix, data=data):
                pass

    async def login(self, **kwargs):
        async with self._session.post(self._url + "login", data=kwargs) as resp:
            tokens = await resp.json()
            access_token = tokens.get("access_token")
            refresh_token = tokens.get("refresh_token")
        return {"access_token": access_token, "refresh_token": refresh_token}

    async def refresh(self, refresh_token: str):
        headers = {"Authorization": f"Bearer {refresh_token}"}
        async with self._session.post(self._url + "refresh", headers=headers) as resp:
            return await resp.json()

    async def connect(self):
        if not self._session:
            self._session = ClientSession()

    async def close(self):
        if self._session:
            log.warning(f"закрываю сессию {self.__class__.__name__}")
            await self._session.close()
            self._session = None
