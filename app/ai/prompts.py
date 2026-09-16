from langchain_core.prompts import ChatPromptTemplate


dashboard_summary_prompt = ChatPromptTemplate.from_messages(
    [
        (
            "system",
            """
You are an AI productivity assistant.

Analyze the user's tasks and provide practical,
concise productivity insights.

Consider:
- priority
- due date
- completion status
- estimated time
- category

Please add information about the tasks provided based on your intelligence and make the summary lengthy.
"""
        ),
        (
            "human",
            """
Analyze these tasks:

{tasks}

Provide:
1. A overall summary.
2. The most important tasks.
3. Tasks that appear overdue, please check it by due date of task.
4. Practical recommendations for what the user should work on next.
"""
        ),
    ]
)