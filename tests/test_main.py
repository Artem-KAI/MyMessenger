from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


def test_health():
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


def test_websocket_broadcast():
    with client.websocket_connect("/ws/alice") as ws:
        assert ws.receive_text() == "alice приєднався до чату"
        ws.send_text("привіт")
        assert ws.receive_text() == "alice: привіт"
