import logging
from typing import Annotated

from fastapi import APIRouter, Depends, status

from app.endpoints.schemas.user import UserInput, UserOutput, UserRolesOutput
from app.exceptions.schemas import ErrorResponse
from core.security import get_user_from_token
from repo import Crud, get_db_manager
from domain import Role, User

router = APIRouter(tags=["own"])
log = logging.getLogger(__name__)
dbManagerDep = Annotated[Crud, Depends(get_db_manager)]
userFromTokenDep = Annotated[int, Depends(get_user_from_token)]


@router.get(
    "",
    status_code=status.HTTP_200_OK,
    summary="Получение пользователя по id из токена",
    response_model=UserOutput,
    responses={
        status.HTTP_404_NOT_FOUND: {
            "detail": "Пользователь не найден",
            "model": ErrorResponse,
        }
    },
)
async def read_user_by_id(user_id: userFromTokenDep, manager: dbManagerDep):
    user = (await manager.read(User, ident="id", ident_val=user_id))[0]
    log.debug("Пользователь получен %s, %s", user.get("id"), user.get("username"))
    return user
