from .keyboards import get_inline_kb
from .external import ExternalApi
from .password_hashing import get_hash_from_pas

ext_api_manager = ExternalApi('http://127.0.0.1:8000/')
