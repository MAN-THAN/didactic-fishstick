from sqlalchemy.orm import Session
from app.models.user_model import User
from sqlalchemy import select
from fastapi import HTTPException, Response
from app.utils.helper_func import getHashedPassword, match_password, create_access_token, create_refresh_token, hash_refresh_token
from app.config import settings
from app.models.refresh_token_model import RefreshToken
from datetime import datetime, timezone, timedelta
import uuid

def register_user(user, db: Session):
    stmt = select(User).where(User.email == user.email)
    existing_user = db.scalar(stmt)

    if(existing_user):
        raise HTTPException(status_code=409, detail='Email alraedy exists')
    
    hashed_pwd = getHashedPassword(user.password)
    newUser = User(first_name=user.first_name, last_name=user.last_name, email=user.email, password_hash=hashed_pwd)
    try:
        db.add(newUser)
        db.commit()
        db.refresh(newUser)

    except Exception:
        db.rollback()
        raise

    return {
        'msg' : 'User regsitered Successfully'
    }

def login(credentials, response : Response, db: Session):
    stmt = select(User).where(User.email == credentials.email)
    user = db.execute(stmt).scalar_one_or_none()

    if(user is None):
        raise HTTPException(status_code=401, detail='Invalid email or password')
    password_matched = match_password(credentials.password, user.password_hash)
    if(not password_matched):
        raise HTTPException(status_code=401, detail='Invalid email or password')
    
    access_token = create_access_token(user.id)
    refresh_token = create_refresh_token()
    hashed_refresh_token = hash_refresh_token(refresh_token)
    # Create refresh-token DB record
    refresh_token_record = RefreshToken(
        token_hash=hashed_refresh_token,
        user_id=user.id,
        family_id=str(uuid.uuid4()),
        expires_at=(
            datetime.now(timezone.utc)
            + timedelta(
                days=settings.REFRESH_TOKEN_EXPIRE_DAYS
            )
        ),
    )
    try :
        db.add(refresh_token_record)
        db.commit()

    except:
        db.rollback()
        raise
    
    response.set_cookie(
        key=settings.REFRESH_COOKIE_NAME,
        value=refresh_token,
        httponly=True,
        secure=settings.COOKIE_SECURE,
        samesite="none",
        max_age=settings.REFRESH_TOKEN_EXPIRE_DAYS * 24 * 60 * 60,
        path="/",
    )

    return {
        'msg' : 'Loggedin successfully',
        'access_token' : access_token,
        'token_type' : 'bearer'
    }

def refresh_token(
    response: Response,
    raw_refresh_token,
    db: Session,
):
    print('ASDFGHJK', raw_refresh_token)
    token_hash = hash_refresh_token(raw_refresh_token)

    stmt = select(RefreshToken).where(
        RefreshToken.token_hash == token_hash
    )

    stored_token = db.scalar(stmt)

    if not stored_token:
        raise HTTPException(
            status_code=401,
            detail="Invalid refresh token",
        )

    if stored_token.revoked_at is not None:
        raise HTTPException(
            status_code=401,
            detail="Refresh token revoked",
        )

    if stored_token.expires_at <= datetime.now(timezone.utc):
        raise HTTPException(
            status_code=401,
            detail="Refresh token expired",
        )

    # revoke old token
    stored_token.revoked_at = datetime.now(timezone.utc)

    # create replacement
    new_raw_token = create_refresh_token()
    new_hash = hash_refresh_token(new_raw_token)

    new_refresh_token = RefreshToken(
        user_id=stored_token.user_id,
        token_hash=new_hash,
        family_id=stored_token.family_id,
        expires_at=datetime.now(timezone.utc)
        + timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS),
    )

    db.add(new_refresh_token)
    db.flush()

    # stored_token.replaced_by_id = new_refresh_token.id

    db.commit()

    access_token = create_access_token(
        stored_token.user_id
    )
      
    response.set_cookie(
        key=settings.REFRESH_COOKIE_NAME,
        value=new_raw_token,
        httponly=True,
        secure=settings.COOKIE_SECURE,
        samesite="none",
        max_age=settings.REFRESH_TOKEN_EXPIRE_DAYS * 24 * 60 * 60,
        path="/",
    )

    return {'access_token' : access_token}  

def logout(response: Response, raw_refresh_token, db : Session):
     
    try:
        if raw_refresh_token:
            hashed_refresh_token = hash_refresh_token(raw_refresh_token)

            stmt = select(RefreshToken).where(
                RefreshToken.token_hash == hashed_refresh_token
            )

            refresh_token = db.scalar(stmt)

            if refresh_token and refresh_token.revoked_at is None:
                refresh_token.revoked_at = datetime.now(timezone.utc)

        db.commit()

    except Exception:
        db.rollback()
        raise

    response.delete_cookie(
        key=settings.REFRESH_COOKIE_NAME,
        path="/",
    )

    return {
        "message": "Logged out successfully"
    }




