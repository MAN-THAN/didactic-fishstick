from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.database import get_db
from app.services import ai_service
from app.dependencies.auth_dependency import get_current_user
from app.models.user_model import User
from fastapi.responses import StreamingResponse
from app.services import ai_service 
from fastapi.sse import EventSourceResponse, ServerSentEvent


router = APIRouter(prefix='/ai', tags=['AI'],dependencies=[Depends(get_current_user)])

@router.get('/dashboard_summary', response_class=EventSourceResponse)
async def get_dashboard_summary(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    """
    Get a summary of the user's dashboard, including task priorities, overdue tasks, and recommendations.
    """
    async for event in ai_service.stream_dashboard_summary(
        current_user,
        db,
    ):
        yield ServerSentEvent(
            event=event["event"],
            data=event["data"],
        )
    
      


