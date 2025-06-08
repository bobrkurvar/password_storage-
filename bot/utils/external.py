from aiohttp import ClientSession
from aiohttp.client_exceptions import ClientConnectorError
import logging
from functools import wraps

log = logging.getLogger('app.bot.utils')

def handle_ext_api(func):
    @wraps(func)
    async def wrapper(self, *args, **kwargs):
        try:
            return await func(self, *args, **kwargs)
        except ClientConnectorError:
            log.warning('поключение не установлено')
    return wrapper

class ExternalApi:
    def __init__(self, url):
        self._url = url
        self._session = None

    @handle_ext_api
    async def create(self, prefix: str, auth: str | None = None, **data):
        headers = {}
        if auth:
            headers.update(Authorization=f'Bearer {auth}')
        res = await self._session.post(self._url+ prefix + '/create', json = data, headers=headers)
        return await res.json()

    @handle_ext_api
    async def remove(self, prefix: str, **args):
        await self._session.delete(self._url + prefix + '/delete', params=args)

    @handle_ext_api
    async def read(self, prefix: str, **kwargs):
        res = await self._session.get(self._url + prefix + '/read', params=kwargs)
        return await res.json()

    @handle_ext_api
    async def update(self, prefix: str, auth: str | None = None, **kwargs):
        headers = {}
        if auth:
            headers.update(Authorization=f'Bearer {auth}')
        await self._session.patch(self._url + prefix + '/update', json=kwargs, headers=headers)

    @handle_ext_api
    async def login(self, prefix: str, **kwargs):
        res = await self._session.post(self._url + prefix + '/login', json=kwargs)
        return await res.json()

    async def connect(self):
        if not self._session:
            self._session = ClientSession()

    async def close(self):
        if self._session:
            log.warning(f'закрываю сессию {self.__class__.__name__}')
            await self._session.close()
            self._session = None

