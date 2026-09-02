from sqlalchemy.orm import Session
from app.models.user_model import User
from sqlalchemy import select
from fastapi import HTTPException

def getUserInfo(user, db:Session):
    stmt = select(User).where(User.id == user.id)
    result = db.execute(stmt)
    curr_user = result.scalar_one_or_none()

    if(curr_user is None):
        raise HTTPException(status_code=404, detail='No user found')
    
    return curr_user
