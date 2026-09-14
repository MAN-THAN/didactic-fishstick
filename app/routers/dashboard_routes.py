from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.database import get_db
from app.services import dashboard_service
from app.dependencies.auth_dependency import get_current_user
from app.models.user_model import User
from fastapi.responses import StreamingResponse

router = APIRouter(prefix='/dashboard', tags=['Dashboard'],dependencies=[Depends(get_current_user)])

@router.get('/')
async def get_dashboard_summary(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
        async def event_generator():
          async for chunk in dashboard_service.get_dashboard_summary(current_user, db):
            yield f"data: {chunk}\n\n"

        return StreamingResponse(
        event_generator(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache, no-transform",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no",
        },
)

