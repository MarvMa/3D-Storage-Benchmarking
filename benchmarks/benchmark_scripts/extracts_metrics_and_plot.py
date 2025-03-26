import requests
import matplotlib.pyplot as plt
from datetime import datetime
import json

PROM_URL = "http://localhost:9090/api/v1"
CONTAINERS = {
    "web_file": "file",
    "web_minio": "minio",
    "web_db": "db",
    # "minio": "minio-storage"
}
COLORS = {
    "web_file": "blue",
    "web_minio": "gold",
    "web_db": "red",
    # "minio": "yellow"
}
EXTENDED_TIME = 30  # 30 Sekunden zusätzlich abfragen


def query_range(query, start, end, step="1s"):
    request = requests.get(f"{PROM_URL}/query_range", params={
        "query": query,
        "start": start,
        "end": end,
        "step": step
    })
    request.raise_for_status()
    return request.json()["data"]["result"]


def plot_resource_metrics_per_benchmark(metric_name, ylabel, file_prefix, query_template):
    for benchmark in time_windows:
        service = benchmark["service"]
        container_label = CONTAINERS[service]
        start = benchmark["start"]
        end = benchmark["end"]
        query = query_template.format(container=container_label)

        print(f"[INFO] Plot {metric_name} für {service} von t={start} bis {end}")

        extended_end = end + EXTENDED_TIME  # 10 Sekunden zusätzlich abfragen
        data = query_range(query, start, extended_end)

        if not data:
            print(f"[WARN] Keine Daten für {service} bei Query: {query}")
            continue

        timestamps = [float(t[0]) - start for t in data[0]["values"]]  # Zeit in Sekunden seit Benchmark-Start
        values = [float(t[1]) for t in data[0]["values"]]

        plt.figure(figsize=(12, 5))
        plt.plot(timestamps, values, label=service, color=COLORS[service])
        plt.title(f"{metric_name} – {service}")
        plt.xlabel("Zeit seit Benchmark-Start [s]")
        plt.ylabel(ylabel)
        plt.legend()
        plt.tight_layout()
        plt.savefig(f"{file_prefix}_{service}.png", dpi=300)
        plt.close()


def plot_combined_metric(metric_name, ylabel, file_prefix, query_template):
    plt.figure(figsize=(12, 6))

    # 1) Ermittle das längste Benchmark-Fenster
    max_duration = 0
    for benchmark in time_windows:
        duration = benchmark["end"] - benchmark["start"] + EXTENDED_TIME
        if duration > max_duration:
            max_duration = duration

    # 2) Alle Benchmarks gemeinsam plotten
    for benchmark in time_windows:
        service = benchmark["service"]
        container_label = CONTAINERS[service]
        start = benchmark["start"]
        end = benchmark["end"]
        duration = end - start

        print(f"[INFO] Kombiniert: {metric_name} für {service} von t={start} bis {end}")
        extended_end = end + EXTENDED_TIME  # 10 Sekunden zusätzlich abfragen
        data = query_range(query_template.format(container=container_label), start, extended_end)
        if not data:
            print(f"[WARN] Keine Daten für {service}")
            continue

        # Zeit relativ zum Benchmark-Start
        rel_times = [float(t[0]) - start for t in data[0]["values"]]
        values = [float(t[1]) for t in data[0]["values"]]

        # Plot Kurve
        plt.plot(rel_times, values, label=service, color=COLORS[service])

        # Vertikale gestrichelte Linie am Benchmark-Start (0) und -Ende (duration)
        plt.axvline(x=0, color="gray", linestyle="--")
        plt.axvline(x=duration, color="gray", linestyle="--")

    # 3) X-Achse bis 10s nach dem längsten Benchmark
    plt.xlim(0, max_duration + 10)

    # Beschriftung, Layout, Speichern
    plt.title(f"{metric_name} – alle Benchmarks")
    plt.xlabel("Zeit seit jeweiligem Benchmark-Start [s]")
    plt.ylabel(ylabel)
    plt.legend()
    plt.tight_layout()
    plt.savefig(f"{file_prefix}_combined.png", dpi=300)
    plt.close()


