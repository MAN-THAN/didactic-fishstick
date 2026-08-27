from fastapi import APIRouter
from fastapi_backend.app.schemas.auth_schema import UserLogin, UserRegister

router = APIRouter(prefix='/auth')

@router.post('/register')
def register_user(user : UserRegister):



@router.post('/login')
def login_user(credentials : UserLogin):
