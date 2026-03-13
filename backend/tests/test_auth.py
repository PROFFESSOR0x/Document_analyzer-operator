"""Authentication endpoint tests."""

import pytest
from httpx import AsyncClient

from app.core.security import create_access_token, create_refresh_token
from app.models.user import User


class TestLogin:
    """Test login endpoint."""

    @pytest.mark.asyncio
    async def test_login_success(self, client: AsyncClient, test_user: User) -> None:
        """Test successful login."""
        response = await client.post(
            "/api/v1/auth/login",
            json={
                "email": "test@example.com",
                "password": "TestPassword123",
            },
        )

        assert response.status_code == 200
        data = response.json()
        assert "access_token" in data
        assert "refresh_token" in data
        assert data["token_type"] == "bearer"
        assert "user" in data
        assert data["user"]["email"] == "test@example.com"

    @pytest.mark.asyncio
    async def test_login_invalid_email(self, client: AsyncClient) -> None:
        """Test login with invalid email."""
        response = await client.post(
            "/api/v1/auth/login",
            json={
                "email": "nonexistent@example.com",
                "password": "TestPassword123",
            },
        )

        assert response.status_code == 401
        data = response.json()
        assert "detail" in data

    @pytest.mark.asyncio
    async def test_login_invalid_password(self, client: AsyncClient, test_user: User) -> None:
        """Test login with invalid password."""
        response = await client.post(
            "/api/v1/auth/login",
            json={
                "email": "test@example.com",
                "password": "WrongPassword",
            },
        )

        assert response.status_code == 401
        data = response.json()
        assert "detail" in data

    @pytest.mark.asyncio
    async def test_login_invalid_email_format(self, client: AsyncClient) -> None:
        """Test login with invalid email format."""
        response = await client.post(
            "/api/v1/auth/login",
            json={
                "email": "invalid-email",
                "password": "TestPassword123",
            },
        )

        assert response.status_code == 422


class TestRegister:
    """Test registration endpoint."""

    @pytest.mark.asyncio
    async def test_register_success(self, client: AsyncClient) -> None:
        """Test successful registration."""
        response = await client.post(
            "/api/v1/auth/register",
            json={
                "email": "newuser@example.com",
                "username": "newuser",
                "password": "NewPassword123",
                "full_name": "New User",
            },
        )

        assert response.status_code == 201
        data = response.json()
        assert data["email"] == "newuser@example.com"
        assert data["username"] == "newuser"
        assert "id" in data

    @pytest.mark.asyncio
    async def test_register_duplicate_email(self, client: AsyncClient, test_user: User) -> None:
        """Test registration with duplicate email."""
        response = await client.post(
            "/api/v1/auth/register",
            json={
                "email": "test@example.com",
                "username": "differentuser",
                "password": "NewPassword123",
            },
        )

        assert response.status_code == 400
        data = response.json()
        assert "Email already registered" in data["detail"]

    @pytest.mark.asyncio
    async def test_register_duplicate_username(self, client: AsyncClient, test_user: User) -> None:
        """Test registration with duplicate username."""
        response = await client.post(
            "/api/v1/auth/register",
            json={
                "email": "different@example.com",
                "username": "testuser",
                "password": "NewPassword123",
            },
        )

        assert response.status_code == 400
        data = response.json()
        assert "Username already taken" in data["detail"]

    @pytest.mark.asyncio
    async def test_register_weak_password(self, client: AsyncClient) -> None:
        """Test registration with weak password."""
        response = await client.post(
            "/api/v1/auth/register",
            json={
                "email": "weak@example.com",
                "username": "weakuser",
                "password": "weak",
            },
        )

        assert response.status_code == 422


class TestGetCurrentUser:
    """Test get current user endpoint."""

    @pytest.mark.asyncio
    async def test_get_current_user_success(
        self,
        client: AsyncClient,
        test_user: User,
    ) -> None:
        """Test getting current user info."""
        # First login to get token
        login_response = await client.post(
            "/api/v1/auth/login",
            json={
                "email": "test@example.com",
                "password": "TestPassword123",
            },
        )
        access_token = login_response.json()["access_token"]

        # Get current user
        response = await client.get(
            "/api/v1/auth/me",
            headers={"Authorization": f"Bearer {access_token}"},
        )

        assert response.status_code == 200
        data = response.json()
        assert data["email"] == "test@example.com"
        assert data["username"] == "testuser"

    @pytest.mark.asyncio
    async def test_get_current_user_unauthorized(self, client: AsyncClient) -> None:
        """Test getting current user without authentication."""
        response = await client.get("/api/v1/auth/me")

        assert response.status_code == 401


class TestTokenRefresh:
    """Test token refresh endpoint."""

    @pytest.mark.asyncio
    async def test_refresh_token_success(self, client: AsyncClient, test_user: User) -> None:
        """Test successful token refresh."""
        # Login to get refresh token
        login_response = await client.post(
            "/api/v1/auth/login",
            json={
                "email": "test@example.com",
                "password": "TestPassword123",
            },
        )
        refresh_token = login_response.json()["refresh_token"]

        # Refresh token
        response = await client.post(
            "/api/v1/auth/refresh",
            json={"refresh_token": refresh_token},
        )

        assert response.status_code == 200
        data = response.json()
        assert "access_token" in data
        assert "refresh_token" in data

    @pytest.mark.asyncio
    async def test_refresh_token_invalid(self, client: AsyncClient) -> None:
        """Test refresh with invalid token."""
        response = await client.post(
            "/api/v1/auth/refresh",
            json={"refresh_token": "invalid-token"},
        )

        assert response.status_code == 401
