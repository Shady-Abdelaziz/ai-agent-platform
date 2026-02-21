# AI Agent Platform

A full-stack AI Agent Platform for creating, managing, and interacting with AI agents via text and voice. Built with FastAPI, async SQLAlchemy, and OpenAI APIs, with a React frontend.

## Quick Start (Docker)

```bash
# 1. Set your OpenAI API key in the .env file
#    Open .env and replace the placeholder with your real key:
#    OPENAI_API_KEY=sk-...

# 2. Start everything
docker-compose up --build

# 3. Open in your browser:
#    - Frontend UI:    http://localhost:3000
#    - Swagger API:    http://localhost:8000/docs
#    - ReDoc API:      http://localhost:8000/redoc
```

That's it. The database is created automatically on first run.

## Tech Stack

- **Language:** Python 3.11
- **Framework:** FastAPI
- **Database:** SQLite with async SQLAlchemy (aiosqlite)
- **AI:** OpenAI API (gpt-5.2 for chat, Whisper for STT, TTS-1 for speech)
- **Testing:** pytest with pytest-asyncio
- **Frontend:** React 18 + Vite (plain CSS, served via nginx in production)
- **Deployment:** Docker / Docker Compose

## Project Structure

```
.
├── .env                      # Environment variables (not committed)
├── .gitignore
├── AI_AGENT_PLATFORM_SPEC.md # Full build specification
├── CLAUDE.md                 # AI agent instructions
├── Dockerfile                # Backend container
├── README.md
├── docker-compose.yml        # Backend + frontend orchestration
├── postman_collection.json   # Postman API collection
├── pytest.ini                # pytest config (asyncio_mode = auto)
├── requirements.txt          # Python dependencies
├── app/
│   ├── __init__.py
│   ├── config.py             # Settings from .env (pydantic-settings)
│   ├── database.py           # Async SQLAlchemy engine & session
│   ├── models.py             # Agent, ChatSession, Message ORM models (UUID PKs)
│   ├── schemas.py            # Pydantic v2 request/response schemas
│   ├── main.py               # FastAPI app, CORS, lifespan, routers
│   ├── routers/
│   │   ├── __init__.py
│   │   ├── agents.py         # Agent CRUD endpoints
│   │   ├── sessions.py       # Session management endpoints
│   │   └── messages.py       # Text messaging & voice interaction
│   └── services/
│       ├── __init__.py
│       ├── openai_chat.py    # Chat completion (gpt-5.2)
│       ├── openai_stt.py     # Speech-to-text (Whisper)
│       └── openai_tts.py     # Text-to-speech (TTS-1)
├── tests/
│   ├── __init__.py
│   ├── conftest.py           # Async test fixtures & helper fixtures
│   ├── test_agents.py        # Agent endpoint tests
│   ├── test_sessions.py      # Session endpoint tests
│   └── test_messages.py      # Text messaging & voice tests (mocked OpenAI)
├── audio_files/              # Generated TTS audio files (runtime)
└── frontend/
    ├── Dockerfile            # Multi-stage build: Vite → nginx
    ├── index.html
    ├── nginx.conf            # Proxies /api/ requests to backend
    ├── package.json
    ├── vite.config.js
    ├── public/
    └── src/
        ├── main.jsx
        ├── App.jsx
        ├── App.css
        ├── api.js            # All backend HTTP calls
        ├── components/
        │   ├── AgentSidebar.jsx
        │   ├── ChatArea.jsx
        │   ├── MessageBubble.jsx
        │   ├── MessageInput.jsx
        │   └── SessionBar.jsx
        └── hooks/
            └── useAudioRecorder.js
```

## Setup & Installation

### Prerequisites

- Python 3.11 or higher
- An OpenAI API key

### 1. Clone the repository

```bash
git clone <repository-url>
cd ai-agent-platform
```

### 2. Create a virtual environment

```bash
python -m venv venv
source venv/bin/activate      # Linux/macOS
venv\Scripts\activate         # Windows
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

### 4. Configure environment variables

Create a `.env` file in the project root:

```env
OPENAI_API_KEY=your-openai-api-key-here
DATABASE_URL=sqlite+aiosqlite:///./app.db
```

### 5. Run the server

```bash
python -m uvicorn app.main:app --reload --port 8000
```

The API will be available at `http://localhost:8000`.

