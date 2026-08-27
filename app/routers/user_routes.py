from fastapi import APIRouter
from app.services import user_service

router = APIRouter(prefix='/user')

@router.get('{user_id}/me')
def get_user_info(user_id : str):
    return user_service.getUserInfo(user_id)