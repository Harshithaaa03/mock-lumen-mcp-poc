# Ontology Instructions

> **POC NOTICE:** This ontology describes the `mock-lumen-mcp-poc` Todo List application.
> It is NOT the official Lumen ontology. Domain terminology is specific to this POC.

## Domain Overview

**Domain name:** Task Management  
**Application:** Todo List POC  
**Source:** `backend/app/models/task.py`, `backend/app/schemas/task.py`

---

## Primary Entity: Task

The `Task` is the single domain entity in this application.

### Fields

| Field | Type | Source | Description |
|-------|------|--------|-------------|
| `id` | `str` (UUID4) | Auto-generated | Primary key; UUID4 string (e.g., `"3fa85f64-5717-4562-b3fc-2c963f66afa6"`) |
| `title` | `str` | User-supplied | Human-readable task name. Required. Max 255 chars. Must not be blank. |
| `description` | `str \| None` | User-supplied | Optional free-text detail. Max 5000 chars. Nullable. |
| `status` | `TaskStatus` (enum) | System-managed | Current lifecycle state. Default: `"todo"`. |
| `assignee` | `str \| None` | User-supplied | Name of the assigned person. Free text. No identity service in POC. Nullable. |
| `created_at` | `datetime` (UTC) | Auto-generated | ISO 8601 UTC timestamp set at insert time. Immutable. |
| `updated_at` | `datetime` (UTC) | Auto-maintained | ISO 8601 UTC timestamp. Updated on every `update_task` call. |

### Primary Key

`id` is the stable identifier for a Task across all API operations.

---

## TaskStatus Enum

Defined in `backend/app/models/task.py` as `class TaskStatus(str, enum.Enum)`.

| Value | Meaning |
|-------|---------|
| `"todo"` | Task created but not yet started |
| `"in_progress"` | Task is actively being worked on |
| `"completed"` | Task has been finished |
| `"cancelled"` | Task was abandoned or will not be completed |

---

## Relationships

### Task ↔ Assignee

- An assignee is referenced by a free-text string in the `Task.assignee` field.
- There is **no separate User entity** in this POC.
- No referential integrity is enforced for assignee values.
- Multiple tasks may share the same assignee value.
- A task with `assignee = null` is considered **unassigned**.

### Task ↔ Status

- Each task has exactly one status at any time.
- Status transitions are performed via:
  - `PATCH /api/v1/tasks/{id}` (set any valid status)
  - `POST /api/v1/tasks/{id}/complete` (shortcut for → `completed`)
  - `POST /api/v1/tasks/{id}/reopen` (shortcut for → `todo`)
- See `rules.instructions.md` for valid transition rules.

---

## Domain Terminology Glossary

| Term | Definition |
|------|-----------|
| **Task** | A unit of work tracked by the application |
| **Title** | Short human-readable name for a task (required) |
| **Description** | Optional long-form details about a task |
| **Status** | The current lifecycle state of a task |
| **Assignee** | The named person responsible for a task (POC: free text, no authentication) |
| **Complete** | The act of setting a task's status to `"completed"` |
| **Reopen** | The act of setting a task's status back to `"todo"` |
| **Filter** | Narrowing the task list by status and/or assignee |
| **Pagination** | Controlling result set size via `skip` and `limit` parameters |

---

## What This Ontology Does NOT Include

- User accounts, authentication, or identity
- Task priorities or due dates (not implemented in this POC)
- Tags, labels, or categories
- Comments or activity history
- Subtasks or dependencies
- Teams or groups
