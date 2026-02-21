"""Tests for the Messaging and Voice interaction endpoints."""

import io
from unittest.mock import AsyncMock, patch

import pytest
from httpx import AsyncClient


# -- Text Messaging Tests --


@pytest.mark.asyncio
async def test_send_message(client: AsyncClient, created_agent: dict, created_session: dict):
    """POST a text message returns 201 with both user and assistant messages."""
    agent_id = created_agent["id"]
    session_id = created_session["id"]

    with patch(
        "app.services.openai_chat.generate_chat_response",
        new_callable=AsyncMock,
        return_value="Hello! How can I help you?",
    ):
        response = await client.post(
            f"/api/agents/{agent_id}/sessions/{session_id}/messages",
            json={"content": "Hi there"},
        )

    assert response.status_code == 201
    data = response.json()
    assert "user_message" in data
    assert "assistant_message" in data
    assert data["user_message"]["role"] == "user"
    assert data["user_message"]["content"] == "Hi there"
    assert data["assistant_message"]["role"] == "assistant"
    assert data["assistant_message"]["content"] == "Hello! How can I help you?"
    assert data["assistant_message"]["session_id"] == session_id


@pytest.mark.asyncio
async def test_send_message_stores_both_messages(
    client: AsyncClient, created_agent: dict, created_session: dict
):
    """Sending a message stores both the user message and the assistant response."""
    agent_id = created_agent["id"]
    session_id = created_session["id"]

    with patch(
        "app.services.openai_chat.generate_chat_response",
        new_callable=AsyncMock,
        return_value="I am an AI assistant.",
    ):
        await client.post(
            f"/api/agents/{agent_id}/sessions/{session_id}/messages",
            json={"content": "Who are you?"},
        )

    # Fetch all messages — should have 2 (user + assistant)
    response = await client.get(
        f"/api/agents/{agent_id}/sessions/{session_id}/messages"
    )
    assert response.status_code == 200
    messages = response.json()
    assert len(messages) == 2
    assert messages[0]["role"] == "user"
    assert messages[0]["content"] == "Who are you?"
    assert messages[1]["role"] == "assistant"
    assert messages[1]["content"] == "I am an AI assistant."


@pytest.mark.asyncio
async def test_list_messages_empty(
    client: AsyncClient, created_agent: dict, created_session: dict
):
    """GET messages for a session with no messages returns an empty list."""
    agent_id = created_agent["id"]
    session_id = created_session["id"]

    response = await client.get(
        f"/api/agents/{agent_id}/sessions/{session_id}/messages"
    )
    assert response.status_code == 200
    assert response.json() == []


@pytest.mark.asyncio
async def test_send_message_agent_not_found(
    client: AsyncClient, created_session: dict
):
    """POST message to a non-existent agent returns 404."""
    response = await client.post(
        "/api/agents/00000000-0000-0000-0000-000000000000/sessions/00000000-0000-0000-0000-000000000001/messages",
        json={"content": "Hello"},
    )
    assert response.status_code == 404


@pytest.mark.asyncio
async def test_send_message_session_not_found(
    client: AsyncClient, created_agent: dict
):
    """POST message to a non-existent session returns 404."""
    agent_id = created_agent["id"]
    response = await client.post(
        f"/api/agents/{agent_id}/sessions/00000000-0000-0000-0000-000000000000/messages",
        json={"content": "Hello"},
    )
    assert response.status_code == 404


@pytest.mark.asyncio
async def test_list_messages_agent_not_found(client: AsyncClient):
    """GET messages for a non-existent agent returns 404."""
    response = await client.get(
        "/api/agents/00000000-0000-0000-0000-000000000000/sessions/00000000-0000-0000-0000-000000000001/messages"
    )
    assert response.status_code == 404


@pytest.mark.asyncio
async def test_list_messages_session_not_found(
    client: AsyncClient, created_agent: dict
):
    """GET messages for a non-existent session returns 404."""
    agent_id = created_agent["id"]
    response = await client.get(
        f"/api/agents/{agent_id}/sessions/00000000-0000-0000-0000-000000000000/messages"
    )
    assert response.status_code == 404


