"""Pydantic schemas for request/response validation."""
from __future__ import annotations

from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field, field_validator

from app.models.task import TaskStatus


# ---------------------------------------------------------------------------
# Request schemas
# ---------------------------------------------------------------------------

class TaskCreate(BaseModel):
    title: str = Field(..., min_length=1, max_length=255, description="Task title")
    description: Optional[str] = Field(None, max_length=5000, description="Optional description")
    assignee: Optional[str] = Field(None, max_length=255, description="Assigned user name (demo feature)")
    status: TaskStatus = Field(default=TaskStatus.TODO, description="Initial task status")

    @field_validator("title")
    @classmethod
    def title_must_not_be_blank(cls, v: str) -> str:
        if not v.strip():
            raise ValueError("Title must not be blank or whitespace only")
        return v.strip()


class TaskUpdate(BaseModel):
    title: Optional[str] = Field(None, min_length=1, max_length=255)
    description: Optional[str] = Field(None, max_length=5000)
    assignee: Optional[str] = Field(None, max_length=255)
    status: Optional[TaskStatus] = None

    @field_validator("title")
    @classmethod
    def title_must_not_be_blank(cls, v: Optional[str]) -> Optional[str]:
        if v is not None and not v.strip():
            raise ValueError("Title must not be blank or whitespace only")
        return v.strip() if v else v


# ---------------------------------------------------------------------------
# Response schemas
# ---------------------------------------------------------------------------

class TaskResponse(BaseModel):
    id: str
    title: str
    description: Optional[str]
    status: TaskStatus
    assignee: Optional[str]
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class TaskListResponse(BaseModel):
    items: list[TaskResponse]
    total: int


class ErrorResponse(BaseModel):
    detail: str
