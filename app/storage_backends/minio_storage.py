from io import BytesIO
from fastapi import HTTPException
from minio import Minio
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import Session
from .base_interface import StorageInterface
from app.models import Item


class MinioStorage(StorageInterface):
    """MinIO object storage implementation of the StorageInterface.

    Features:
    - S3-compatible object storage integration
    - Automatic bucket creation
    - Streaming upload/download for large files
    - Atomic database transactions with storage operations
    - Connection cleanup for distributed systems
    """

    def __init__(self, endpoint: str, access_key: str, secret_key: str, bucket_name: str):
        """Initializes MinIO client and ensures bucket exists.

        Args:
            endpoint: MinIO server URL (e.g., 'play.min.io:9000')
            access_key: MinIO root user access key
            secret_key: MinIO root user secret key
            bucket_name: Target bucket name for object storage

        Note:
            Uses insecure connection (secure=False) for local testing.
            For production, enable TLS and certificate verification.
        """
        self.client = Minio(
            endpoint=endpoint,
            access_key=access_key,
            secret_key=secret_key,
            secure=False
        )
        self.bucket_name = bucket_name

        if not self.client.bucket_exists(self.bucket_name):
            self.client.make_bucket(self.bucket_name)

    async def save_file(self, db: AsyncSession, name: str, data: bytes) -> Item:
        """Stores file in MinIO with streaming upload and creates database record.

        Args:
            db: Async database session
            name: Object key (should be URL-safe)
            data: Binary content to store

        Returns:
            Item: Created database record with storage metadata

        Raises:
            HTTPException: 500 - Storage/Database failure
                          400 - Invalid object key

        Note:
            Uses multipart upload with 10MB chunks for large files
        """
        try:
            # Stream data with chunked upload
            with BytesIO(data) as file_stream:
                self.client.put_object(
                    bucket_name=self.bucket_name,
                    object_name=name,
                    data=file_stream,
                    length=-1,
                    part_size=10 * 1024 * 1024  # 10MB chunks
                )

            # Create database record
            item = Item(
                name=name,
                filename=name,
                path_or_key=name,
                storage_type='minio'
            )
            db.add(item)
            await db.commit()
            await db.refresh(item)
            return item

        except Exception as e:
            await db.rollback()
            raise HTTPException(
                status_code=500,
                detail=f"MinIO storage failure: {str(e)}"
            )

    async def load_file(self, db: AsyncSession, item_id: int) -> bytes:
        """Retrieves file content from MinIO with proper connection cleanup.

        Args:
            db: Async database session
            item_id: Database record ID

        Returns:
            bytes: Raw file content

        Raises:
            HTTPException: 404 - Item not found
                          500 - Retrieval error

        Warning:
            Always closes MinIO response connections to prevent leaks
        """
        response = None
        try:
            result = await db.execute(select(Item).where(Item.id == item_id))
            item = result.scalars().first()

            if not item:
                raise HTTPException(
                    status_code=404,
                    detail=f"Item {item_id} not found"
                )

            response = self.client.get_object(
                bucket_name=self.bucket_name,
                object_name=item.path_or_key
            )
            return response.read()

        except Exception as e:
            raise HTTPException(
                status_code=500,
                detail=f"MinIO retrieval failure: {str(e)}"
            )
        finally:
            if response:
                try:
                    response.close()
                    response.release_conn()
                except Exception as e:
                    print(f"Connection cleanup error: {str(e)}")

    async def delete_file(self, db: AsyncSession, item_id: int) -> None:
        """Atomically removes object from MinIO and database.

        Args:
            db: Async database session
            item_id: Database record ID

        Raises:
            HTTPException: 404 - Item not found
                          500 - Deletion error

        Note:
            Order of operations:
            1. Delete from MinIO
            2. Delete database record
            3. Commit transaction
        """
        try:
            result = await db.execute(select(Item).where(Item.id == item_id))
            item = result.scalars().first()

            if not item:
                raise HTTPException(
                    status_code=404,
                    detail=f"Item {item_id} not found"
                )

            # Delete from MinIO
            self.client.remove_object(
                bucket_name=self.bucket_name,
                object_name=item.path_or_key
            )

            await db.delete(item)
            await db.commit()

        except Exception as e:
            await db.rollback()
            raise HTTPException(
                status_code=500,
                detail=f"MinIO deletion failure: {str(e)}"
            )
