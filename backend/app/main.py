from fastapi import Depends, FastAPI, HTTPException, status
from sqlalchemy import text
from sqlalchemy.orm import Session

from app import crud, schemas
from app.database import get_db, Base, engine

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
def create_user_endpoint(
    user: schemas.UserCreate, db: Session = Depends(get_db)  # noqa: B008
) -> schemas.UserRead:
    """Создание пользователя."""
    try:
        return crud.user.create_user(db=db, user=user)
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
