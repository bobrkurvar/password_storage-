from fastapi.encoders import jsonable_encoder
from fastapi.responses import JSONResponse
from fastapi import Request, status
from app.exceptions.schemas import CustomExceptionModel
from utils import ext_api_manager
import logging


log = logging.getLogger(__name__)

def custom_exception_handler(request: Request, exc):
    error = jsonable_encoder(CustomExceptionModel(status_code=exc.status_code,
                                                  er_message=exc.message,
                                                  er_details=exc.detail))
    log.exception(error['er_message'])
    return JSONResponse(status_code=exc.status_code, content=error)

async def token_expire_exception_handler(request: Request, exc):
    log.exception("Access token expire error")
    await ext_api_manager.refresh(prefix='/refresh')


def global_exception_handler(request: Request, exc):
    log.exception("Internal server error")
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={"error": "Internal server error"}
    )