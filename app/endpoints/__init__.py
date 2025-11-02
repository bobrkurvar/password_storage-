from fastapi import APIRouter, status

from app.exceptions.schemas import ErrorResponse

from . import accounts, params, token, user

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
main_router.include_router(user.router)
main_router.include_router(params.router, prefix="/account/params")
main_router.include_router(accounts.router)
main_router.include_router(token.router)
