import pytest

from app.services import MessengerService
from app.storage import JsonStorage
from app.validation import ValidationError


@pytest.fixture
def path(tmp_path):
    return tmp_path / "data.json"


def make_chat(svc):
    a, b = svc.create_user("alice"), svc.create_user("bob")
    return a, b, svc.create_conversation([a.id, b.id])


def test_empty_message_rejected(path):
    svc = MessengerService(JsonStorage(path))
    a, _, conv = make_chat(svc)
    with pytest.raises(ValidationError):
        svc.send_message(conv.id, a.id, "   ")


def test_duplicate_username_rejected(path):
    svc = MessengerService(JsonStorage(path))
    svc.create_user("alice")
    with pytest.raises(ValidationError):
        svc.create_user("Alice")


def test_persistence_after_restart(path):
    svc = MessengerService(JsonStorage(path))
    a, _, conv = make_chat(svc)
    svc.send_message(conv.id, a.id, "привіт")

    reloaded = MessengerService(JsonStorage(path))
    history = reloaded.get_history(conv.id)
    assert [m.text for m in history] == ["привіт"]
    assert history[0].created_at.tzinfo is not None
