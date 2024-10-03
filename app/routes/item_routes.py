import os
import shutil

from fastapi import APIRouter, File, UploadFile, HTTPException, Depends, Form
from fastapi.responses import FileResponse  # Import for file response
from sqlalchemy.orm import Session

from app.models import Item, get_db
from app.schemas import ItemRead

router = APIRouter()

UPLOAD_DIRECTORY = "./uploaded_models"

if not os.path.exists(UPLOAD_DIRECTORY):
    os.makedirs(UPLOAD_DIRECTORY)


@router.post("/items/", response_model=ItemRead)
def create_item(
        name: str = Form(...),
        description: str = Form(...),
        file: UploadFile = File(...),
        db: Session = Depends(get_db)):
    # Save file to disk
    file_location = f"{UPLOAD_DIRECTORY}/{file.filename}"
    with open(file_location, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    # Save file info to the database
    new_item = Item(name=name, description=description, file_path=file_location)
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


# New endpoint to retrieve the file
@router.get("/items/{item_id}/download", response_class=FileResponse)
def download_item(item_id: int, db: Session = Depends(get_db)):
    # Retrieve the item from the database
    item = db.query(Item).filter(Item.id == item_id).first()
    if item is None:
        raise HTTPException(status_code=404, detail="Item not found")

    # Check if file exists in the storage
    if not os.path.exists(item.file_path):
        raise HTTPException(status_code=404, detail="File not found on server")

    # Return the file using FileResponse
    return FileResponse(path=item.file_path, filename=item.name, media_type='application/octet-stream')


@router.delete("/items/{item_id}", status_code=204)
def delete_item(item_id: int, db: Session = Depends(get_db)):
    # Retrieve the item from the database
    item = db.query(Item).filter(Item.id == item_id).first()
    if item is None:
        raise HTTPException(status_code=404, detail="Item not found")

    # Delete the item from the database
    db.delete(item)
    db.commit()
    return {"message": "Item deleted"}
