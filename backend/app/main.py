from datetime import datetime, timedelta, timezone

from fastapi import Depends, FastAPI, HTTPException, Request, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy import text
from sqlalchemy.orm import Session

from app import crud, schemas
from app.core.config import settings
from app.core.security import (
    create_access_token,
    create_refresh_token,
    get_current_user,
    get_token_from_request,
    verify_refresh_token,
)
from app.database import Base, engine, get_db
from app.models.user import User

Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="Dev Team AI",
    version="1.0.0",
    description="Многоагентная система для разработчиков",
)


@app.get("/users/me", response_model=schemas.UserRead)
async def read_users_me(cur_user: User = Depends(get_current_user)):
    """Получение информации о пользователе."""
    return schemas.UserRead.from_orm(cur_user)


@app.get("/db-test'")
async def test_bd(db: Session = Depends(get_db)):  # noqa: B008
    try:
        res = db.execute(text("SELECT version();"))
        version = res.fetchone()[0]
        return {"status": "OK", "postgres_version": version}
    except Exception as e:
        return {"status": "ERROR", "detail": str(e)}


@app.post("/users/", response_model=schemas.UserRead)
async def create_user_endpoint(
    user: schemas.UserCreate, db: Session = Depends(get_db)  # noqa: B008
) -> schemas.UserRead:
    """Создание пользователя."""
    try:
        return crud.user.create_user(db=db, user=user)
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail=str(e)
        ) from e


@app.get("/users/{email}", response_model=schemas.UserRead)
async def get_user(email: str, db: Session = Depends(get_db)):
    db_user = crud.user.get_user_by_email(db, email=email)
    if db_user is None:
        raise HTTPException(status_code=404, detail="User not found")
    return db_user


@app.post("/login", response_model=schemas.token.Token)
async def login(
    form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)
) -> dict:
    """Вход в систему."""
    user = crud.user.authenticate_user(db, form_data.username, form_data.password)
    if not user:
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

    from app.crud.token import create_refresh_token as create_db_token

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


@app.post("/refresh", response_model=schemas.token.Token)
async def refresh_access_token(request: Request, db: Session = Depends(get_db)) -> dict:
    """Обновление access-токена."""
    token = get_token_from_request(request)
    current_user = verify_refresh_token(token, db)
    crud.token.delete_refresh_token(db, token)

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


@app.post("/logout")
async def logout(request: Request, db: Session = Depends(get_db)):
    """Выход из системы."""
    token = get_token_from_request(request)
    crud.token.delete_refresh_token(db, token)
    return {"message": "Successfully logged out"}


@app.put("/users/me", response_model=schemas.UserRead)
async def update_user_me(
    user_update: schemas.UserUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Обновление профиля текущего пользователя."""
    updated_user = crud.user.update_user(
        db, user_id=current_user.id, user_update=user_update
    )
    return schemas.UserRead.from_orm(updated_user)
