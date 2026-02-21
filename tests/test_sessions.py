"""Tests for the Session management endpoints (/api/agents/{agent_id}/sessions)."""

import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_create_session(client: AsyncClient, created_agent: dict):
    """POST /api/agents/{agent_id}/sessions creates a session and returns 201."""
    agent_id = created_agent["id"]
    response = await client.post(f"/api/agents/{agent_id}/sessions", json={})

    assert response.status_code == 201
    data = response.json()
    assert data["agent_id"] == agent_id
    assert "id" in data
    assert isinstance(data["id"], str)
    assert len(data["id"]) == 36
    assert "title" in data
    assert "created_at" in data
    # When no title is supplied, the backend generates "Chat N (h:mm:ss AM/PM)"
    assert data["title"].startswith("Chat ")


@pytest.mark.asyncio
async def test_create_session_with_title(client: AsyncClient, created_agent: dict):
    """POST session with a custom title stores that title."""
    agent_id = created_agent["id"]
    response = await client.post(
        f"/api/agents/{agent_id}/sessions", json={"title": "My Custom Session"}
    )

    assert response.status_code == 201
    data = response.json()
    assert data["title"] == "My Custom Session"
    assert data["agent_id"] == agent_id


@pytest.mark.asyncio
async def test_create_session_agent_not_found(client: AsyncClient):
    """POST session for a non-existent agent returns 404."""
    response = await client.post(
        "/api/agents/00000000-0000-0000-0000-000000000000/sessions", json={}
    )
    assert response.status_code == 404


@pytest.mark.asyncio
async def test_list_sessions(client: AsyncClient, created_agent: dict):
    """GET /api/agents/{agent_id}/sessions lists all sessions for the agent."""
    agent_id = created_agent["id"]

    await client.post(
        f"/api/agents/{agent_id}/sessions", json={"title": "Session A"}
    )
    await client.post(
        f"/api/agents/{agent_id}/sessions", json={"title": "Session B"}
    )

    response = await client.get(f"/api/agents/{agent_id}/sessions")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    assert len(data) == 2


@pytest.mark.asyncio
async def test_list_sessions_agent_not_found(client: AsyncClient):
    """GET sessions for a non-existent agent returns 404."""
    response = await client.get(
        "/api/agents/00000000-0000-0000-0000-000000000000/sessions"
    )
    assert response.status_code == 404


@pytest.mark.asyncio
async def test_get_session(
    client: AsyncClient, created_agent: dict, created_session: dict
):
    """GET /api/agents/{agent_id}/sessions/{session_id} returns the session."""
    agent_id = created_agent["id"]
    session_id = created_session["id"]

    response = await client.get(
        f"/api/agents/{agent_id}/sessions/{session_id}"
    )

    assert response.status_code == 200
    data = response.json()
    assert data["id"] == session_id
    assert data["agent_id"] == agent_id
    assert data["title"] == created_session["title"]


@pytest.mark.asyncio
async def test_get_session_not_found(client: AsyncClient, created_agent: dict):
    """GET a non-existent session returns 404."""
    agent_id = created_agent["id"]
    response = await client.get(
        f"/api/agents/{agent_id}/sessions/00000000-0000-0000-0000-000000000000"
    )
    assert response.status_code == 404


@pytest.mark.asyncio
async def test_delete_session(
    client: AsyncClient, created_agent: dict, created_session: dict
):
    """DELETE /api/agents/{agent_id}/sessions/{session_id} returns 204 and removes it."""
    agent_id = created_agent["id"]
    session_id = created_session["id"]

    response = await client.delete(
        f"/api/agents/{agent_id}/sessions/{session_id}"
    )
    assert response.status_code == 204

    response = await client.get(
        f"/api/agents/{agent_id}/sessions/{session_id}"
    )
    assert response.status_code == 404


@pytest.mark.asyncio
async def test_delete_session_not_found(client: AsyncClient, created_agent: dict):
    """DELETE a non-existent session returns 404."""
    agent_id = created_agent["id"]
    response = await client.delete(
        f"/api/agents/{agent_id}/sessions/00000000-0000-0000-0000-000000000000"
    )
    assert response.status_code == 404
