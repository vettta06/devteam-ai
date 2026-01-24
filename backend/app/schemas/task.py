from datetime import datetime
from typing import Optional

from pydantic import BaseModel


class TaskBase(BaseModel):
    """Задача."""

    title: str
    description: Optional[str] = None
    status: str = "pending"
    parent_task_id: Optional[int] = None


class TaskCreate(TaskBase):
    """Создание задачи."""

    pass


class TaskRead(TaskBase):
    """Отображение задачи."""

    id: int
    user_id: int
    created_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class TaskUpdate(BaseModel):
    """Обновление задачи."""

    title: Optional[str] = None
    description: Optional[str] = None
    status: Optional[str] = None
