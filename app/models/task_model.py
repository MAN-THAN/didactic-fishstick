from datetime import datetime
from enum import Enum

from sqlalchemy import (
    Boolean,
    DateTime,
    String,
    text,
    ForeignKey,
    Integer,
    Date,
    Enum as SQLEnum,
    JSON,
)
from sqlalchemy.orm import Mapped, mapped_column

from app.database import Base


class TaskPriority(str, Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    URGENT = "urgent"


class Task(Base):
    __tablename__ = "tasks"

    # Primary Key
    id: Mapped[int] = mapped_column(
        primary_key=True,
        autoincrement=True
    )

    # Basic Task Information
    title: Mapped[str] = mapped_column(
        String(100),
        nullable=False
    )

    description: Mapped[str | None] = mapped_column(
        String(500),
        nullable=True
    )

    # Priority
    priority: Mapped[TaskPriority] = mapped_column(
    SQLEnum(TaskPriority, name="taskpriority"),
    default=TaskPriority.MEDIUM,
    nullable=False
)

    # Deadline
    due_date: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True
    )

    # Category
    category: Mapped[str | None] = mapped_column(
        String(50),
        nullable=True
    )

    # Estimated time required to complete task
    estimated_minutes: Mapped[int | None] = mapped_column(
        Integer,
        nullable=True
    )

    # Completion status
    is_completed: Mapped[bool] = mapped_column(
        Boolean,
        server_default=text("false"),
        nullable=False
    )

    # When task was actually completed
    completed_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True
    )

    # Flexible tags
    tags: Mapped[list[str] | None] = mapped_column(
        JSON,
        nullable=True
    )

    # Timestamps
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=text("CURRENT_TIMESTAMP"),
        nullable=False
    )

    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=text("CURRENT_TIMESTAMP"),
        nullable=False
    )

    # Foreign Key
    user_id: Mapped[int] = mapped_column(
        ForeignKey("users.id"),
        nullable=False
    )