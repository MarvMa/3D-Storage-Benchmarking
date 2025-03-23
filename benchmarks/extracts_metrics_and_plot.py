# extract_metrics_and_plot.py
import requests
import matplotlib.pyplot as plt
import pandas as pd
from datetime import datetime
import json

PROM_URL = "http://localhost:9090/api/v1"
CONTAINERS = {
    "web_file": "file",
    "web_minio": "minio",
    "web_db": "db"
}

def query_range(query, start, end, step="10s"):
    request = requests.get(f"{PROM_URL}/query_range", params={
        "query": query,
        "start": start,
        "end": end,
        "step": step
    })
    request.raise_for_status()
    return request.json()["data"]["result"]

def plot_metric(metric_name, ylabel, file_prefix, query_template):
    plt.figure(figsize=(12, 6))
    plotted = False
    for label, cname in CONTAINERS.items():
        query = query_template.format(container=cname)
        data = query_range(query, start_time, end_time)
        if not data:
            print(f"[WARN] Keine Daten für {label} bei Query: {query}")
            continue
        timestamps = [datetime.fromtimestamp(float(t[0])) for t in data[0]["values"]]
        values = [float(t[1]) for t in data[0]["values"]]
        plt.plot(timestamps, values, label=label)
        plotted = True

    if plotted:
        plt.legend()

    plt.title(f"{metric_name} während der Benchmarks")
    plt.xlabel("Zeit")
    plt.ylabel(ylabel)
    plt.legend()
    plt.tight_layout()
    plt.savefig(f"{file_prefix}.png", dpi=300)
    plt.close()

# Lade Zeitintervalle
with open("benchmark_times.json") as f:
    time_windows = json.load(f)

start_time = min(b["start"] for b in time_windows)
end_time = max(b["end"] for b in time_windows)

# Diagramme erzeugen
plot_metric("CPU-Auslastung (%)", "CPU [%]", "cpu_usage",
            'docker_container_cpu_usage_percent{{container_name="{container}",cpu="cpu-total"}}')

plot_metric("RAM-Verbrauch (MB)", "RAM [MB]", "mem_usage",
            'docker_container_mem_usage{{container_name="{container}"}} / 1024 / 1024')

plot_metric("Block I/O (MB/s)", "I/O [MB/s]", "io_usage",
            'rate(docker_container_blkio_io_service_bytes_recursive_total{{container_name="{container}"}}[1m]) / 1024 / 1024')

# Locust-Latenz (pro Benchmark separat)
for b in time_windows:
    q = 'avg_over_time(locust_request_duration_seconds_avg{{}}[{duration}s])'.format(
        duration=b["end"] - b["start"]
    )
    r = query_range("locust_request_duration_seconds_avg", b["start"], b["end"])
    if not r: continue
    timestamps = [datetime.fromtimestamp(float(t[0])) for t in r[0]["values"]]
    values = [float(t[1]) for t in r[0]["values"]]
    plt.figure(figsize=(12, 5))
    plt.plot(timestamps, values, label=b["service"])
    plt.title(f"Antwortzeiten – {b['service']}")
    plt.xlabel("Zeit")
    plt.ylabel("Antwortzeit [s]")
    plt.legend()
    plt.tight_layout()
    plt.savefig(f"response_time_{b['service']}.png", dpi=300)
    plt.close()

print("✅ Alle Diagramme wurden gespeichert.")
