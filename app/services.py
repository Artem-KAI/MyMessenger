from dataclasses import asdict
from datetime import datetime

from .models import Conversation, Message, User
from .storage import JsonStorage
from .validation import ValidationError, validate_message_text, validate_username


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

    def create_user(self, username: str) -> User:
        username = validate_username(username)
        if any(u.username.lower() == username.lower() for u in self.users):
            raise ValidationError("Користувач з таким ім'ям вже існує")
        user = User(username=username)
        self.users.append(user)
        self._save()
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

    def get_history(self, conversation_id: str) -> list[Message]:
        return sorted(
            (m for m in self.messages if m.conversation_id == conversation_id),
            key=lambda m: m.created_at,
        )
