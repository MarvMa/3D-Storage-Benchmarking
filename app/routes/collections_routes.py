from typing import List

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.services.collections_service import CollectionService
from app.schemas import CollectionCreate, CollectionRead
from app.models import get_db

router = APIRouter()


@router.post("/collections/", response_model=CollectionRead)
def create_collection(collection: CollectionCreate, db: Session = Depends(get_db)):
    """
    Create a new collection with optional items.

    This endpoint allows the creation of a new collection with a name and description.
    Optionally, a list of item IDs can be provided to add items to the collection upon creation.

    Parameters:
        - collection: JSON body containing the name, description, and optional item IDs.
        - db: Database session (injected).

    Returns:
        - The newly created collection, including its ID, name, description, and optionally the associated items.

    Raises:
        - 404 HTTPException if any item in the provided item_ids is not found.
    """
    return CollectionService.create_collection(db, collection.name, collection.description, collection.item_ids)


@router.post("/collections/{collection_id}/add-items", response_model=CollectionRead)
def add_items_to_collection(collection_id: int, item_ids: list[int], db: Session = Depends(get_db)):
    """
    Add items to an existing collection.

    This endpoint allows users to add multiple items to an existing collection by providing a list of item IDs.

    Parameters:
        - collection_id: The unique ID of the collection to update.
        - item_ids: List of item IDs to add to the collection.
        - db: Database session (injected).

    Returns:
        - The updated collection details including the newly added items.

    Raises:
        - 404 HTTPException if the collection or any item in the item_ids is not found.
    """
    return CollectionService.add_items_to_collection(db, collection_id, item_ids)


@router.post("/collections/{collection_id}/remove-items", response_model=CollectionRead)
def remove_items_from_collection(collection_id: int, item_ids: list[int], db: Session = Depends(get_db)):
    """
    Remove items from an existing collection.

    This endpoint allows users to remove multiple items from an existing collection by providing a list of item IDs.

    Parameters:
        - collection_id: The unique ID of the collection to update.
        - item_ids: List of item IDs to remove from the collection.
        - db: Database session (injected).

    Returns:
        - The updated collection details with the items removed.

    Raises:
        - 404 HTTPException if the collection or any item in the item_ids is not found.
    """
    return CollectionService.remove_items_from_collection(db, collection_id, item_ids)


@router.put("/collections/{collection_id}", response_model=CollectionRead)
def update_collection(collection_id: int, collection_data: CollectionCreate, db: Session = Depends(get_db)):
    """
    Update an existing collection and optionally manage its items.

    This endpoint allows updating a collection's name, description, and managing items.

    Parameters:
        - collection_id: The unique ID of the collection to update.
        - collection_data: JSON body containing the updated name, description, and optional list of item IDs.
        - db: Database session (injected).

    Returns:
        - The updated collection with its name, description, and updated items (if any).

    Raises:
        - 404 HTTPException if the collection or any item in the new item_ids is not found.
    """
    return CollectionService.update_collection(db, collection_id, collection_data.name, collection_data.description,
                                               collection_data.item_ids)


@router.get("/collections/{collection_id}", response_model=CollectionRead)
def get_collection(collection_id: int, db: Session = Depends(get_db)):
    """
    Retrieve a collection by its ID along with its associated items.

    This endpoint allows users to retrieve the details of a collection, including its associated items,
    by providing the collection's unique ID.

    Parameters:
        - collection_id: The unique ID of the collection to retrieve.
        - db: Database session (injected).

    Returns:
        - The collection's details, including its name, description, and associated items.

    Raises:
        - 404 HTTPException if the collection is not found.
    """
    collection = CollectionService.get_collection(db, collection_id)
    return collection


@router.get("/collections/", response_model=List[CollectionRead])
def list_collections(db: Session = Depends(get_db)):
    """
    List all collections with their associated items.

    This endpoint retrieves and returns all collections stored in the database,
    along with the items associated with each collection.

    Parameters:
        - db: Database session (injected).

    Returns:
        - A list of collections, each containing its name, description, and associated items.
    """
    return CollectionService.list_collections(db)


@router.delete("/collections/{collection_id}", status_code=204)
def delete_collection(collection_id: int, db: Session = Depends(get_db)):
    """
    Delete a collection by its ID.

    This endpoint allows users to delete a collection from the database by providing its unique ID.
    All associations between the collection and its items will be removed.

    Parameters:
        - collection_id: The unique ID of the collection to delete.
        - db: Database session (injected).

    Returns:
        - A message confirming that the collection has been successfully deleted.

    Raises:
        - 404 HTTPException if the collection is not found.
    """
    CollectionService.delete_collection(db, collection_id)
    return {"message": "Collection deleted successfully"}
