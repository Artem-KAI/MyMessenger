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


def register(client, name, tag=None, password="secret1", repeat=None):
    return client.post("/api/users", json={
        "username": name, "tag": tag or name + "_tag",
        "password": password, "password_repeat": repeat or password,
    })


def user(client, name):
    return register(client, name).json()["id"]


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
    assert register(client, "alice2", tag="alice_tag").status_code == 400  # tag taken


def test_register_password_mismatch_and_login(client):
    r = register(client, "alice", password="secret1", repeat="secret2")
    assert r.status_code == 400
    ok = register(client, "alice")
    assert ok.status_code == 201
    assert "password" not in str(ok.json()) and ok.json()["tag"] == "alice_tag"

    good = client.post("/api/login", json={"tag": "Alice_Tag", "password": "secret1"})
    assert good.status_code == 200 and good.json()["id"] == ok.json()["id"]
    bad = client.post("/api/login", json={"tag": "alice_tag", "password": "nope-nope"})
    assert bad.status_code == 401
    assert client.get("/api/users").json()[0].keys() == {"id", "username", "tag"}
