from fastapi import HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.models import Item
from .base_interface import StorageInterface


class DBStorage(StorageInterface):
    """SQLAlchemy implementation storing files as BLOBs in relational database.

    Features:
    - ACID-compliant transactions
    - Async I/O operations
    - Integrated metadata+content storage
    - Automatic rollback on failures
    """

    async def save_file(self, db: AsyncSession, name: str, data: bytes) -> Item:
        """Persists file content as BLOB with metadata in single transaction.

        Args:
            db: Async database session for transaction isolation
            name: Logical filename for metadata tracking
            data: Binary content to store as BLOB

        Returns:
            Item: Created database record with generated ID

        Raises:
            HTTPException: 500 for database errors, 400 for invalid inputs

        Note:
            Performs implicit size validation through database column constraints
        """
        try:
            item = Item(
                name=name,
                filename=name,
                content=data,
                storage_type='db'
            )
            db.add(item)
            await db.commit()
            await db.refresh(item)
            return item
        except Exception as e:
            await db.rollback()
            raise HTTPException(
                status_code=500,
                detail=f"Database storage failure: {str(e)}"
            )

    async def load_file(self, db: AsyncSession, item_id: int) -> bytes:
        """Retrieves BLOB content through database-record lookup.

        Args:
            db: Async database session with read consistency
            item_id: Primary key of persisted Item record

        Returns:
            bytes: Raw binary content from BLOB column

        Raises:
            HTTPException: 404 for missing records, 500 for query errors
        """
        try:
            stmt = select(Item).where(Item.id == item_id)
            result = await db.execute(stmt)
            item = result.scalars().first()

            if not item:
                raise HTTPException(
                    status_code=404,
                    detail=f"Item {item_id} not found in database storage"
                )

            return item.content
        except Exception as e:
            raise HTTPException(
                status_code=500,
                detail=f"Database retrieval failure: {str(e)}"
            )

    async def delete_file(self, db: AsyncSession, item_id: int) -> None:
        """Atomic deletion of database record and associated BLOB content.

        Args:
            db: Async database session with write lock
            item_id: Primary key of record to purge

        Raises:
            HTTPException: 404 for missing records, 500 for deletion errors
        """
        try:
            stmt = select(Item).where(Item.id == item_id)
            result = await db.execute(stmt)
            item = result.scalars().first()

            if not item:
                raise HTTPException(
                    status_code=404,
                    detail=f"Item {item_id} not found for deletion"
                )

            await db.delete(item)
            await db.commit()
        except Exception as e:
            await db.rollback()
            raise HTTPException(
                status_code=500,
                detail=f"Database deletion failure: {str(e)}"
            )
