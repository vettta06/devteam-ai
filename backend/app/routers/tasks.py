from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.core.auth import get_current_user
from app.crud.task import (
    create_task,
    delete_task,
    get_task_by_id,
    get_tasks_by_user,
    update_task,
)
from app.database import get_db
from app.models.user import User
from app.schemas.task import TaskCreate, TaskRead, TaskUpdate

router = APIRouter()


@router.post("/", response_model=TaskRead)
async def create_new_task(
    task: TaskCreate,
    cur_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Создание задачи."""
    db_task = create_task(db=db, task=task, user_id=cur_user.id)
    return TaskRead.model_validate(db_task)


@router.get("/{task_id}", response_model=TaskRead)
async def read_task(
    task_id: int,
    cur_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Получение задачи по ID."""
    db_task = get_task_by_id(db, task_id=task_id)
    if not db_task:
        raise HTTPException(status_code=404, detail="Task not found")
    if db_task.user_id != cur_user.id:
        raise HTTPException(status_code=403, detail="Not enough permissions")
    return TaskRead.model_validate(db_task)


@router.get("/", response_model=list[TaskRead])
async def read_user_tasks(
    skip: int = 0,
    limit: int = 10,
    cur_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Получение всех задач пользователя."""
    tasks = get_tasks_by_user(db, user_id=cur_user.id, skip=skip, limit=limit)
    return [TaskRead.model_validate(task) for task in tasks]


@router.put("/{task_id}", response_model=TaskRead)
async def update__cur_task(
    task_id: int,
    task_update: TaskUpdate,
    cur_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Обновление задачи."""
    db_task = get_task_by_id(db, task_id=task_id)
    if not db_task:
        raise HTTPException(status_code=404, detail="task not found")
    if db_task.user_id != cur_user.id:
        raise HTTPException(status_code=403, detail="Not enouhg permissions")
    updated_task = update_task(db, task_id=task_id, task_update=task_update)
    return TaskRead.model_validate(updated_task)


@router.delete("/{task_id}")
async def delete__cur_task(
    task_id: int,
    cur_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Удаление задачи."""
    db_task = get_task_by_id(db, task_id=task_id)
    if not db_task:
        raise HTTPException(status_code=404, detail="task not found")
    if db_task.user_id != cur_user.id:
        raise HTTPException(status_code=403, detail="Not enouhg permissions")
    success = delete_task(db, task_id=task_id)
    if not success:
        raise HTTPException(status_code=404, detail="Task not found")
    return {"message": "Task deleted successfully"}
