from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from app.database import get_db
from app.schemas.task import Task, TaskCreate, TaskUpdate
from app.models.task import TaskStatus
from app.crud import task as crud_task

router = APIRouter(
    prefix="/tasks",
    tags=["tasks"]
)


@router.post("/", response_model=Task, status_code=status.HTTP_201_CREATED)
def create_task(
    task: TaskCreate,
    user_id: int,
    db: Session = Depends(get_db)
):
    """
    Создать новую задачу
    """
    return crud_task.create_task(db=db, task=task, user_id=user_id)


@router.get("/", response_model=List[Task])
def read_tasks(
    user_id: int,
    skip: int = 0,
    limit: int = 100,
    status_filter: Optional[TaskStatus] = None,
    db: Session = Depends(get_db)
):
    """
    Получить список задач пользователя с возможностью фильтрации по статусу
    """
    if status_filter:
        tasks = crud_task.get_tasks_by_status(
            db, user_id=user_id, status=status_filter, skip=skip, limit=limit
        )
    else:
        tasks = crud_task.get_tasks(db, user_id=user_id, skip=skip, limit=limit)
    return tasks


@router.get("/completed", response_model=List[Task])
def read_completed_tasks(
    user_id: int,
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db)
):
    """
    Получить завершенные задачи
    """
    return crud_task.get_completed_tasks(db, user_id=user_id, skip=skip, limit=limit)


@router.get("/{task_id}", response_model=Task)
def read_task(
    task_id: int,
    user_id: int,
    db: Session = Depends(get_db)
):
    """
    Получить задачу по ID
    """
    db_task = crud_task.get_task(db, task_id=task_id, user_id=user_id)
    if db_task is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Task not found"
        )
    return db_task


@router.put("/{task_id}", response_model=Task)
def update_task(
    task_id: int,
    task: TaskUpdate,
    user_id: int,
    db: Session = Depends(get_db)
):
    """
    Обновить задачу
    """
    db_task = crud_task.update_task(db, task_id=task_id, task=task, user_id=user_id)
    if db_task is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Task not found"
        )
    return db_task


@router.delete("/{task_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_task(
    task_id: int,
    user_id: int,
    db: Session = Depends(get_db)
):
    """
    Удалить задачу
    """
    success = crud_task.delete_task(db, task_id=task_id, user_id=user_id)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Task not found"
        )
    return None


@router.post("/{task_id}/complete", response_model=Task)
def mark_task_completed(
    task_id: int,
    user_id: int,
    db: Session = Depends(get_db)
):
    """
    Пометить задачу как завершенную
    """
    db_task = crud_task.mark_task_completed(db, task_id=task_id, user_id=user_id)
    if db_task is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Task not found"
        )
    return db_task
