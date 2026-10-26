import re

MAX_MESSAGE_LENGTH = 2000
MAX_USERNAME_LENGTH = 32
USERNAME_RE = re.compile(r"^[\w.-]+$")


MIN_TAG_LENGTH = 3
MAX_TAG_LENGTH = 32
TAG_RE = re.compile(r"^[A-Za-z0-9_]+$")
MIN_PASSWORD_LENGTH = 6
MAX_PASSWORD_LENGTH = 128


class ValidationError(ValueError):
    pass


class AuthError(Exception):
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


def validate_tag(tag: str) -> str:
    tag = tag.strip().removeprefix("@")
    if not tag:
        raise ValidationError("Тег не може бути порожнім")
    if not MIN_TAG_LENGTH <= len(tag) <= MAX_TAG_LENGTH:
        raise ValidationError(f"Тег має містити від {MIN_TAG_LENGTH} до {MAX_TAG_LENGTH} символів")
    if not TAG_RE.match(tag):
        raise ValidationError("Тег може містити лише латинські літери, цифри та '_'")
    return tag.lower()


def validate_password(password: str, repeat: str) -> str:
    if not MIN_PASSWORD_LENGTH <= len(password) <= MAX_PASSWORD_LENGTH:
        raise ValidationError(
            f"Пароль має містити від {MIN_PASSWORD_LENGTH} до {MAX_PASSWORD_LENGTH} символів"
        )
    if password != repeat:
        raise ValidationError("Паролі не збігаються")
    return password
