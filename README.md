# Benchmarking Framework für 3D-Objekte in AR-Anwendungen

Dieses Repository enthält ein Benchmarking-Framework zur Evaluierung verschiedener Speichertechnologien (Dateisystem,
Datenbank, MinIO) für die Speicherung und Bereitstellung von 3D-Objekten in webbasierten Augmented-Reality-Plattformen.
Die Benchmark-Ergebnisse werden anschließend visuell aufbereitet.

---

## Inhaltsverzeichnis

- [Voraussetzungen](#voraussetzungen)
- [Ablauf](#ablauf)
    - [1. Generierung der Testdaten](#1-generierung-der-testdaten)
    - [2. Start der Docker-Umgebung](#2-start-der-docker-umgebung)
    - [3. Benchmark-Konfiguration und Ausführung](#3-benchmark-konfiguration-und-ausführung)
    - [4. Erzeugung der Diagramme](#4-erzeugung-der-diagramme)
- [WebUIs der Docker-Container](#webuis-der-docker-container)

---

## Voraussetzungen

- **Python 3.x** – zum Ausführen der Skripte
- **Docker** und **Docker Compose** – für die Containerisierung
- Alle notwendigen Python-Pakete (siehe `requirements.txt`)

---

## Ablauf

### 1. Generierung der Testdaten

1. Navigiere in das Verzeichnis `benchmark_files`:
   ```bash
   cd benchmark_files
    ```
2. Führe das Skript `gltf_file_generator.py` aus, um die Testdaten zu generieren:
   ```bash
   python gltf_file_generator.py
   ```
    - Das Skript erzeugt standardisierte Testdaten im glTF 2.0-Format in den Größen small, medium und large. Diese
      Dateien werden benötigt, um den Einfluss der Dateigröße auf die Performanz der Speichertechnologien zu evaluieren.
    - Die generierten GLTF-Dateien werden im Verzeichnis `benchmark_files` gespeichert.

### 2. Start der Docker-Umgebung

1. Nenne die Datei template.env in .env um:
   ```bash
   mv template.env .env
   ```
2. Stelle sicher, dass alle erforderlichen Umgebungsvariablen in der Datei .env korrekt gesetzt sind.
3. Starte die Docker-Container mit dem folgenden Befehl:
   ```bash
   docker-compose up --build -d
   ```
   Dadurch werden folgende Services gestartet:
   • Backend-Services: web_file, web_db, web_minio
   • Speicher-Dienste: MinIO, PostgreSQL
   • Lasttest-Infrastruktur: Locust, Locust Metrics Exporter
   • Monitoring: Telegraf, Prometheus, Grafana
   • Utilities: socat

### 3. Benchmark-Konfiguration und Ausführung

1. Öffne die Datei run_benchmarks.py und passe die Benchmark-Konfiguration (z.B. Anzahl paralleler Requests, Testdauer,
   Dateigrößen etc.) an.
2. Führe das Skript aus, um die Benchmarks zu starten:
   ```bash
   python run_benchmarks.py
   ```
    - Die Benchmarks werden für alle drei Speichertechnologien (Dateisystem, Datenbank, MinIO) durchgeführt.
    - Die Ergebnisse werden in der Datei benchmark_results.json gespeichert.

### 4. Erzeugung der Diagramme

1. Nach Abschluss des Benchmarks lege ein neues Verzeichnis im Ordner benchmark_results an:

```bash
  mkdir benchmark_results/<your_test_run>
  cd benchmark_results/<your_test_run>
   ```

2. Kopiere die Datei benchmark_results.json in das neue Verzeichnis:

```bash
  cp ../benchmark_results.json .
   ```

3. Navigiere in das Verzeichnis und führe das Skript create_diagrams.py aus, um die Diagramme zu erstellen:

```bash
  python ../../benchmark_scripts/create_diagrams.py
```

Das Diagramm-Skript erstellt:
* **Bar-Plots**: Für jede Metrik (Latenz, CPU-Auslastung, RAM-Nutzung) werden Balkendiagramme erstellt, die den Medianwert pro Dateigröße (small, medium, large) und pro Speichertechnologie (db, file, minio) darstellen.
* **Line-Plots**: Für jede Metrik (Latenz, CPU, Memory) und jede Dateigröße (small, medium, large) werden Liniendiagramme mit der Zeit auf der X-Achse erstellt, wobei jeweils drei Linien für die drei Speichertechnologien dargestellt werden.

## WebUIs der Docker-Container

- **Grafana**: [http://localhost:3000](http://localhost:3000)
- **Prometheus**: [http://localhost:9090](http://localhost:9090)
- **MinIO**: [http://localhost:9000](http://localhost:9000) (Standard-Login: minio/minio123)
- **PostgreSQL**: [http://localhost:5432](http://localhost:5432)
- **Locust**: [http://localhost:8089](http://localhost:8089)
- **Locust Metrics Exporter**: [http://localhost:9100](http://localhost:9100)
- **Telegraf**: [http://localhost:8125](http://localhost:8125)
