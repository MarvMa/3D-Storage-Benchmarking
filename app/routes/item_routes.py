import os
import shutil

from fastapi import APIRouter, File, UploadFile, HTTPException, Depends, Form
from fastapi.responses import FileResponse  # Import for file response
from sqlalchemy.orm import Session

from app.models import Item, get_db
from app.schemas import ItemRead

router = APIRouter()

UPLOAD_DIRECTORY = "./uploaded_models"

# Create the upload directory if it does not exist
if not os.path.exists(UPLOAD_DIRECTORY):
    os.makedirs(UPLOAD_DIRECTORY)


@router.post("/items/", response_model=ItemRead)
def create_item(
        name: str = Form(...),
        description: str = Form(...),
        file: UploadFile = File(...),
        db: Session = Depends(get_db)):
    """
       Upload a new item.

       This endpoint allows users to upload a new item along with its file. The file will be saved on the server,
       and the item's information will be stored in the database.

       Parameters:
           - name: The name of the item (as a form field).
           - description: The description of the item (as a form field).
           - file: The file to be uploaded.
           - db: Database session (injected).

       Returns:
           - The newly created item's details, including its ID.
       """
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


@router.put("/items/{item_id}", response_model=ItemRead)
def update_item(
        item_id: int,
        name: str = Form(...),
        description: str = Form(...),
        file: UploadFile = File(None),  # File is optional
        db: Session = Depends(get_db)):
    """
       Update an existing item.

       This endpoint allows users to update the name, description, and optionally the file of an existing item.

       Parameters:
           - item_id: The unique ID of the item to be updated.
           - name: The new name of the item (as a form field).
           - description: The new description of the item (as a form field).
           - file: The new file to be uploaded (optional).
           - db: Database session (injected).

       Returns:
           - The updated item details, including its ID.

       Raises:
           - 404 HTTPException if the item is not found.
           - 400 HTTPException if file update fails.
    """
    # Retrieve the item from the database
    item = db.query(Item).filter(Item.id == item_id).first()
    if item is None:
        raise HTTPException(status_code=404, detail="Item not found")

    # Update the item's name and description
    item.name = name
    item.description = description

    # If a new file is uploaded, update the file as well
    if file:
        # Remove old file if it exists
        if os.path.exists(item.file_path):
            os.remove(item.file_path)

        # Save new file to disk
        file_location = f"{UPLOAD_DIRECTORY}/{file.filename}"
        try:
            with open(file_location, "wb") as buffer:
                shutil.copyfileobj(file.file, buffer)
            item.file_path = file_location
        except Exception as e:
            raise HTTPException(status_code=400, detail=f"Failed to update file: {str(e)}")

    # Commit the updates to the database
    db.commit()
    db.refresh(item)

    return item


@router.get("/items/{item_id}", response_model=ItemRead)
def read_item(item_id: int, db: Session = Depends(get_db)):
    """
        Retrieve item by ID.

        This endpoint retrieves the details of an item based on its ID.

        Parameters:
            - item_id: The unique ID of the item.
            - db: Database session (injected).

        Returns:
            - The details of the item including its name and description.

        Raises:
            - 404 HTTPException if the item is not found.
        """
    item = db.query(Item).filter(Item.id == item_id).first()
    if item is None:
        raise HTTPException(status_code=404, detail="Item not found")
    return item


# New endpoint to retrieve the file
@router.get("/items/{item_id}/download", response_class=FileResponse)
def download_item(item_id: int, db: Session = Depends(get_db)):
    """
       Download item file by ID.

       This endpoint allows users to download the file associated with an item using its ID.

       Parameters:
           - item_id: The unique ID of the item.
           - db: Database session (injected).

       Returns:
           - The file associated with the item as a file response.

       Raises:
           - 404 HTTPException if the item is not found or the file does not exist on the server.
       """
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
    """
        Delete item by ID.

        This endpoint allows users to delete an item from the database using its ID.

        Parameters:
            - item_id: The unique ID of the item to be deleted.
            - db: Database session (injected).

        Returns:
            - A message confirming that the item has been successfully deleted.

        Raises:
            - 404 HTTPException if the item is not found.
        """
    # Retrieve the item from the database
    item = db.query(Item).filter(Item.id == item_id).first()
    if item is None:
        raise HTTPException(status_code=404, detail="Item not found")

    # Delete the item from the database
    db.delete(item)
    db.commit()
    return {"message": "Item deleted"}
