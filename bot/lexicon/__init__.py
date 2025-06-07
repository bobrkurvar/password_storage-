from pydantic import BaseModel
from .core_lexicon import COMMAND_CORE
from .user_lexicon import AUTHENTICATION, ACCOUNTS

class Phrases(BaseModel):
    start: str = COMMAND_CORE['start']
    help: str = COMMAND_CORE['help']
    login: str = AUTHENTICATION['login']
    password: str = AUTHENTICATION['password']
    accounts: str = ACCOUNTS['list']
    resource: str = ACCOUNTS['resource']
    resource_password: str = ACCOUNTS['password']

phrases = Phrases()