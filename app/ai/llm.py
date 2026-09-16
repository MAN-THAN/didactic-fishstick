from langchain_google_genai import ChatGoogleGenerativeAI as GoogleGenAI
from app.config import settings

llm = GoogleGenAI(
    model=settings.GOOGLE_GENAI_MODEL,
    temperature=settings.GOOGLE_GENAI_TEMPERATURE,
    api_key=settings.GOOGLE_GENAI_API_KEY
)

