# app/storage_backends/minio_storage.py

from io import BytesIO

from fastapi import UploadFile
from minio import Minio, S3Error
from .base_interface import StorageInterface


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
        if not self.client.bucket_exists(self.bucket_name):
            self.client.make_bucket(self.bucket_name)

    async def save_file(self, object_id: str, file: UploadFile) -> None:
        if not isinstance(object_id, str):
            object_id = str(object_id)

        file_bytes = await file.read()
        data_stream = BytesIO(file_bytes)
        data_len = len(file_bytes)
        self.client.put_object(
            bucket_name=self.bucket_name,
            object_name=object_id,
            data=data_stream,
            length=data_len,
            content_type="application/octet-stream"
        )

    async def load_file(self, object_id: str) -> bytes:
        if not isinstance(object_id, str):
            object_id = str(object_id)
        try:
            response = self.client.get_object(self.bucket_name, object_id)
            data = response.read()
            response.close()
            response.release_conn()
            return data
        except S3Error:
            return b""

    async def delete_file(self, object_id: str) -> None:
        if not isinstance(object_id, str):
            object_id = str(object_id)
        try:
            self.client.remove_object(self.bucket_name, object_id)
        except S3Error:
            pass  # Handle logging or error re-throw as needed
