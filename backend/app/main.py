from datetime import timedelta

from fastapi import Depends, FastAPI, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy import text
from sqlalchemy.orm import Session

from app import crud, schemas
from app.core.config import settings
from app.core.security import create_access_token, get_current_user
from app.database import Base, engine, get_db
from app.models.user import User

Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="Dev Team AI",
    version="1.0.0",
    description="Многоагентная система для разработчиков",
)


@app.get("/health")
async def check_health():
    """Проверка работы сервера."""
    return {"message": "Hi"}


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
    return {"access_token": access_token, "token_type": "bearer"}


@app.get("/users/me", response_model=schemas.UserRead)
async def read_users_me(cur_user: User = Depends(get_current_user)) -> User:
    """Получение информации о пользователе."""
    return cur_user
