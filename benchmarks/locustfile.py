import time

from locust import HttpUser, task, between
import json
from pathlib import Path


class FastAPIUser(HttpUser):
    wait_time = between(1, 3)
    uploaded_id = None

    def on_start(self):
        time.sleep(10)
        try:
            with open(Path(__file__).parent / "benchmark_results" / "current_benchmark.json", "r") as f:
                config = json.load(f)
        except Exception as e:
            print(f"Critical config load failure {e}")
            raise

        with open(Path(__file__).parent / "benchmark_results" / "preuploaded_ids.json", "r") as f:
            preuploaded_ids = json.load(f)

        self.uploaded_id = preuploaded_ids[config["storage"]][config["file_size"]]

    @task(1)
    def download_file(self):
        self.client.get(f"/items/{self.uploaded_id}/download")
