from sqlalchemy.orm import Session

from app.models.task import Task
from app.schemas.task import TaskCreate, TaskUpdate


def create_task(db: Session, task: TaskCreate, user_id: int) -> Task:
    """Создание задачи."""
    db_task = Task(
        title=task.title,
        description=task.description,
        status=task.status,
        parent_task_id=task.parent_task_id,
        user_id=user_id,
    )
    db.add(db_task)
    db.commit()
    db.refresh(db_task)
    return db_task


def get_task_by_id(db: Session, task_id: int) -> Task:
    """Получение задачи по ID."""
    return db.query(Task).filter(Task.id == task_id).first()


def get_tasks_by_user(
    db: Session, user_id: int, skip: int = 0, limit: int = 10
) -> list[Task]:
    """Получение задач пользователя."""
    return (
        db.query(Task).filter(Task.user_id == user_id).offset(skip).limit(limit).all()
    )


def update_task(db: Session, task_id: int, task_update: TaskUpdate) -> Task | None:
    """Обновление задачи."""
    db_task = get_task_by_id(db, task_id)
    if not db_task:
        return None
    for field, value in task_update.model_dump(exclude_unset=True).items():
        setattr(db_task, field, value)
    db.commit()
    db.refresh(db_task)
    return db_task


def delete_task(db: Session, task_id: int) -> bool:
    """Удаление задачи."""
    db_task = get_task_by_id(db, task_id)
    if not db_task:
        return False
    db.delete(db_task)
    db.commit()
    return True
