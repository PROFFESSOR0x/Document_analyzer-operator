"""Additional security utilities."""

import hashlib
import hmac
import secrets
import string
from typing import Optional, Tuple

from app.core.settings import get_settings

settings = get_settings()


def generate_secure_token(length: int = 32) -> str:
    """Generate a cryptographically secure random token.

    Args:
        length: Length of the token in characters.

    Returns:
        str: Secure random token.
    """
    alphabet = string.ascii_letters + string.digits
    return "".join(secrets.choice(alphabet) for _ in range(length))


def generate_api_key(prefix: str = "sk") -> str:
    """Generate a secure API key.

    Args:
        prefix: Prefix for the API key.

    Returns:
        str: API key with prefix.
    """
    random_part = secrets.token_urlsafe(32)
    return f"{prefix}_{random_part}"


def verify_api_key(provided_key: str, stored_hash: str, salt: str) -> bool:
    """Verify an API key against a stored hash.

    Args:
        provided_key: The API key to verify.
        stored_hash: The stored hash to compare against.
        salt: The salt used for hashing.

    Returns:
        bool: True if the key matches.
    """
    provided_hash = hash_api_key(provided_key, salt)
    return hmac.compare_digest(provided_hash, stored_hash)


def hash_api_key(api_key: str, salt: Optional[str] = None) -> Tuple[str, str]:
    """Hash an API key with a salt.

    Args:
        api_key: The API key to hash.
        salt: Optional salt (generated if not provided).

    Returns:
        Tuple: (hashed_key, salt)
    """
    if salt is None:
        salt = secrets.token_hex(16)

    salted_key = f"{salt}{api_key}".encode("utf-8")
    hashed = hashlib.sha256(salted_key).hexdigest()

    return hashed, salt


def constant_time_compare(a: str, b: str) -> bool:
    """Compare two strings in constant time to prevent timing attacks.

    Args:
        a: First string.
        b: Second string.

    Returns:
        bool: True if strings are equal.
    """
    return hmac.compare_digest(a.encode("utf-8"), b.encode("utf-8"))


def sanitize_input(input_str: str, max_length: int = 1000) -> str:
    """Sanitize user input by removing potentially dangerous characters.

    Args:
        input_str: The input string to sanitize.
        max_length: Maximum allowed length.

    Returns:
        str: Sanitized string.
    """
    # Truncate to max length
    sanitized = input_str[:max_length]

    # Remove null bytes
    sanitized = sanitized.replace("\x00", "")

    # Strip leading/trailing whitespace
    sanitized = sanitized.strip()

    return sanitized


def generate_csrf_token() -> str:
    """Generate a CSRF protection token.

    Returns:
        str: CSRF token.
    """
    return secrets.token_urlsafe(32)


def verify_csrf_token(token: str, session_token: str) -> bool:
    """Verify a CSRF token.

    Args:
        token: The token to verify.
        session_token: The session's stored token.

    Returns:
        bool: True if tokens match.
    """
    return constant_time_compare(token, session_token)
