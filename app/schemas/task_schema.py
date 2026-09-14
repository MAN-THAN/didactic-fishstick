from datetime import datetime

from pydantic import BaseModel, Field

from app.models.task_model import TaskPriority


class TaskCreate(BaseModel):
    title: str = Field(
        ...,
        min_length=1,
        max_length=100
    )

    description: str | None = Field(
        default=None,
        max_length=500
    )

    priority: TaskPriority = TaskPriority.MEDIUM

    due_date: datetime | None = None

    category: str | None = Field(
        default=None,
        max_length=50
    )

    estimated_minutes: int | None = Field(
        default=None,
        gt=0
    )

    tags: list[str] | None = None


class TaskUpdate(BaseModel):
    title: str | None = Field(
        default=None,
        min_length=1,
        max_length=100
    )

    description: str | None = Field(
        default=None,
        max_length=500
    )

    priority: TaskPriority | None = None

    due_date: datetime | None = None

    category: str | None = Field(
        default=None,
        max_length=50
    )

    estimated_minutes: int | None = Field(
        default=None,
        gt=0
    )

    tags: list[str] | None = None


class TaskSchema(BaseModel):
    id: int

    title: str

    description: str | None = None

    priority: TaskPriority

    due_date: datetime | None = None

    category: str | None = None

    estimated_minutes: int | None = None

    is_completed: bool

    completed_at: datetime | None = None

    tags: list[str] | None = None

    created_at: datetime

    updated_at: datetime

    user_id: int

    model_config = {
        "from_attributes": True
    }


class TaskResponse(BaseModel):
    msg: str
    task: TaskSchema


class TaskListResponse(BaseModel):
    msg: str
    task_list: list[TaskSchema]
    page: int
    limit: int
    has_more: bool