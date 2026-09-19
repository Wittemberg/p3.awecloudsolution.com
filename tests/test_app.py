from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def test_bootstrap_is_explicit_and_accessible():
    response = client.get("/")
    assert response.status_code == 200
    assert 'lang="pt-BR"' in response.text
    assert "ainda não está disponível" in response.text

def test_health_reports_revision(monkeypatch):
    monkeypatch.setenv("APP_REVISION", "test-revision")
    assert client.get("/api/health").json() == {
        "status": "ok", "stage": "bootstrap", "revision": "test-revision"}

def test_hello():
    assert client.get("/api/hello").status_code == 200

def test_business_ingestion_is_not_exposed():
    assert client.post("/api/v1/events", json={}).status_code == 404
