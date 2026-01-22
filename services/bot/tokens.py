import logging
from bot.lexicon import phrases
from shared import MyExternalApiForBot
from enum import Enum

class TokenStatus(Enum):
    SUCCESS = "success"
    NEED_PASSWORD = "need_password"
    NEED_REGISTRATION = "need_registration"

log = logging.getLogger(__name__)

async def token_get_flow(ext_api_manager: MyExternalApiForBot, user_id: int, password: str | None = None):
    text = phrases.start
    buttons = ("MENU",)
    status = TokenStatus.SUCCESS
    token = None
    log.debug("PASSWORD IN BOT: %s", password)
    try:
        token = await ext_api_manager.token(user_id, password)
        if not token:
            if password is not None:
                text = "Неправильный пароль"
                buttons = ("MENU", "SIGN IN")
            else:
                text = phrases.login
                status = TokenStatus.NEED_PASSWORD
    except:
        log.debug("USER NOT REGISTER")
        text = phrases.register
        status = TokenStatus.NEED_REGISTRATION

    return token, text, buttons, status


