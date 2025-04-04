from fastapi import HTTPException, UploadFile
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.config import get_storage_backend
from app.models import Item

storage_backend = get_storage_backend()


class ItemService:
    """
    Service layer for managing items and their associated files.

    This class provides methods for creating, updating, retrieving, downloading, and deleting items.
    """

    @staticmethod
    async def create_item(db: AsyncSession, name: str, description: str, file: UploadFile):
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
        file_bytes = await file.read()
        return await storage_backend.save_file(db, name, file_bytes)

    @staticmethod
    async def download_item(db: AsyncSession, item_id: int):
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
        stmt = select(Item).where(Item.id == item_id)
        result = await db.execute(stmt)
        item = result.scalars().first()

        if item is None:
            raise HTTPException(status_code=404, detail="Item not found")

        return await storage_backend.load_file(db, item.id), item.filename

    @staticmethod
    async def delete_item(db: AsyncSession, item_id: int):
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

        await storage_backend.delete_file(db, item_id)

        return {"message": "Item deleted successfully"}
