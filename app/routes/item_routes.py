import io

from fastapi import APIRouter, Depends, File, UploadFile, Form
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session
from starlette.responses import StreamingResponse

from app.models import get_db
from app.services.item_service import ItemService

router = APIRouter()


@router.post("/items/")
async def create_item(
        name: str = Form(...),
        description: str = Form(...),
        file: UploadFile = File(...),
        db: Session = Depends(get_db)
):
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
    return await ItemService.create_item(db, name, description, file)


@router.get("/items/{item_id}/download", response_class=FileResponse)
async def download_item(item_id: int, db: Session = Depends(get_db)):
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

    file_data, file_name = await ItemService.download_item(db, item_id)

    stream = io.BytesIO(file_data)
    return StreamingResponse(
        stream,
        media_type="application/octet-stream",
        headers={"Content-Disposition": f"attachment; filename={file_name}"}
    )


@router.delete("/items/{item_id}", status_code=204)
async def delete_item(item_id: int, db: Session = Depends(get_db)):
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
    return await ItemService.delete_item(db, item_id)
