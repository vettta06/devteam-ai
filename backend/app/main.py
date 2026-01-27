import os
from pydoc import text

from fastapi import Depends, FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from sqlalchemy.orm import Session

from app.database import Base, engine, get_db
from app.routers import ai, auth, email, tasks, users

Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="Dev Team AI",
    version="1.0.0",
    description="Многоагентная система для разработчиков",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:8000",
        "http://127.0.0.1:8000",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth.router, prefix="/auth", tags=["auth"])
app.include_router(users.router, prefix="/users", tags=["users"])
app.include_router(email.router, prefix="/email", tags=["email"])
app.include_router(tasks.router, prefix="/tasks", tags=["task"])
app.include_router(ai.router, prefix="/ai", tags=["ai"])


frontend_dir = os.path.join(os.path.dirname(__file__), "..", "..", "frontend")
app.mount("/static", StaticFiles(directory=frontend_dir), name="static")


@app.get("/{full_path:path}")
async def serve_frontend(full_path: str):
    if (
        full_path.startswith("api/")
        or full_path.startswith("docs")
        or full_path.startswith("openapi")
    ):
        return {"detail": "Not Found"}, 404
    file_path = os.path.join(frontend_dir, "index.html")
    if os.path.exists(file_path):
        return FileResponse(file_path)
    return {"detail": "Frontend not found"}, 500


@app.get("/db-test")
async def test_bd(db: Session = Depends(get_db)):  # noqa: B008
    try:
        res = db.execute(text("SELECT version();"))
        version = res.fetchone()[0]
        return {"status": "OK", "postgres_version": version}
    except Exception as e:
        return {"status": "ERROR", "detail": str(e)}
