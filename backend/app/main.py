from pydoc import text

from fastapi import Depends, FastAPI
from sqlalchemy.orm import Session

from app.database import Base, engine, get_db
from app.routers import auth, email, tasks, users

Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="Dev Team AI",
    version="1.0.0",
    description="Многоагентная система для разработчиков",
)

app.include_router(auth.router, prefix="/auth", tags=["auth"])
app.include_router(users.router, prefix="/users", tags=["users"])
app.include_router(email.router, prefix="/email", tags=["email"])
app.include_router(tasks.router, prefix="/tasks", tags=["task"])


@app.get("/health")
async def health_check():
    return {"status": "OK"}


@app.get("/db-test")
async def test_bd(db: Session = Depends(get_db)):  # noqa: B008
    try:
        res = db.execute(text("SELECT version();"))
        version = res.fetchone()[0]
        return {"status": "OK", "postgres_version": version}
    except Exception as e:
        return {"status": "ERROR", "detail": str(e)}
