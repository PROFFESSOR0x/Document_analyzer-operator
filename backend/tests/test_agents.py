"""Agent endpoint tests."""

import pytest
from httpx import AsyncClient

from app.models.agent import Agent
from app.models.user import User


class TestListAgents:
    """Test list agents endpoint."""

    @pytest.mark.asyncio
    async def test_list_agents_empty(
        self,
        client: AsyncClient,
        test_user: User,
    ) -> None:
        """Test listing agents when none exist."""
        login_response = await client.post(
            "/api/v1/auth/login",
            json={
                "email": "test@example.com",
                "password": "TestPassword123",
            },
        )
        access_token = login_response.json()["access_token"]

        response = await client.get(
            "/api/v1/agents",
            headers={"Authorization": f"Bearer {access_token}"},
        )

        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        assert len(data) == 0

    @pytest.mark.asyncio
    async def test_list_agents_with_data(
        self,
        client: AsyncClient,
        test_user: User,
    ) -> None:
        """Test listing agents with existing data."""
        # Login
        login_response = await client.post(
            "/api/v1/auth/login",
            json={
                "email": "test@example.com",
                "password": "TestPassword123",
            },
        )
        access_token = login_response.json()["access_token"]

        # Create an agent
        await client.post(
            "/api/v1/agents",
            headers={"Authorization": f"Bearer {access_token}"},
            json={
                "name": "Test Agent",
                "description": "A test agent",
                "model": "gpt-4",
            },
        )

        # List agents
        response = await client.get(
            "/api/v1/agents",
            headers={"Authorization": f"Bearer {access_token}"},
        )

        assert response.status_code == 200
        data = response.json()
        assert len(data) == 1
        assert data[0]["name"] == "Test Agent"


class TestCreateAgent:
    """Test create agent endpoint."""

    @pytest.mark.asyncio
    async def test_create_agent_success(
        self,
        client: AsyncClient,
        test_user: User,
    ) -> None:
        """Test successful agent creation."""
        login_response = await client.post(
            "/api/v1/auth/login",
            json={
                "email": "test@example.com",
                "password": "TestPassword123",
            },
        )
        access_token = login_response.json()["access_token"]

        response = await client.post(
            "/api/v1/agents",
            headers={"Authorization": f"Bearer {access_token}"},
            json={
                "name": "New Agent",
                "description": "A new test agent",
                "model": "gpt-4",
                "temperature": 0.7,
            },
        )

        assert response.status_code == 201
        data = response.json()
        assert data["name"] == "New Agent"
        assert data["description"] == "A new test agent"
        assert "id" in data
        assert "owner_id" in data

    @pytest.mark.asyncio
    async def test_create_agent_unauthorized(self, client: AsyncClient) -> None:
        """Test agent creation without authentication."""
        response = await client.post(
            "/api/v1/agents",
            json={
                "name": "Unauthorized Agent",
            },
        )

        assert response.status_code == 401

    @pytest.mark.asyncio
    async def test_create_agent_invalid_data(
        self,
        client: AsyncClient,
        test_user: User,
    ) -> None:
        """Test agent creation with invalid data."""
        login_response = await client.post(
            "/api/v1/auth/login",
            json={
                "email": "test@example.com",
                "password": "TestPassword123",
            },
        )
        access_token = login_response.json()["access_token"]

        response = await client.post(
            "/api/v1/agents",
            headers={"Authorization": f"Bearer {access_token}"},
            json={
                "name": "",  # Empty name
            },
        )

        assert response.status_code == 422


class TestGetAgent:
    """Test get agent endpoint."""

    @pytest.mark.asyncio
    async def test_get_agent_success(
        self,
        client: AsyncClient,
        test_user: User,
    ) -> None:
        """Test successful agent retrieval."""
        login_response = await client.post(
            "/api/v1/auth/login",
            json={
                "email": "test@example.com",
                "password": "TestPassword123",
            },
        )
        access_token = login_response.json()["access_token"]

        # Create agent
        create_response = await client.post(
            "/api/v1/agents",
            headers={"Authorization": f"Bearer {access_token}"},
            json={
                "name": "Get Test Agent",
            },
        )
        agent_id = create_response.json()["id"]

        # Get agent
        response = await client.get(
            f"/api/v1/agents/{agent_id}",
            headers={"Authorization": f"Bearer {access_token}"},
        )

        assert response.status_code == 200
        data = response.json()
        assert data["id"] == agent_id
        assert data["name"] == "Get Test Agent"

    @pytest.mark.asyncio
    async def test_get_agent_not_found(
        self,
        client: AsyncClient,
        test_user: User,
    ) -> None:
        """Test getting non-existent agent."""
        login_response = await client.post(
            "/api/v1/auth/login",
            json={
                "email": "test@example.com",
                "password": "TestPassword123",
            },
        )
        access_token = login_response.json()["access_token"]

        response = await client.get(
            "/api/v1/agents/non-existent-id",
            headers={"Authorization": f"Bearer {access_token}"},
        )

        assert response.status_code == 404


class TestUpdateAgent:
    """Test update agent endpoint."""

    @pytest.mark.asyncio
    async def test_update_agent_success(
        self,
        client: AsyncClient,
        test_user: User,
    ) -> None:
        """Test successful agent update."""
        login_response = await client.post(
            "/api/v1/auth/login",
            json={
                "email": "test@example.com",
                "password": "TestPassword123",
            },
        )
        access_token = login_response.json()["access_token"]

        # Create agent
        create_response = await client.post(
            "/api/v1/agents",
            headers={"Authorization": f"Bearer {access_token}"},
            json={
                "name": "Update Test Agent",
            },
        )
        agent_id = create_response.json()["id"]

        # Update agent
        response = await client.patch(
            f"/api/v1/agents/{agent_id}",
            headers={"Authorization": f"Bearer {access_token}"},
            json={
                "name": "Updated Agent Name",
                "temperature": 0.9,
            },
        )

        assert response.status_code == 200
        data = response.json()
        assert data["name"] == "Updated Agent Name"
        assert data["temperature"] == 0.9


class TestDeleteAgent:
    """Test delete agent endpoint."""

    @pytest.mark.asyncio
    async def test_delete_agent_success(
        self,
        client: AsyncClient,
        test_user: User,
    ) -> None:
        """Test successful agent deletion."""
        login_response = await client.post(
            "/api/v1/auth/login",
            json={
                "email": "test@example.com",
                "password": "TestPassword123",
            },
        )
        access_token = login_response.json()["access_token"]

        # Create agent
        create_response = await client.post(
            "/api/v1/agents",
            headers={"Authorization": f"Bearer {access_token}"},
            json={
                "name": "Delete Test Agent",
            },
        )
        agent_id = create_response.json()["id"]

        # Delete agent
        response = await client.delete(
            f"/api/v1/agents/{agent_id}",
            headers={"Authorization": f"Bearer {access_token}"},
        )

        assert response.status_code == 204

        # Verify deletion
        get_response = await client.get(
            f"/api/v1/agents/{agent_id}",
            headers={"Authorization": f"Bearer {access_token}"},
        )
        assert get_response.status_code == 404
