from fastapi.testclient import TestClient
from main import app

client = TestClient(app)

def test_healthz_endpoint():
    """Verifica que el endpoint de salud responde correctamente y la base de datos está viva."""
    response = client.get("/v1/healthz")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}

def test_list_events_pagination():
    """Verifica que la lista de eventos devuelve el contrato JSON estructurado correctamente."""
    response = client.get("/v1/events/?page=1&page_size=5")
    assert response.status_code == 200
    data = response.json()
    assert "count" in data
    assert "page" in data
    assert "results" in data
    assert isinstance(data["results"], list)

def test_event_not_found():
    """Verifica que buscar un UUID que no existe devuelve un error 404."""
    fake_uuid = "12345678-1234-5678-1234-567812345678"
    response = client.get(f"/v1/events/{fake_uuid}")
    assert response.status_code == 404

def test_rate_limiter_blocks_bots():
    """Simula un ataque de bot haciendo peticiones rápidas a los eventos para verificar el bloqueo (429)"""
    for _ in range(20):
        client.get("/v1/events/")
        
    response = client.get("/v1/events/")
    assert response.status_code == 429
    assert "Retry-After" in response.headers

def test_search_endpoint():
    response = client.get("/v1/events/search/?query=NASA")
    assert response.status_code == 200
    assert "results" in response.json()