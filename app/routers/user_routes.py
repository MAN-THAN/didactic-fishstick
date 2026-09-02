from fastapi import APIRouter, Depends
from app.services import user_service
from sqlalchemy.orm import Session
from app.database import get_db
from app.dependencies.auth_dependency import get_current_user
from app.schemas.user_schema import User_Response
from app.models.user_model import User



router = APIRouter(prefix='/user', tags=['User'])

@router.get('/me', response_model=User_Response)
def get_user_info(current_user : User = Depends(get_current_user) , db : Session = Depends(get_db)):
    return user_service.getUserInfo(current_user, db)