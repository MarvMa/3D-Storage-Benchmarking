import os

from fastapi import UploadFile

from .base_interface import StorageInterface


class FileStorage(StorageInterface):
    def __init__(self, folder="3D-Objects"):
        self.folder = folder
        os.makedirs(self.folder, exist_ok=True)

    async def save_file(self, object_id: str, file: UploadFile) -> None:
        destination = os.path.join(self.folder, str(object_id))
        content = await file.read() if hasattr(file, "read") and callable(file.read) else file.read()
        with open(destination, "wb") as dst:
            dst.write(content)

    async def load_file(self, object_id):
        path = os.path.join(self.folder, str(object_id))
        if not os.path.exists(path):
            return None
        with open(path, "rb") as f:
            return f.read()

    async def delete_file(self, object_id):
        path = os.path.join(self.folder, str(object_id))
        if os.path.exists(path):
            os.remove(path)
