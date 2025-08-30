from pydantic import BaseModel
from .core_lexicon import COMMAND_CORE, AUTHENTICATION, ACCOUNT

class Phrases(BaseModel):
    start: str = COMMAND_CORE['start']
    help: str = COMMAND_CORE['help']
    register: str = AUTHENTICATION['register']
    login: str = AUTHENTICATION['login']
    already_reg: str = AUTHENTICATION['already_registered']
    user_not_exists: str = AUTHENTICATION['user_not_exists']
    account_name: str = ACCOUNT['account name']
    account_password: str = ACCOUNT['account password']
    account_created: str = ACCOUNT['account created']
    account_list: str = ACCOUNT['account list']

phrases = Phrases()