import os
from itertools import cycle

from locust import HttpUser, task, between

FILE_PATHS = {
    "small": "./benchmark_files/small_model.gltf",  # ~1MB
    "medium": "./benchmark_files/medium_model.gltf",  # ~10MB
    "large": "./benchmark_files/large_model.gltf"  # ~100MB
}
ITEMS_ENDPOINT = "/items/"
APPLICATION_OCTET_STREAM = "application/octet-stream"


class FastAPIUser(HttpUser):
    wait_time = between(1, 3)
    file_size_cycle = cycle(["small", "medium", "large"])  # Cycle through sizes evenly

    @task(3)
    def upload_and_delete_file(self):
        size_category = next(self.file_size_cycle)  # Get next file size in order
        file_path = FILE_PATHS[size_category]
        print(f"Uploading {size_category} file: {file_path}")
        with open(file_path, "rb") as f:
            files = {"file": (os.path.basename(file_path), f, APPLICATION_OCTET_STREAM)}
            data = {"name": f"{size_category}_model", "description": f"A {size_category} 3D model"}

            response = self.client.post(
                ITEMS_ENDPOINT,
                files=files,
                data=data,
                name=f"POST /items [{size_category}]"
            )
            if response.status_code == 200:
                obj_id = response.json().get("id")
                print(f"Uploaded {size_category} file with ID: {obj_id}")
                self._delete_item(obj_id, size_category)
            else:
                print(f"Upload failed: {response.status_code} => {response.text}")

    @task(2)
    def download_and_delete_file(self):
        size_category = next(self.file_size_cycle)
        file_path = FILE_PATHS[size_category]
        with open(file_path, "rb") as f:
            files = {"file": (os.path.basename(file_path), f, APPLICATION_OCTET_STREAM)}
            data = {"name": f"{size_category}_model", "description": f"A {size_category} 3D model"}

            response = self.client.post(
                ITEMS_ENDPOINT,
                files=files,
                data=data,
                name=f"POST /items [{size_category}]"
            )
            if response.status_code == 200:
                obj_id = response.json().get("id")
                print(f"Uploaded {size_category} file with ID: {obj_id}")
                download_response = self.client.get(
                    f"{ITEMS_ENDPOINT}{obj_id}/download",
                    name=f"GET /items/download [{size_category}]"
                )
                if download_response.status_code == 200:
                    print(f"Downloaded file with ID: {obj_id}")
                    self._delete_item(obj_id, size_category)
                else:
                    print(f"Download failed: {download_response.status_code} => {download_response.text}")
            else:
                print(f"Upload failed: {response.status_code} => {response.text}")

    @task(1)
    def update_and_delete_file(self):
        size_category = "small"
        file_path = FILE_PATHS[size_category]
        with open(file_path, "rb") as f:
            files = {"file": (os.path.basename(file_path), f, APPLICATION_OCTET_STREAM)}
            data = {"name": "Temporary Model", "description": "A temporary model for update testing"}
            response = self.client.post(
                ITEMS_ENDPOINT,
                files=files,
                data=data,
                name=f"POST /items [{size_category}]"
            )
            if response.status_code == 200:
                obj_id = response.json().get("id")
                print(f"Uploaded file with ID: {obj_id}")
                with open(file_path, "rb") as f_update:
                    update_files = {"file": (os.path.basename(file_path), f_update, APPLICATION_OCTET_STREAM)}
                    update_data = {"name": "Updated Model", "description": "Updated description"}
                    update_response = self.client.put(
                        f"{ITEMS_ENDPOINT}{obj_id}",
                        files=update_files,
                        data=update_data,
                        name=f"PUT /items [{size_category}]"
                    )
                    if update_response.status_code == 200:
                        print(f"Updated file with ID: {obj_id}")
                        self._delete_item(obj_id, size_category)
                    else:
                        print(f"Update failed: {update_response.status_code} => {update_response.text}")
            else:
                print(f"Upload failed: {response.status_code} => {response.text}")

    def _delete_item(self, item_id, size_category):
        response = self.client.delete(
            f"{ITEMS_ENDPOINT}{item_id}",
            name=f"DELETE /items [{size_category}]"
        )
        if response.status_code == 204:
            print(f"Deleted file with ID: {item_id}")
        else:
            print(f"Delete failed: {response.status_code} => {response.text}")
