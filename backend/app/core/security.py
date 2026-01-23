import secrets
from datetime import datetime, timedelta, timezone
from typing import Optional

from fastapi.security import OAuth2PasswordBearer
from jose import jwt
from passlib.context import CryptContext

from app.core.config import settings

ALGORITHM = "HS256"
pwd_context = CryptContext(schemes=["argon2"], deprecated="auto")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="login")


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Верификация пароля."""
    return pwd_context.verify(plain_password, hashed_password)


def get_password_hash(password: str) -> str:
    """Получение хеша пароля."""
    return pwd_context.hash(password)


def decode_jwt(token: str) -> dict:
    """Декодирование JWT-токена."""
    return jwt.decode(token, settings.SECRET_KEY, algorithms=[ALGORITHM])


def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    """Генерация access-токена."""
    to_encode = data.copy()
    expire = datetime.now(timezone.utc) + (expires_delta or timedelta(minutes=15))
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, settings.SECRET_KEY, algorithm=ALGORITHM)


def create_refresh_token(data: dict, expires_delta: timedelta) -> str:
    """Создание refresh-токена."""
    to_encode = data.copy()
    expire = datetime.now(timezone.utc) + expires_delta
    to_encode.update({"exp": expire, "type": "refresh"})
    return jwt.encode(to_encode, settings.SECRET_KEY, algorithm=ALGORITHM)


def generate_confirmation_token() -> str:
    """Генерация токена подтверждения."""
    return secrets.token_urlsafe(32)
