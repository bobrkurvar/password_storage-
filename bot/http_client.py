import logging
from functools import wraps

from aiohttp import ClientResponseError, ClientSession
from aiohttp.client_exceptions import ClientConnectorError

from bot.services.exceptions import UnauthorizedError, UnlockStorageError
from core import conf

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

    async def auth(self, user_id: int, password: str | None = None):
        async with self._session.post(
            self._url + "auth", json={"user_id": user_id, "password": password}
        ) as resp:
            if resp.status == 401:
                raise UnauthorizedError
            if resp.status == 409:
                raise UnauthorizedError(True)
            resp.raise_for_status()
            return await resp.json()

    async def sign_up(self, user_id: int | None, username: str | None, password: str):
        async with self._session.post(
            self._url + "user",
            json={"user_id": user_id, "username": username, "password": password},
        ) as resp:
            try:
                resp.raise_for_status()
                return await resp.json()
            except ClientResponseError:
                return None

    async def read_user(
        self, user_id: int | None = None, access_token: str | None = None
    ):
        headers = {"Authorization": f"Bearer {access_token}"}
        path = (
            self._url + f"user/{user_id}" if user_id is not None else self._url + "user"
        )
        async with self._session.get(path, headers=headers) as resp:
            try:
                resp.raise_for_status()
                return await resp.json()
            except ClientResponseError:
                return None


    async def read_own_account(self, access_token: str):
        headers = {"Authorization": f"Bearer {access_token}"}
        async with self._session.get(
            self._url + "accounts", headers=headers
        ) as resp:
            resp.raise_for_status()
            return await resp.json()


    async def master_key(self, access_token: str, password: str):
        headers = {"Authorization": f"Bearer {access_token}"}
        async with self._session.post(
            self._url + "auth/master-key", headers=headers, data=password
        ) as resp:
            if resp.status == 403:
                raise UnauthorizedError
            resp.raise_for_status()
            return await resp.json()

    async def create_account(
        self,
        access_token: str,
        account_name: str,
        password: str,
        params: list,
    ):
        headers = {"Authorization": f"Bearer {access_token}"}
        async with self._session.post(
            self._url + "accounts",
            json={
                "name": account_name,
                "params": params,
                "password": password,
            },
            headers=headers,
        ) as resp:
            if resp.status == 403:
                raise UnlockStorageError
            resp.raise_for_status()
            return await resp.json()

    async def delete_account(self, access_token: str, account_id: int):
        headers = {"Authorization": f"Bearer {access_token}"}
        async with self._session.delete(
            self._url + f"accounts/{account_id}",
            headers=headers,
        ) as resp:
            resp.raise_for_status()
            return await resp.json()


    async def search_full_text(self, access_token: str, search_query: str, **filters):
        headers = {"Authorization": f"Bearer {access_token}"}
        filters.update(name=search_query)
        async with self._session.get(
            self._url + "accounts/search",
            json=filters,
            headers=headers,
        ) as resp:
            resp.raise_for_status()
            return await resp.json()


    async def connect(self):
        if not self._session:
            self._session = ClientSession()

    async def close(self):
        if self._session:
            log.warning(f"закрываю сессию {self.__class__.__name__}")
            await self._session.close()
            self._session = None


host = conf.api_host
ext_api_manager = MyExternalApiForBot(f"http://{host}:8000/")
