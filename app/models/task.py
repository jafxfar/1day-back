from sqlalchemy import Column, Integer, String, Boolean, DateTime, ForeignKey, Enum
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
import enum
from app.database import Base


class TaskPriority(enum.Enum):
    """
    Приоритет задачи
    """
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"


class TaskStatus(enum.Enum):
    """
    Статус задачи
    """
    TODO = "todo"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"


class Task(Base):
    """
    Модель задачи
    """
    __tablename__ = "tasks"
    
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(255), nullable=False)
    description = Column(String(500), nullable=True)
    
    # Статус и приоритет
    status = Column(Enum(TaskStatus), default=TaskStatus.TODO, nullable=False)
    priority = Column(Enum(TaskPriority), default=TaskPriority.MEDIUM, nullable=False)
    
    # Флаг завершения
    is_completed = Column(Boolean, default=False, nullable=False)
    
    # Даты
    due_date = Column(DateTime(timezone=True), nullable=True)
    completed_at = Column(DateTime(timezone=True), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Внешний ключ на пользователя
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    
    # Связь с пользователем
    owner = relationship("User", back_populates="tasks")
    
    def __repr__(self):
        return f"<Task(id={self.id}, title={self.title[:20]}, status={self.status.value})>"