from datetime import datetime

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
        """Загрузка настроек."""

        from_attributes = True


class Config:
    orm_mode = True
