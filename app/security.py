import hashlib
import hmac
import os

_N, _R, _P = 2**14, 8, 1


def _derive(password: str, salt: bytes) -> bytes:
    return hashlib.scrypt(password.encode("utf-8"), salt=salt, n=_N, r=_R, p=_P)


def hash_password(password: str) -> str:
    """Salted scrypt hash, stored as `salt$hash` (hex). Never store the plain password."""
    salt = os.urandom(16)
    return f"{salt.hex()}${_derive(password, salt).hex()}"


def verify_password(password: str, stored: str) -> bool:
    try:
        salt_hex, hash_hex = stored.split("$")
        expected = bytes.fromhex(hash_hex)
        salt = bytes.fromhex(salt_hex)
    except ValueError:
        return False
    return hmac.compare_digest(_derive(password, salt), expected)
