from contextlib import asynccontextmanager

from fastapi import FastAPI

from app.models import init_db
from app.routes import collections_routes
from app.routes import instances_routes
from app.routes import item_routes
from app.routes import projects_routes


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup-Logik: init_db() wird beim Start der Anwendung aufgerufen
    init_db()
    yield
    # Hier könntest du auch eine Shutdown-Logik einfügen, falls nötig


app = FastAPI(lifespan=lifespan)

# register routes
app.include_router(collections_routes.router)
app.include_router(instances_routes.router)
app.include_router(item_routes.router)
app.include_router(projects_routes.router)
