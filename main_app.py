from fastapi import FastAPI
from web.endpoints import main_router

app = FastAPI()
app.include_router(main_router)
