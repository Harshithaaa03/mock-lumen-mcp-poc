# mock-lumen-mcp-poc

> ⚠️ **POC NOTICE:** This is a proof-of-concept demonstration project.
> The MCP server is NOT the official Lumen service. The context format is a proposed POC schema,
> not a verified Lumen schema.

## Overview

This project demonstrates how a **Microsoft Copilot Studio Business Stakeholder Agent** can
retrieve application context through a **Model Context Protocol (MCP) server**.

It contains three components:

| Component | Technology | Directory |
|-----------|-----------|-----------|
| **Todo List Application** | React + Vite + TypeScript (frontend) / Python + FastAPI + SQLite (backend) | `frontend/`, `backend/` |
| **Repository Context Files** | 8 structured Markdown files | `.github/instructions/` |
| **Mock Lumen MCP Server** | Python + MCP SDK 2.x | `mcp_server/` |

---

## Quick Start

### Prerequisites

- Python 3.12+
- Node.js 18+ and npm
- Git

### 1. Clone the repository

```bash
git clone https://github.com/Harshitha-307482/mock-lumen-mcp-poc.git
cd mock-lumen-mcp-poc
```

### 2. Start the backend API

```bash
cd backend
pip install -r requirements.txt
python -m uvicorn app.main:app --reload --port 8000
```

The API is available at `http://localhost:8000`.
OpenAPI docs at `http://localhost:8000/docs`.

### 3. Start the frontend

```bash
cd frontend
npm install
npm run dev
```

The UI is available at `http://localhost:5173`.

### 4. Start the MCP server

```bash
cd mcp_server
pip install -r requirements.txt
python server.py --transport streamable-http --port 8001
```

MCP endpoint: `http://localhost:8001/mcp` (POST, Streamable HTTP)

---

## Running Tests

### Backend API Tests (20 tests)

```bash
cd backend
python -m pytest tests/ -v
```

### MCP Server Tests (18 tests)

```bash
cd mcp_server
python -m pytest tests/ -v
```

### Generate Context Metadata

```bash
python scripts/generate_context_metadata.py
```

---

## Project Structure

```
mock-lumen-mcp-poc/
├── .github/instructions/           # 8 context files consumed by MCP server
│   ├── architecture.instructions.md
│   ├── context.instructions.md
│   ├── instruction.instructions.md
│   ├── ontology.instructions.md
│   ├── policies.instructions.md
│   ├── README.instructions.md
│   ├── rules.instructions.md
│   ├── standards.instructions.md
│   └── .context_metadata.json      # Auto-generated freshness metadata
├── frontend/                       # React + Vite + TypeScript
│   ├── src/
│   │   ├── App.tsx                 # Root component
│   │   ├── api/tasks.ts            # Axios API client
│   │   ├── types/task.ts           # TypeScript types
│   │   └── components/             # UI components
│   └── package.json
├── backend/                        # Python FastAPI + SQLite
│   ├── app/
│   │   ├── main.py                 # FastAPI application
│   │   ├── core/                   # Config, database
│   │   ├── models/                 # SQLAlchemy ORM
│   │   ├── schemas/                # Pydantic schemas
│   │   ├── crud/                   # CRUD operations
│   │   └── api/v1/                 # REST routes
│   └── tests/                      # pytest test suite (20 tests)
├── mcp_server/                     # Mock Lumen MCP server
│   ├── server.py                   # MCPServer with 4 tools
│   ├── context_loader.py           # File I/O for context files
│   └── tests/                      # pytest test suite (18 tests)
├── scripts/
│   └── generate_context_metadata.py
├── deployment/
│   ├── Dockerfile                  # Container deployment
│   └── render.yaml                 # Render.com blueprint
├── .gitignore
├── .env.example
└── README.md
```

---

## MCP Server Tools

| Tool | Purpose |
|------|---------|
| `get_application_context` | Architecture, repo structure, API design, implementation details |
| `get_business_context` | Domain entities, business rules, workflows |
| `get_compliance_context` | Policies, standards, sample constraints (POC only) |
| `get_context_freshness` | Context file timestamps, git commit, generation metadata |

### MCP Transport

- **Protocol:** Model Context Protocol (MCP) 2.x
- **Transport:** Streamable HTTP
- **Endpoint:** `POST /mcp`
- **SDK:** `mcp` 2.x (Python), MCPServer class

---

## Backend API Endpoints

| Method | Path | Description |
|--------|------|-------------|
| POST | /api/v1/tasks/ | Create a task |
| GET | /api/v1/tasks/ | List tasks (filters: ?status=, ?assignee=) |
| GET | /api/v1/tasks/{id} | Get task by ID |
| PATCH | /api/v1/tasks/{id} | Update task (partial) |
| POST | /api/v1/tasks/{id}/complete | Mark task completed |
| POST | /api/v1/tasks/{id}/reopen | Reopen a task |
| DELETE | /api/v1/tasks/{id} | Delete a task |
| GET | /health | Health check |
| GET | /docs | Swagger UI |

---

## Deployment

### Option A: Render.com (Recommended for free-tier POC)

