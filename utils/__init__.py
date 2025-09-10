from core import conf

from .external import MyExternalApiForBot

host = conf.api_host
ext_api_manager = MyExternalApiForBot(f"http://{host}:8000/")
