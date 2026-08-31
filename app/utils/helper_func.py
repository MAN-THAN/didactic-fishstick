from pwdlib import PasswordHash
from datetime import datetime, timedelta, timezone

import jwt

from app.config import settings


ALGORITHM = "HS256"

def create_access_token(user_id: int) -> str:
    expire = datetime.now(timezone.utc) + timedelta(
        minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES
    )

    payload = {
        "sub": str(user_id),
        "exp": expire,
    }

    return jwt.encode(
        payload,
        settings.SECRET_KEY,
        algorithm=ALGORITHM
    )

password_hash = PasswordHash.recommended()

def getHashedPassword(pwd):
    return password_hash.hash(pwd) 

def match_password(hashed_pwd, user_pwd):
    return password_hash.verify(user_pwd, hashed_pwd)

