# app/main.py

from fastapi import FastAPI
from app.routes import item_routes
from app.models import init_db

app = FastAPI()


# initialize database
@app.on_event("startup")
def on_startup():
    init_db()


# register routes
app.include_router(item_routes.router)


@app.get("/")
def read_root():
    return {"message": "Hello, AR World!"}
