from pathlib import Path

import pytest_asyncio
from httpx import ASGITransport, AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from app.database import Base, get_db
from app.main import app

TEST_DATABASE_URL = "sqlite+aiosqlite:///./test.db"


@pytest_asyncio.fixture(scope="function")
async def async_db_session():
    """Create a fresh database and session for each test function."""
    engine = create_async_engine(TEST_DATABASE_URL, echo=False)

    # Create all tables
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    session_maker = async_sessionmaker(
        engine, class_=AsyncSession, expire_on_commit=False
    )

    async with session_maker() as session:
        yield session

    # Drop all tables after each test for isolation
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)

    await engine.dispose()


@pytest_asyncio.fixture(scope="function")
async def client(async_db_session):
    """Provide an httpx AsyncClient wired to the FastAPI app with an overridden DB."""

    async def override_get_db():
        yield async_db_session

    app.dependency_overrides[get_db] = override_get_db

    # Ensure the audio_files directory exists so the app doesn't fail
    Path("audio_files").mkdir(parents=True, exist_ok=True)

    transport = ASGITransport(app=app)
    async with AsyncClient(
        transport=transport, base_url="http://test", follow_redirects=True
    ) as ac:
        yield ac

    app.dependency_overrides.clear()


# -- Helper fixtures --


@pytest_asyncio.fixture
async def created_agent(client: AsyncClient) -> dict:
    """Create and return a single agent for tests that need one."""
    response = await client.post(
        "/api/agents", json={"name": "Test Agent", "prompt": "You are a test agent."}
    )
    assert response.status_code == 201
    return response.json()


@pytest_asyncio.fixture
async def created_session(client: AsyncClient, created_agent: dict) -> dict:
    """Create and return a session under the pre-created agent."""
    agent_id = created_agent["id"]
    response = await client.post(
        f"/api/agents/{agent_id}/sessions", json={"title": "Test Session"}
    )
    assert response.status_code == 201
    return response.json()
