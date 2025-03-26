import time
import requests
import json

BENCHMARKS = [
    {"name": "web_file", "host": "http://web_file:8000"},
    {"name": "web_minio", "host": "http://web_minio:8000"},
    {"name": "web_db", "host": "http://web_db:8000"},
]

LOCUST_API = "http://localhost:8089"
USERS = 50
SPAWN_RATE = 5
RUNTIME = 60
PAUSE = 20


def wait_until_running():
    for _ in range(30):
        try:
            stats = requests.get(f"{LOCUST_API}/stats/requests").json()
            if stats["state"] == "running" and stats["user_count"] == USERS:
                return
        except:
            time.sleep(1)
    raise TimeoutError("Locust nicht bereit")


def run_benchmark(target):
    response = requests.post(
        f"{LOCUST_API}/swarm",
        json={"user_count": USERS, "spawn_rate": SPAWN_RATE, "host": target["host"]}
    )
    response.raise_for_status()
    # wait_until_running()
    start = time.time()
    time.sleep(RUNTIME)
    end = time.time()
    return {"service": target["name"], "start": start, "end": end}


results = []
for benchmark in BENCHMARKS:
    result = run_benchmark(benchmark)
    results.append(result)
    time.sleep(PAUSE)

with open("benchmark_times.json", "w") as f:
    json.dump(results, f, indent=2)
