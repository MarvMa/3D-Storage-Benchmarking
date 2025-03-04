from contextlib import asynccontextmanager
from app.models import init_db

from fastapi import FastAPI

from app.routes import item_routes


@asynccontextmanager
async def lifespan(fast_api: FastAPI):
    init_db()
    yield


app = FastAPI(lifespan=lifespan)

# register routes
# app.include_router(collections_routes.router)
# app.include_router(instances_routes.router)
app.include_router(item_routes.router)
# app.include_router(projects_routes.router)
