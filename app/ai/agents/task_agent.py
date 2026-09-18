from langchain.agents import create_agent

from app.ai.llm import llm
from app.ai.tools.task_tools import create_task_tools


SYSTEM_PROMPT = """
You are an AI task management assistant.

Your job is to help the authenticated user manage and understand
their tasks.

Follow these rules:

1. Use the available tools whenever you need task information.
2. Never invent task data.
3. Use get_tasks_tool when the user wants to list, search, filter,
   or inspect multiple tasks.
4. Use get_task_tool when you need information about one specific task.
5. Use get_task_overview_tool when the user asks for a task summary,
   overview, productivity snapshot, or what needs attention.
6. Use create_task_tool when the user asks to create or add a task.
7. Use update_task_tool when the user asks to modify task details.
8. Use update_task_status_tool when the user asks to complete,
   finish, reopen, or mark a task as done.
9. Use delete_task_tool when the user asks to delete a task.
10. Before modifying or deleting a task, make sure you have identified
    the correct task.
11. After a successful task operation, clearly tell the user what happened.
12. Keep responses concise and useful.
"""


def create_task_agent(current_user, db):
    """
    Create an AI task agent scoped to the authenticated user.

    """

    tools = create_task_tools(
        current_user=current_user,
        db=db,
    )

    agent = create_agent(
        model=llm,
        tools=tools,
        system_prompt=SYSTEM_PROMPT,
        name='task_agent'
    )

    return agent