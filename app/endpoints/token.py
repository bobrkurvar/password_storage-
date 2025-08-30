import logging
from fastapi import APIRouter, status, HTTPException
from core.security import create_access_token, verify, create_refresh_token
from app.endpoints.schemas.user import UserInput, OutputToken
from db import DbManagerDep
from db.models import User
from core.security import getUserFromTokenDep


router = APIRouter(tags=['Token',])
log = logging.getLogger(__name__)

@router.post('/login', status_code=status.HTTP_200_OK, summary='аутентификация пользователя', response_model=OutputToken)
async def login_user(user: UserInput, manager: DbManagerDep):
    cur = (await manager.read(model=User, ident='id', ident_val=user.id))[0]
    if not cur:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='user not found')
    log.info(cur.get('password'))
    if verify(user.password, cur.get('password')):
        access_token = create_access_token({'sub': str(user.id)})
        refresh_token = create_refresh_token({'sub': str(user.id)})
        return {"access_token": access_token, 'refresh_token': refresh_token}
    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='user not found')

@router.post('/refresh', status_code=status.HTTP_200_OK, summary='обновление access и refresh токенов', response_model=OutputToken)
async def update_tokens(user_id: getUserFromTokenDep, manager: DbManagerDep):
    cur = (await manager.read(model=User, ident='id', ident_val=int(user_id)))[0]
    if cur:
        access_token = create_access_token({'sub': user_id, 'type': 'access'})
        refresh_token = create_refresh_token({'sub': user_id, 'type': 'refresh'})
        return {"access_token": access_token, 'refresh_token': refresh_token}
    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='user not found')