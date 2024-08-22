# tests/test_routes.py
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def test_read_examples():
    response = client.get("/examples/")
    assert response.status_code == 200
    assert isinstance(response.json(), list)
