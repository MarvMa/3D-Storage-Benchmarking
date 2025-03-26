from fastapi import HTTPException
from sqlalchemy.orm import Session

from app.models import Item

from .base_interface import StorageInterface


class DBStorage(StorageInterface):
    async def save_file(self, db: Session, name: str, data: bytes) -> Item:
        try:
            item = Item(name=name, filename=name, content=data, storage_type='db')
            db.add(item)
            db.commit()
            db.refresh(item)
            return item
        except Exception as e:
            db.rollback()
            raise HTTPException(status_code=500, detail=str(e))

    async def load_file(self, db: Session, item_id: int) -> bytes:
        try:
            item = db.query(Item).get(item_id)
            if item is None:
                raise HTTPException(status_code=404, detail="Item not found")
            return item.content
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))

    async def delete_file(self, db: Session, item_id: int) -> None:
        try:
            item = db.query(Item).get(item_id)
            if item is None:
                raise HTTPException(status_code=404, detail="Item not found")
            db.delete(item)
            db.commit()
        except Exception as e:
            db.rollback()
            raise HTTPException(status_code=500, detail=str(e))
