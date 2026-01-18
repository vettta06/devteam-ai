from datetime import datetime

from pydantic import BaseModel


class UserBase(BaseModel):
    """Базовая модель пользователя."""

    email: str


class UserCreate(UserBase):
    """Пользователь + пароль."""

    password: str


class UserRead(UserBase):
    """Полная версия пользователя."""

    id: int
    is_active: bool
    created_at: datetime

    class Config:
        """Загрузка настроек."""

        from_attributes = True
