from io import BytesIO

from fastapi import HTTPException
from minio import Minio
from sqlalchemy.orm import Session

from .base_interface import StorageInterface
from app.models import Item


class MinioStorage(StorageInterface):
    def __init__(self, endpoint: str, access_key: str, secret_key: str, bucket_name: str):
        self.client = Minio(
            endpoint=endpoint,
            access_key=access_key,
            secret_key=secret_key,
            secure=False
        )
        self.bucket_name = bucket_name

        bucket = self.client.bucket_exists(self.bucket_name)
        if not bucket:
            self.client.make_bucket(self.bucket_name)

    async def save_file(self, db: Session, name: str, data: bytes) -> Item:
        try:
            file = BytesIO(data)
            self.client.put_object(self.bucket_name, name, file, length=-1, part_size=10 * 1024 * 1024)
            item = Item(name=name, filename=name, path_or_key=name, storage_type='minio')
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
            response = self.client.get_object(self.bucket_name, item.path_or_key)
            return response.read()
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))

    async def delete_file(self, db: Session, item_id: int) -> None:
        try:
            item = db.query(Item).get(item_id)
            self.client.remove_object(self.bucket_name, item.path_or_key)
            db.delete(item)
            db.commit()
        except Exception as e:
            db.rollback()
            raise HTTPException(status_code=500, detail=str(e))
