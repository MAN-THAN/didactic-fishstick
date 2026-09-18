from pydantic import BaseModel, Field

class DashboardAiResponse(BaseModel):
    summary: str
    priorities: list[str]
    overdue_tasks: list[str]
    recommendations: list[str]



# =========================================================
# REQUEST SCHEMA
# =========================================================


class AIChatRequest(BaseModel):
    message: str = Field(
        ...,
        min_length=1,
        max_length=5000,
        description="Message sent to the AI task assistant.",
    )