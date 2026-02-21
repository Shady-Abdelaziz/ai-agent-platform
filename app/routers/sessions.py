from datetime import datetime, timezone
from typing import List

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.models import Agent, ChatSession
from app.schemas import SessionCreate, SessionResponse

router = APIRouter(prefix="/api/agents/{agent_id}/sessions", tags=["Sessions"])


async def _get_agent_or_404(agent_id: str, db: AsyncSession) -> Agent:
    """Fetch an agent by ID or raise 404."""
    result = await db.execute(select(Agent).where(Agent.id == agent_id))
    agent = result.scalar_one_or_none()
    if agent is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Agent with id {agent_id} not found",
        )
    return agent


@router.post("", response_model=SessionResponse, status_code=status.HTTP_201_CREATED)
async def create_session(
    agent_id: str,
    payload: SessionCreate,
    db: AsyncSession = Depends(get_db),
) -> ChatSession:
    """Create a new chat session for an agent."""
    await _get_agent_or_404(agent_id, db)

    title = payload.title
    if not title:
        # Count existing sessions for this agent to determine N
        count_result = await db.execute(
            select(func.count()).select_from(ChatSession).where(
                ChatSession.agent_id == agent_id
            )
        )
        n = count_result.scalar() + 1
        now = datetime.now(timezone.utc)
        time_str = now.strftime("%I:%M:%S %p").lstrip("0")
        title = f"Chat {n} ({time_str})"

    session = ChatSession(agent_id=agent_id, title=title)
    db.add(session)
    await db.commit()
    await db.refresh(session)
    return session


@router.get("", response_model=List[SessionResponse])
async def list_sessions(
    agent_id: str,
    db: AsyncSession = Depends(get_db),
) -> List[ChatSession]:
    """List all sessions for a given agent."""
    await _get_agent_or_404(agent_id, db)

    result = await db.execute(
        select(ChatSession)
        .where(ChatSession.agent_id == agent_id)
        .order_by(ChatSession.created_at.desc())
    )
    sessions = result.scalars().all()
    return list(sessions)


@router.get("/{session_id}", response_model=SessionResponse)
async def get_session(
    agent_id: str,
    session_id: str,
    db: AsyncSession = Depends(get_db),
) -> ChatSession:
    """Retrieve a single session by ID."""
    await _get_agent_or_404(agent_id, db)

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


@router.delete("/{session_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_session(
    agent_id: str,
    session_id: str,
    db: AsyncSession = Depends(get_db),
) -> None:
    """Delete a session by ID."""
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

    await db.delete(session)
    await db.commit()
