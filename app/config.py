import os
from app.storage_backends.file_storage import FileStorage
from app.storage_backends.db_storage import DBStorage
from app.storage_backends.minio_storage import MinioStorage


def get_storage_backend():
    """Factory function to instantiate the configured storage backend.

    Reads configuration from environment variables and initializes the appropriate
    storage implementation. Supports hot-swapping storage backends without code changes.

    Environment Variables:
        STORAGE_BACKEND (str): Storage system to use (file/db/minio) - default: file
        MINIO_ENDPOINT (str): [minio] Server URL - default: minio:9000
        MINIO_ACCESS_KEY (str): [minio] Access key - default: minio
        MINIO_SECRET_KEY (str): [minio] Secret key - default: minio123
        MINIO_BUCKET_NAME (str): [minio] Target bucket - default: 3d-files

    Returns:
        StorageInterface: Concrete storage implementation instance

    Raises:
        ValueError: For unsupported storage backend configurations
        RuntimeError: If required environment variables are missing
    """
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
