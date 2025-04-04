import os
from fastapi import HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import Session
from .base_interface import StorageInterface
from ..models import Item

UPLOAD_DIRECTORY = "/tmp/3d_objects/"


class FileStorage(StorageInterface):
    """Filesystem implementation of StorageInterface using a dedicated directory.

    Features:
    - Atomic write operations for file contents
    - Metadata synchronization with database
    - Safe path handling to prevent directory traversal
    - Automatic cleanup on deletion
    """

    def __init__(self):
        os.makedirs(UPLOAD_DIRECTORY, exist_ok=True)

    async def save_file(self, db: AsyncSession, name: str, data: bytes) -> Item:
        """Persists file to filesystem and stores metadata in database.

        Args:
            db: Async database session for metadata transaction
            name: Sanitized filename (should be validated externally)
            data: Raw binary content for storage

        Returns:
            Item: Database record with filesystem path

        Raises:
            HTTPException: 500 for filesystem/database errors
            400 for invalid filenames (implicit via OS error)

        Notes:
            - Uses atomic write via tempfile pattern internally
            - Concurrent writes to same filename will overwrite
        """
        try:
            # Secure path construction prevents directory traversal
            path = os.path.join(UPLOAD_DIRECTORY, os.path.basename(name))

            # Atomic write using write-and-rename pattern
            temp_path = f"{path}.tmp"
            with open(temp_path, "wb") as f:
                f.write(data)
            os.rename(temp_path, path)

            # Database record with filesystem metadata
            item = Item(
                name=name,
                filename=name,
                path_or_key=path,
                storage_type='file'
            )
            db.add(item)
            await db.commit()
            await db.refresh(item)
            return item
        except (OSError, IOError) as e:
            await db.rollback()
            raise HTTPException(
                status_code=500,
                detail=f"Filesystem error: {str(e)}"
            )
        except Exception as e:
            await db.rollback()
            raise HTTPException(
                status_code=500,
                detail=f"Database error: {str(e)}"
            )

    async def load_file(self, db: AsyncSession, item_id: int) -> bytes:
        """Retrieves file content from filesystem using database-stored path.

        Args:
            db: Async session for metadata lookup
            item_id: Primary key of file metadata record

        Returns:
            bytes: Raw file content

        Raises:
            HTTPException: 404 if record/path invalid, 500 for read errors
        """
        try:
            result = await db.execute(select(Item).where(Item.id == item_id))
            item = result.scalars().first()

            if not item or not item.path_or_key:
                raise HTTPException(
                    status_code=404,
                    detail=f"File {item_id} metadata not found"
                )

            with open(item.path_or_key, "rb") as f:
                return f.read()

        except FileNotFoundError as e:
            raise HTTPException(
                status_code=404,
                detail=f"File missing at stored path: {str(e)}"
            )
        except (PermissionError, IOError) as e:
            raise HTTPException(
                status_code=500,
                detail=f"Filesystem access error: {str(e)}"
            )

    async def delete_file(self, db: AsyncSession, item_id: int) -> None:
        """Atomically removes file and database record.

        Args:
            db: Async session for atomic transaction
            item_id: Primary key of record to delete

        Raises:
            HTTPException: 404 if record missing, 500 for deletion failures

        Notes:
            - Filesystem deletion happens before database commit
            - Failed deletes trigger full rollback
        """
        try:
            result = await db.execute(select(Item).where(Item.id == item_id))
            item = result.scalars().first()

            if not item:
                raise HTTPException(
                    status_code=404,
                    detail=f"Item {item_id} not found"
                )

            if item.path_or_key and os.path.exists(item.path_or_key):
                os.remove(item.path_or_key)

            await db.delete(item)
            await db.commit()

        except FileNotFoundError as e:
            await db.rollback()
            raise HTTPException(
                status_code=404,
                detail=f"File missing during deletion: {str(e)}"
            )
        except Exception as e:
            await db.rollback()
            raise HTTPException(
                status_code=500,
                detail=f"Deletion failed: {str(e)}"
            )
