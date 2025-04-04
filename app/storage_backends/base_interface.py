from abc import ABC, abstractmethod
from sqlalchemy.orm import Session
from app.models import Item


class StorageInterface(ABC):
    """Abstract base class defining the interface for storage implementations.

    Provides the contract for CRUD operations handling binary file data while
    maintaining database consistency through SQLAlchemy sessions.
    """

    @abstractmethod
    async def save_file(self, db: Session, name: str, data: bytes) -> Item:
        """Persists file data to storage and creates corresponding database record.

        Args:
            db: SQLAlchemy database session for transaction management
            name: Human-readable identifier for the stored file
            data: Binary content of the file to be stored

        Returns:
            Item: SQLAlchemy model instance representing the stored file metadata

        Raises:
            ValueError: If input validation fails (e.g., empty data)
            StorageException: For implementation-specific storage errors
        """
        pass

    @abstractmethod
    async def load_file(self, db: Session, item_id: int) -> bytes:
        """Retrieves file content from storage using associated database ID.

        Args:
            db: SQLAlchemy database session for transaction management
            item_id: Primary key identifier of the Item record

        Returns:
            bytes: Raw binary content of the requested file

        Raises:
            ItemNotFoundError: If no Item exists with the specified ID
            StorageException: For implementation-specific retrieval errors
        """
        pass

    @abstractmethod
    async def delete_file(self, db: Session, item_id: int) -> None:
        """Removes file data from storage and deletes associated database record.

        Args:
            db: SQLAlchemy database session for transaction management
            item_id: Primary key identifier of the Item record to delete

        Raises:
            ItemNotFoundError: If no Item exists with the specified ID
            StorageException: For implementation-specific deletion errors
        """
        pass
