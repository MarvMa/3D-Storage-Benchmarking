# ARPAS-backend

## ARPAS-Backend Docker-Commands

Build Image and Run Container

```bash
docker-compose up
```

Stop and delete container

```bash
docker-compose down
```

## Testing

Activate virtual environment

```bash
source venv/Scripts/activate
```

Run Test without coverage

```bash
pytest
```

Run Test with coverage and html coverage

```bash
pytest --cov=app --cov-report=html
```
Run Test with coverage and cmd coverage

```bash
pytest --cov=app --cov-report=html
```

Deactivate virtual environment

```bash
deactivate
```

## Documentation

Swagger Annotation öffnen
http://localhost:8000/docs

