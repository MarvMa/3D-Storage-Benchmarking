import time
import random

from locust import (HttpUser, task, between)
import json
from pathlib import Path


class FastAPIUser(HttpUser):
    """Simulates user behavior for file download load testing.

       Attributes:
           wait_time: Dynamic wait time between tasks (1-3 seconds)
           uploaded_ids: List of preuploaded file IDs for download testing
           benchmark_name: Identifier for current test configuration (storage_type_file_size)
       """
    wait_time = between(1, 3)
    uploaded_ids = []
    benchmark_name = None

    def on_start(self):
        """Initializes user instance with test configuration.

                Loads current benchmark parameters and preuploaded file IDs from JSON files.
                Runs once when each simulated user starts.

                Raises:
                    Exception: If critical configuration files cannot be loaded
                    JSONDecodeError: If configuration files contain invalid JSON
                    FileNotFoundError: If configuration files are missing
                """
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
        """Simulates a file download request.

            Randomly selects a preuploaded file ID and sends a GET request to the
            download endpoint. The request is tagged with the current benchmark
            name for metric tracking.

            Endpoint:
                GET /items/{item_id}/download
            """
        item_id = random.choice(self.uploaded_ids)
        self.client.get(f"/items/{item_id}/download", name=f"{self.benchmark_name}")
