from locust import HttpUser, task, between, tag, events
from pathlib import Path
import random
import threading
import requests

BASE_DIR = Path(__file__).parent
FILE_PATHS = {
    "small": str(BASE_DIR / "benchmark_files" / "small_model.gltf"),
    "medium": str(BASE_DIR / "benchmark_files" / "medium_model.gltf"),
    "large": str(BASE_DIR / "benchmark_files" / "large_model.gltf")
}

shared_ids = {
    "small": [],
    "medium": [],
    "large": []
}
lock = threading.Lock()
INITIAL_UPLOADS_PER_CATEGORY = 10


@events.test_start.add_listener
def on_test_start(environment, **kwargs):
    print("THIS IS BEEING CALLED")
    session = requests.Session()

    for size in ["small", "medium", "large"]:
        for _ in range(INITIAL_UPLOADS_PER_CATEGORY):
            with open(FILE_PATHS[size], "rb") as f:
                response = session.post(
                    f"{environment.host}/items/",
                    files={"file": f},
                    data={"name": f"{size}_model", "description": f"Shared {size} file"}
                )
                print(response.status_code)
                print(response.json())
                if response.status_code == 200:
                    with lock:
                        shared_ids[size].append(response.json()["id"])


class FastAPIUser(HttpUser):
    wait_time = between(1, 3)

    @task(1)
    @tag("small")
    def download_small(self):
        self.download_random_file("small")

    @task(1)
    @tag("medium")
    def download_medium(self):
        self.download_random_file("medium")

    @task(1)
    @tag("large")
    def download_large(self):
        self.download_random_file("large")

    def download_random_file(self, size_category):
        with lock:
            if not shared_ids[size_category]:
                return

            random_id = random.choice(shared_ids[size_category])

        self.client.get(f"/items/{random_id}/download", name=f"Download {size_category}")
