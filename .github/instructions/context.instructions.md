# Context Instructions

> **POC NOTICE:** This context package is a proposed format for the `mock-lumen-mcp-poc` project.
> It is NOT an official Lumen schema. The Lumen team has not verified this format.

## Application Purpose

The `mock-lumen-mcp-poc` project is a proof-of-concept demonstrating how a Microsoft Copilot Studio Business Stakeholder Agent can retrieve application context through a Model Context Protocol (MCP) server.

The primary application is a **Todo List web application** with the following characteristics:
- Enables users to manage tasks with full CRUD operations
- Supports task assignment to named users (demonstration feature — no authentication implemented)
- Provides status tracking (todo, in_progress, completed, cancelled)
- Designed for local POC use; not hardened for production deployment

## Repository Structure

```
mock-lumen-mcp-poc/
├── .github/
│   └── instructions/          # This context package (8 .md files)
├── frontend/                  # React + Vite + TypeScript UI
│   ├── src/
│   │   ├── App.tsx            # Root component
│   │   ├── main.tsx           # Entry point
│   │   ├── index.css          # Design system
│   │   ├── api/tasks.ts       # Axios API client
│   │   ├── types/task.ts      # TypeScript types
│   │   └── components/        # UI components
│   ├── package.json
│   ├── vite.config.ts
│   └── index.html
├── backend/                   # Python FastAPI + SQLite
│   ├── app/
│   │   ├── main.py            # FastAPI application
│   │   ├── core/              # Config, database
│   │   ├── models/            # SQLAlchemy ORM models
│   │   ├── schemas/           # Pydantic request/response schemas
│   │   ├── crud/              # Database operations
│   │   └── api/v1/            # REST API routes
│   ├── tests/                 # pytest test suite
│   ├── requirements.txt
│   └── pyproject.toml
├── mcp_server/                # Mock Lumen MCP server
│   ├── server.py              # MCPServer with 4 tools
│   ├── context_loader.py      # Reads .github/instructions files
│   ├── requirements.txt
│   └── tests/
├── scripts/
│   └── generate_context_metadata.py  # Context freshness metadata generator
├── deployment/                # Deployment configuration
├── .gitignore
├── .env.example
└── README.md
```

## Domain Context

**Domain:** Personal and team task management
**Primary entity:** Task
**Supporting concept:** Assignee (a string username; no identity service in POC)
**Status lifecycle:** todo → in_progress → completed (or cancelled at any point)

## Existing Features (Verified in Source Code)

All features listed here are implemented in the actual source code:

1. **Create task** – POST /api/v1/tasks/ with title (required), description, assignee, status
2. **View all tasks** – GET /api/v1/tasks/ with optional ?status= and ?assignee= query filters
3. **View single task** – GET /api/v1/tasks/{id}
4. **Update task** – PATCH /api/v1/tasks/{id} (partial updates supported)
5. **Mark complete** – POST /api/v1/tasks/{id}/complete (sets status=completed)
6. **Reopen task** – POST /api/v1/tasks/{id}/reopen (sets status=todo)
7. **Delete task** – DELETE /api/v1/tasks/{id} (returns 204 No Content)
8. **Filter by status** – ?status= query parameter
9. **Filter by assignee** – ?assignee= query parameter
10. **Input validation** – Title required, max lengths enforced, blank titles rejected
11. **Error handling** – 404 for missing tasks, 422 for validation failures

## Important Implementation Details

- **Authentication:** NOT implemented. Assignee is a free-text string. No JWT, OAuth, or session management.
- **Authorization:** NOT implemented. Any client can read or modify any task.
- **Database:** SQLite file (`backend/todo.db`). Not suitable for multi-process or production use.
- **MCP SDK:** MCP 2.x (MCPServer class; FastMCP was renamed in v2)
- **Transport:** Streamable HTTP at `POST /mcp` (MCP 2.x default)
- **CORS:** Configured for localhost:5173 and localhost:3000 in development
- **Pagination:** Supported via ?skip= and ?limit= (max 500) query parameters
