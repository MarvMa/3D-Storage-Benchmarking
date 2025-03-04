from fastapi import HTTPException, UploadFile
from sqlalchemy.orm import Session

from app.config import get_storage_backend
from app.models import Item

UPLOAD_DIRECTORY = "./uploaded_models"

storage_backend = get_storage_backend()


class ItemService:
    """
    Service layer for managing items and their associated files.

    This class provides methods for creating, updating, retrieving, downloading, and deleting items.
    """

    @staticmethod
    async def create_item(db: Session, name: str, description: str, file: UploadFile):
        """
        Create a new item and upload its associated file.

        Parameters:
            - db: Database session.
            - name: The name of the item.
            - description: The description of the item.
            - file: The file to be uploaded.

        Returns:
            - The newly created item, including its ID and file path.

        Raises:
            - HTTPException with status code 500 if the file upload fails.
        """
        if not name or not description:
            raise HTTPException(status_code=400, detail="Name and description are required fields.")

        file_location = f"{UPLOAD_DIRECTORY}/{file.filename}"
        new_item = Item(name=name, description=description, file_path=file_location)

        db.add(new_item)
        db.commit()
        db.refresh(new_item)

        await storage_backend.save_file(new_item.id, file)

        return new_item

    @staticmethod
    async def update_item(db: Session, item_id: int, name: str, description: str, file=None):
        """
        Update an existing item, including its name, description, and optionally its file.

        Parameters:
            - db: Database session.
            - item_id: The unique ID of the item to update.
            - name: The updated name of the item.
            - description: The updated description of the item.
            - file: The new file to upload (optional).

        Returns:
            - The updated item details, including its ID and updated file path.

        Raises:
            - HTTPException with status code 404 if the item is not found.
            - HTTPException with status code 400 if file update fails.
        """
        # Retrieve the item from the database
        item = db.query(Item).filter(Item.id == item_id).first()
        if item is None:
            raise HTTPException(status_code=404, detail="Item not found")

        # Update the item's name and description
        item.name = name
        item.description = description

        if file:
            await storage_backend.delete_file(item.id)

            try:
                await storage_backend.save_file(item.id, file)
                item.file_path = f"{UPLOAD_DIRECTORY}/{file.filename}"
            except Exception as e:
                raise HTTPException(status_code=400, detail=f"Failed to update file: {str(e)}")

        db.commit()
        db.refresh(item)

        return item

    @staticmethod
    async def get_item(db: Session, item_id: int):
        """
        Retrieve an item by its ID.

        Parameters:
            - db: Database session.
            - item_id: The unique ID of the item to retrieve.

        Returns:
            - The item details, including its name and description.

        Raises:
            - HTTPException with status code 404 if the item is not found.
        """
        item = db.query(Item).filter(Item.id == item_id).first()
        if item is None:
            raise HTTPException(status_code=404, detail="Item not found")
        return item

    @staticmethod
    async def download_item(db: Session, item_id: int):
        """
        Retrieve the file associated with an item by its ID.

        Parameters:
            - db: Database session.
            - item_id: The unique ID of the item whose file to retrieve.

        Returns:
            - The file associated with the item as a file response.

        Raises:
            - HTTPException with status code 404 if the item or the file is not found.
        """
        item = db.query(Item).filter(Item.id == item_id).first()
        if item is None:
            raise HTTPException(status_code=404, detail="Item not found")

        return await storage_backend.load_file(item.id)

    @staticmethod
    async def delete_item(db: Session, item_id: int):
        """
        Delete an item by its ID, and remove the associated file from the server.

        Parameters:
            - db: Database session.
            - item_id: The unique ID of the item to delete.

        Returns:
            - A message confirming the successful deletion.

        Raises:
            - HTTPException with status code 404 if the item is not found.
        """
        item = db.query(Item).filter(Item.id == item_id).first()
        if item is None:
            raise HTTPException(status_code=404, detail="Item not found")

        await storage_backend.delete_file(item.id)
        # Delete the item from the database
        db.delete(item)
        db.commit()
        return {"message": "Item deleted successfully"}
