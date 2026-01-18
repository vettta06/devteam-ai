from fastapi import Depends, FastAPI
from sqlalchemy import text
from sqlalchemy.orm import Session

from app.database import get_db

app = FastAPI(
    title="Dev Team AI",
    version="1.0.0",
    description="Многоагентная система для разработчиков"
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
        return {
            "status": "OK",
            "postgres_version": version
        }
    except Exception as e:
        return {
            "status": "ERROR",
            "detail": str(e)
        }
