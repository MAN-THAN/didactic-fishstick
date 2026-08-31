from fastapi import APIRouter, Depends
from app.schemas.auth_schema import UserLogin, UserRegister
from sqlalchemy.orm import Session
from app.database import get_db
from app.services import auth_service

router = APIRouter(prefix='/auth')

@router.post('/register')
def register_user(user : UserRegister, db : Session = Depends(get_db)):
    return auth_service.register_user(user, db)


@router.post('/login')
def login_user(credentials : UserLogin, db : Session = Depends(get_db)):
    return auth_service.login(credentials, db)
