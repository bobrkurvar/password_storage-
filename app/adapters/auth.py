import logging
from typing import Annotated

import jwt
from fastapi import Depends
from fastapi.security.oauth2 import OAuth2PasswordBearer

from app.adapters.crud import Crud, get_db_manager
from app.domain.exceptions import (AccessTokenExpireError,
                                   InvalidAccessTokenError)
from app.services.tokens import user_info_from_token, user_roles
from app.infra.tokens import TokensManager

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/login", auto_error=False)
log = logging.getLogger(__name__)

tokensManagerDep = Annotated[TokensManager, Depends()]

def get_user_from_token(token: Annotated[str, Depends(oauth2_scheme)], tokens_manager: tokensManagerDep):
    log.debug("Starting get_user_from_token")
    try:
        log.debug("token %s", token)
        user = user_info_from_token(token, tokens_manager)
    except jwt.ExpiredSignatureError:
        raise AccessTokenExpireError
    except jwt.InvalidTokenError:
        raise InvalidAccessTokenError
    return user


getUserFromTokenDep = Annotated[dict, Depends(get_user_from_token)]
dbManagerDep = Annotated[Crud, Depends(get_db_manager)]

def make_role_checker(required_roles: list):
    async def check_user_roles(manager: dbManagerDep, user: getUserFromTokenDep):
        return user_roles(manager, user, required_roles)
    return check_user_roles
