from abc import ABC, abstractmethod

from sqlalchemy.orm import Session

from app.models import Item


class StorageInterface(ABC):
    @abstractmethod
    async def save_file(self, db: Session, name: str, data: bytes) -> Item:
        pass

    @abstractmethod
    async def load_file(self, db: Session, item_id: int) -> bytes:
        pass

    @abstractmethod
    async def delete_file(self, db: Session, item_id: int) -> None:
        pass
