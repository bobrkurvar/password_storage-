from fastapi import APIRouter, status

from app.endpoints.schemas.errors import ErrorResponse

from . import accounts, accounts_manage, users, users_manage

main_router = APIRouter(
    responses={
        status.HTTP_500_INTERNAL_SERVER_ERROR: {
            "detail": "Unexpected error",
            "model": ErrorResponse,
        },
        status.HTTP_401_UNAUTHORIZED: {
            "detail": "Unauthorized error",
            "model": ErrorResponse,
        },
        status.HTTP_403_FORBIDDEN: {"detail": "Role error", "model": ErrorResponse},
    },
)
main_router.include_router(users.router)
main_router.include_router(accounts.router)
main_router.include_router(users_manage.router)
main_router.include_router(accounts_manage.router)
