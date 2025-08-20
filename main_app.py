from fastapi import FastAPI
from app.endpoints import main_router
from app.exceptions.handlers import global_exception_handler, custom_exception_handler
from app.exceptions.custom_errors import CustomDbException

app = FastAPI()
app.include_router(main_router)
app.add_exception_handler(Exception, global_exception_handler)
app.add_exception_handler(CustomDbException, custom_exception_handler)