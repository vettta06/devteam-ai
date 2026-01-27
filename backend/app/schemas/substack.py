from pydantic import BaseModel


class SubtaskBase(BaseModel):
    """Подзадача."""

    title: str
    description: str
    status: str = "pending"


class SubtaskCreate(SubtaskBase):
    """Создание подзадачи."""

    pass


class SubtaskRead(SubtaskBase):
    """Получение задачи."""

    id: int
    task_id: int

    class Config:
        from_attributes = True
