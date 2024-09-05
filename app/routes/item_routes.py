# item_routes.py

from fastapi import APIRouter, File, UploadFile, HTTPException, Depends
from sqlalchemy.orm import Session
from app.models import Item, get_db
from app.schemas import ItemCreate, ItemRead
import shutil
import os

router = APIRouter()

UPLOAD_DIRECTORY = "./uploaded_models"

if not os.path.exists(UPLOAD_DIRECTORY):
    os.makedirs(UPLOAD_DIRECTORY)


@router.post("/items/", response_model=ItemRead)
def create_item(file: UploadFile = File(...), db: Session = Depends(get_db)):
    # Save file to disk
    file_location = f"{UPLOAD_DIRECTORY}/{file.filename}"
    with open(file_location, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    # Save file info to the database
    new_item = Item(name=file.filename, description="A GLTF Model", file_path=file_location)
    db.add(new_item)
    db.commit()
    db.refresh(new_item)

    return new_item


@router.get("/items/{item_id}", response_model=ItemRead)
def read_item(item_id: int, db: Session = Depends(get_db)):
    item = db.query(Item).filter(Item.id == item_id).first()
    if item is None:
        raise HTTPException(status_code=404, detail="Item not found")
    return item
