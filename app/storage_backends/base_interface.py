from abc import ABC, abstractmethod

from fastapi import UploadFile


class StorageInterface(ABC):
    @abstractmethod
    async def save_file(self, object_id: str, file: UploadFile) -> None:
        pass

    @abstractmethod
    async def load_file(self, object_id: str) -> bytes:
        pass

    @abstractmethod
    async def delete_file(self, object_id: str) -> None:
        pass
