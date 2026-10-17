import os
from functools import lru_cache

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel

from .models import Conversation, Message, User
from .services import MessengerService
from .storage import JsonStorage, StorageError
from .validation import ValidationError

router = APIRouter(prefix="/api")


@lru_cache
def get_service() -> MessengerService:
    path = os.environ.get("MESSENGER_DATA", "data/messenger.json")
    return MessengerService(JsonStorage(path))


class UserIn(BaseModel):
    username: str


class ConversationIn(BaseModel):
    participant_ids: list[str]
    title: str | None = None


class MessageIn(BaseModel):
    sender_id: str
    text: str


def user_out(u: User) -> dict:
    return {"id": u.id, "username": u.username}


def conversation_out(c: Conversation) -> dict:
    return {"id": c.id, "title": c.title, "participants": c.participants}


def message_out(m: Message) -> dict:
    return {
        "id": m.id,
        "conversation_id": m.conversation_id,
        "sender_id": m.sender_id,
        "text": m.text,
        "created_at": m.created_at.isoformat(),  # UTC, ISO 8601
    }


def fail(e: Exception) -> HTTPException:
    if isinstance(e, StorageError):
        return HTTPException(500, str(e))
    return HTTPException(400, str(e))


# Endpoints are `async def` on purpose: they run on the event loop one at a time,
# so the in-memory service needs no extra locking.
@router.post("/users", status_code=201)
async def create_user(body: UserIn, svc: MessengerService = Depends(get_service)):
    try:
        return user_out(svc.create_user(body.username))
    except (ValidationError, StorageError) as e:
        raise fail(e)


@router.get("/users")
async def list_users(svc: MessengerService = Depends(get_service)):
    return [user_out(u) for u in svc.users]


@router.post("/conversations", status_code=201)
async def create_conversation(
    body: ConversationIn, svc: MessengerService = Depends(get_service)
):
    try:
        return conversation_out(svc.create_conversation(body.participant_ids, body.title))
    except (ValidationError, StorageError) as e:
        raise fail(e)


@router.get("/conversations")
async def list_conversations(
    user_id: str | None = None, svc: MessengerService = Depends(get_service)
):
    return [conversation_out(c) for c in svc.list_conversations(user_id)]


@router.get("/conversations/{conversation_id}/messages")
async def get_history(conversation_id: str, svc: MessengerService = Depends(get_service)):
    return [message_out(m) for m in svc.get_history(conversation_id)]


@router.post("/conversations/{conversation_id}/messages", status_code=201)
async def send_message(
    conversation_id: str, body: MessageIn, svc: MessengerService = Depends(get_service)
):
    try:
        return message_out(svc.send_message(conversation_id, body.sender_id, body.text))
    except (ValidationError, StorageError) as e:
        raise fail(e)


@router.get("/search")
async def search(
    q: str, user_id: str | None = None, svc: MessengerService = Depends(get_service)
):
    try:
        return [message_out(m) for m in svc.search_messages(q, user_id)]
    except ValidationError as e:
        raise fail(e)
