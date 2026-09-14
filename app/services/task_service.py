from datetime import datetime, timezone

from fastapi import HTTPException
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.task_model import Task, TaskPriority


def get_tasks(
    search,
    page,
    limit,
    status,
    sort,
    current_user,
    db: Session
):
    stmt = select(Task).where(
        Task.user_id == current_user.id
    )

    # -------------------------
    # SEARCH
    # -------------------------
    if search:
        stmt = stmt.where(
            Task.title.ilike(f"%{search}%")
        )

    # -------------------------
    # STATUS FILTER
    # -------------------------
    if status == "active":
        stmt = stmt.where(
            Task.is_completed.is_(False)
        )

    elif status == "completed":
        stmt = stmt.where(
            Task.is_completed.is_(True)
        )

    # -------------------------
    # SORT
    # -------------------------
    if sort == "oldest":
        stmt = stmt.order_by(
            Task.created_at.asc()
        )

    elif sort == "due_soon":
        stmt = stmt.order_by(
            Task.due_date.asc().nullslast()
        )

    elif sort == "priority":
        # Temporary sorting by due date.
        # We can add explicit priority ordering later:
        # urgent > high > medium > low
        stmt = stmt.order_by(
            Task.due_date.asc().nullslast(),
            Task.created_at.desc()
        )

    else:
        # Default = newest
        stmt = stmt.order_by(
            Task.created_at.desc()
        )

    # -------------------------
    # PAGINATION
    # -------------------------
    stmt = (
        stmt
        .offset((page - 1) * limit)
        .limit(limit)
    )

    tasks = db.scalars(stmt).all()

    # If we received a full page,
    # there may be another page.
    has_more = len(tasks) == limit

    return {
        "msg": "Successful",
        "task_list": tasks,
        "page": page,
        "limit": limit,
        "has_more": has_more
    }


def get_task(
    task_id: int,
    current_user,
    db: Session
):
    stmt = select(Task).where(
        Task.id == task_id,
        Task.user_id == current_user.id
    )

    task = db.scalars(stmt).one_or_none()

    if task is None:
        raise HTTPException(
            status_code=404,
            detail="Task not found"
        )

    return {
        "msg": "Successful",
        "task": task
    }


def create_task(
    task,
    current_user,
    db: Session
):
    new_task = Task(
        title=task.title,
        description=task.description,
        priority=task.priority or TaskPriority.MEDIUM,
        due_date=task.due_date,
        category=task.category,
        estimated_minutes=task.estimated_minutes,
        tags=task.tags,
        user_id=current_user.id
    )

    db.add(new_task)
    db.commit()
    db.refresh(new_task)

    return {
        "msg": "Task CREATED SUCCESSFULLY!!!",
        "task": new_task
    }


def update_task(
    task_id: int,
    updated_task,
    current_user,
    db: Session
):
    stmt = select(Task).where(
        Task.id == task_id,
        Task.user_id == current_user.id
    )

    task = db.scalars(stmt).one_or_none()

    if task is None:
        raise HTTPException(
            status_code=404,
            detail="Task not found"
        )

    # -------------------------
    # UPDATE TASK FIELDS
    # -------------------------
    task.title = updated_task.title
    task.description = updated_task.description
    task.priority = updated_task.priority
    task.due_date = updated_task.due_date
    task.category = updated_task.category
    task.estimated_minutes = updated_task.estimated_minutes
    task.tags = updated_task.tags

    # -------------------------
    # UPDATE TIMESTAMP
    # -------------------------
    task.updated_at = datetime.now(timezone.utc)

    db.commit()
    db.refresh(task)

    return {
        "msg": f"TaskId {task_id} updated successfully",
        "task": task
    }


def delete_task(
    task_id: int,
    current_user,
    db: Session
):
    stmt = select(Task).where(
        Task.id == task_id,
        Task.user_id == current_user.id
    )

    task = db.scalars(stmt).one_or_none()

    if task is None:
        raise HTTPException(
            status_code=404,
            detail="Task not found"
        )

    db.delete(task)
    db.commit()

    return {
        "msg": f"TaskId {task_id} deleted successfully!!!"
    }


def update_task_status(
    task_id: int,
    current_user,
    db: Session
):
    stmt = select(Task).where(
        Task.id == task_id,
        Task.user_id == current_user.id
    )

    task = db.scalars(stmt).one_or_none()

    if task is None:
        raise HTTPException(
            status_code=404,
            detail="Task not found"
        )

    # -------------------------
    # TOGGLE COMPLETION STATUS
    # -------------------------
    task.is_completed = not task.is_completed

    # -------------------------
    # UPDATE COMPLETED_AT
    # -------------------------
    if task.is_completed:
        task.completed_at = datetime.now(timezone.utc)
    else:
        task.completed_at = None

    # -------------------------
    # UPDATE TIMESTAMP
    # -------------------------
    task.updated_at = datetime.now(timezone.utc)

    db.commit()
    db.refresh(task)

    return {
        "msg": "Task status changed successfully!!",
        "task": task
    }