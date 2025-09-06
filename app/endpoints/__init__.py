from fastapi import APIRouter
from . import user, account, token, params

main_router = APIRouter()
main_router.include_router(user.router, prefix='/user')
main_router.include_router(account.router, prefix='/account')
main_router.include_router(token.router)
main_router.include_router(params.router, prefix='/account/params')