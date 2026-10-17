import pytest
from fastapi.testclient import TestClient

from app.api import get_service
from app.main import app
from app.services import MessengerService
from app.storage import JsonStorage


@pytest.fixture
def client(tmp_path):
    svc = MessengerService(JsonStorage(tmp_path / "data.json"))
    app.dependency_overrides[get_service] = lambda: svc
    yield TestClient(app)
    app.dependency_overrides.clear()


def user(client, name):
    return client.post("/api/users", json={"username": name}).json()["id"]


def test_group_chat_send_history_search(client):
    ids = [user(client, n) for n in ("alice", "bob", "carol")]
    conv = client.post("/api/conversations", json={"participant_ids": ids, "title": "team"})
    assert conv.status_code == 201
    cid = conv.json()["id"]

    assert client.post(f"/api/conversations/{cid}/messages",
                       json={"sender_id": ids[0], "text": "Привіт усім"}).status_code == 201
    history = client.get(f"/api/conversations/{cid}/messages").json()
    assert [m["text"] for m in history] == ["Привіт усім"]

    found = client.get("/api/search", params={"q": "привіт", "user_id": ids[2]}).json()
    assert len(found) == 1


def test_validation_errors_return_400(client):
    a, b = user(client, "alice"), user(client, "bob")
    cid = client.post("/api/conversations", json={"participant_ids": [a, b]}).json()["id"]
    r = client.post(f"/api/conversations/{cid}/messages", json={"sender_id": a, "text": "  "})
    assert r.status_code == 400
    assert client.post("/api/users", json={"username": "alice"}).status_code == 400
