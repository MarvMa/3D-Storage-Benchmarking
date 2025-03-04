import os
import random
from locust import HttpUser, task, between

FILE_NAME = "./benchmark_files/model.gltf"


class FastAPIUser(HttpUser):
    """
    Simulated user that hits your FastAPI service for load testing.
    We'll do store, list, retrieve, etc.
    """
    wait_time = between(1, 3)  # seconds between tasks

    # Prepare data in memory once to avoid repeated disk reads.
    with open(FILE_NAME, "rb") as f:
        file_data = f.read()

    @task(2)
    def upload_file(self):
        files = {
            "file": ("model.gltf", self.file_data, "application/octet-stream")
        }
        data = {
            "name": "model.gltf",
            "description": "A 3D model"
        }

        response = self.client.post("/items/", files=files, data=data)
        obj_id = None
        if response.status_code == 200:
            obj_id = response.json().get("id")
        if obj_id:
            print(f"Uploaded file with ID: {obj_id}")
        else:
            print(f"Upload failed: {response.status_code} => {response.text}")

# @task(1)
# def list_items(self):
#     """Hit the 'list' endpoint (GET /items or similar)."""
#     response = self.client.get("/items")
#     if response.status_code != 200:
#         print(f"List items failed: {response.status_code}")

# @task(1)
# def retrieve_random_item(self):
#     """
#     Optionally retrieve a random item (GET /items/{id} or /retrieve/{obj_id}).
#     You might also parse a list from the 'list_items' call and pick an ID.
#     For now, we assume a placeholder item ID or handle 404 gracefully.
#     """
#     random_id = 123  # Replace with logic to pick a real ID
#     response = self.client.get(f"/retrieve/{random_id}")
#     # If it returns 404 for nonexistent ID, not necessarily an error:
#     if response.status_code not in (200, 404):
#         print(f"Retrieve item error: {response.status_code}")
