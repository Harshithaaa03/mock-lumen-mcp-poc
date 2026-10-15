# Architecture Instructions

> **POC NOTICE:** This is a proposed context format for the `mock-lumen-mcp-poc` project.
> It is NOT the official Lumen schema or service. The Lumen team has not verified this schema.

## System Overview

The `mock-lumen-mcp-poc` project is a proof-of-concept (POC) Todo List application with an associated Mock Lumen MCP server. It demonstrates how a Microsoft Copilot Studio Business Stakeholder Agent can retrieve application context through an MCP server.

## Components

### 1. Frontend (React + Vite + TypeScript)
- **Location:** `frontend/`
- **Entry point:** `frontend/src/main.tsx`
- **Root component:** `frontend/src/App.tsx`
- **Port:** `5173` (development)
- **Build tool:** Vite 5.x
- **HTTP client:** Axios 1.x

**Component hierarchy:**
```
App.tsx
├── TaskCard.tsx          (task list item with inline actions)
├── TaskDetailPanel.tsx   (selected task edit/view panel)
└── StatusBadge.tsx       (status indicator chip)
```

**API client:** `frontend/src/api/tasks.ts` wraps Axios and communicates via Vite proxy to `http://localhost:8000`.

### 2. Backend (Python + FastAPI + SQLite)
- **Location:** `backend/`
- **Entry point:** `backend/app/main.py` (FastAPI app factory)
- **Port:** `8000` (development, via uvicorn)
- **Database:** SQLite via SQLAlchemy 2.x async (`aiosqlite`)
- **ORM:** SQLAlchemy declarative models
- **Validation:** Pydantic v2 schemas

**Module structure:**
```
backend/app/
├── main.py               (FastAPI application factory, CORS, lifespan)
├── core/
│   ├── config.py         (pydantic-settings configuration)
│   └── database.py       (async engine, session factory, Base, init_db)
├── models/
│   └── task.py           (Task SQLAlchemy ORM model, TaskStatus enum)
├── schemas/
│   └── task.py           (TaskCreate, TaskUpdate, TaskResponse Pydantic schemas)
├── crud/
│   └── tasks.py          (create_task, get_task, list_tasks, update_task, delete_task)
└── api/
    └── v1/
        ├── __init__.py   (api_router, prefix=/api/v1)
        └── tasks.py      (APIRouter, prefix=/tasks)
```

### 3. Mock Lumen MCP Server (Python + MCP SDK 2.x)
- **Location:** `mcp_server/`
- **Entry point:** `mcp_server/server.py`
- **Port:** `8001` (development)
- **SDK:** `mcp` 2.x (MCPServer, renamed from FastMCP)
- **Transport:** Streamable HTTP (`POST /mcp`)

**File structure:**
```
mcp_server/
├── server.py             (MCPServer, 4 MCP tool definitions)
├── context_loader.py     (file I/O for .github/instructions/*.md)
└── tests/
    └── test_mcp_server.py
```

## API Structure

### Backend REST API

Base URL: `http://localhost:8000/api/v1`

| Method | Path | Description |
|--------|------|-------------|
| POST | /tasks/ | Create task |
| GET | /tasks/ | List tasks (with optional ?status= and ?assignee= filters) |
| GET | /tasks/{id} | Get task by ID |
| PATCH | /tasks/{id} | Partially update task |
| POST | /tasks/{id}/complete | Mark task completed |
| POST | /tasks/{id}/reopen | Reopen a task (set status=todo) |
| DELETE | /tasks/{id} | Delete task (204 No Content) |
| GET | /health | Health check |

OpenAPI documentation available at `http://localhost:8000/docs` (Swagger UI).

### MCP Server API

Endpoint: `http://localhost:8001/mcp` (POST, Streamable HTTP transport)

| Tool | Purpose |
|------|---------|
| get_application_context | Architecture, repo structure, implementation details |
| get_business_context | Domain entities, business rules, workflows |
| get_compliance_context | Policies, standards, sample constraints |
| get_context_freshness | Context file generation timestamps and metadata |

## Database Interactions

- **Engine:** `create_async_engine` with `sqlite+aiosqlite:///./todo.db`
- **Sessions:** `async_sessionmaker` yielded per request via FastAPI `Depends(get_db)`
- **Table creation:** `Base.metadata.create_all` called on startup via lifespan context manager
- **Transactions:** Session commits on successful request completion; rollback on exception

## Module Responsibilities and Dependencies

```
frontend/src/api/tasks.ts
  └── depends on: Axios, backend REST API

backend/app/api/v1/tasks.py
  └── depends on: crud.tasks, schemas.task, models.task, FastAPI

backend/app/crud/tasks.py
  └── depends on: models.task, schemas.task, SQLAlchemy AsyncSession

backend/app/models/task.py
  └── depends on: SQLAlchemy ORM, core.database.Base

mcp_server/server.py
  └── depends on: context_loader.py, MCP SDK 2.x (MCPServer)

mcp_server/context_loader.py
  └── depends on: .github/instructions/*.md (file system)
  └── reads: .github/instructions/.context_metadata.json (optional)
```
