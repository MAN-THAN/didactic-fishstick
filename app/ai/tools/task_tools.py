from datetime import datetime, timezone

from langchain.tools import tool
from langgraph.config import get_stream_writer
from pydantic import BaseModel, Field

from app.models.task_model import TaskPriority
from app.schemas.task_schema import TaskCreate, TaskUpdate
from app.services.task_service import (
    get_tasks as service_get_tasks,
    get_task as service_get_task,
    create_task as service_create_task,
    update_task as service_update_task,
    delete_task as service_delete_task,
    update_task_status as service_update_task_status,
)


# =========================================================
# TOOL INPUT SCHEMAS
# =========================================================


class GetTasksInput(BaseModel):
    search: str | None = Field(
        default=None,
        description="Optional text to search for in task titles."
    )

    status: str = Field(
        default="all",
        description="Task status filter. Allowed values: all, active, completed."
    )

    sort: str = Field(
        default="newest",
        description="Sorting option. Allowed values: newest, oldest, due_soon, priority."
    )

    limit: int = Field(
        default=50,
        ge=1,
        le=100,
        description="Maximum number of tasks to return."
    )


class GetTaskInput(BaseModel):
    task_id: int = Field(
        description="The ID of the task."
    )


class CreateTaskInput(BaseModel):
    title: str = Field(
        min_length=1,
        max_length=100,
        description="The title of the task."
    )

    description: str | None = Field(
        default=None,
        max_length=500,
        description="Optional description of the task."
    )

    priority: TaskPriority = Field(
        default=TaskPriority.MEDIUM,
        description="Task priority. Allowed values: low, medium, high, urgent."
    )

    due_date: datetime | None = Field(
        default=None,
        description="Optional task deadline in ISO datetime format."
    )

    category: str | None = Field(
        default=None,
        max_length=50,
        description="Optional category such as Work, Personal, Learning, etc."
    )

    estimated_minutes: int | None = Field(
        default=None,
        gt=0,
        description="Estimated time required to complete the task in minutes."
    )

    tags: list[str] | None = Field(
        default=None,
        description="Optional list of tags."
    )


class UpdateTaskInput(BaseModel):
    task_id: int = Field(
        description="The ID of the task to update."
    )

    title: str | None = Field(
        default=None,
        min_length=1,
        max_length=100,
        description="New task title."
    )

    description: str | None = Field(
        default=None,
        max_length=500,
        description="New task description."
    )

    priority: TaskPriority | None = Field(
        default=None,
        description="New task priority."
    )

    due_date: datetime | None = Field(
        default=None,
        description="New task deadline."
    )

    category: str | None = Field(
        default=None,
        max_length=50,
        description="New task category."
    )

    estimated_minutes: int | None = Field(
        default=None,
        gt=0,
        description="New estimated time in minutes."
    )

    tags: list[str] | None = Field(
        default=None,
        description="New list of tags."
    )


class DeleteTaskInput(BaseModel):
    task_id: int = Field(
        description="The ID of the task to delete."
    )


class UpdateTaskStatusInput(BaseModel):
    task_id: int = Field(
        description="The ID of the task whose completion status should be toggled."
    )


# =========================================================
# HELPER FUNCTIONS
# =========================================================


def _emit_tool_activity(
    event: str,
    tool_name: str,
    message: str,
    data: dict | None = None,
):
    """
    Send custom activity information to the LangChain stream.

    The information is intended for the frontend UI and does not
    contain model chain-of-thought or private reasoning.
    """

    try:
        writer = get_stream_writer()

        writer(
            {
                "event": event,
                "tool": tool_name,
                "message": message,
                "data": data,
            }
        )

    except Exception:
        # The tool should still work normally when it is called
        # outside of a streaming LangChain execution.
        pass


def _serialize_task(task):
    """
    Convert SQLAlchemy Task object into plain JSON-friendly data.
    """

    return {
        "id": task.id,
        "title": task.title,
        "description": task.description,
        "priority": (
            task.priority.value
            if task.priority
            else None
        ),
        "due_date": (
            task.due_date.isoformat()
            if task.due_date
            else None
        ),
        "category": task.category,
        "estimated_minutes": task.estimated_minutes,
        "is_completed": task.is_completed,
        "completed_at": (
            task.completed_at.isoformat()
            if task.completed_at
            else None
        ),
        "tags": task.tags,
        "created_at": (
            task.created_at.isoformat()
            if task.created_at
            else None
        ),
        "updated_at": (
            task.updated_at.isoformat()
            if task.updated_at
            else None
        ),
    }


