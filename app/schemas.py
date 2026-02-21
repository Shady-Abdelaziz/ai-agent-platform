from datetime import datetime
from typing import Optional

from pydantic import BaseModel, ConfigDict


# -- Agent Schemas --

class AgentCreate(BaseModel):
    name: str
    prompt: str


class AgentUpdate(BaseModel):
    name: Optional[str] = None
    prompt: Optional[str] = None


class AgentResponse(BaseModel):
    id: str
    name: str
    prompt: str
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


# -- Session Schemas --

class SessionCreate(BaseModel):
    title: Optional[str] = None


class SessionResponse(BaseModel):
    id: str
    agent_id: str
    title: Optional[str]
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


# -- Message Schemas --

class MessageCreate(BaseModel):
    content: str


class MessageResponse(BaseModel):
    id: str
    session_id: str
    role: str
    content: str
    audio_url: Optional[str] = None
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class MessagePairResponse(BaseModel):
    user_message: MessageResponse
    assistant_message: MessageResponse
