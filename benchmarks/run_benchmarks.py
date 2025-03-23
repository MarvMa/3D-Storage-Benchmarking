import time
import requests
import json
from datetime import datetime

BENCHMARKS = [
    {"name": "web_file", "host": "http://web_file:8000"},
    {"name": "web_minio", "host": "http://web_minio:8000"},
    {"name": "web_db", "host": "http://web_db:8000"},
]

LOCUST_API = "http://localhost:8089"  # falls lokal, ggf. anpassen bei Container-Nutzung
USERS = 50
SPAWN_RATE = 5
RUNTIME = 20  #300 Sekunden (z.B. 5 Minuten Benchmark)
PAUSE = 10  # Sekunden zwischen Benchmarks

results = []


def start_benchmark(target):
    print(f"[{target['name']}] Starte Benchmark...")
    r = requests.post(f"{LOCUST_API}/swarm", data={
        "user_count": USERS,
        "spawn_rate": SPAWN_RATE,
        "host": target["host"]
    })
    if r.status_code != 200:
        raise RuntimeError(f"Fehler beim Starten von {target['name']}: {r.text}")
    return time.time()


def stop_benchmark():
    r = requests.get(f"{LOCUST_API}/stop")
    if r.status_code != 200:
        raise RuntimeError(f"Fehler beim Stoppen: {r.text}")
    return time.time()


for benchmark in BENCHMARKS:
    start = start_benchmark(benchmark)
    time.sleep(RUNTIME)
    end = stop_benchmark()
    results.append({
        "service": benchmark["name"],
        "start": int(start),
        "end": int(end)
    })
    print(f"[{benchmark['name']}] Benchmark abgeschlossen. Warte {PAUSE}s...\n")
    time.sleep(PAUSE)

with open("benchmark_times.json", "w") as f:
    json.dump(results, f, indent=2)

print("✅ Alle Benchmarks abgeschlossen. Zeitfenster gespeichert in benchmark_times.json.")
