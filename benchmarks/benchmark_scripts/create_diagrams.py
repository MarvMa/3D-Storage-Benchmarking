import requests
import matplotlib.pyplot as plt
import json

PROM_URL = "http://localhost:9090/api/v1"
CONTAINERS = {
    "web_file": "file",
    "web_minio": "minio",
    "web_db": "db"
}
METRICS = {
    "cpu": 'rate(container_cpu_usage_seconds_total{container_name="%s"}[1m])',
    "memory": 'container_memory_usage_bytes{container_name="%s"} / 1024 / 1024',
    "io_read": 'rate(container_fs_reads_bytes_total{container_name="%s"}[1m]) / 1024 / 1024',
    "io_write": 'rate(container_fs_writes_bytes_total{container_name="%s"}[1m]) / 1024 / 1024',
    "latency": 'locust_requests_median_response_time{tag="%s"} / 1000'
}


def fetch_metric_data(query, start, end):
    try:
        response = requests.get(
            f"{PROM_URL}/query_range",
            params={
                "query": query,
                "start": start,
                "end": end,
                "step": "1s"
            },
            timeout=10
        )
        return response.json()["data"]["result"]
    except Exception as e:
        print(f"Fehler bei Abfrage: {query}\n{str(e)}")
        return []


def plot_combined_metric(metric, ylabel, filename):
    plt.figure(figsize=(12, 6))

    for benchmark in benchmarks:
        service = benchmark["service"]
        container_label = CONTAINERS[service]
        query = METRICS[metric] % container_label

        data = fetch_metric_data(
            query,
            benchmark["start"],
            benchmark["end"]
        )

        if not data:
            continue

        timestamps = [float(point[0]) - benchmark["start"] for point in data[0]["values"]]
        values = [float(point[1]) for point in data[0]["values"]]

        plt.plot(
            timestamps,
            values,
            label=f"{service}",
            linewidth=2
        )

    plt.xlabel("Zeit seit Benchmark-Start (s)")
    plt.ylabel(ylabel)
    plt.xlim(0, RUNTIME)  # X-Achse auf Benchmark-Dauer beschränken
    plt.legend()
    plt.grid(True)
    plt.savefig(f"{filename}.png", dpi=300, bbox_inches="tight")
    plt.close()


with open("benchmark_times.json") as f:
    benchmarks = json.load(f)

RUNTIME = 60  # Muss mit run_benchmarks.py übereinstimmen
plot_combined_metric("cpu", "CPU Usage (Kerne)", "cpu_usage")
plot_combined_metric("memory", "Memory Usage (MB)", "memory_usage")
plot_combined_metric("io_read", "Read I/O (MB/s)", "io_read")
plot_combined_metric("io_write", "Write I/O (MB/s)", "io_write")
