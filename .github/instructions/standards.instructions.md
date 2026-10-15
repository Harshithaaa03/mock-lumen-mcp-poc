# Standards Instructions

> **POC NOTICE:** These coding standards apply to the `mock-lumen-mcp-poc` project.
> They reflect current conventions in the actual source code, supplemented by recommendations
> for future development. This is NOT an official Lumen standards document.

## Coding Conventions

### Python (Backend & MCP Server)

Source: Observed in `backend/` and `mcp_server/` directories.

1. **Python version:** 3.12+ (required for `str | None` union syntax)
2. **Style:** PEP 8. Type hints on all public functions. `from __future__ import annotations` used.
3. **Imports:** Standard library → third-party → local, with blank lines between groups.
4. **Docstrings:** Module-level and function-level docstrings required for all public interfaces.
5. **Type hints:** `from typing import Optional` used for compatibility; `X | None` syntax preferred in Python 3.10+.
6. **Naming:**
   - Modules: `snake_case`
   - Classes: `PascalCase`
   - Functions/variables: `snake_case`
   - Constants: `UPPER_SNAKE_CASE`
7. **Error handling:** Use `raise` with explicit `HTTPException` in route handlers; let unexpected exceptions propagate to FastAPI's default 500 handler.
8. **Async:** All database operations use `async/await` with `AsyncSession`. Route handlers are `async def`.

### TypeScript / React (Frontend)

Source: Observed in `frontend/src/`.

1. **TypeScript strict mode:** enabled in `tsconfig.json`.
2. **Component style:** Functional components with hooks. No class components.
3. **Naming:**
   - Components: `PascalCase.tsx`
   - Utilities/hooks: `camelCase.ts`
   - CSS class names: kebab-case
4. **State management:** React `useState`/`useCallback`/`useEffect` – no external state library in POC.
5. **API calls:** Centralized in `frontend/src/api/tasks.ts`. Components do not call Axios directly.
6. **Error handling:** All API calls wrapped in try/catch; errors surfaced via toast notifications.
7. **Styling:** Vanilla CSS in `index.css`. No CSS-in-JS or utility frameworks.

---

## API Design Practices

Source: `backend/app/api/v1/tasks.py`

1. **URL structure:** `/api/v1/tasks/` – versioned prefix, plural noun resource name.
2. **HTTP methods:** REST-standard. PATCH for partial updates, not PUT.
3. **Status codes:**
   - 200 OK – successful read or update
   - 201 Created – successful creation
   - 204 No Content – successful deletion
   - 404 Not Found – resource does not exist
   - 422 Unprocessable Entity – validation failure
4. **Response format:** All responses are JSON. Error responses follow FastAPI's default `{"detail": "..."}` format.
5. **OpenAPI docs:** Available at `/docs` (Swagger UI) and `/redoc`. Always maintained automatically by FastAPI.
6. **Pagination:** `skip`/`limit` query parameters. Default `limit=100`, max `limit=500`.
7. **Filters:** Query string parameters, not request body.

---

## Testing Expectations

Source: `backend/tests/`, `mcp_server/tests/`

### Backend (pytest)
- **Framework:** pytest + pytest-asyncio
- **Mode:** `asyncio_mode = "auto"` (set in `pyproject.toml`)
- **Isolation:** In-memory SQLite for tests (override via `app.dependency_overrides`)
- **Coverage target:** All CRUD operations, all status codes, validation failures, edge cases
- **Test naming:** `test_<action>_<condition>` (e.g., `test_create_task_blank_title_rejected`)

### MCP Server (pytest)
- **Framework:** pytest
- **Coverage:** Context file existence, loader module functions, tool output structure
- **Philosophy:** Never test against live network; test file I/O and function contracts directly

### Frontend
- No automated tests in the POC. **[PROPOSED]** Add Vitest + React Testing Library for component tests.

---

## Documentation Standards

1. **README.md** – Must include local startup commands, dependency versions, test commands, and known limitations.
2. **Context files** – Must be labeled with `[IMPLEMENTED]`, `[PROPOSED]`, or `[POC ONLY]` where ambiguity exists.
3. **POC notices** – Every context file and every MCP tool response must include a POC notice.
4. **API documentation** – FastAPI auto-generates OpenAPI docs; `summary=` and `description=` parameters must be populated on all routes.
5. **Docstrings** – All Python modules, classes, and public functions require docstrings.

---

## Error Handling Expectations

### Backend
- All 404 responses include a human-readable `detail` message identifying the missing resource.
- All 422 responses use FastAPI's default Pydantic error format.
- Routes do not catch and swallow unexpected exceptions; they propagate to the global handler.

### MCP Server
- Missing context files → tool returns `{"found": false, "error": "..."}`. Never fabricate content.
- Unknown section keys → tool returns `{"found": false, "error": "...", "available_sections": [...]}`.
- Unexpected exceptions → logged and re-raised; the MCP SDK handles transport-level error reporting.

### Frontend
- API errors → displayed as toast notifications (red, 3.5s timeout).
- Loading states → spinner displayed during async operations.
- Empty states → friendly message when task list is empty.