# -- Voice Interaction Tests --


@pytest.mark.asyncio
async def test_voice_interaction(
    client: AsyncClient, created_agent: dict, created_session: dict
):
    """POST voice file returns 201 with user and assistant messages."""
    agent_id = created_agent["id"]
    session_id = created_session["id"]

    with patch(
        "app.services.openai_stt.transcribe_audio",
        new_callable=AsyncMock,
        return_value="What is the weather today?",
    ), patch(
        "app.services.openai_chat.generate_chat_response",
        new_callable=AsyncMock,
        return_value="I cannot check the weather, but it looks nice!",
    ), patch(
        "app.services.openai_tts.generate_speech",
        new_callable=AsyncMock,
        return_value="fake_audio.mp3",
    ):
        audio_bytes = b"\x00" * 100
        response = await client.post(
            f"/api/agents/{agent_id}/sessions/{session_id}/voice",
            files={"audio": ("recording.webm", io.BytesIO(audio_bytes), "audio/webm")},
        )

    assert response.status_code == 201
    data = response.json()
    assert "user_message" in data
    assert "assistant_message" in data
    assert data["user_message"]["role"] == "user"
    assert data["user_message"]["content"] == "What is the weather today?"
    assert data["assistant_message"]["role"] == "assistant"
    assert data["assistant_message"]["content"] == "I cannot check the weather, but it looks nice!"
    assert data["assistant_message"]["audio_url"].startswith("/api/audio/")
    assert data["assistant_message"]["audio_url"].endswith(".mp3")


@pytest.mark.asyncio
async def test_voice_interaction_stores_messages(
    client: AsyncClient, created_agent: dict, created_session: dict
):
    """Voice interaction stores both user (transcribed) and assistant messages."""
    agent_id = created_agent["id"]
    session_id = created_session["id"]

    with patch(
        "app.services.openai_stt.transcribe_audio",
        new_callable=AsyncMock,
        return_value="Hello voice",
    ), patch(
        "app.services.openai_chat.generate_chat_response",
        new_callable=AsyncMock,
        return_value="Hello from AI",
    ), patch(
        "app.services.openai_tts.generate_speech",
        new_callable=AsyncMock,
        return_value="fake_audio.mp3",
    ):
        await client.post(
            f"/api/agents/{agent_id}/sessions/{session_id}/voice",
            files={"audio": ("recording.webm", io.BytesIO(b"\x00" * 100), "audio/webm")},
        )

    # Check stored messages
    response = await client.get(
        f"/api/agents/{agent_id}/sessions/{session_id}/messages"
    )
    assert response.status_code == 200
    messages = response.json()
    assert len(messages) == 2
    assert messages[0]["role"] == "user"
    assert messages[0]["content"] == "Hello voice"
    assert messages[1]["role"] == "assistant"
    assert messages[1]["content"] == "Hello from AI"
    assert messages[1]["audio_url"] is not None


@pytest.mark.asyncio
async def test_voice_interaction_agent_not_found(client: AsyncClient):
    """POST voice to a non-existent agent returns 404."""
    response = await client.post(
        "/api/agents/00000000-0000-0000-0000-000000000000/sessions/00000000-0000-0000-0000-000000000001/voice",
        files={"audio": ("recording.webm", io.BytesIO(b"\x00" * 100), "audio/webm")},
    )
    assert response.status_code == 404


@pytest.mark.asyncio
async def test_voice_interaction_session_not_found(
    client: AsyncClient, created_agent: dict
):
    """POST voice to a non-existent session returns 404."""
    agent_id = created_agent["id"]
    response = await client.post(
        f"/api/agents/{agent_id}/sessions/00000000-0000-0000-0000-000000000000/voice",
        files={"audio": ("recording.webm", io.BytesIO(b"\x00" * 100), "audio/webm")},
    )
    assert response.status_code == 404
