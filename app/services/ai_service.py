import json

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.task_model import Task
from app.ai.chains.dashboard_chain import dashboard_chain


def _serialize_tasks(tasks):
    return [
        {
            "id": task.id,
            "title": task.title,
            "description": task.description,
            "priority": task.priority.value
            if task.priority
            else None,
            "due_date": task.due_date.isoformat()
            if task.due_date
            else None,
            "category": task.category,
            "estimated_minutes": task.estimated_minutes,
            "is_completed": task.is_completed,
            "completed_at": task.completed_at.isoformat()
            if task.completed_at
            else None,
            "tags": task.tags,
        }
        for task in tasks
    ]


async def stream_dashboard_summary(
    current_user,
    db: Session,
):
    try:
        # -----------------------------
        # Fetch user's tasks
        # -----------------------------
        stmt = (
            select(Task)
            .where(Task.user_id == current_user.id)
            .order_by(Task.created_at.desc())
        )

        tasks = db.scalars(stmt).all()

        task_data = _serialize_tasks(tasks)
        print("Serialized Task Data:", task_data)  # Debugging line

        # -----------------------------
        # Start event
        # -----------------------------
        yield {
            "event": "start",
            "data": {
                "message": "Analyzing your tasks..."
            },
        }

        # -----------------------------
        # Stream structured response
        # -----------------------------
        async for chunk in dashboard_chain.astream(
            {"tasks": task_data}
        ):
            if chunk is None:
                continue

            yield {
                "event": "chunk",
                "data": chunk.model_dump(
                    exclude_none=True
                ),
            }

        # -----------------------------
        # Done event
        # -----------------------------
        yield {
            "event": "done",
            "data": {
                "message": "Analysis completed"
            },
        }

    except Exception as exc:
        yield {
            "event": "error",
            "data": {
                "message": str(exc)
            },
        }

