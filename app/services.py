from dataclasses import asdict
from datetime import datetime

from .models import Conversation, Message, User
from .security import hash_password, verify_password
from .storage import JsonStorage
from .validation import (
    AuthError,
    ValidationError,
    validate_message_text,
    validate_password,
    validate_tag,
    validate_username,
)


class MessengerService:
    """Business logic. Loads data once at startup, saves on every change."""

    def __init__(self, storage: JsonStorage) -> None:
        self.storage = storage
        data = storage.load()
        self.users = [User(**u) for u in data["users"]]
        self.conversations = [Conversation(**c) for c in data["conversations"]]
        self.messages = [
            Message(**{**m, "created_at": datetime.fromisoformat(m["created_at"])})
            for m in data["messages"]
        ]

    def _save(self) -> None:
        self.storage.save(
            {
                "users": [asdict(u) for u in self.users],
                "conversations": [asdict(c) for c in self.conversations],
                "messages": [
                    {**asdict(m), "created_at": m.created_at.isoformat()}
                    for m in self.messages
                ],
            }
        )

    def create_user(
        self, username: str, tag: str, password: str, password_repeat: str
    ) -> User:
        username = validate_username(username)
        tag = validate_tag(tag)
        validate_password(password, password_repeat)
        if any(u.username.lower() == username.lower() for u in self.users):
            raise ValidationError("Користувач з таким ім'ям вже існує")
        if any(u.tag == tag for u in self.users):
            raise ValidationError("Цей тег уже зайнятий")
        user = User(username=username, tag=tag, password_hash=hash_password(password))
        self.users.append(user)
        self._save()
        return user

    def authenticate(self, tag: str, password: str) -> User:
        try:
            tag = validate_tag(tag)
        except ValidationError:
            raise AuthError("Невірний тег або пароль") from None
        user = next((u for u in self.users if u.tag == tag), None)
        # Hash even for an unknown tag so response time doesn't reveal which tags exist.
        stored = user.password_hash if user else hash_password("")
        if not verify_password(password, stored) or user is None:
            raise AuthError("Невірний тег або пароль")
        return user

    def create_conversation(
        self, participant_ids: list[str], title: str | None = None
    ) -> Conversation:
        ids = list(dict.fromkeys(participant_ids))
        if len(ids) < 2:
            raise ValidationError("У розмові має бути щонайменше 2 учасники")
        known = {u.id for u in self.users}
        if not set(ids) <= known:
            raise ValidationError("Невідомий учасник розмови")
        conv = Conversation(participants=ids, title=title)
        self.conversations.append(conv)
        self._save()
        return conv

    def send_message(self, conversation_id: str, sender_id: str, text: str) -> Message:
        conv = next((c for c in self.conversations if c.id == conversation_id), None)
        if conv is None:
            raise ValidationError("Розмову не знайдено")
        if sender_id not in conv.participants:
            raise ValidationError("Відправник не є учасником розмови")
        msg = Message(
            conversation_id=conversation_id,
            sender_id=sender_id,
            text=validate_message_text(text),
        )
        self.messages.append(msg)
        self._save()
        return msg

    def list_conversations(self, user_id: str | None = None) -> list[Conversation]:
        if user_id is None:
            return list(self.conversations)
        return [c for c in self.conversations if user_id in c.participants]

    def search_messages(self, query: str, user_id: str | None = None) -> list[Message]:
        query = query.strip().lower()
        if not query:
            raise ValidationError("Пошуковий запит не може бути порожнім")
        allowed = {c.id for c in self.list_conversations(user_id)}
        return sorted(
            (
                m
                for m in self.messages
                if m.conversation_id in allowed and query in m.text.lower()
            ),
            key=lambda m: m.created_at,
        )

    def get_history(self, conversation_id: str) -> list[Message]:
        return sorted(
            (m for m in self.messages if m.conversation_id == conversation_id),
            key=lambda m: m.created_at,
        )
