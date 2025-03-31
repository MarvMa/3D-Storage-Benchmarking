import os
from contextlib import asynccontextmanager

from app.models import init_db

from fastapi import FastAPI

from app.routes import item_routes


@asynccontextmanager
async def lifespan(fast_api: FastAPI):
    if os.getenv("STORAGE_BACKEND") == "db":
        await init_db()
    yield


app = FastAPI(lifespan=lifespan)

app.include_router(item_routes.router)  # app.include_router(projects_routes.router)
