from fastapi import FastAPI

from app.models import init_db
from app.routes import collections_routes
from app.routes import instances_routes
from app.routes import item_routes
from app.routes import projects_routes

app = FastAPI()


# initialize database
@app.on_event("startup")
def on_startup():
    init_db()


# register routes
app.include_router(collections_routes.router)
app.include_router(instances_routes.router)
app.include_router(item_routes.router)
app.include_router(projects_routes.router)


@app.get("/")
def read_root():
    return {"message": "Hello, AR World!"}
