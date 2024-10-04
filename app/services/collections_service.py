from fastapi import HTTPException
from sqlalchemy.orm import Session

from app.models import Collection, Item, CollectionItem


class CollectionService:
    """
    Service layer for managing collections and their associated items.

    This class provides methods for creating, updating, and managing the relationship between collections and items.
    """

    @staticmethod
    def create_collection(db: Session, name: str, description: str, item_ids: list = None):
        """
        Create a new collection and optionally associate it with items.

        Parameters:
            - db: Database session.
            - name: The name of the collection.
            - description: The description of the collection.
            - item_ids: A list of item IDs to associate with the collection (optional).

        Returns:
            - The newly created collection, including its ID, name, description, and associated items.

        Raises:
            - HTTPException with status code 404 if any item in the provided item_ids is not found.
        """
        # check if name is present
        if not name:
            raise HTTPException(status_code=400, detail="Collection name is required")

        new_collection = Collection(name=name, description=description)
        db.add(new_collection)
        db.commit()

        # Optionally add items to the collection
        if item_ids:
            for item_id in item_ids:
                item = db.query(Item).filter(Item.id == item_id).first()
                if not item:
                    raise HTTPException(status_code=404, detail=f"Item with id {item_id} not found")
                collection_item = CollectionItem(collection_id=new_collection.id, item_id=item_id)
                db.add(collection_item)

        db.commit()
        db.refresh(new_collection)
        return new_collection

    @staticmethod
    def add_items_to_collection(db: Session, collection_id: int, item_ids: list):
        """
        Add items to an existing collection.

        Parameters:
            - db: Database session.
            - collection_id: The ID of the collection to which the items will be added.
            - item_ids: A list of item IDs to be added to the collection.

        Returns:
            - The updated collection details including the newly added items.

        Raises:
            - HTTPException with status code 404 if the collection or any item in the item_ids is not found.
        """
        collection = db.query(Collection).filter(Collection.id == collection_id).first()
        if not collection:
            raise HTTPException(status_code=404, detail="Collection not found")

        for item_id in item_ids:
            item = db.query(Item).filter(Item.id == item_id).first()
            if not item:
                raise HTTPException(status_code=404, detail=f"Item with id {item_id} not found")
            if not db.query(CollectionItem).filter_by(collection_id=collection_id, item_id=item_id).first():
                collection_item = CollectionItem(collection_id=collection_id, item_id=item_id)
                db.add(collection_item)

        db.commit()
        return collection

    @staticmethod
    def remove_items_from_collection(db: Session, collection_id: int, item_ids: list):
        """
        Remove items from an existing collection.

        Parameters:
            - db: Database session.
            - collection_id: The ID of the collection from which the items will be removed.
            - item_ids: A list of item IDs to be removed from the collection.

        Returns:
            - The updated collection details after the items have been removed.

        Raises:
            - HTTPException with status code 404 if the collection or any item in the item_ids is not found.
        """
        collection = db.query(Collection).filter(Collection.id == collection_id).first()
        if not collection:
            raise HTTPException(status_code=404, detail="Collection not found")

        for item_id in item_ids:
            collection_item = db.query(CollectionItem).filter_by(collection_id=collection_id, item_id=item_id).first()
            if collection_item:
                db.delete(collection_item)

        db.commit()
        return collection

    @staticmethod
    def update_collection(db: Session, collection_id: int, name: str, description: str, item_ids: list = None):
        """
        Update an existing collection and optionally manage its items.

        Parameters:
            - db: Database session.
            - collection_id: The ID of the collection to update.
            - name: The updated name of the collection.
            - description: The updated description of the collection.
            - item_ids: A list of new item IDs to replace the current associated items (optional).

        Returns:
            - The updated collection with its new name, description, and associated items.

        Raises:
            - HTTPException with status code 404 if the collection or any item in the item_ids is not found.
        """
        collection = db.query(Collection).filter(Collection.id == collection_id).first()
        if not collection:
            raise HTTPException(status_code=404, detail="Collection not found")

        collection.name = name
        collection.description = description

        if item_ids is not None:
            # Remove all existing items and add the new items
            db.query(CollectionItem).filter(CollectionItem.collection_id == collection_id).delete()
            for item_id in item_ids:
                item = db.query(Item).filter(Item.id == item_id).first()
                if not item:
                    raise HTTPException(status_code=404, detail=f"Item with id {item_id} not found")
                collection_item = CollectionItem(collection_id=collection_id, item_id=item_id)
                db.add(collection_item)

        db.commit()
        db.refresh(collection)
        return collection

    @staticmethod
    def get_collection(db: Session, collection_id: int):
        """
        Retrieve a collection by its ID along with its associated items.

        Parameters:
            - db: Database session.
            - collection_id: The ID of the collection to retrieve.

        Returns:
            - The collection's details, including its name, description, and associated items.

        Raises:
            - HTTPException with status code 404 if the collection is not found.
        """
        collection = db.query(Collection).filter(Collection.id == collection_id).first()
        if not collection:
            raise HTTPException(status_code=404, detail="Collection not found")

        # Retrieve associated items for the collection
        items = db.query(Item).join(CollectionItem).filter(CollectionItem.collection_id == collection_id).all()
        collection.items = items
        return collection

    @staticmethod
    def list_collections(db: Session):
        """
        List all collections along with their associated items.

        Parameters:
            - db: Database session.

        Returns:
            - A list of collections, each containing its name, description, and associated items.
        """
        collections = db.query(Collection).all()
        for collection in collections:
            # Retrieve associated items for each collection
            items = db.query(Item).join(CollectionItem).filter(CollectionItem.collection_id == collection.id).all()
            collection.items = items
        return collections

    @staticmethod
    def delete_collection(db: Session, collection_id: int):
        """
        Delete a collection by its ID and remove all associations with items.

        Parameters:
            - db: Database session.
            - collection_id: The ID of the collection to delete.

        Returns:
            - A message confirming the successful deletion of the collection.

        Raises:
            - HTTPException with status code 404 if the collection is not found.
        """
        collection = db.query(Collection).filter(Collection.id == collection_id).first()
        if not collection:
            raise HTTPException(status_code=404, detail="Collection not found")

        # Remove all associated items in the CollectionItem table
        db.query(CollectionItem).filter(CollectionItem.collection_id == collection_id).delete()

        db.delete(collection)
        db.commit()
        return {"message": "Collection deleted successfully"}
