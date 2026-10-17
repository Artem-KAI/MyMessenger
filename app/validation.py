import re

MAX_MESSAGE_LENGTH = 2000
MAX_USERNAME_LENGTH = 32
USERNAME_RE = re.compile(r"^[\w.-]+$")


class ValidationError(ValueError):
    pass


def validate_message_text(text: str) -> str:
    text = text.strip()
    if not text:
        raise ValidationError("Повідомлення не може бути порожнім")
    if len(text) > MAX_MESSAGE_LENGTH:
        raise ValidationError(f"Повідомлення довше за {MAX_MESSAGE_LENGTH} символів")
    return text


def validate_username(username: str) -> str:
    username = username.strip()
    if not username:
        raise ValidationError("Ім'я користувача не може бути порожнім")
    if len(username) > MAX_USERNAME_LENGTH:
        raise ValidationError(f"Ім'я довше за {MAX_USERNAME_LENGTH} символів")
    if not USERNAME_RE.match(username):
        raise ValidationError("Ім'я може містити лише літери, цифри, '.', '_' і '-'")
    return username
