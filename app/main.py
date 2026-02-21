from contextlib import asynccontextmanager
from pathlib import Path

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from app.database import init_db
from app.routers import agents, messages, sessions


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Startup and shutdown logic for the application."""
    await init_db()
    Path("audio_files").mkdir(parents=True, exist_ok=True)
    yield


app = FastAPI(
    title="AI Agent Platform",
    description="Backend API for creating AI agents, managing chat sessions, "
    "and handling text and voice messaging powered by OpenAI.",
    version="1.0.0",
    lifespan=lifespan,
)

# -- CORS Middleware --

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# -- Static Files (audio) --

Path("audio_files").mkdir(parents=True, exist_ok=True)
app.mount("/api/audio", StaticFiles(directory="audio_files"), name="audio")

# -- Routers --

app.include_router(agents.router)
app.include_router(sessions.router)
app.include_router(messages.router)


# -- Root Endpoint --

@app.get("/")
async def root():
    """Health-check / welcome endpoint."""
    return {
        "message": "AI Agent Platform API",
        "docs": "/docs",
    }
