from .external import MyExternalApiForBot
from core import conf

host = conf.api_host
ext_api_manager = MyExternalApiForBot(f'http://{host}:8000/')