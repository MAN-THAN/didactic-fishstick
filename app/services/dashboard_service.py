from sqlalchemy.orm import Session
from app.models.task_model import Task
from sqlalchemy import select
from app.services.gemini_service import generate_tasks_summary

async def get_dashboard_summary(current_user, db: Session):
    stmt = select(Task).where(Task.user_id == current_user.id).where(Task.is_completed == False).limit(5)
    user_incomplete_tasks = db.scalars(stmt).all()
    user_incomplete_tasks_list = [
        {
            "id": task.id,
            "title": task.title,
            "description": task.description,
            "priority": task.priority,
            "is_completed": task.is_completed,
        }
        for task in user_incomplete_tasks
    ]
    dashboard_data = {
        "incomplete_tasks": user_incomplete_tasks_list,
        "incomplete_tasks_count": len(user_incomplete_tasks_list),
    }
    async for chunk in generate_tasks_summary(dashboard_data):
        yield chunk    



