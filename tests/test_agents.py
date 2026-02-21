"""Tests for the Agent CRUD endpoints (POST, GET, PUT, DELETE /api/agents)."""

import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_create_agent(client: AsyncClient):
    """POST /api/agents with valid data returns 201 and the created agent."""
    payload = {"name": "My Agent", "prompt": "You are a helpful assistant."}
    response = await client.post("/api/agents", json=payload)

    assert response.status_code == 201
    data = response.json()
    assert data["name"] == "My Agent"
    assert data["prompt"] == "You are a helpful assistant."
    assert "id" in data
    assert isinstance(data["id"], str)
    assert len(data["id"]) == 36  # UUID format
    assert "created_at" in data
    assert "updated_at" in data


@pytest.mark.asyncio
async def test_create_agent_missing_fields(client: AsyncClient):
    """POST /api/agents without required fields returns 422 validation error."""
    response = await client.post("/api/agents", json={})
    assert response.status_code == 422

    response = await client.post("/api/agents", json={"name": "Only Name"})
    assert response.status_code == 422

    response = await client.post("/api/agents", json={"prompt": "Only Prompt"})
    assert response.status_code == 422


@pytest.mark.asyncio
async def test_list_agents(client: AsyncClient):
    """GET /api/agents returns all created agents."""
    await client.post(
        "/api/agents", json={"name": "Agent One", "prompt": "Prompt one"}
    )
    await client.post(
        "/api/agents", json={"name": "Agent Two", "prompt": "Prompt two"}
    )

    response = await client.get("/api/agents")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    assert len(data) == 2


@pytest.mark.asyncio
async def test_get_agent(client: AsyncClient, created_agent: dict):
    """GET /api/agents/{id} returns the correct agent."""
    agent_id = created_agent["id"]
    response = await client.get(f"/api/agents/{agent_id}")

    assert response.status_code == 200
    data = response.json()
    assert data["id"] == agent_id
    assert data["name"] == created_agent["name"]
    assert data["prompt"] == created_agent["prompt"]


@pytest.mark.asyncio
async def test_get_agent_not_found(client: AsyncClient):
    """GET /api/agents/{id} for a non-existent agent returns 404."""
    response = await client.get("/api/agents/00000000-0000-0000-0000-000000000000")
    assert response.status_code == 404


@pytest.mark.asyncio
async def test_update_agent(client: AsyncClient, created_agent: dict):
    """PUT /api/agents/{id} updates the agent and returns the updated data."""
    agent_id = created_agent["id"]
    response = await client.put(
        f"/api/agents/{agent_id}",
        json={"name": "Updated Agent", "prompt": "Updated prompt"},
    )

    assert response.status_code == 200
    data = response.json()
    assert data["name"] == "Updated Agent"
    assert data["prompt"] == "Updated prompt"
    assert data["id"] == agent_id


@pytest.mark.asyncio
async def test_update_agent_partial(client: AsyncClient, created_agent: dict):
    """PUT /api/agents/{id} with partial data only updates provided fields."""
    agent_id = created_agent["id"]
    original_prompt = created_agent["prompt"]

    response = await client.put(
        f"/api/agents/{agent_id}", json={"name": "New Name Only"}
    )

    assert response.status_code == 200
    data = response.json()
    assert data["name"] == "New Name Only"
    assert data["prompt"] == original_prompt


@pytest.mark.asyncio
async def test_update_agent_not_found(client: AsyncClient):
    """PUT /api/agents/{id} for a non-existent agent returns 404."""
    response = await client.put(
        "/api/agents/00000000-0000-0000-0000-000000000000",
        json={"name": "Ghost Agent"},
    )
    assert response.status_code == 404


@pytest.mark.asyncio
async def test_delete_agent(client: AsyncClient, created_agent: dict):
    """DELETE /api/agents/{id} removes the agent and returns 204."""
    agent_id = created_agent["id"]

    response = await client.delete(f"/api/agents/{agent_id}")
    assert response.status_code == 204

    response = await client.get(f"/api/agents/{agent_id}")
    assert response.status_code == 404


@pytest.mark.asyncio
async def test_delete_agent_not_found(client: AsyncClient):
    """DELETE /api/agents/{id} for a non-existent agent returns 404."""
    response = await client.delete("/api/agents/00000000-0000-0000-0000-000000000000")
    assert response.status_code == 404
