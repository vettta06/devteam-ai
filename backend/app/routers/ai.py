from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.orm import Session

from app.agents.project_manager import project_manager_agent
from app.core.auth import get_current_user
from app.database import get_db
from app.models.task import Subtask, Task
from app.models.user import User

router = APIRouter()


class TaskRequest(BaseModel):
    task: str


@router.post("/tasks/{task_id}/split")
async def split_task_into_subtasks(
    task_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    task = (
        db.query(Task)
        .filter(Task.id == task_id, Task.owner_id == current_user.id)
        .first()
    )
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    result = await project_manager_agent(f"{task.title}: {task.description}")
    for sub in result["subtasks"]:
        db_sub = Subtask(
            title=sub["title"], description=sub["description"], task_id=task_id
        )
        db.add(db_sub)
    db.commit()
    return result
