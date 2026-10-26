import pytest

from app.services import MessengerService
from app.storage import JsonStorage
from app.validation import AuthError, ValidationError


@pytest.fixture
def path(tmp_path):
    return tmp_path / "data.json"


def add_user(svc, name, password="secret1"):
    return svc.create_user(name, name.lower() + "_tag", password, password)


def make_chat(svc):
    a, b = add_user(svc, "alice"), add_user(svc, "bob")
    return a, b, svc.create_conversation([a.id, b.id])


def test_empty_message_rejected(path):
    svc = MessengerService(JsonStorage(path))
    a, _, conv = make_chat(svc)
    with pytest.raises(ValidationError):
        svc.send_message(conv.id, a.id, "   ")


def test_duplicate_username_rejected(path):
    svc = MessengerService(JsonStorage(path))
    add_user(svc, "alice")
    with pytest.raises(ValidationError):
        svc.create_user("Alice", "other_tag", "secret1", "secret1")


def test_duplicate_tag_rejected_case_insensitive(path):
    svc = MessengerService(JsonStorage(path))
    svc.create_user("alice", "Alice_1", "secret1", "secret1")
    with pytest.raises(ValidationError, match="зайнятий"):
        svc.create_user("bob", "@alice_1", "secret1", "secret1")


@pytest.mark.parametrize(
    "tag, password, repeat",
    [("ab", "secret1", "secret1"), ("bad tag", "secret1", "secret1"),
     ("good_tag", "short", "short"), ("good_tag", "secret1", "secret2")],
)
def test_registration_validation(path, tag, password, repeat):
    svc = MessengerService(JsonStorage(path))
    with pytest.raises(ValidationError):
        svc.create_user("alice", tag, password, repeat)
    assert svc.users == []


def test_authenticate_and_hash_not_plaintext(path):
    svc = MessengerService(JsonStorage(path))
    add_user(svc, "alice")
    assert svc.authenticate("ALICE_TAG", "secret1").username == "alice"
    with pytest.raises(AuthError):
        svc.authenticate("alice_tag", "wrong-pass")
    with pytest.raises(AuthError):
        svc.authenticate("nobody", "secret1")
    assert "secret1" not in path.read_text(encoding="utf-8")
    assert MessengerService(JsonStorage(path)).authenticate("alice_tag", "secret1")


def test_persistence_after_restart(path):
    svc = MessengerService(JsonStorage(path))
    a, _, conv = make_chat(svc)
    svc.send_message(conv.id, a.id, "привіт")

    reloaded = MessengerService(JsonStorage(path))
    history = reloaded.get_history(conv.id)
    assert [m.text for m in history] == ["привіт"]
    assert history[0].created_at.tzinfo is not None


def test_corrupted_file_raises_storage_error(path):
    from app.storage import StorageError

    path.write_text("{ не json", encoding="utf-8")
    with pytest.raises(StorageError):
        MessengerService(JsonStorage(path))
