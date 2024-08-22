# app/routes/example_routes.py
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.models import ExampleModel, SessionLocal

router = APIRouter()


# Dependency Injection für die Datenbank-Session
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@router.get("/examples/")
def read_examples(db: Session = Depends(get_db)):
    return db.query(ExampleModel).all()


@router.post("/examples/")
def create_example(name: str, db: Session = Depends(get_db)):
    example = ExampleModel(name=name)
    db.add(example)
    db.commit()
    db.refresh(example)
    return example
