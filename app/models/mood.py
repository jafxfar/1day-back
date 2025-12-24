from sqlalchemy import Column, Integer, String, Date, DateTime, ForeignKey, Enum, Text
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
import enum
from app.database import Base


class MoodLevel(enum.Enum):
    """
    Уровень настроения (1-5)
    """
    VERY_BAD = 1
    BAD = 2
    NEUTRAL = 3
    GOOD = 4
    EXCELLENT = 5


class Mood(Base):
    """
    Модель настроения пользователя за день
    """
    __tablename__ = "moods"
    
    id = Column(Integer, primary_key=True, index=True)
    
    # Уровень настроения (1-5)
    mood_level = Column(Enum(MoodLevel), nullable=False)
    
    # Дата, за которую фиксируется настроение
    mood_date = Column(Date, nullable=False, index=True)
    
    # Опциональная заметка к настроению
    note = Column(Text, nullable=True)
    
    # Даты создания и обновления
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Внешний ключ на пользователя
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    
    # Связь с пользователем
    owner = relationship("User", back_populates="moods")
    
    def __repr__(self):
        return f"<Mood(id={self.id}, date={self.mood_date}, level={self.mood_level.value})>"