from pydantic import BaseModel, Field
from datetime import datetime, time, date
from typing import Optional, List
from app.models.habit import HabitFrequency


# ===== Habit Schemas =====

class HabitBase(BaseModel):
    """
    Базовая схема привычки
    """
    title: str = Field(..., min_length=1, max_length=255)
    description: Optional[str] = Field(None, max_length=500)
    frequency: HabitFrequency = HabitFrequency.DAILY
    target_time: Optional[time] = None
    duration_minutes: Optional[int] = Field(None, ge=1, le=1440)  # от 1 минуты до 24 часов
    weekdays: Optional[List[int]] = Field(None, description="Дни недели для weekly: [0-6], где 0=Пн")
    custom_interval_days: Optional[int] = Field(None, ge=1, description="Интервал в днях для custom")
    is_active: bool = True
    color: Optional[str] = Field(None, pattern="^#[0-9A-Fa-f]{6}$")  # HEX цвет


class HabitCreate(HabitBase):
    """
    Схема для создания привычки
    """
    pass


class HabitUpdate(BaseModel):
    """
    Схема для обновления привычки
    """
    title: Optional[str] = Field(None, min_length=1, max_length=255)
    description: Optional[str] = Field(None, max_length=500)
    frequency: Optional[HabitFrequency] = None
    target_time: Optional[time] = None
    duration_minutes: Optional[int] = Field(None, ge=1, le=1440)
    weekdays: Optional[List[int]] = None
    custom_interval_days: Optional[int] = Field(None, ge=1)
    is_active: Optional[bool] = None
    color: Optional[str] = Field(None, pattern="^#[0-9A-Fa-f]{6}$")


class HabitInDB(HabitBase):
    """
    Схема привычки в БД
    """
    id: int
    user_id: int
    created_at: datetime
    updated_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True


class Habit(HabitInDB):
    """
    Схема для возврата привычки
    """
    pass


# ===== HabitCompletion Schemas =====

class HabitCompletionBase(BaseModel):
    """
    Базовая схема выполнения привычки
    """
    note: Optional[str] = Field(None, max_length=500)


class HabitCompletionCreate(HabitCompletionBase):
    """
    Схема для создания выполнения привычки
    """
    pass


class HabitCompletionInDB(HabitCompletionBase):
    """
    Схема выполнения привычки в БД
    """
    id: int
    habit_id: int
    completed_at: datetime
    
    class Config:
        from_attributes = True


class HabitCompletion(HabitCompletionInDB):
    """
    Схема для возврата выполнения привычки
    """
    pass


# ===== Extended Schemas для удобного отображения =====

class HabitWithStreak(Habit):
    """
    Привычка с информацией о streak (серии выполнений)
    """
    current_streak: int = 0
    longest_streak: int = 0
    total_completions: int = 0
    completion_rate: float = 0.0  # Процент выполнения за все время


class HabitForDate(Habit):
    """
    Привычка для конкретной даты с информацией о выполнении
    """
    is_completed_today: bool = False
    completion_id: Optional[int] = None
    completion_note: Optional[str] = None
    completed_at: Optional[datetime] = None
