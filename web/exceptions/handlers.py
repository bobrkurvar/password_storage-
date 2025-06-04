from fastapi.encoders import jsonable_encoder
from fastapi.responses import JSONResponse
from fastapi import Request, status
from web.exceptions.schemas import CustomExceptionModel
import logging

def custom_exception_handler(request: Request, exc):
    log = logging.getLogger('proj.app.except')
    error = jsonable_encoder(CustomExceptionModel(status_code=exc.status_code,
                                                  er_message=exc.message,
                                                  er_details=exc.detail))
    log.exception(error['er_message'])
    return JSONResponse(status_code=exc.status_code, content=error)


# def request_validation_exception_handler(request, exc):
#     return JSONResponse(
#         status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
#         content={"message": "Invalid input", "errors": exc.errors()}
#     )
#
def global_exception_handler(request: Request, exc):
    log = logging.getLogger('proj.app.db')
    log.exception("Internal server error")
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={"error": "Internal server error"}
    )