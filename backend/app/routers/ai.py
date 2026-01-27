from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from app.agents.project_manager import project_manager_agent

router = APIRouter(prefix="/ai", tags=["AI"])


class TaskRequest(BaseModel):
    task: str


@router.post("/split-task")
async def split_task(request: TaskRequest):
    if not request.task.strip():
        raise HTTPException(status_code=400, detail="Task description is required")
    result = await project_manager_agent(request.task)
    return result
