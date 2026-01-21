from core import conf

from .external import MyExternalApiForBot
from shared.redis import init_redis

host = conf.api_host
ext_api_manager = MyExternalApiForBot(f"http://{host}:8000/")
