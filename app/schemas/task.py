from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional
from app.models.task import TaskStatus, TaskPriority


class TaskBase(BaseModel):
    """
    Базовая схема задачи
    """
    title: str = Field(..., min_length=1, max_length=255)
    description: Optional[str] = Field(None, max_length=500)
    status: TaskStatus = TaskStatus.TODO
    priority: TaskPriority = TaskPriority.MEDIUM
    due_date: Optional[datetime] = None


class TaskCreate(TaskBase):
    """
    Схема для создания задачи
    """
    pass


class TaskUpdate(BaseModel):
    """
    Схема для обновления задачи
    """
    title: Optional[str] = Field(None, min_length=1, max_length=255)
    description: Optional[str] = Field(None, max_length=500)
    status: Optional[TaskStatus] = None
    priority: Optional[TaskPriority] = None
    is_completed: Optional[bool] = None
    due_date: Optional[datetime] = None


class TaskInDB(TaskBase):
    """
    Схема задачи в БД
    """
    id: int
    user_id: int
    is_completed: bool
    completed_at: Optional[datetime] = None
    created_at: datetime
    updated_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True


class Task(TaskInDB):
    """
    Схема для возврата задачи
    """
    pass