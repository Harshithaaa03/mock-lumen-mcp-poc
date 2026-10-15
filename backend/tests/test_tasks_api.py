"""Integration tests for the Task API endpoints."""
import pytest
from httpx import AsyncClient

pytestmark = pytest.mark.asyncio


# ---------------------------------------------------------------------------
# Health check
# ---------------------------------------------------------------------------

async def test_health_check(client: AsyncClient):
    response = await client.get("/health")
    assert response.status_code == 200
    assert response.json()["status"] == "ok"


# ---------------------------------------------------------------------------
# Create
# ---------------------------------------------------------------------------

async def test_create_task_minimal(client: AsyncClient):
    """Create a task with only a title."""
    response = await client.post("/api/v1/tasks/", json={"title": "Buy milk"})
    assert response.status_code == 201
    data = response.json()
    assert data["title"] == "Buy milk"
    assert data["status"] == "todo"
    assert data["description"] is None
    assert data["assignee"] is None
    assert "id" in data
    assert "created_at" in data
    assert "updated_at" in data


async def test_create_task_full(client: AsyncClient):
    """Create a task with all fields."""
    payload = {
        "title": "Write tests",
        "description": "Cover all edge cases",
        "assignee": "alice",
        "status": "in_progress",
    }
    response = await client.post("/api/v1/tasks/", json=payload)
    assert response.status_code == 201
    data = response.json()
    assert data["title"] == "Write tests"
    assert data["assignee"] == "alice"
    assert data["status"] == "in_progress"


async def test_create_task_blank_title_rejected(client: AsyncClient):
    response = await client.post("/api/v1/tasks/", json={"title": "   "})
    assert response.status_code == 422


async def test_create_task_empty_title_rejected(client: AsyncClient):
    response = await client.post("/api/v1/tasks/", json={"title": ""})
    assert response.status_code == 422


async def test_create_task_missing_title_rejected(client: AsyncClient):
    response = await client.post("/api/v1/tasks/", json={})
    assert response.status_code == 422


# ---------------------------------------------------------------------------
# Read
# ---------------------------------------------------------------------------

async def test_list_tasks_empty(client: AsyncClient):
    response = await client.get("/api/v1/tasks/")
    assert response.status_code == 200
    data = response.json()
    assert data["items"] == []
    assert data["total"] == 0


async def test_list_tasks_returns_created(client: AsyncClient):
    await client.post("/api/v1/tasks/", json={"title": "Task A"})
    await client.post("/api/v1/tasks/", json={"title": "Task B"})
    response = await client.get("/api/v1/tasks/")
    assert response.status_code == 200
    data = response.json()
    assert data["total"] == 2
    assert len(data["items"]) == 2


async def test_get_task_by_id(client: AsyncClient):
    create_response = await client.post("/api/v1/tasks/", json={"title": "Find me"})
    task_id = create_response.json()["id"]
    response = await client.get(f"/api/v1/tasks/{task_id}")
    assert response.status_code == 200
    assert response.json()["title"] == "Find me"


async def test_get_task_not_found(client: AsyncClient):
    response = await client.get("/api/v1/tasks/nonexistent-id")
    assert response.status_code == 404


# ---------------------------------------------------------------------------
# Filter
# ---------------------------------------------------------------------------

async def test_filter_by_status(client: AsyncClient):
    await client.post("/api/v1/tasks/", json={"title": "Todo task", "status": "todo"})
    await client.post("/api/v1/tasks/", json={"title": "Done task", "status": "completed"})
    response = await client.get("/api/v1/tasks/?status=todo")
    assert response.status_code == 200
    data = response.json()
    assert data["total"] == 1
    assert data["items"][0]["title"] == "Todo task"


async def test_filter_by_assignee(client: AsyncClient):
    await client.post("/api/v1/tasks/", json={"title": "Alice task", "assignee": "alice"})
    await client.post("/api/v1/tasks/", json={"title": "Bob task", "assignee": "bob"})
    response = await client.get("/api/v1/tasks/?assignee=alice")
    assert response.status_code == 200
    data = response.json()
    assert data["total"] == 1
    assert data["items"][0]["assignee"] == "alice"


# ---------------------------------------------------------------------------
# Update
# ---------------------------------------------------------------------------

async def test_update_task_title(client: AsyncClient):
    create_response = await client.post("/api/v1/tasks/", json={"title": "Old title"})
    task_id = create_response.json()["id"]
    response = await client.patch(f"/api/v1/tasks/{task_id}", json={"title": "New title"})
    assert response.status_code == 200
    assert response.json()["title"] == "New title"


async def test_update_task_assignee(client: AsyncClient):
    create_response = await client.post("/api/v1/tasks/", json={"title": "Unassigned"})
    task_id = create_response.json()["id"]
    response = await client.patch(f"/api/v1/tasks/{task_id}", json={"assignee": "charlie"})
    assert response.status_code == 200
    assert response.json()["assignee"] == "charlie"


async def test_update_task_not_found(client: AsyncClient):
    response = await client.patch("/api/v1/tasks/nope", json={"title": "X"})
    assert response.status_code == 404


# ---------------------------------------------------------------------------
# Complete / Reopen
# ---------------------------------------------------------------------------

async def test_complete_task(client: AsyncClient):
    create_response = await client.post("/api/v1/tasks/", json={"title": "Finish me"})
    task_id = create_response.json()["id"]
    response = await client.post(f"/api/v1/tasks/{task_id}/complete")
    assert response.status_code == 200
    assert response.json()["status"] == "completed"


async def test_reopen_task(client: AsyncClient):
    create_response = await client.post("/api/v1/tasks/", json={"title": "Reopen me", "status": "completed"})
    task_id = create_response.json()["id"]
    response = await client.post(f"/api/v1/tasks/{task_id}/reopen")
    assert response.status_code == 200
    assert response.json()["status"] == "todo"


# ---------------------------------------------------------------------------
# Delete
# ---------------------------------------------------------------------------

async def test_delete_task(client: AsyncClient):
    create_response = await client.post("/api/v1/tasks/", json={"title": "Delete me"})
    task_id = create_response.json()["id"]
    response = await client.delete(f"/api/v1/tasks/{task_id}")
    assert response.status_code == 204
    # Verify it's gone
    get_response = await client.get(f"/api/v1/tasks/{task_id}")
    assert get_response.status_code == 404


async def test_delete_task_not_found(client: AsyncClient):
    response = await client.delete("/api/v1/tasks/ghost")
    assert response.status_code == 404


# ---------------------------------------------------------------------------
# Persistence check
# ---------------------------------------------------------------------------

async def test_task_persisted_across_requests(client: AsyncClient):
    """Verify the task remains queryable after creation (persistence check)."""
    create_response = await client.post("/api/v1/tasks/", json={"title": "Persistent"})
    task_id = create_response.json()["id"]
    list_response = await client.get("/api/v1/tasks/")
    ids = [t["id"] for t in list_response.json()["items"]]
    assert task_id in ids
