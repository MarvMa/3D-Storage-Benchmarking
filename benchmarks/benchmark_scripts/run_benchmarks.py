import time
import requests
import json
import docker

WEB_FILE_URL = "http://web_file:8000"
WEB_DB_URL = "http://web_db:8000"
WEB_MINIO_URL = "http://web_minio:8000"

BENCHMARKS = [
    {"storage": "file", "file_size": "small", "host": f"{WEB_FILE_URL}", "storage_container_name": "file"},
    {"storage": "file", "file_size": "medium", "host": f"{WEB_FILE_URL}", "storage_container_name": "file"},
    {"storage": "file", "file_size": "large", "host": f"{WEB_FILE_URL}", "storage_container_name": "file"},
    {"storage": "db", "file_size": "small", "host": f"{WEB_DB_URL}", "storage_container_name": "arpas_postgres"},
    {"storage": "db", "file_size": "medium", "host": f"{WEB_DB_URL}", "storage_container_name": "arpas_postgres"},
    {"storage": "db", "file_size": "large", "host": f"{WEB_DB_URL}", "storage_container_name": "arpas_postgres"},
    {"storage": "minio", "file_size": "small", "host": f"{WEB_MINIO_URL}", "storage_container_name": "minio-storage"},
    {"storage": "minio", "file_size": "medium", "host": f"{WEB_MINIO_URL}", "storage_container_name": "minio-storage"},
    {"storage": "minio", "file_size": "large", "host": f"{WEB_MINIO_URL}", "storage_container_name": "minio-storage"},
]

LOCUST_API = "http://localhost:8089"
PROMETHEUS_API = "http://localhost:9090/api/v1"

USERS = 200
SPAWN_RATE = 10
RUNTIME = 600  # 60 seconds per benchmark
PAUSE = 60  # Cooldown between benchmarks

client = docker.from_env()


def start_benchmark(host, file_size):
    print(f"Starting benchmark for {file_size} model")
    response = requests.post(f"{LOCUST_API}/swarm", data={
        "user_count": USERS,
        "spawn_rate": SPAWN_RATE,
        "host": host,
        "tags": [file_size]
    })
    response.raise_for_status()
    return time.time()


def stop_benchmark():
    requests.get(f"{LOCUST_API}/stop")
    return time.time()


def query_prometheus(query, start, end):
    response = requests.get(
        f"{PROMETHEUS_API}/query_range",
        params={
            "query": query,
            "start": start,
            "end": end,
            "step": "5s"
        }
    )
    response.raise_for_status()
    return response.json()["data"]["result"]


def collect_metrics(benchmark_name, storage_container_name, file_size, start_time, end_time):
    metrics = {
        "storage": benchmark_name,
        "file_size": file_size,
        "start_time": start_time,
        "end_time": end_time,
        "latency": [],
        "cpu_usage": [],
        "memory_usage": [],
        "io_read": [],
        "io_write": []
    }

    # Latency (median response time)
    latency_data = query_prometheus('locust_requests_median_response_time', start_time, end_time)
    if latency_data:
        metrics["latency"] = [float(point[1]) / 1000 for point in latency_data[0]["values"]]

    # CPU Usage (%)
    cpu_data = query_prometheus(f'docker_container_cpu_usage_percent{{container_name="{storage_container_name}"}}',
                                start_time,
                                end_time)
    if cpu_data:
        metrics["cpu_usage"] = [float(point[1]) for point in cpu_data[0]["values"]]

    # Memory Usage (MB)
    memory_data = query_prometheus(
        f'docker_container_mem_usage{{container_name="{storage_container_name}"}} / 1024 / 1024',
        start_time, end_time)
    if memory_data:
        metrics["memory_usage"] = [float(point[1]) for point in memory_data[0]["values"]]

    # I/O Read (MB/s)
    io_read_data = query_prometheus(
        f'rate(docker_container_blkio_io_service_bytes_recursive_read{{container_name="{storage_container_name}"}}[1m]) / 1024 / 1024',
        start_time, end_time)
    if io_read_data:
        metrics["io_read"] = [float(point[1]) for point in io_read_data[0]["values"]]

    # I/O Write (MB/s)
    io_write_data = query_prometheus(
        f'rate(docker_container_blkio_io_service_bytes_recursive_write{{container_name="{storage_container_name}"}}[1m]) / 1024 / 1024',
        start_time, end_time)
    if io_write_data:
        metrics["io_write"] = [float(point[1]) for point in io_write_data[0]["values"]]

    return metrics


def main():
    results = []
    for benchmark in BENCHMARKS:
        storage = benchmark["storage"]
        file_size = benchmark["file_size"]
        host = benchmark["host"]
        storage_container_name = benchmark["storage_container_name"]

        print(f"\n=== Benchmark: {storage} | File: {file_size} | Host: {host} ===")

        start_time = start_benchmark(host, file_size)
        time.sleep(RUNTIME)
        end_time = stop_benchmark()

        metrics = collect_metrics(storage, storage_container_name, file_size, start_time, end_time)
        results.append(metrics)

        with open("benchmark_results.json", "w") as f:
            json.dump(results, f, indent=2)

        time.sleep(PAUSE)

    print("✅ Alle Benchmarks abgeschlossen. Ergebnisse in benchmark_results.json.")


if __name__ == "__main__":
    main()
