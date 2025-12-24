from pydantic import BaseModel, Field
from datetime import datetime, date
from typing import Optional
from app.models.mood import MoodLevel


class MoodBase(BaseModel):
    """
    Базовая схема настроения
    """
    mood_level: MoodLevel
    mood_date: date
    note: Optional[str] = None


class MoodCreate(MoodBase):
    """
    Схема для создания записи настроения
    """
    pass


class MoodUpdate(BaseModel):
    """
    Схема для обновления записи настроения
    """
    mood_level: Optional[MoodLevel] = None
    mood_date: Optional[date] = None
    note: Optional[str] = None


class MoodInDB(MoodBase):
    """
    Схема настроения в БД
    """
    id: int
    user_id: int
    created_at: datetime
    updated_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True


class Mood(MoodInDB):
    """
    Схема для возврата настроения
    """
    pass


class MoodStats(BaseModel):
    """
    Схема для статистики настроения
    """
    average_mood: float
    total_records: int
    mood_distribution: dict
    best_day: Optional[date] = None
    worst_day: Optional[date] = None