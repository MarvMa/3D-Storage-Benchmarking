import time
import random

from locust import (HttpUser, task, between)
import json
from pathlib import Path


class FastAPIUser(HttpUser):
    wait_time = between(1, 3)
    uploaded_ids = []
    benchmark_name = None

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

        self.uploaded_ids = preuploaded_ids[config["storage"]][config["file_size"]]
        self.benchmark_name = f"{config['storage']}_{config['file_size']}"

    @task(1)
    def download_file(self):
        item_id = random.choice(self.uploaded_ids)
        self.client.get(f"/items/{item_id}/download", name=f"{self.benchmark_name}")
