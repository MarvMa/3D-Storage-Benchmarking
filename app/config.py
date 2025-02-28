import os
from app.storage_backends.file_storage import FileStorage
from app.storage_backends.db_storage import DBStorage


def get_storage_backend():
    backend = os.getenv("STORAGE_BACKEND", "file")
    if backend == "file":
        return FileStorage("uploaded_files")
    elif backend == "db":
        return DBStorage("my_database.db")
    elif backend == "minio":
        return MinioStorage("minio:9000", "minio", "minio123", "3d-files")
    else:
        raise ValueError(f"Unknown storage backend: {backend}")
