from datetime import datetime, timedelta, timezone

from fastapi import APIRouter, Depends, HTTPException, Request, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session

from app.core.config import settings
from app.core.security import create_access_token, create_refresh_token, verify_password
from app.core.tokens import get_token_from_request, verify_refresh_token
from app.crud import token as crud_token
from app.crud.token import create_refresh_token as create_db_token
from app.database import get_db
from app.models.user import User
from app.schemas.token import Token

router = APIRouter()


@router.post("/login", response_model=Token)
async def login(
    form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)
) -> dict:
    """Вход в систему."""
    user = db.query(User).filter(User.email == form_data.username).first()
    if not user or not verify_password(form_data.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token_exp = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": str(user.id)}, expires_delta=access_token_exp
    )
    refresh_expires = timedelta(days=7)
    refresh_token = create_refresh_token(
        data={"sub": str(user.id)}, expires_delta=refresh_expires
    )

    create_db_token(
        db=db,
        user_id=user.id,
        token=refresh_token,
        expires_at=datetime.now(timezone.utc) + refresh_expires,
    )

    return {
        "access_token": access_token,
        "refresh_token": refresh_token,
        "token_type": "bearer",
    }


@router.post("/refresh", response_model=Token)
async def refresh_access_token(request: Request, db: Session = Depends(get_db)) -> dict:
    """Обновление access-токена."""
    token = get_token_from_request(request)
    current_user = verify_refresh_token(token, db)
    crud_token.delete_refresh_token(db, token)

    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    new_access_token = create_access_token(
        data={"sub": str(current_user.id)}, expires_delta=access_token_expires
    )
    new_refresh_token = create_refresh_token(
        data={"sub": str(current_user.id)}, expires_delta=timedelta(days=7)
    )
    return {
        "access_token": new_access_token,
        "refresh_token": new_refresh_token,
        "token_type": "bearer",
    }


@router.post("/logout")
async def logout(request: Request, db: Session = Depends(get_db)):
    """Выход из системы."""
    token = get_token_from_request(request)
    crud_token.delete_refresh_token(db, token)
    return {"message": "Successfully logged out"}