1. Push to GitHub
2. Create a new **Web Service** on [render.com](https://render.com)
3. Connect your GitHub repo
4. Set **Root Directory** to the repo root
5. Set **Build Command:** `pip install -r mcp_server/requirements.txt`
6. Set **Start Command:** `cd mcp_server && python server.py --transport streamable-http --host 0.0.0.0 --port $PORT`
7. Set **Python Version** environment variable: `3.12.3`

### Option B: Docker

```bash
docker build -f deployment/Dockerfile -t mock-lumen-mcp .
docker run -p 8001:8001 mock-lumen-mcp
```

### Option C: Railway, Azure, etc.

The server is a standard Python HTTP application. Any platform supporting Python 3.12+ and
persistent HTTPS endpoints can host it.

---

## Connecting to Microsoft Copilot Studio

> Reference: https://learn.microsoft.com/en-us/microsoft-copilot-studio/mcp-add-existing-server-to-agent

### Steps

1. **Open Copilot Studio** → Select your agent → Go to **Actions** tab
2. **Add an action** → Select **MCP Server (Preview)**
3. **Enter the MCP endpoint URL:** `https://<your-deployed-host>/mcp`
4. **Authentication:** Select the method matching your deployment:
   - For anonymous POC testing: select **None** (if approved for the test environment)
   - For production: implement and select **API Key** or **OAuth 2.0**
5. **Authorize the connection** when prompted
6. **Tool discovery:** Copilot Studio will automatically discover the 4 tools
7. **Test:** Send a message like *"What is the architecture of the Todo app?"*
8. **Inspect traces:** Use Copilot Studio's **Activity** tab to view MCP tool invocations

### Troubleshooting

| Issue | Solution |
|-------|----------|
| Connection timeout | Verify the endpoint is reachable from the internet (not localhost) |
| No tools discovered | Verify MCP transport is Streamable HTTP and endpoint path is `/mcp` |
| Authentication failure | Check the auth method matches what the endpoint expects |
| Tools return empty content | Verify `.github/instructions/` files are deployed with the server |

---

## Known Limitations

- **No authentication** on the Todo List API or MCP server (POC only)
- **SQLite** database – not suitable for production or multi-process deployments
- **Assignee** is free text – no identity service integration
- **No strict state machine** for task status transitions
- **No frontend tests** (proposed for future development)
- **Context files are hand-authored** – not auto-generated from source code analysis
- This is NOT the official Lumen MCP service

---

## Test Results

### Backend API: ✅ 20/20 passed

```
tests/test_tasks_api.py::test_health_check PASSED
tests/test_tasks_api.py::test_create_task_minimal PASSED
tests/test_tasks_api.py::test_create_task_full PASSED
tests/test_tasks_api.py::test_create_task_blank_title_rejected PASSED
tests/test_tasks_api.py::test_create_task_empty_title_rejected PASSED
tests/test_tasks_api.py::test_create_task_missing_title_rejected PASSED
tests/test_tasks_api.py::test_list_tasks_empty PASSED
tests/test_tasks_api.py::test_list_tasks_returns_created PASSED
tests/test_tasks_api.py::test_get_task_by_id PASSED
tests/test_tasks_api.py::test_get_task_not_found PASSED
tests/test_tasks_api.py::test_filter_by_status PASSED
tests/test_tasks_api.py::test_filter_by_assignee PASSED
tests/test_tasks_api.py::test_update_task_title PASSED
tests/test_tasks_api.py::test_update_task_assignee PASSED
tests/test_tasks_api.py::test_update_task_not_found PASSED
tests/test_tasks_api.py::test_complete_task PASSED
tests/test_tasks_api.py::test_reopen_task PASSED
tests/test_tasks_api.py::test_delete_task PASSED
tests/test_tasks_api.py::test_delete_task_not_found PASSED
tests/test_tasks_api.py::test_task_persisted_across_requests PASSED
```

### MCP Server: ✅ 18/18 passed

```
tests/test_mcp_server.py::TestContextFiles::test_instructions_directory_exists PASSED
tests/test_mcp_server.py::TestContextFiles::test_all_eight_context_files_exist PASSED
tests/test_mcp_server.py::TestContextFiles::test_all_context_files_are_non_empty PASSED
tests/test_mcp_server.py::TestContextFiles::test_context_files_mention_todo PASSED
tests/test_mcp_server.py::TestContextLoader::test_load_valid_section PASSED
tests/test_mcp_server.py::TestContextLoader::test_load_invalid_section PASSED
tests/test_mcp_server.py::TestContextLoader::test_load_all_context_files_returns_all_keys PASSED
tests/test_mcp_server.py::TestContextLoader::test_search_context_returns_list PASSED
tests/test_mcp_server.py::TestContextLoader::test_search_context_no_match PASSED
tests/test_mcp_server.py::TestContextLoader::test_freshness_metadata_returns_dict PASSED
tests/test_mcp_server.py::TestContextLoader::test_freshness_fallback_includes_file_times PASSED
tests/test_mcp_server.py::TestMCPTools::test_get_application_context_all PASSED
tests/test_mcp_server.py::TestMCPTools::test_get_application_context_specific_section PASSED
tests/test_mcp_server.py::TestMCPTools::test_get_application_context_missing_section_handled PASSED
tests/test_mcp_server.py::TestMCPTools::test_get_business_context_structure PASSED
tests/test_mcp_server.py::TestMCPTools::test_get_compliance_context_structure PASSED
tests/test_mcp_server.py::TestMCPTools::test_get_context_freshness_structure PASSED
tests/test_mcp_server.py::TestMCPTools::test_no_fabricated_content_for_missing_file PASSED
```

---

## Dependencies

### Backend
| Package | Version |
|---------|---------|
| FastAPI | 0.128.0+ |
| uvicorn | 0.40.0+ |
| SQLAlchemy | 2.0.41+ |
| aiosqlite | 0.20.0+ |
| Pydantic | 2.11.4+ |
| pydantic-settings | 2.9.1+ |
| httpx | 0.28.1+ |
| pytest | 9.1.0+ |
| pytest-asyncio | 1.4.0+ |

### Frontend
| Package | Version |
|---------|---------|
| React | 18.3.x |
| react-dom | 18.3.x |
| axios | 1.7.x |
| TypeScript | 5.5.x |
| Vite | 5.4.x |

### MCP Server
| Package | Version |
|---------|---------|
| mcp | 2.3.0+ |
| httpx | 0.28.0+ |
