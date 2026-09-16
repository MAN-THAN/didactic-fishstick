from app.ai.llm import llm
from app.schemas.ai_schema import DashboardAiResponse
from app.ai.prompts import dashboard_summary_prompt

structured_llm = llm.with_structured_output(DashboardAiResponse, method='json_schema')

dashboard_chain = (dashboard_summary_prompt | structured_llm)

    

       