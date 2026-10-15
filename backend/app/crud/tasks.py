"""CRUD operations for Task entity."""
from __future__ import annotations

from datetime import datetime, timezone
from typing import Optional

from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.task import Task, TaskStatus
from app.schemas.task import TaskCreate, TaskUpdate


async def create_task(db: AsyncSession, payload: TaskCreate) -> Task:
    """Insert a new task and return the persisted instance."""
    task = Task(
        title=payload.title,
        description=payload.description,
        assignee=payload.assignee,
        status=payload.status,
    )
    db.add(task)
    await db.flush()
    await db.refresh(task)
    return task


async def get_task(db: AsyncSession, task_id: str) -> Optional[Task]:
    """Fetch a single task by primary key."""
    result = await db.execute(select(Task).where(Task.id == task_id))
    return result.scalar_one_or_none()


async def list_tasks(
    db: AsyncSession,
    status: Optional[TaskStatus] = None,
    assignee: Optional[str] = None,
    skip: int = 0,
    limit: int = 100,
) -> tuple[list[Task], int]:
    """Return a filtered, paginated list of tasks plus the total count."""
    query = select(Task)
    count_query = select(func.count()).select_from(Task)

    if status is not None:
        query = query.where(Task.status == status)
        count_query = count_query.where(Task.status == status)
    if assignee is not None:
        query = query.where(Task.assignee == assignee)
        count_query = count_query.where(Task.assignee == assignee)

    total_result = await db.execute(count_query)
    total = total_result.scalar_one()

    query = query.order_by(Task.created_at.desc()).offset(skip).limit(limit)
    result = await db.execute(query)
    tasks = list(result.scalars().all())
    return tasks, total


async def update_task(
    db: AsyncSession, task_id: str, payload: TaskUpdate
) -> Optional[Task]:
    """Apply partial updates to an existing task."""
    task = await get_task(db, task_id)
    if task is None:
        return None

    update_data = payload.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(task, field, value)

    # Manually refresh updated_at since SQLite onupdate doesn't fire on attribute set
    task.updated_at = datetime.now(timezone.utc)
    await db.flush()
    await db.refresh(task)
    return task


async def delete_task(db: AsyncSession, task_id: str) -> bool:
    """Delete a task by id. Returns True if deleted, False if not found."""
    task = await get_task(db, task_id)
    if task is None:
        return False
    await db.delete(task)
    await db.flush()
    return True