# =========================================================
# TOOL FACTORY
# =========================================================


def create_task_tools(current_user, db):
    """
    Create all task-management tools for the authenticated user.

    current_user and db are captured inside the tool closures.
    They are never exposed as arguments that the LLM can control.
    """

    # =====================================================
    # GET TASKS
    # =====================================================

    @tool(args_schema=GetTasksInput)
    def get_tasks_tool(
        search: str | None = None,
        status: str = "all",
        sort: str = "newest",
        limit: int = 50,
    ):
        """
        Retrieve tasks belonging to the current authenticated user.

        Use this when the user asks to list, search, filter,
        or inspect multiple tasks.
        """

        _emit_tool_activity(
            event="tool_started",
            tool_name="get_tasks",
            message="Fetching your tasks...",
        )

        result = service_get_tasks(
            search=search,
            page=1,
            limit=limit,
            status=status,
            sort=sort,
            current_user=current_user,
            db=db,
        )

        tasks = [
            _serialize_task(task)
            for task in result["task_list"]
        ]

        _emit_tool_activity(
            event="tool_completed",
            tool_name="get_tasks",
            message=f"Found {len(tasks)} tasks.",
            data={
                "count": len(tasks),
            },
        )

        return {
            "tasks": tasks,
            "count": len(tasks),
            "has_more": result["has_more"],
        }

    # =====================================================
    # GET SINGLE TASK
    # =====================================================

    @tool(args_schema=GetTaskInput)
    def get_task_tool(task_id: int):
        """
        Retrieve one task belonging to the current authenticated user.

        Use this when detailed information about a specific task
        is required.
        """

        _emit_tool_activity(
            event="tool_started",
            tool_name="get_task",
            message=f"Fetching task #{task_id}...",
            data={
                "task_id": task_id,
            },
        )

        result = service_get_task(
            task_id=task_id,
            current_user=current_user,
            db=db,
        )

        task = _serialize_task(result["task"])

        _emit_tool_activity(
            event="tool_completed",
            tool_name="get_task",
            message=f"Task #{task_id} loaded.",
            data={
                "task_id": task_id,
            },
        )

        return task

    # =====================================================
    # GET TASK OVERVIEW
    # =====================================================

    @tool
    def get_task_overview_tool():
        """
        Get an overview of the current user's tasks.

        Use this when the user asks for a task summary,
        productivity overview, what needs attention, or
        similar high-level information.
        """

        _emit_tool_activity(
            event="tool_started",
            tool_name="get_task_overview",
            message="Analyzing your task overview...",
        )

        result = service_get_tasks(
            search=None,
            page=1,
            limit=100,
            status="all",
            sort="newest",
            current_user=current_user,
            db=db,
        )

        tasks = result["task_list"]

        now = datetime.now(timezone.utc)

        total_tasks = len(tasks)

        completed_tasks = sum(
            1
            for task in tasks
            if task.is_completed
        )

        active_tasks = sum(
            1
            for task in tasks
            if not task.is_completed
        )

        overdue_tasks = [
            _serialize_task(task)
            for task in tasks
            if (
                task.due_date
                and not task.is_completed
                and task.due_date < now
            )
        ]

        urgent_tasks = [
            _serialize_task(task)
            for task in tasks
            if (
                not task.is_completed
                and task.priority == TaskPriority.URGENT
            )
        ]

        high_priority_tasks = [
            _serialize_task(task)
            for task in tasks
            if (
                not task.is_completed
                and task.priority == TaskPriority.HIGH
            )
        ]

        overview = {
            "total_tasks": total_tasks,
            "completed_tasks": completed_tasks,
            "active_tasks": active_tasks,
            "overdue_count": len(overdue_tasks),
            "urgent_count": len(urgent_tasks),
            "high_priority_count": len(high_priority_tasks),
            "overdue_tasks": overdue_tasks,
            "urgent_tasks": urgent_tasks,
            "high_priority_tasks": high_priority_tasks,
        }

        _emit_tool_activity(
            event="tool_completed",
            tool_name="get_task_overview",
            message="Task overview prepared.",
            data={
                "total_tasks": total_tasks,
                "active_tasks": active_tasks,
                "completed_tasks": completed_tasks,
                "overdue_count": len(overdue_tasks),
            },
        )

        return overview

    # =====================================================
    # CREATE TASK
    # =====================================================

    @tool(args_schema=CreateTaskInput)
    def create_task_tool(
        title: str,
        description: str | None = None,
        priority: TaskPriority = TaskPriority.MEDIUM,
        due_date: datetime | None = None,
        category: str | None = None,
        estimated_minutes: int | None = None,
        tags: list[str] | None = None,
    ):
        """
        Create a new task for the current authenticated user.

        Use this when the user asks to create, add, or make
        a new task.
        """

        _emit_tool_activity(
            event="tool_started",
            tool_name="create_task",
            message=f"Creating task '{title}'...",
        )

        task_data = TaskCreate(
            title=title,
            description=description,
            priority=priority,
            due_date=due_date,
            category=category,
            estimated_minutes=estimated_minutes,
            tags=tags,
        )

        result = service_create_task(
            task=task_data,
            current_user=current_user,
            db=db,
        )

        created_task = _serialize_task(
            result["task"]
        )

        _emit_tool_activity(
            event="tool_completed",
            tool_name="create_task",
            message="Task created successfully.",
            data={
                "task_id": created_task["id"],
                "title": created_task["title"],
            },
        )

        return {
            "success": True,
            "message": result["msg"],
            "task": created_task,
        }

    # =====================================================
    # UPDATE TASK
    # =====================================================

    @tool(args_schema=UpdateTaskInput)
    def update_task_tool(
        task_id: int,
        title: str | None = None,
        description: str | None = None,
        priority: TaskPriority | None = None,
        due_date: datetime | None = None,
        category: str | None = None,
        estimated_minutes: int | None = None,
        tags: list[str] | None = None,
    ):
        """
        Update a task belonging to the current authenticated user.

        Use this when the user asks to modify task details such as
        title, description, priority, due date, category,
        estimated time, or tags.
        """

        _emit_tool_activity(
            event="tool_started",
            tool_name="update_task",
            message=f"Updating task #{task_id}...",
            data={
                "task_id": task_id,
            },
        )

        update_data = TaskUpdate(
            title=title,
            description=description,
            priority=priority,
            due_date=due_date,
            category=category,
            estimated_minutes=estimated_minutes,
            tags=tags,
        )

        result = service_update_task(
            task_id=task_id,
            updated_task=update_data,
            current_user=current_user,
            db=db,
        )

        updated_task = _serialize_task(
            result["task"]
        )

        _emit_tool_activity(
            event="tool_completed",
            tool_name="update_task",
            message=f"Task #{task_id} updated successfully.",
            data={
                "task_id": task_id,
            },
        )

        return {
            "success": True,
            "message": result["msg"],
            "task": updated_task,
        }

    # =====================================================
    # UPDATE TASK STATUS
    # =====================================================

    @tool(args_schema=UpdateTaskStatusInput)
    def update_task_status_tool(task_id: int):
        """
        Toggle the completion status of a task.

        Use this when the user asks to complete, finish,
        reopen, or mark a task as done.
        """

        _emit_tool_activity(
            event="tool_started",
            tool_name="update_task_status",
            message=f"Updating completion status for task #{task_id}...",
            data={
                "task_id": task_id,
            },
        )

        result = service_update_task_status(
            task_id=task_id,
            current_user=current_user,
            db=db,
        )

        updated_task = _serialize_task(
            result["task"]
        )

        _emit_tool_activity(
            event="tool_completed",
            tool_name="update_task_status",
            message=(
                f"Task #{task_id} is now "
                f"{'completed' if updated_task['is_completed'] else 'active'}."
            ),
            data={
                "task_id": task_id,
                "is_completed": updated_task["is_completed"],
            },
        )

        return {
            "success": True,
            "message": result["msg"],
            "task": updated_task,
        }

    # =====================================================
    # DELETE TASK
    # =====================================================

    @tool(args_schema=DeleteTaskInput)
    def delete_task_tool(task_id: int):
        """
        Delete a task belonging to the current authenticated user.

        Use this when the user explicitly asks to delete or
        remove a task.
        """

        _emit_tool_activity(
            event="tool_started",
            tool_name="delete_task",
            message=f"Deleting task #{task_id}...",
            data={
                "task_id": task_id,
            },
        )

        result = service_delete_task(
            task_id=task_id,
            current_user=current_user,
            db=db,
        )

        _emit_tool_activity(
            event="tool_completed",
            tool_name="delete_task",
            message=f"Task #{task_id} deleted successfully.",
            data={
                "task_id": task_id,
            },
        )

        return {
            "success": True,
            "message": result["msg"],
            "task_id": task_id,
        }

    # =====================================================
    # RETURN ALL TOOLS
    # =====================================================

    return [
        get_tasks_tool,
        get_task_tool,
        get_task_overview_tool,
        create_task_tool,
        update_task_tool,
        update_task_status_tool,
        delete_task_tool,
    ]