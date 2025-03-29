from locust import HttpUser, task, between, tag
from pathlib import Path

BASE_DIR = Path(__file__).parent  # /app/benchmarks
FILE_PATHS = {
    "small": str(BASE_DIR / "benchmark_files" / "small_model.gltf"),
    "medium": str(BASE_DIR / "benchmark_files" / "medium_model.gltf"),
    "large": str(BASE_DIR / "benchmark_files" / "large_model.gltf")
}


class FastAPIUser(HttpUser):
    wait_time = between(1, 3)
    uploaded_id = None

    def on_start(self):

        size_tags = self.environment.parsed_options.tags  # kann str oder Set sein
        print("TAGS: ", self.environment.parsed_options.tags)
        if isinstance(size_tags, (set, list)):
            file_size = list(size_tags)[0]
        else:
            file_size = str(size_tags)
        file_size = file_size.lower()
        if file_size not in FILE_PATHS:
            raise ValueError(f"Ungültiger FILE_SIZE-Tag: {file_size}")

        with open(FILE_PATHS[file_size], "rb") as f:
            resp = self.client.post(
                "/items/",
                files={"file": f},
                data={"name": f"{file_size}_model", "description": f"Testupload {file_size}"}
            )
        if resp.status_code == 200:
            self.uploaded_id = resp.json().get("id")
        else:
            print(f"Upload fehlgeschlagen: {resp.status_code} - {resp.text}")

    @tag("small")
    @task(1)
    def download_small_file(self):
        if self.uploaded_id and "small" in self.environment.parsed_options.tags:
            self.client.get(f"/items/{self.uploaded_id}/download")

    @tag("medium")
    @task(1)
    def download_medium_file(self):
        if self.uploaded_id and "medium" in self.environment.parsed_options.tags:
            self.client.get(f"/items/{self.uploaded_id}/download")

    @tag("large")
    @task(1)
    def download_large_file(self):
        if self.uploaded_id and "large" in self.environment.parsed_options.tags:
            self.client.get(f"/items/{self.uploaded_id}/download")

    def on_stop(self):
        if self.uploaded_id:
            self.client.delete(f"/items/{self.uploaded_id}")
