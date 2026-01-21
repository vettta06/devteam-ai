from datetime import datetime
from typing import Optional

from pydantic import BaseModel, EmailStr, Field


class UserBase(BaseModel):
    """Базовая модель пользователя."""

    email: EmailStr


class UserCreate(UserBase):
    """Пользователь + пароль."""

    password: str = Field(min_length=4, max_length=72)


class UserRead(UserBase):
    """Полная версия пользователя."""

    id: int
    is_active: bool
    created_at: datetime

    class Config:
        from_attributes = True


class UserUpdate(BaseModel):
    """Обновление пользователя."""

    email: Optional[str] = None
    password: Optional[str] = None


class UserList(UserBase):
    """Получение всех пользователейю"""

    id: int
    is_active: int
    created_at: datetime

    class Config:
        from_attributes = True
