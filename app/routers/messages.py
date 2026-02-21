import os
import tempfile
import uuid
from pathlib import Path
from typing import List

from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.models import Agent, ChatSession, Message
from app.schemas import MessageCreate, MessagePairResponse, MessageResponse
from app.services import openai_chat, openai_stt, openai_tts

router = APIRouter(prefix="/api", tags=["Messages"])

AUDIO_DIR = Path("audio_files")


async def _get_agent_or_404(agent_id: str, db: AsyncSession) -> Agent:
    """Fetch an agent or raise 404."""
    result = await db.execute(select(Agent).where(Agent.id == agent_id))
    agent = result.scalar_one_or_none()
    if agent is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Agent with id {agent_id} not found",
        )
    return agent


async def _get_session_or_404(
    session_id: str, agent_id: str, db: AsyncSession
) -> ChatSession:
    """Fetch a session belonging to an agent, or raise 404."""
    result = await db.execute(
        select(ChatSession).where(
            ChatSession.id == session_id,
            ChatSession.agent_id == agent_id,
        )
    )
    session = result.scalar_one_or_none()
    if session is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Session with id {session_id} not found for agent {agent_id}",
        )
    return session


async def _build_conversation_history(
    session_id: str, db: AsyncSession
) -> List[dict]:
    """Build the list of message dicts for the OpenAI chat API."""
    result = await db.execute(
        select(Message)
        .where(Message.session_id == session_id)
        .order_by(Message.created_at.asc())
    )
    messages = result.scalars().all()
    return [{"role": msg.role, "content": msg.content} for msg in messages]


# -- Text Messaging --

@router.post(
    "/agents/{agent_id}/sessions/{session_id}/messages",
    response_model=MessagePairResponse,
    status_code=status.HTTP_201_CREATED,
)
async def send_message(
    agent_id: str,
    session_id: str,
    payload: MessageCreate,
    db: AsyncSession = Depends(get_db),
):
    """Send a text message and receive an AI response."""
    agent = await _get_agent_or_404(agent_id, db)
    await _get_session_or_404(session_id, agent_id, db)

    # 1. Save the user message
    user_message = Message(
        session_id=session_id,
        role="user",
        content=payload.content,
    )
    db.add(user_message)
    await db.commit()
    await db.refresh(user_message)

    # 2. Build conversation history
    conversation = await _build_conversation_history(session_id, db)
    full_messages = [{"role": "system", "content": agent.prompt}] + conversation

    # 3. Get AI response
    assistant_text = await openai_chat.generate_chat_response(full_messages)

    # 4. Save assistant message
    assistant_message = Message(
        session_id=session_id,
        role="assistant",
        content=assistant_text,
    )
    db.add(assistant_message)
    await db.commit()
    await db.refresh(assistant_message)

    return MessagePairResponse(
        user_message=MessageResponse.model_validate(user_message),
        assistant_message=MessageResponse.model_validate(assistant_message),
    )


@router.get(
    "/agents/{agent_id}/sessions/{session_id}/messages",
    response_model=List[MessageResponse],
)
async def list_messages(
    agent_id: str,
    session_id: str,
    db: AsyncSession = Depends(get_db),
) -> List[Message]:
    """List all messages in a session, ordered by created_at ascending."""
    await _get_agent_or_404(agent_id, db)
    await _get_session_or_404(session_id, agent_id, db)

    result = await db.execute(
        select(Message)
        .where(Message.session_id == session_id)
        .order_by(Message.created_at.asc())
    )
    messages = result.scalars().all()
    return list(messages)


# -- Voice Messaging --

@router.post(
    "/agents/{agent_id}/sessions/{session_id}/voice",
    response_model=MessagePairResponse,
    status_code=status.HTTP_201_CREATED,
)
async def voice_interaction(
    agent_id: str,
    session_id: str,
    audio: UploadFile = File(...),
    db: AsyncSession = Depends(get_db),
):
    """Handle a voice interaction: STT -> Chat -> TTS."""
    agent = await _get_agent_or_404(agent_id, db)
    await _get_session_or_404(session_id, agent_id, db)

    # 1. Save uploaded audio to a temporary file
    suffix = os.path.splitext(audio.filename or "audio.webm")[1] or ".webm"
    tmp = tempfile.NamedTemporaryFile(delete=False, suffix=suffix)
    try:
        audio_bytes = await audio.read()
        tmp.write(audio_bytes)
        tmp.flush()
        tmp.close()

        # 2. Transcribe with Whisper
        transcription_text = await openai_stt.transcribe_audio(tmp.name)
    finally:
        if os.path.exists(tmp.name):
            os.unlink(tmp.name)

    # 3. Save user message with transcribed text
    user_message = Message(
        session_id=session_id,
        role="user",
        content=transcription_text,
    )
    db.add(user_message)
    await db.commit()
    await db.refresh(user_message)

    # 4. Build conversation history and get AI response
    conversation = await _build_conversation_history(session_id, db)
    full_messages = [{"role": "system", "content": agent.prompt}] + conversation
    assistant_text = await openai_chat.generate_chat_response(full_messages)

    # 5. Save assistant message
    assistant_message = Message(
        session_id=session_id,
        role="assistant",
        content=assistant_text,
    )
    db.add(assistant_message)
    await db.commit()
    await db.refresh(assistant_message)

    # 6. Convert assistant response to audio via TTS
    audio_filename = f"{uuid.uuid4().hex}.mp3"
    audio_path = AUDIO_DIR / audio_filename
    AUDIO_DIR.mkdir(parents=True, exist_ok=True)

    await openai_tts.generate_speech(assistant_text, str(audio_path))

    audio_url = f"/api/audio/{audio_filename}"

    # 7. Update the assistant message with the audio URL
    assistant_message.audio_url = audio_url
    await db.commit()
    await db.refresh(assistant_message)

    return MessagePairResponse(
        user_message=MessageResponse.model_validate(user_message),
        assistant_message=MessageResponse.model_validate(assistant_message),
    )
