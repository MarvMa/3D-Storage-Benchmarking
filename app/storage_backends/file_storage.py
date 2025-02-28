import os
from .base_interface import StorageInterface


class FileStorage(StorageInterface):
    def __init__(self, folder="3D-Objects"):
        self.folder = folder
        os.makedirs(self.folder, exist_ok=True)

    def save_file(self, object_id: str, file: bytes) -> None:
        destination = os.path.join(self.folder, object_id)
        with open(destination, "wb") as dst:
            dst.write(file)

    def load_file(self, object_id: str) -> bytes:
        path = os.path.join(self.folder, object_id)
        with open(path, "rb") as src:
            return src.read()

    def delete_file(self, object_id: str) -> None:
        path = os.path.join(self.folder, object_id)
        if os.path.exists(path):
            os.remove(path)
