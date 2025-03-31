# ARPAS-backend

## ARPAS-Backend Docker-Commands
### Start Project

docker-compose down -v && docker-compose up -d


### Telegraf
http://localhost:9273/metrics
### Locust
http://localhost:8089
### Grafana
http://localhost:3000
### Prometheus
Prometheus Targets: http://localhost:9090/targets

## Documentation

Swagger Annotation öffnen
http://localhost:8000/docs


Locust

http://web_file:8000

forward docker.sock to tcp
socat TCP-LISTEN:2375,reuseaddr, fork UNIX-CONNECT:/var/run/docker.sock


https://github.com/locustio/locust/issues/2849


# Benchmark
50 Users
23-25 Requests per Second
Duration: 10 Minuten
Cooldown = 100
Durchläufe: small, medium, large
Dateispeicher: File-Storage, MinIO, Database
Requests pro Benchmark: ~14.600 +- 100
```