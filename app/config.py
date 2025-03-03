import os
from app.storage_backends.file_storage import FileStorage
from app.storage_backends.db_storage import DBStorage
from app.storage_backends.minio_storage import MinioStorage


def get_storage_backend():
    backend = os.getenv("STORAGE_BACKEND", "file")
    if backend == "file":
        folder = os.getenv("STORAGE_FOLDER", "uploaded_files")
        return FileStorage(folder)
    elif backend == "db":
        db_path = os.getenv("DATABASE_URL", "sqlite:///./arpas-dev.db")
        return DBStorage(db_path)
    elif backend == "minio":
        endpoint = os.getenv("MINIO_ENDPOINT", "minio:9000")
        access_key = os.getenv("MINIO_ACCESS_KEY", "minio")
        secret_key = os.getenv("MINIO_SECRET_KEY", "minio123")
        bucket_name = os.getenv("MINIO_BUCKET_NAME", "3d-files")
        return MinioStorage(endpoint, access_key, secret_key, bucket_name)
    else:
        raise ValueError(f"Unknown storage backend: {backend}")
