from typing import List

from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session

from app.models import Collection, get_db
from app.schemas import CollectionCreate, CollectionRead

router = APIRouter()


@router.post("/collections/", response_model=CollectionRead)
def create_collection(collection: CollectionCreate, db: Session = Depends(get_db)):
    """
       Create a new collection.

       This endpoint allows the creation of a new collection with a name and description.
       Once created, the collection is stored in the database and returned with its details.

       Parameters:
           - collection: JSON body containing the name and description of the collection.
           - db: Database session (injected).

       Returns:
           - The newly created collection, including its ID, name, and description.
       """
    new_collection = Collection(name=collection.name, description=collection.description)
    db.add(new_collection)
    db.commit()
    db.refresh(new_collection)
    return new_collection


@router.get("/collections/{collection_id}", response_model=CollectionRead)
def get_collection(collection_id: int, db: Session = Depends(get_db)):
    """
        Retrieve a collection by its ID.

        This endpoint retrieves a collection's details using its unique ID.
        If the collection is not found, a 404 error is returned.

        Parameters:
            - collection_id: The unique ID of the collection to retrieve.
            - db: Database session (injected).

        Returns:
            - The collection's details including its ID, name, and description.
        """
    collection = db.query(Collection).filter(Collection.id == collection_id).first()
    if collection is None:
        raise HTTPException(status_code=404, detail="Collection not found")
    return collection


@router.get("/collections/", response_model=List[CollectionRead])
def list_collections(db: Session = Depends(get_db)):
    """
       List all collections.

       This endpoint retrieves and returns all collections stored in the database.

       Parameters:
           - db: Database session (injected).

       Returns:
           - A list of collections, each containing its ID, name, and description.
       """
    collections = db.query(Collection).all()
    return collections


@router.delete("/collections/{collection_id}", status_code=204)
def delete_collection(collection_id: int, db: Session = Depends(get_db)):
    """
       Delete a collection by its ID.

       This endpoint deletes a collection using its unique ID.
       If the collection is not found, a 404 error is returned.

       Parameters:
           - collection_id: The unique ID of the collection to delete.
           - db: Database session (injected).

       Returns:
           - A message confirming that the collection has been deleted successfully.
       """
    collection = db.query(Collection).filter(Collection.id == collection_id).first()
    if collection is None:
        raise HTTPException(status_code=404, detail="Collection not found")
    db.delete(collection)
    db.commit()
    return {"message": "Collection deleted successfully"}
