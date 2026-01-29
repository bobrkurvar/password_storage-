import logging
from typing import Annotated

import jwt
from fastapi import Depends, HTTPException, status
from fastapi.security.oauth2 import OAuth2PasswordBearer

from app.adapters.crud import Crud, get_db_manager
from app.domain import Role
from app.domain.exceptions import UnauthorizedError
from core import conf

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/login", auto_error=False)
secret_key = conf.secret_key
algorithm = conf.algorithm
log = logging.getLogger(__name__)


def get_user_from_token(token: Annotated[str, Depends(oauth2_scheme)]):
    log.debug("Starting get_user_from_token")
    try:
        log.debug("token %s", token)
        payload = jwt.decode(token, secret_key, algorithms=algorithm)
        log.debug("Decoded payload: %s", payload)
        user_id = payload.get("sub")
        roles = payload.get("roles")
        if user_id is None:
            log.debug("user_id is None")
            raise UnauthorizedError(validate=True)
        user = {"user_id": int(user_id), "roles": roles}
    except jwt.ExpiredSignatureError:
        raise UnauthorizedError(refresh_token=True)
    except jwt.InvalidTokenError:
        raise UnauthorizedError(access_token=True)
    return user


getUserFromTokenDep = Annotated[dict, Depends(get_user_from_token)]
dbManagerDep = Annotated[Crud, Depends(get_db_manager)]


def make_role_checker(required_role: list):
    async def check_user_roles(manager: dbManagerDep, user: getUserFromTokenDep):
        roles = user.get("roles")
        if "admin" in roles or "moderator" in roles:
            log.debug("управляющая роль проверка роли за базы данных")
            roles = await manager.read(
                Role,
                ident="user_id",
                ident_val=int(user.get("user_id")),
                to_join="users_roles",
            )
            roles = [role.get("role_name") for role in roles]
        log.debug("проверка роли %s на присутствие в %s", roles, required_role)
        log.debug("user role %s", roles)
        if all(role not in required_role for role in roles):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN, detail="не доступно"
            )
        return user

    return check_user_roles
