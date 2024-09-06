from typing import List

from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session

from app.models import Collection, get_db
from app.schemas import CollectionCreate, CollectionRead

router = APIRouter()


@router.post("/collections/", response_model=CollectionRead)
def create_collection(collection: CollectionCreate, db: Session = Depends(get_db)):
    new_collection = Collection(name=collection.name, description=collection.description)
    db.add(new_collection)
    db.commit()
    db.refresh(new_collection)
    return new_collection


@router.get("/collections/{collection_id}", response_model=CollectionRead)
def get_collection(collection_id: int, db: Session = Depends(get_db)):
    collection = db.query(Collection).filter(Collection.id == collection_id).first()
    if collection is None:
        raise HTTPException(status_code=404, detail="Collection not found")
    return collection


@router.get("/collections/", response_model=List[CollectionRead])
def list_collections(db: Session = Depends(get_db)):
    collections = db.query(Collection).all()
    return collections


@router.delete("/collections/{collection_id}", status_code=204)
def delete_collection(collection_id: int, db: Session = Depends(get_db)):
    collection = db.query(Collection).filter(Collection.id == collection_id).first()
    if collection is None:
        raise HTTPException(status_code=404, detail="Collection not found")
    db.delete(collection)
    db.commit()
    return {"message": "Collection deleted successfully"}
