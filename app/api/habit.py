from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from typing import List
from datetime import date
from app.database import get_db
from app.schemas.habit import (
    Habit, HabitCreate, HabitUpdate,
    HabitCompletion, HabitCompletionCreate,
    HabitWithStreak, HabitForDate
)
from app.crud import habit as crud_habit

router = APIRouter(
    prefix="/habits",
    tags=["habits"]
)


# ===== Habit Endpoints =====

@router.post("/", response_model=Habit, status_code=status.HTTP_201_CREATED)
def create_habit(
    habit: HabitCreate,
    user_id: int,
    db: Session = Depends(get_db)
):
    """
    Создать новую привычку
    """
    return crud_habit.create_habit(db=db, habit=habit, user_id=user_id)


@router.get("/", response_model=List[Habit])
def read_habits(
    user_id: int,
    active_only: bool = Query(False, description="Показывать только активные привычки"),
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db)
):
    """
    Получить список привычек пользователя
    """
    return crud_habit.get_habits(
        db, user_id=user_id, skip=skip, limit=limit, active_only=active_only
    )


@router.get("/{habit_id}", response_model=Habit)
def read_habit(
    habit_id: int,
    user_id: int,
    db: Session = Depends(get_db)
):
    """
    Получить привычку по ID
    """
    db_habit = crud_habit.get_habit(db, habit_id=habit_id, user_id=user_id)
    if db_habit is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Habit not found"
        )
    return db_habit


@router.put("/{habit_id}", response_model=Habit)
def update_habit(
    habit_id: int,
    habit: HabitUpdate,
    user_id: int,
    db: Session = Depends(get_db)
):
    """
    Обновить привычку
    """
    db_habit = crud_habit.update_habit(db, habit_id=habit_id, habit=habit, user_id=user_id)
    if db_habit is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Habit not found"
        )
    return db_habit


@router.delete("/{habit_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_habit(
    habit_id: int,
    user_id: int,
    db: Session = Depends(get_db)
):
    """
    Удалить привычку
    """
    success = crud_habit.delete_habit(db, habit_id=habit_id, user_id=user_id)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Habit not found"
        )
    return None


# ===== Habit Statistics =====

@router.get("/{habit_id}/streak", response_model=dict)
def read_habit_streak(
    habit_id: int,
    user_id: int,
    db: Session = Depends(get_db)
):
    """
    Получить статистику streak (серии выполнений) для привычки
    Возвращает текущую серию, самую длинную серию и общее количество выполнений
    """
    return crud_habit.get_habit_streak(db, habit_id=habit_id, user_id=user_id)


# ===== Habit Completion Endpoints =====

@router.post("/{habit_id}/complete", response_model=HabitCompletion, status_code=status.HTTP_201_CREATED)
def complete_habit(
    habit_id: int,
    user_id: int,
    db: Session = Depends(get_db),
    completion: HabitCompletionCreate = HabitCompletionCreate(note=None)
):
    """
    Отметить привычку как выполненную
    """
    db_completion = crud_habit.complete_habit(
        db, habit_id=habit_id, user_id=user_id, completion=completion
    )
    if db_completion is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Habit not found"
        )
    return db_completion


@router.delete("/completions/{completion_id}", status_code=status.HTTP_204_NO_CONTENT)
def uncomplete_habit(
    completion_id: int,
    user_id: int,
    db: Session = Depends(get_db)
):
    """
    Удалить запись о выполнении привычки (отменить выполнение)
    """
    success = crud_habit.uncomplete_habit(db, completion_id=completion_id, user_id=user_id)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Completion not found"
        )
    return None


@router.get("/{habit_id}/completions", response_model=List[HabitCompletion])
def read_habit_completions(
    habit_id: int,
    user_id: int,
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db)
):
    """
    Получить историю выполнений конкретной привычки
    """
    return crud_habit.get_completions_for_habit(
        db, habit_id=habit_id, user_id=user_id, skip=skip, limit=limit
    )


@router.get("/date/{target_date}/completions", response_model=List[HabitCompletion])
def read_completions_by_date(
    target_date: date,
    user_id: int,
    db: Session = Depends(get_db)
):
    """
    Получить все выполнения привычек за конкретную дату
    """
    return crud_habit.get_completions_by_date(db, user_id=user_id, target_date=target_date)
