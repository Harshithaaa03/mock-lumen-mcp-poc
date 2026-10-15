# Rules Instructions

> **POC NOTICE:** These are the actual business rules of the `mock-lumen-mcp-poc` Todo List
> application as implemented in the source code. Rules labeled **[PROPOSED]** are not
> implemented. This is NOT an official Lumen rules document.

## Task Creation Rules

Source: `backend/app/schemas/task.py`, `backend/app/crud/tasks.py`

1. **[IMPLEMENTED]** `title` is **required** for task creation. Omitting it returns HTTP 422.
2. **[IMPLEMENTED]** `title` must be a non-empty, non-whitespace-only string. Whitespace-only titles
   are rejected (`"   "` → HTTP 422).
3. **[IMPLEMENTED]** `title` is automatically stripped of leading/trailing whitespace before storage.
4. **[IMPLEMENTED]** `title` max length: **255 characters**.
5. **[IMPLEMENTED]** `description` is optional. Max length: **5000 characters**.
6. **[IMPLEMENTED]** `assignee` is optional. Max length: **255 characters**. Free text; no validation
   against a user directory.
7. **[IMPLEMENTED]** `status` on creation defaults to `"todo"` if not specified.
8. **[IMPLEMENTED]** `id` is auto-generated as a UUID4 string. Clients cannot supply their own ID.
9. **[IMPLEMENTED]** `created_at` and `updated_at` are auto-set to the current UTC time on creation.

## Task Update Rules

Source: `backend/app/schemas/task.py`, `backend/app/crud/tasks.py`

1. **[IMPLEMENTED]** Updates are **partial** (HTTP PATCH). Only supplied fields are changed.
2. **[IMPLEMENTED]** If `title` is supplied in an update, it must also be non-blank (same rule as creation).
3. **[IMPLEMENTED]** `updated_at` is explicitly refreshed to the current UTC time on every successful update.
4. **[IMPLEMENTED]** `created_at` is **immutable** and cannot be changed by clients.
5. **[IMPLEMENTED]** Updating a non-existent task returns HTTP 404.

## Status Transition Rules

Source: `backend/app/models/task.py`, `backend/app/api/v1/tasks.py`

Valid status values: `todo`, `in_progress`, `completed`, `cancelled`

### Implemented Transitions

The API does **not enforce a strict state machine**. Any status can be set to any other
status via `PATCH /api/v1/tasks/{id}` with `{"status": "<value>"}`.

Two convenience endpoints enforce specific transitions:

| Endpoint | Effect | Source |
|----------|--------|--------|
| `POST /tasks/{id}/complete` | Sets status to `"completed"` regardless of current status | `tasks.py:complete_task` |
| `POST /tasks/{id}/reopen` | Sets status to `"todo"` regardless of current status | `tasks.py:reopen_task` |

### Proposed Strict State Machine (NOT IMPLEMENTED)

A production version might enforce:
```
todo → in_progress
todo → cancelled
in_progress → completed
in_progress → cancelled
completed → todo  (reopen)
cancelled → todo  (reopen)
```
This restriction is **not enforced in the current POC**.

## Assignee Rules

1. **[IMPLEMENTED]** Assignee is a free-text string with no validation against a user list.
2. **[IMPLEMENTED]** Multiple tasks may share the same assignee value.
3. **[IMPLEMENTED]** Setting `assignee` to `null` or omitting it leaves the task unassigned.
4. **[NOT IMPLEMENTED]** No notification is sent to the assignee on assignment.
5. **[NOT IMPLEMENTED]** No permission check verifies that the assignee exists or has access.

## Deletion Rules

1. **[IMPLEMENTED]** Deleting a task is permanent. There is no soft-delete or recycle bin.
2. **[IMPLEMENTED]** Deleting a non-existent task returns HTTP 404.
3. **[IMPLEMENTED]** Successful deletion returns HTTP 204 No Content with no body.

## Input Validation and Application Invariants

Source: Pydantic schemas in `backend/app/schemas/task.py`

| Field | Rule | HTTP Response on Violation |
|-------|------|---------------------------|
| title | Required, non-blank, max 255 chars | 422 Unprocessable Entity |
| description | Optional, max 5000 chars | 422 Unprocessable Entity |
| assignee | Optional, max 255 chars | 422 Unprocessable Entity |
| status | Must be one of the 4 valid enum values | 422 Unprocessable Entity |
| id | UUID format enforced by UUID generation | N/A (server-generated) |

## Filtering Rules

1. **[IMPLEMENTED]** Filtering by `status` returns only tasks with exactly that status value.
2. **[IMPLEMENTED]** Filtering by `assignee` returns only tasks where `assignee == <value>` (exact match, case-sensitive).
3. **[IMPLEMENTED]** Filters are combinable: `?status=todo&assignee=alice` returns tasks that match both conditions.
4. **[IMPLEMENTED]** With no filters, all tasks are returned (up to the `limit` parameter).
5. **[IMPLEMENTED]** Default pagination: `skip=0`, `limit=100`. Maximum `limit=500`.

## Error Handling Invariants

1. Missing resource (task not found) → **HTTP 404** with `{"detail": "Task '<id>' not found"}`
2. Validation failure → **HTTP 422** with Pydantic error details
3. Internal server error → **HTTP 500** (default FastAPI behavior)