## API Documentation

FastAPI auto-generates interactive API docs:

- **Swagger UI:** http://localhost:8000/docs
- **ReDoc:** http://localhost:8000/redoc

## API Endpoints

### Agents

| Method | Endpoint              | Description          | Status |
|--------|-----------------------|----------------------|--------|
| POST   | `/api/agents`         | Create a new agent   | 201    |
| GET    | `/api/agents`         | List all agents      | 200    |
| GET    | `/api/agents/{id}`    | Get agent by ID      | 200    |
| PUT    | `/api/agents/{id}`    | Update an agent      | 200    |
| DELETE | `/api/agents/{id}`    | Delete an agent      | 204    |

### Sessions

| Method | Endpoint                                       | Description              | Status |
|--------|-------------------------------------------------|--------------------------|--------|
| POST   | `/api/agents/{agent_id}/sessions`              | Create a chat session    | 201    |
| GET    | `/api/agents/{agent_id}/sessions`              | List sessions for agent  | 200    |
| GET    | `/api/agents/{agent_id}/sessions/{id}`         | Get session by ID        | 200    |
| DELETE | `/api/agents/{agent_id}/sessions/{id}`         | Delete a session         | 204    |

### Messages

| Method | Endpoint                                                           | Description                     | Status |
|--------|--------------------------------------------------------------------|---------------------------------|--------|
| POST   | `/api/agents/{agent_id}/sessions/{session_id}/messages`           | Send text message, get AI reply | 201    |
| GET    | `/api/agents/{agent_id}/sessions/{session_id}/messages`           | List messages in session        | 200    |

### Voice

| Method | Endpoint                                                         | Description                                          | Status |
|--------|------------------------------------------------------------------|------------------------------------------------------|--------|
| POST   | `/api/agents/{agent_id}/sessions/{session_id}/voice`            | Upload audio, get transcription + AI audio response  | 201    |
| GET    | `/api/audio/{filename}`                                          | Serve TTS audio file                                 | 200    |

The voice endpoint accepts an audio file upload (`multipart/form-data` with field `audio`), transcribes it via Whisper, generates an AI response, converts it to speech, and returns both user and assistant messages (assistant includes `audio_url`).

## Running Tests

### Prerequisites

Make sure you have installed the project dependencies first:

```bash
pip install -r requirements.txt
```

### Run the full test suite

```bash
python -m pytest tests/ -v
```

### Run specific test files

```bash
python -m pytest tests/test_agents.py -v      # Agent CRUD tests
python -m pytest tests/test_sessions.py -v     # Session management tests
python -m pytest tests/test_messages.py -v     # Text messaging & voice interaction tests
```

### Test coverage

The test suite includes **30 tests** covering:

- **Agent Management (10 tests):** Create, list, get, update (full & partial), delete, and error handling (missing fields, not found)
- **Session Management (8 tests):** Create (auto-title & custom title), list, get, delete, and error handling (agent not found, session not found)
- **Text Messaging (7 tests):** Send message, verify storage of both user & assistant messages, list messages, and error handling (agent/session not found)
- **Voice Interaction (5 tests):** Full voice pipeline (upload audio → STT → chat → TTS), verify message storage with audio URL, and error handling (agent/session not found)

All OpenAI API calls in tests are mocked — no API key is needed to run the test suite. Tests use a separate SQLite database (`test.db`) that is automatically created and cleaned up.

## Docker Deployment

### Backend only

```bash
docker build -t ai-agent-platform .
docker run -p 8000:8000 --env-file .env ai-agent-platform
```

### Full stack (backend + frontend)

```bash
docker-compose up --build
```

- Backend API: http://localhost:8000
- Frontend UI: http://localhost:3000

The frontend is served via nginx, which proxies `/api/` requests to the backend container.

## Frontend

The React frontend is in the `frontend/` directory.

### Development

```bash
cd frontend
npm install
npm run dev
```

The Vite dev server runs at http://localhost:5173 and proxies `/api` requests to the backend at port 8000.

### Production

In Docker, the frontend is built with Vite and served via nginx on port 80 (mapped to 3000 on the host). The nginx config proxies API requests to the backend service.
