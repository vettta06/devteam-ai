import uuid

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker

import app.core.config as config_module
from app.core.config import TestSettings

config_module.settings = TestSettings()

from app.database import Base, get_db  # noqa: E402
from app.main import app  # noqa: E402

SQLALCHEMY_DATABASE_URL = config_module.settings.DATABASE_URL
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


@pytest.fixture(scope="function")
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
    db.execute(text("DELETE FROM refresh_tokens;"))
    db.execute(text("DELETE FROM tasks;"))
    db.execute(text("DELETE FROM users;"))
    db.commit()
    db.close()
