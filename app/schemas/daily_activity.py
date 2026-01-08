from pydantic import BaseModel
from typing import Sequence, Optional
from datetime import date
from app.schemas.mood import Mood
from app.schemas.task import Task
from app.schemas.note import Note
from app.schemas.habit import HabitForDate


class HabitWithCompletion(BaseModel):
    """
    Привычка с информацией о выполнении за конкретный день
    """
    habit_id: int
    title: str
    description: Optional[str] = None
    target_time: Optional[str] = None
    duration_minutes: Optional[int] = None
    color: Optional[str] = None
    is_completed: bool = False
    completion_id: Optional[int] = None
    completion_note: Optional[str] = None
    
    class Config:
        from_attributes = True


class DailyActivity(BaseModel):
    """
    Схема для полной активности пользователя за день
    """
    date: date
    mood: Optional[Mood] = None
    tasks: Sequence[Task] = []
    notes: Sequence[Note] = []
    habits: Sequence[HabitWithCompletion] = []
    
    class Config:
        from_attributes = True


class DailyActivityNotFound(BaseModel):
    """
    Ответ когда активности за день не найдено
    """
    message: str
    date: date
