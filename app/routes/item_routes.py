from fastapi import APIRouter, Depends, File, UploadFile, Form
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session

from app.models import get_db
from app.schemas import ItemRead
from app.services.item_service import ItemService

router = APIRouter()


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
    return ItemService.create_item(db, name, description, file)


@router.put("/items/{item_id}", response_model=ItemRead)
def update_item(
        item_id: int,
        name: str = Form(...),
        description: str = Form(...),
        file: UploadFile = File(None),
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
    return ItemService.update_item(db, item_id, name, description, file)


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
    return ItemService.get_item(db, item_id)


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
    file_path = ItemService.download_item(db, item_id)
    return FileResponse(path=file_path, filename=file_path.split("/")[-1], media_type='application/octet-stream')


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
    return ItemService.delete_item(db, item_id)
