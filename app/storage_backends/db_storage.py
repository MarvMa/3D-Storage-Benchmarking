from fastapi import HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models import Item

from .base_interface import StorageInterface


class DBStorage(StorageInterface):
    async def save_file(self, db: AsyncSession, name: str, data: bytes) -> Item:
        try:
            item = Item(name=name, filename=name, content=data, storage_type='db')
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
            if item is None:
                raise HTTPException(status_code=404, detail="Item not found")
            return item.content
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))

    async def delete_file(self, db: AsyncSession, item_id: int) -> None:
        try:
            stmt = select(Item).where(Item.id == item_id)
            result = await db.execute(stmt)
            item = result.scalars().first()
            if item is None:
                raise HTTPException(status_code=404, detail="Item not found")
            await db.delete(item)
            await db.commit()
        except Exception as e:
            await db.rollback()
            raise HTTPException(status_code=500, detail=str(e))
