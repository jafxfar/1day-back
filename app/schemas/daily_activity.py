from pydantic import BaseModel
from typing import Sequence, Optional
from datetime import date
from app.schemas.mood import Mood
from app.schemas.task import Task
from app.schemas.note import Note


class DailyActivity(BaseModel):
    """
    Схема для полной активности пользователя за день
    """
    date: date
    mood: Optional[Mood] = None
    tasks: Sequence[Task] = []
    notes: Sequence[Note] = []
    
    class Config:
        from_attributes = True


class DailyActivityNotFound(BaseModel):
    """
    Ответ когда активности за день не найдено
    """
    message: str
    date: date
