from pydantic import BaseModel

class DashboardAiResponse(BaseModel):
    summary: str
    priorities: list[str]
    overdue_tasks: list[str]
    recommendations: list[str]