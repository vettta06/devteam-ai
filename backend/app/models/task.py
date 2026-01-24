from sqlalchemy import Column, ForeignKey, Integer, String
from sqlalchemy.orm import relationship

from app.database import Base


class Task(Base):
    """Задача."""

    __tablename__ = "tasks"
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, nullable=False)
    description = Column(String, nullable=True)
    status = Column(String, default="pending")
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    parent_task_id = Column(Integer, ForeignKey("tasks.id"), nullable=True)
    owner = relationship("User", back_populates="tasks")
    subtasks = relationship("Task", back_populates="parent")
    parent = relationship("Task", remote_side=[id], back_populates="subtasks")
