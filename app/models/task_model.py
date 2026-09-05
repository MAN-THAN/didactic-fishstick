from datetime import datetime
from sqlalchemy import Boolean, DateTime, String, text, ForeignKey, Integer
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.database import Base


class Task(Base):
    __tablename__ = "tasks"

    id: Mapped[int] = mapped_column(
        primary_key=True,
        autoincrement=True
    )

    title: Mapped[str] = mapped_column(
        String(100),
        nullable=False
    )

    description: Mapped[str | None] = mapped_column(
        String(500),
        nullable=True
    )

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

    is_completed: Mapped[bool] = mapped_column(
        Boolean,
        server_default=text("false"),
        nullable=False
    )

    priority: Mapped[int] = mapped_column(Integer, nullable=True) 

       # Foreign Key
    user_id: Mapped[int] = mapped_column(
        ForeignKey("users.id"),
        nullable=False
    )

    # Relationship
    # user: Mapped["User"] = relationship(
    #     back_populates="tasks"
    # )