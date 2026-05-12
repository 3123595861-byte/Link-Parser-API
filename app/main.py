from fastapi import FastAPI
from app.api.endpoints import router

app = FastAPI(
    title = "Link Parser API",
    version = "0.1.0"
)

app.include_router(router)