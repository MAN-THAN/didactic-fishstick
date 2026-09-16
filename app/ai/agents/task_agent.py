from langchain.agents import create_agent
from app.ai.llm import llm


ai_task_agent = create_agent(model=llm, tools=[])