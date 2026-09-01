from fastapi import APIRouter, Depends, Response, Cookie
from app.schemas.auth_schema import UserLogin, UserRegister
from sqlalchemy.orm import Session
from app.database import get_db
from app.services import auth_service

router = APIRouter(prefix='/auth', tags=['Auth'])

@router.post('/register')
def register_user(user : UserRegister, db : Session = Depends(get_db)):
    return auth_service.register_user(user, db)

@router.post('/login')
def login_user(credentials : UserLogin, response: Response, db : Session = Depends(get_db)):
    return auth_service.login(credentials, response, db)

@router.post('/refresh')
def refresh_token(response: Response, refresh_token: str | None = Cookie(default=None), db : Session = Depends(get_db)):
    return auth_service.refresh_token(response, refresh_token, db)

@router.post('/logout')
def logout_user(response : Response, raw_refresh_token: str | None = Cookie(default=None), db:Session = Depends(get_db)):
    return auth_service.logout(response, raw_refresh_token, db)

