import os

from fastapi import HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import Session

from .base_interface import StorageInterface
from ..models import Item

UPLOAD_DIRECTORY = "/tmp/3d_objects/"


class FileStorage(StorageInterface):
    def __init__(self):
        os.makedirs(UPLOAD_DIRECTORY, exist_ok=True)

    async def save_file(self, db: AsyncSession, name: str, data: bytes) -> Item:
        try:

            path = os.path.join(UPLOAD_DIRECTORY, name)
            with open(path, "wb") as f:
                f.write(data)
            item = Item(name=name, filename=name, path_or_key=path, storage_type='file')
            db.add(item)
            await db.commit()
            await db.refresh(item)
            return item
        except Exception as e:
            await db.rollback()
            raise HTTPException(status_code=500, detail=str(e))

    async def load_file(self, db: AsyncSession, item_id: int) -> bytes:
        try:
            stmt = select(Item).where(Item.id == item_id)
            result = await db.execute(stmt)
            item = result.scalars().first()

            with open(item.path_or_key, "rb") as f:
                return f.read()
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))

    async def delete_file(self, db: AsyncSession, item_id: int) -> None:
        try:
            stmt = select(Item).where(Item.id == item_id)
            result = await db.execute(stmt)
            item = result.scalars().first()

            os.remove(item.path_or_key)
            await db.delete(item)
            await db.commit()
        except Exception as e:
            await db.rollback()
            raise HTTPException(status_code=500, detail=str(e))
