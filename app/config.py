import os
from app.storage_backends.file_storage import FileStorage
from app.storage_backends.db_storage import DBStorage
from app.storage_backends.minio_storage import MinioStorage


def get_storage_backend():
    backend = os.getenv("STORAGE_BACKEND", "file")
    if backend == "file":
        return FileStorage()
    elif backend == "db":
        return DBStorage()
    elif backend == "minio":
        endpoint = os.getenv("MINIO_ENDPOINT", "minio:9000")
        access_key = os.getenv("MINIO_ACCESS_KEY", "minio")
        secret_key = os.getenv("MINIO_SECRET_KEY", "minio123")
        bucket_name = os.getenv("MINIO_BUCKET_NAME", "3d-files")
        return MinioStorage(endpoint, access_key, secret_key, bucket_name)
    else:
        raise ValueError(f"Unknown storage backend: {backend}")
