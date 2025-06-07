from pydantic import BaseModel
from .core_lexicon import COMMAND_CORE
from .user_lexicon import AUTHENTICATION, ACCOUNT

class Phrases(BaseModel):
    start: str = COMMAND_CORE['start']
    help: str = COMMAND_CORE['help']
    login: str = AUTHENTICATION['login']
    password: str = AUTHENTICATION['password']
    account_name: str = ACCOUNT['account name']
    account_password: str = ACCOUNT['account password']
    account_created: str = ACCOUNT['account create']

phrases = Phrases()