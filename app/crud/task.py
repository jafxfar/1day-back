from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import datetime
from app.models.task import Task, TaskStatus
from app.schemas.task import TaskCreate, TaskUpdate


def get_task(db: Session, task_id: int, user_id: int) -> Optional[Task]:
    """
    Получить задачу по ID
    """
    return db.query(Task).filter(
        Task.id == task_id,
        Task.user_id == user_id
    ).first()


def get_tasks(db: Session, user_id: int, skip: int = 0, limit: int = 100) -> List[Task]:
    """
    Получить список задач пользователя с пагинацией
    """
    return db.query(Task).filter(
        Task.user_id == user_id
    ).order_by(Task.created_at.desc()).offset(skip).limit(limit).all()


def get_tasks_by_status(db: Session, user_id: int, status: TaskStatus, skip: int = 0, limit: int = 100) -> List[Task]:
    """
    Получить задачи по статусу
    """
    return db.query(Task).filter(
        Task.user_id == user_id,
        Task.status == status
    ).order_by(Task.created_at.desc()).offset(skip).limit(limit).all()


def get_completed_tasks(db: Session, user_id: int, skip: int = 0, limit: int = 100) -> List[Task]:
    """
    Получить завершенные задачи
    """
    return db.query(Task).filter(
        Task.user_id == user_id,
        Task.is_completed == True
    ).order_by(Task.completed_at.desc()).offset(skip).limit(limit).all()


def create_task(db: Session, task: TaskCreate, user_id: int) -> Task:
    """
    Создать новую задачу
    """
    db_task = Task(
        **task.model_dump(),
        user_id=user_id
    )
    db.add(db_task)
    db.commit()
    db.refresh(db_task)
    return db_task


def update_task(db: Session, task_id: int, task: TaskUpdate, user_id: int) -> Optional[Task]:
    """
    Обновить задачу
    """
    db_task = get_task(db, task_id, user_id)
    if not db_task:
        return None
    
    # Обновляем только переданные поля
    update_data = task.model_dump(exclude_unset=True)
    
    # Если задача помечена как завершенная, устанавливаем время завершения
    if "is_completed" in update_data and update_data["is_completed"]:
        update_data["completed_at"] = datetime.now()
        update_data["status"] = TaskStatus.COMPLETED
    
    for field, value in update_data.items():
        setattr(db_task, field, value)
    
    db.commit()
    db.refresh(db_task)
    return db_task


def delete_task(db: Session, task_id: int, user_id: int) -> bool:
    """
    Удалить задачу
    """
    db_task = get_task(db, task_id, user_id)
    if not db_task:
        return False
    
    db.delete(db_task)
    db.commit()
    return True


def mark_task_completed(db: Session, task_id: int, user_id: int) -> Optional[Task]:
    """
    Пометить задачу как завершенную
    """
    db_task = get_task(db, task_id, user_id)
    if not db_task:
        return None
    
    setattr(db_task, "is_completed", True)
    setattr(db_task, "completed_at", datetime.now())
    setattr(db_task, "status", TaskStatus.COMPLETED)
    
    db.commit()
    db.refresh(db_task)
    return db_task