from abc import ABC, abstractmethod


class StorageInterface(ABC):
    @abstractmethod
    def save_file(self, object_id: str, file: bytes) -> None:
        pass

    @abstractmethod
    def load_file(self, object_id: str) -> bytes:
        pass

    @abstractmethod
    def delete_file(self, object_id: str) -> None:
        pass