def plot_combined_avg_locust_latency():
    plt.figure(figsize=(12, 6))

    # Längstes Benchmark-Fenster bestimmen (inkl. EXTENDED_TIME)
    max_duration = 0
    for benchmark in time_windows:
        duration = benchmark["end"] - benchmark["start"] + EXTENDED_TIME
        if duration > max_duration:
            max_duration = duration

    # Alle Benchmarks gemeinsam plotten
    for benchmark in time_windows:
        service = benchmark["service"]
        start = benchmark["start"]
        end = benchmark["end"]
        duration = end - start
        extended_end = end + EXTENDED_TIME

        print(f"[INFO] Kombinierte Latenz (AVG) für {service} von t={start} bis {extended_end}")

        # PromQL-Abfrage: Aggregation über alle Methoden/Endpunkte
        # => locust_requests_avg_response_time oder locust_requests_median_response_time
        query = 'avg without (method, name) (locust_requests_avg_response_time)'
        # Falls du median statt avg willst:
        # query = 'avg without (method, name) (locust_requests_median_response_time)'

        # Zeitbereich abfragen
        result = query_range(query, start, extended_end)
        if not result:
            print(f"[WARN] Keine Latenzdaten für {service}")
            continue

        # Zeit relativ zum Benchmark-Start
        rel_times = [float(t[0]) - start for t in result[0]["values"]]
        values = [float(t[1]) / 1000.0 for t in result[0]["values"]]

        # Zeichnen der Kurve in einer festgelegten Farbe
        plt.plot(rel_times, values, label=service, color=COLORS[service])

        # Vertikale gestrichelte Linien bei Benchmark-Start (0) und -Ende (duration)
        plt.axvline(x=0, color="gray", linestyle="--")
        plt.axvline(x=duration, color="gray", linestyle="--")

    # X-Achse bis 10s nach dem längsten Benchmark
    plt.xlim(0, max_duration + 10)
    plt.title("Latenz (AVG über alle Endpunkte) – alle Benchmarks")
    plt.xlabel("Zeit seit Benchmark-Start [s]")
    plt.ylabel("Latenz [s]")  # Falls in ms, entsprechend anpassen oder umrechnen
    plt.legend()
    plt.tight_layout()
    plt.savefig("latency_combined_avg.png", dpi=300)
    plt.close()


# Lade Zeitintervalle
with open("benchmark_times.json") as f:
    time_windows = json.load(f)

# # Pro Benchmark → einzelne Diagramme für jede Metrik
# plot_resource_metrics_per_benchmark("CPU-Auslastung (%)", "CPU [%]", "cpu_usage",
#                                     'docker_container_cpu_usage_percent{{container_name="{container}",cpu="cpu-total"}}')
#
# plot_resource_metrics_per_benchmark("RAM-Verbrauch (MB)", "RAM [MB]", "mem_usage",
#                                     'docker_container_mem_usage{{container_name="{container}"}} / 1024 / 1024')
#
# plot_resource_metrics_per_benchmark("Write I/O (MB/s)", "I/O [MB/s]", "io_usage",
#                                     'rate(docker_container_blkio_io_service_bytes_recursive_write{{container_name="{container}"}}[1m]) / 1024 / 1024')

# Kombinierte Diagramme
plot_combined_metric("CPU-Auslastung (%)", "CPU [%]", "cpu_usage",
                     'docker_container_cpu_usage_percent{{container_name="{container}",cpu="cpu-total"}}')

plot_combined_metric("RAM-Verbrauch (MB)", "RAM [MB]", "mem_usage",
                     'docker_container_mem_usage{{container_name="{container}"}} / 1024 / 1024')

plot_combined_metric("Read I/O (MB/s)", "Read I/O [MB/s]", "io_read_usage",
                     'rate(docker_container_blkio_io_service_bytes_recursive_read{{container_name="{container}"}}[1m]) / 1024 / 1024')

plot_combined_metric("Write I/O (MB/s)", "Write I/O [MB/s]", "io_write_usage",
                     'rate(docker_container_blkio_io_service_bytes_recursive_write{{container_name="{container}"}}[1m]) / 1024 / 1024')

# Latenz separat
plot_combined_avg_locust_latency()

print("✅ Alle Diagramme wurden erfolgreich erstellt.")
