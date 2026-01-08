from sqlalchemy import Column, Integer, String, Boolean, DateTime, ForeignKey, Enum, Time, JSON
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
import enum
from app.database import Base


class HabitFrequency(enum.Enum):
    """
    Частота выполнения привычки
    """
    DAILY = "daily"  # Каждый день
    WEEKLY = "weekly"  # Определенные дни недели
    CUSTOM = "custom"  # Кастомный интервал


class Habit(Base):
    """
    Модель привычки (шаблон)
    """
    __tablename__ = "habits"
    
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(255), nullable=False)
    description = Column(String(500), nullable=True)
    
    # Параметры повторения
    frequency = Column(Enum(HabitFrequency), default=HabitFrequency.DAILY, nullable=False)
    
    # Время выполнения (опционально, например "07:00")
    target_time = Column(Time, nullable=True)
    
    # Продолжительность в минутах (опционально)
    duration_minutes = Column(Integer, nullable=True)
    
    # Дни недели для weekly (JSON массив: [0,1,2,3,4,5,6] где 0=Понедельник)
    # Например: [0,2,4] = Пн, Ср, Пт
    weekdays = Column(JSON, nullable=True)
    
    # Кастомный интервал в днях для custom frequency
    custom_interval_days = Column(Integer, nullable=True)
    
    # Активна ли привычка
    is_active = Column(Boolean, default=True, nullable=False)
    
    # Цвет для отображения (опционально)
    color = Column(String(7), nullable=True)  # HEX цвет, например "#FF5733"
    
    # Даты
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Внешний ключ на пользователя
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    
    # Связи
    owner = relationship("User", back_populates="habits")
    completions = relationship("HabitCompletion", back_populates="habit", cascade="all, delete-orphan")
    
    def __repr__(self):
        return f"<Habit(id={self.id}, title={self.title[:20]}, frequency={self.frequency.value})>"


class HabitCompletion(Base):
    """
    Модель выполнения привычки (факт выполнения в конкретный день)
    """
    __tablename__ = "habit_completions"
    
    id = Column(Integer, primary_key=True, index=True)
    
    # Привычка
    habit_id = Column(Integer, ForeignKey("habits.id"), nullable=False)
    
    # Когда выполнено
    completed_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Заметка о выполнении (опционально)
    note = Column(String(500), nullable=True)
    
    # Связь с привычкой
    habit = relationship("Habit", back_populates="completions")
    
    def __repr__(self):
        return f"<HabitCompletion(id={self.id}, habit_id={self.habit_id}, completed_at={self.completed_at})>"
