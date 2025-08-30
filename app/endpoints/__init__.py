from fastapi import APIRouter
from . import user
from . import account
from . import token

main_router = APIRouter()
main_router.include_router(user.router, prefix='/user')
main_router.include_router(account.router, prefix='/account')
main_router.include_router(token.router)