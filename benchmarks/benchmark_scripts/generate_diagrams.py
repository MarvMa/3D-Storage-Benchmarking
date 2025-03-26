import requests
import matplotlib.pyplot as plt
from datetime import datetime
import json

PROM_URL = "http://localhost:9090/api/v1"
CONTAINERS = {"web_file": "file", "web_minio": "minio", "web_db": "db"}
COLORS = {"web_file": "blue", "web_minio": "gold", "web_db": "red"}
EXTENDED_TIME = 0


def query_range(query, start, end, step="1s"):
    r = requests.get(f"{PROM_URL}/query_range", params={"query": query, "start": start, "end": end, "step": step})
    r.raise_for_status()
    print(f"[DEBUG] Abfrage: {query}, Zeitraum: {start}–{end}")
    print(f"[DEBUG] Ergebnis: {len(r.json()["data"])} Datenpunkte")

    return r.json()["data"]["result"]


def get_plot_window(benchmark):
    start = benchmark["start"]
    end = benchmark["end"]
    warmup_end = start + 0.2 * (end - start)  # 20% Warmup
    bench_duration = end - warmup_end
    left = -5  # Start bei -5s für bessere Visualisierung
    right = (end - start) + 5  # +5s Puffer
    warmup_line = warmup_end - start
    bench_line = end - start
    return left, right, warmup_line, bench_line


def plot_resource_metrics_per_benchmark(metric_name, ylabel, file_prefix, query_template):
    for benchmark in time_windows:
        left, right, warmup_line, bench_line = get_plot_window(benchmark)
        service = benchmark["service"]
        data = query_range(query_template.format(container=CONTAINERS[service]), benchmark["start"],
                           benchmark["end"] + EXTENDED_TIME)
        if not data:
            continue
        x = [float(t[0]) - benchmark["start"] for t in data[0]["values"]]
        y = [float(t[1]) for t in data[0]["values"]]
        plt.figure(figsize=(12, 5))
        plt.plot(x, y, label=service, color=COLORS[service])
        plt.axvline(x=warmup_line, color="gray", linestyle="--")
        plt.axvline(x=bench_line, color="gray", linestyle="--")
        plt.xlim(left, right)
        plt.title(metric_name + " – " + service)
        plt.xlabel("Zeit seit Benchmark-Start [s]")
        plt.ylabel(ylabel)
        plt.legend()
        plt.tight_layout()
        plt.savefig(f"{file_prefix}_{service}.png", dpi=300)
        plt.close()


def plot_combined_metric(metric_name, ylabel, file_prefix, query_template):
    plt.figure(figsize=(12, 6))
    left_list = []
    right_list = []
    for benchmark in time_windows:
        left, right, warmup_line, bench_line = get_plot_window(benchmark)
        left_list.append(left)
        right_list.append(right)
        service = benchmark["service"]
        data = query_range(query_template.format(container=CONTAINERS[service]), benchmark["start"],
                           benchmark["end"] + EXTENDED_TIME)
        if not data:
            print(f"[WARN] Keine Daten für {service} bei {metric_name}")
            continue
        x = [float(t[0]) - benchmark["start"] for t in data[0]["values"]]
        y = [float(t[1]) for t in data[0]["values"]]
        plt.plot(x, y, label=service, color=COLORS[service])
        plt.axvline(x=warmup_line, color="gray", linestyle="--")
        plt.axvline(x=bench_line, color="gray", linestyle="--")
    plt.xlim(min(left_list), max(right_list))
    plt.title(metric_name + " – alle Benchmarks")
    plt.xlabel("Zeit seit Benchmark-Start [s]")
    plt.ylabel(ylabel)
    plt.legend()
    plt.tight_layout()
    plt.savefig(file_prefix + "_combined.png", dpi=300)
    plt.close()


def plot_latency():
    plt.figure(figsize=(12, 6))
    left_list = []
    right_list = []
    for benchmark in time_windows:
        left, right, warmup_line, bench_line = get_plot_window(benchmark)
        left_list.append(left)
        right_list.append(right)
        service = benchmark["service"]
        result = query_range(
            'locust_requests_median_response_time', benchmark["start"], benchmark["end"]
        )
        if not result:
            print(
                f"[WARN] Keine Daten für {service} bei locust_requests_median_response_time")
            continue
        x = [float(t[0]) - benchmark["start"] for t in result[0]["values"]]
        y = [float(t[1]) / 1000.0 for t in result[0]["values"]]
        plt.plot(x, y, label=service, color=COLORS[service])
        plt.axvline(x=warmup_line, color="gray", linestyle="--")
        plt.axvline(x=bench_line, color="gray", linestyle="--")
    plt.xlim(min(left_list), max(right_list))
    plt.title("Latenz (Median) – alle Benchmarks")
    plt.xlabel("Zeit seit Benchmark-Start [s]")
    plt.ylabel("Latenz [s]")
    plt.legend()
    plt.tight_layout()
    plt.savefig("latency_combined.png", dpi=300)
    plt.close()


with open("benchmark_times.json") as f:
    time_windows = json.load(f)

# plot_resource_metrics_per_benchmark("CPU-Auslastung (%)", "CPU [%]", "cpu_usage",
#                                     'docker_container_cpu_usage_percent{{container_name="{container}",cpu="cpu-total"}}')
# plot_resource_metrics_per_benchmark("RAM-Verbrauch (MB)", "RAM [MB]", "mem_usage",
#                                     'docker_container_mem_usage{{container_name="{container}"}} / 1024 / 1024')
# plot_resource_metrics_per_benchmark("Read I/O (MB/s)", "Read I/O [MB/s]", "io_read_usage",
#                                     'rate(docker_container_blkio_io_service_bytes_recursive_read{{container_name="{container}"}}[1m]) / 1024 / 1024')
# plot_resource_metrics_per_benchmark("Write I/O (MB/s)", "Write I/O [MB/s]", "io_write_usage",
#                                     'rate(docker_container_blkio_io_service_bytes_recursive_write{{container_name="{container}"}}[1m]) / 1024 / 1024')
plot_combined_metric("CPU-Auslastung (%)", "CPU [%]", "cpu_usage",
                     'docker_container_cpu_usage_percent{{container_name="{container}",cpu="cpu-total"}}')
plot_combined_metric("RAM-Verbrauch (MB)", "RAM [MB]", "mem_usage",
                     'docker_container_mem_usage{{container_name="{container}"}} / 1024 / 1024')
plot_combined_metric("Read I/O (MB/s)", "Read I/O [MB/s]", "io_read_usage",
                     'rate(docker_container_blkio_io_service_bytes_recursive_read{{container_name="{container}"}}[1m]) / 1024 / 1024')
plot_combined_metric("Write I/O (MB/s)", "Write I/O [MB/s]", "io_write_usage",
                     'rate(docker_container_blkio_io_service_bytes_recursive_write{{container_name="{container}"}}[1m]) / 1024 / 1024')
plot_latency()
print("✅ Alle Diagramme wurden erfolgreich erstellt.")
