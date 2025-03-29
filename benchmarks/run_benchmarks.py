import time
import requests
import json
from datetime import datetime

BENCHMARKS = [
    {"name": "web_file", "host": "http://web_file:8000"},
    {"name": "web_minio", "host": "http://web_minio:8000"},
    {"name": "web_db", "host": "http://web_db:8000"},
]

LOCUST_API = "http://localhost:8089"
USERS = 50
SPAWN_RATE = 5
RUNTIME = 60  #300 Sekunden (z.B. 5 Minuten Benchmark)
PAUSE = 20  # Sekunden zwischen Benchmarks

results = []

def wait_until_spawn_complete(timeout=60):
    import time
    start_wait = time.time()
    while time.time() - start_wait < timeout:
        try:
            r = requests.get(f"{LOCUST_API}/stats/requests")
            r.raise_for_status()
            data = r.json()
            if data.get("state") == "running":
                print("[INFO] Locust hat die Spawnphase beendet (state=running).")
                return
        except Exception as e:
            print(f"[WARN] Warte auf Spawnabschluss: {e}")
        time.sleep(1)
    raise RuntimeError("Timeout: Locust hat den Zustand 'running' nicht erreicht.")


def start_benchmark(target):
    print(f"[{target['name']}] Starte Benchmark...")
    r = requests.post(f"{LOCUST_API}/swarm", data={
        "user_count": USERS,
        "spawn_rate": SPAWN_RATE,
        "host": target["host"]
    })
    if r.status_code != 200:
        raise RuntimeError(f"Fehler beim Starten von {target['name']}: {r.text}")

    wait_until_spawn_complete()

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
        "start": start,
        "end": end
    })
    print(f"[{benchmark['name']}] Benchmark abgeschlossen. Warte {PAUSE}s...\n")
    time.sleep(PAUSE)

with open("benchmark_times.json", "w") as f:
    json.dump(results, f, indent=2)

print("✅ Alle Benchmarks abgeschlossen. Zeitfenster gespeichert in benchmark_times.json.")
