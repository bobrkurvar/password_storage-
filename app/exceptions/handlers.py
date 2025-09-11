import logging

from fastapi import Request, status, HTTPException
from fastapi.encoders import jsonable_encoder
from fastapi.responses import JSONResponse

from app.exceptions.schemas import ErrorResponse

log = logging.getLogger(__name__)
#
# def global_exception_handler(request: Request, exc):
#     # error = jsonable_encoder(
#     #     ErrorResponse(code=exc.status_code, detail=exc.detail)
#     # )
#     # log.error(error['detail'])
#     return JSONResponse(
#         status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
#         content={"error": "Internal server error"},
#     )

def exception_handler_to_error_response(request: Request, exc):
    error = jsonable_encoder(
        ErrorResponse(code=exc.status_code, detail=exc.detail)
    )
    log.error(error['detail'])
    return JSONResponse(status_code=error['code'], content=dict(detail=error['detail'], code=error['code']))