from google import genai
from app.config import settings
import json

client = genai.Client(
    api_key=settings.GEMINI_API_KEY
)


async def generate_tasks_summary(dashboard_data):

    prompt = f"""
You are an AI productivity assistant for a task management application.

Analyze the user's incomplete tasks and write a helpful productivity briefing.

User's task data:
{json.dumps(dashboard_data, default=str)}

Writing requirements:
- Write as a natural, polished paragraph.
- Do not use Markdown headings.
- Do not use bullet points.
- Do not use numbered lists.
- Do not use "---".
- Do not mention that you are analyzing data.
- Speak directly to the user.
- Discuss the tasks one by one where useful.
- Explain which tasks deserve attention and why.
- Mention urgency or deadlines only when supported by the task data.
- Do not invent deadlines, priorities, or facts that are not present.
- Keep the tone professional, friendly, and concise.
- Make it feel like a personalized productivity briefing.
- Aim for around 200 words.
"""

    response = await client.aio.models.generate_content_stream(
        model="gemini-3.1-flash-lite",
        contents=prompt,
    )

    async for chunk in response:
        if chunk.text:
            yield chunk.text


