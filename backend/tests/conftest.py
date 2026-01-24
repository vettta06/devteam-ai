import uuid
from pathlib import Path

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker

from app.database import Base, get_db
from app.main import app

env_path = Path(__file__).parent.parent.parent / ".env.test"
if env_path.exists():
    from dotenv import load_dotenv

    load_dotenv(env_path, override=True)

SQLALCHEMY_DATABASE_URL = "sqlite:///./test.db"

engine = create_engine(
    SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False}
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base.metadata.create_all(bind=engine)


def override_get_db():
    try:
        db = TestingSessionLocal()
        yield db
    finally:
        db.close()


app.dependency_overrides[get_db] = override_get_db


@pytest.fixture(scope="module")
def client():
    return TestClient(app)


@pytest.fixture(scope="function")
def test_user():
    return {"email": f"test_{uuid.uuid4()}@example.com", "password": "1234"}


@pytest.fixture(scope="function")
def auth_token(client, test_user):
    client.post("/users/", json=test_user)
    response = client.post(
        "/auth/login",
        data={"username": test_user["email"], "password": test_user["password"]},
    )
    return response.json()["access_token"]


@pytest.fixture(scope="function", autouse=True)
def clean_db():
    """Очищает БД перед каждым тестом."""
    db = TestingSessionLocal()
    db.execute(text("DELETE FROM tasks;"))
    db.execute(text("DELETE FROM refresh_tokens;"))
    db.execute(text("DELETE FROM users;"))
    db.commit()
    db.close()
