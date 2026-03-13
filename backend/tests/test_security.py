"""Security utility tests."""

import pytest
from freezegun import freeze_time
from datetime import timedelta, timezone

from app.core.security import (
    create_access_token,
    create_refresh_token,
    decode_token,
    get_password_hash,
    is_token_expired,
    verify_password,
)


class TestPasswordHashing:
    """Test password hashing utilities."""

    def test_password_hashing(self) -> None:
        """Test password hashing and verification."""
        password = "TestPassword123"
        hashed = get_password_hash(password)

        assert hashed != password
        assert verify_password(password, hashed)
        assert not verify_password("WrongPassword", hashed)

    def test_different_hashes_for_same_password(self) -> None:
        """Test that same password produces different hashes."""
        password = "TestPassword123"
        hash1 = get_password_hash(password)
        hash2 = get_password_hash(password)

        assert hash1 != hash2
        assert verify_password(password, hash1)
        assert verify_password(password, hash2)


class TestAccessToken:
    """Test access token creation and validation."""

    @freeze_time("2024-01-01 12:00:00")
    def test_create_access_token(self) -> None:
        """Test access token creation."""
        token = create_access_token(subject="user123")

        assert token is not None
        assert isinstance(token, str)

        payload = decode_token(token)
        assert payload is not None
        assert payload["sub"] == "user123"
        assert payload["type"] == "access"

    @freeze_time("2024-01-01 12:00:00")
    def test_access_token_expiration(self) -> None:
        """Test access token expiration."""
        token = create_access_token(
            subject="user123",
            expires_delta=timedelta(minutes=5),
        )

        # Token should be valid now
        assert not is_token_expired(token)

        # Token should be expired after 6 minutes
        with freeze_time("2024-01-01 12:06:00"):
            assert is_token_expired(token)

    def test_decode_invalid_token(self) -> None:
        """Test decoding invalid token."""
        result = decode_token("invalid-token")
        assert result is None

    def test_decode_expired_token(self) -> None:
        """Test decoding expired token."""
        with freeze_time("2024-01-01 12:00:00"):
            token = create_access_token(
                subject="user123",
                expires_delta=timedelta(minutes=-1),  # Already expired
            )

        result = decode_token(token)
        assert result is None


class TestRefreshToken:
    """Test refresh token creation and validation."""

    @freeze_time("2024-01-01 12:00:00")
    def test_create_refresh_token(self) -> None:
        """Test refresh token creation."""
        token = create_refresh_token(subject="user123")

        assert token is not None
        assert isinstance(token, str)

        payload = decode_token(token)
        assert payload is not None
        assert payload["sub"] == "user123"
        assert payload["type"] == "refresh"

    @freeze_time("2024-01-01 12:00:00")
    def test_refresh_token_longer_expiration(self) -> None:
        """Test refresh token has longer expiration than access token."""
        access_token = create_access_token(subject="user123")
        refresh_token = create_refresh_token(subject="user123")

        access_payload = decode_token(access_token)
        refresh_payload = decode_token(refresh_token)

        assert access_payload["exp"] < refresh_payload["exp"]


class TestTokenAdditionalClaims:
    """Test token with additional claims."""

    def test_access_token_with_additional_claims(self) -> None:
        """Test access token with custom claims."""
        token = create_access_token(
            subject="user123",
            additional_claims={"role": "admin", "department": "engineering"},
        )

        payload = decode_token(token)
        assert payload is not None
        assert payload["role"] == "admin"
        assert payload["department"] == "engineering"
