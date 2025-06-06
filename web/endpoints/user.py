from fastapi import APIRouter
from core.security import getUserFromTokenDep
from web.endpoints.schemas.user import UserInput, OutputUser
from db import manager
from db.models import User

router = APIRouter()

@router.post('/create', response_model=OutputUser)
async def user_register(user: UserInput):
    print(user.model_dump())
    user_id = await manager.create(model=User, **user.model_dump())
    return user_id

@router.get('/auth')
async def user_auth(user_id: int, token: getUserFromTokenDep):
    pass

