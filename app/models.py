from dataclasses import dataclass, field
from datetime import datetime, timezone
from uuid import uuid4


def utcnow() -> datetime:
    return datetime.now(timezone.utc)


def new_id() -> str:
    return uuid4().hex


@dataclass
class User:
    username: str
    tag: str = ""  # unique login handle, lowercase, without "@"
    password_hash: str = ""  # salted scrypt hash, see security.py
    id: str = field(default_factory=new_id)


@dataclass
class Conversation:
    participants: list[str]  # user ids
    title: str | None = None
    id: str = field(default_factory=new_id)


@dataclass
class Message:
    conversation_id: str
    sender_id: str
    text: str
    id: str = field(default_factory=new_id)
    created_at: datetime = field(default_factory=utcnow)  # always UTC
