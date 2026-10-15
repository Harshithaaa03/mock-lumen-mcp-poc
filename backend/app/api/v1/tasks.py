"""Task API router – v1 endpoints."""
from __future__ import annotations

from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Query, Response, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.crud import tasks as crud
from app.models.task import TaskStatus
from app.schemas.task import (
    TaskCreate,
    TaskListResponse,
    TaskResponse,
    TaskUpdate,
)

router = APIRouter(prefix="/tasks", tags=["tasks"])


# ---------------------------------------------------------------------------
# Create
# ---------------------------------------------------------------------------

@router.post(
    "/",
    response_model=TaskResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create a task",
)
async def create_task(
    payload: TaskCreate,
    db: AsyncSession = Depends(get_db),
) -> TaskResponse:
    task = await crud.create_task(db, payload)
    return TaskResponse.model_validate(task)


# ---------------------------------------------------------------------------
# Read – list
# ---------------------------------------------------------------------------

@router.get(
    "/",
    response_model=TaskListResponse,
    summary="List tasks with optional filters",
)
async def list_tasks(
    status: Optional[TaskStatus] = Query(None, description="Filter by task status"),
    assignee: Optional[str] = Query(None, description="Filter by assignee name"),
    skip: int = Query(0, ge=0, description="Number of records to skip"),
    limit: int = Query(100, ge=1, le=500, description="Maximum records to return"),
    db: AsyncSession = Depends(get_db),
) -> TaskListResponse:
    task_list, total = await crud.list_tasks(db, status=status, assignee=assignee, skip=skip, limit=limit)
    return TaskListResponse(
        items=[TaskResponse.model_validate(t) for t in task_list],
        total=total,
    )


# ---------------------------------------------------------------------------
# Read – single
# ---------------------------------------------------------------------------

@router.get(
    "/{task_id}",
    response_model=TaskResponse,
    summary="Get a task by ID",
)
async def get_task(
    task_id: str,
    db: AsyncSession = Depends(get_db),
) -> TaskResponse:
    task = await crud.get_task(db, task_id)
    if task is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Task {task_id!r} not found")
    return TaskResponse.model_validate(task)


# ---------------------------------------------------------------------------
# Update
# ---------------------------------------------------------------------------

@router.patch(
    "/{task_id}",
    response_model=TaskResponse,
    summary="Partially update a task",
)
async def update_task(
    task_id: str,
    payload: TaskUpdate,
    db: AsyncSession = Depends(get_db),
) -> TaskResponse:
    task = await crud.update_task(db, task_id, payload)
    if task is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Task {task_id!r} not found")
    return TaskResponse.model_validate(task)


# ---------------------------------------------------------------------------
# Complete / Reopen convenience endpoints
# ---------------------------------------------------------------------------

@router.post(
    "/{task_id}/complete",
    response_model=TaskResponse,
    summary="Mark a task as completed",
)
async def complete_task(
    task_id: str,
    db: AsyncSession = Depends(get_db),
) -> TaskResponse:
    payload = TaskUpdate(status=TaskStatus.COMPLETED)
    task = await crud.update_task(db, task_id, payload)
    if task is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Task {task_id!r} not found")
    return TaskResponse.model_validate(task)


@router.post(
    "/{task_id}/reopen",
    response_model=TaskResponse,
    summary="Reopen a completed or cancelled task",
)
async def reopen_task(
    task_id: str,
    db: AsyncSession = Depends(get_db),
) -> TaskResponse:
    payload = TaskUpdate(status=TaskStatus.TODO)
    task = await crud.update_task(db, task_id, payload)
    if task is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Task {task_id!r} not found")
    return TaskResponse.model_validate(task)


# ---------------------------------------------------------------------------
# Delete
# ---------------------------------------------------------------------------

@router.delete(
    "/{task_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    response_class=Response,
    summary="Delete a task",
)
async def delete_task(
    task_id: str,
    db: AsyncSession = Depends(get_db),
) -> Response:
    deleted = await crud.delete_task(db, task_id)
    if not deleted:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Task {task_id!r} not found")
    return Response(status_code=status.HTTP_204_NO_CONTENT)
