import logging

from fastapi import Request, status
from fastapi.encoders import jsonable_encoder
from fastapi.responses import JSONResponse

from app.exceptions.schemas import CustomExceptionModel

log = logging.getLogger(__name__)


def custom_exception_handler(request: Request, exc):
    error = jsonable_encoder(
        CustomExceptionModel(
            status_code=exc.status_code, er_message=exc.message, er_details=exc.detail
        )
    )
    log.exception(error["er_message"])
    return JSONResponse(status_code=exc.status_code, content=error)


def global_exception_handler(request: Request, exc):
    log.exception("Internal server error")
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={"error": "Internal server error"},
    )
