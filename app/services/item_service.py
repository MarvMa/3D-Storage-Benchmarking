import os
import shutil

from fastapi import HTTPException
from sqlalchemy.orm import Session

from app.models import Item

UPLOAD_DIRECTORY = "./uploaded_models"


class ItemService:
    """
    Service layer for managing items and their associated files.

    This class provides methods for creating, updating, retrieving, downloading, and deleting items.
    """

    @staticmethod
    def create_item(db: Session, name: str, description: str, file):
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
        # Ensure the upload directory exists
        if not os.path.exists(UPLOAD_DIRECTORY):
            os.makedirs(UPLOAD_DIRECTORY)

        # Save file to disk
        file_location = f"{UPLOAD_DIRECTORY}/{file.filename}"
        with open(file_location, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)

        # Save item info to the database
        new_item = Item(name=name, description=description, file_path=file_location)
        db.add(new_item)
        db.commit()
        db.refresh(new_item)

        return new_item

    @staticmethod
    def update_item(db: Session, item_id: int, name: str, description: str, file=None):
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

    @staticmethod
    def get_item(db: Session, item_id: int):
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
    def download_item(db: Session, item_id: int):
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

        if not os.path.exists(item.file_path):
            raise HTTPException(status_code=404, detail="File not found on server")

        return item.file_path

    @staticmethod
    def delete_item(db: Session, item_id: int):
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

        # Delete the file from the server
        if os.path.exists(item.file_path):
            os.remove(item.file_path)

        # Delete the item from the database
        db.delete(item)
        db.commit()
        return {"message": "Item deleted successfully"}
