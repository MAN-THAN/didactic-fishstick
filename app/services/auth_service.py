from sqlalchemy.orm import Session
from app.models.user_model import User
from sqlalchemy import select
from fastapi import HTTPException
from app.utils.helper_func import getHashedPassword, match_password, create_access_token

def register_user(user, db: Session):
    stmt = select(User).where(User.email == user.email)
    existing_user = db.scalar(stmt)

    if(existing_user):
        raise HTTPException(status_code=409, detail='Email alraedy exists')
    
    hashed_pwd = getHashedPassword(user.password)
    newUser = User(first_name=user.first_name, last_name=user.last_name, email=user.email, password=hashed_pwd)
    try:
        db.add(newUser)
        db.commit()
        db.refresh(newUser)

    except Exception:
        db.rollback()
        raise

    return {
        'msg' : 'Regsitered Successfully'
    }

def login(credentials, db: Session):
    stmt = select(User).where(User.email == credentials.email)
    user = db.execute(stmt).scalar_one_or_none()

    if(user is None):
        raise HTTPException(status_code=404, detail='Invalid email or password')
    
    password_matched = match_password(credentials.password, user.password_hash)
    if(not password_matched):
        raise HTTPException(status_code=401, detail='Invalid email or password')
    
    access_token = create_access_token(user.id)

    return {
        'msg' : 'Loggedin successfully',
        'access_token' : access_token,
        'token_type' : 'bearer'
    }


