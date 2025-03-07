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
socat TCP-LISTEN:2375,reuseaddr,fork UNIX-CONNECT:/var/run/docker.sock