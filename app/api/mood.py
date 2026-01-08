from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from typing import List, Optional, Union
from datetime import date
from app.database import get_db
from app.schemas.mood import Mood, MoodCreate, MoodUpdate
from app.schemas.daily_activity import DailyActivity, HabitWithCompletion
from app.crud import mood as crud_mood
from app.crud import task as crud_task
from app.crud import note as crud_note
from app.crud import habit as crud_habit
from pydantic import BaseModel


class MoodNotFoundResponse(BaseModel):
    """
    Ответ когда запись о настроении не найдена
    """
    message: str
    date: date

router = APIRouter(
    prefix="/moods",
    tags=["moods"]
)


@router.post("/", response_model=Mood, status_code=status.HTTP_201_CREATED)
def create_mood(
    mood: MoodCreate,
    user_id: int,
    db: Session = Depends(get_db)
):
    """
    Создать запись о настроении
    """
    return crud_mood.create_mood(db=db, mood=mood, user_id=user_id)


@router.get("/", response_model=List[Mood])
def read_moods(
    user_id: int,
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db)
):
    """
    Получить список записей о настроении пользователя
    """
    return crud_mood.get_moods(db, user_id=user_id, skip=skip, limit=limit)


@router.get("/today", response_model=Union[Mood, MoodNotFoundResponse])
def read_today_mood(
    user_id: int,
    db: Session = Depends(get_db)
):
    """
    Получить настроение пользователя за сегодняшний день
    """
    from datetime import date as date_cls
    today = date_cls.today()
    db_mood = crud_mood.get_mood_by_date(db, user_id=user_id, mood_date=today)
    if db_mood is None:
        return MoodNotFoundResponse(
            message="Настроение на сегодня еще не отмечено",
            date=today
        )
    return db_mood


@router.get("/date/{mood_date}", response_model=DailyActivity)
def read_daily_activity(
    mood_date: date,
    user_id: int,
    db: Session = Depends(get_db)
):
    """
    Получить полную активность пользователя за конкретную дату:
    - Настроение
    - Задачи
    - Заметки
    - Привычки
    """
    # Получаем настроение за день
    db_mood = crud_mood.get_mood_by_date(db, user_id=user_id, mood_date=mood_date)
    
    # Получаем задачи за день
    db_tasks = crud_task.get_tasks_by_date(db, user_id=user_id, target_date=mood_date)
    
    # Получаем заметки за день
    db_notes = crud_note.get_notes_by_date(db, user_id=user_id, target_date=mood_date)
    
    # Получаем привычки за день с информацией о выполнении
    habits_data = crud_habit.get_habits_for_date(db, user_id=user_id, target_date=mood_date)
    
    # Преобразуем в нужный формат
    habits_list = []
    for item in habits_data:
        habit = item["habit"]
        completion = item["completion"]
        habits_list.append(HabitWithCompletion(
            habit_id=habit.id,
            title=habit.title,
            description=habit.description,
            target_time=habit.target_time.isoformat() if habit.target_time else None,
            duration_minutes=habit.duration_minutes,
            color=habit.color,
            is_completed=item["is_completed"],
            completion_id=completion.id if completion else None,
            completion_note=completion.note if completion else None
        ))
    
    # Формируем ответ (Pydantic автоматически преобразует ORM модели в схемы)
    return DailyActivity(
        date=mood_date,
        mood=db_mood,
        tasks=db_tasks,
        notes=db_notes,
        habits=habits_list
    )


@router.get("/month/{year}/{month}", response_model=List[Mood])
def read_moods_by_month(
    year: int,
    month: int,
    user_id: int,
    db: Session = Depends(get_db)
):
    """
    Получить записи о настроении за конкретный месяц
    Для отображения календаря с цветовой палитрой настроения
    """
    if month < 1 or month > 12:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Month must be between 1 and 12"
        )
    
    if year < 1900 or year > 2100:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Year must be between 1900 and 2100"
        )
    
    return crud_mood.get_moods_by_month(db, user_id=user_id, year=year, month=month)


@router.get("/range/", response_model=List[Mood])
def read_moods_by_range(
    user_id: int,
    start_date: date = Query(..., description="Start date (YYYY-MM-DD)"),
    end_date: date = Query(..., description="End date (YYYY-MM-DD)"),
    db: Session = Depends(get_db)
):
    """
    Получить записи о настроении за период времени
    """
    if start_date > end_date:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Start date must be before end date"
        )
    
    return crud_mood.get_moods_by_date_range(db, user_id=user_id, start_date=start_date, end_date=end_date)


@router.get("/statistics/", response_model=dict)
def read_mood_statistics(
    user_id: int,
    days: int = Query(30, ge=1, le=365, description="Number of days for statistics"),
    db: Session = Depends(get_db)
):
    """
    Получить статистику настроения за последние N дней
    """
    return crud_mood.get_mood_statistics(db, user_id=user_id, days=days)


@router.get("/{mood_id}", response_model=Mood)
def read_mood(
    mood_id: int,
    user_id: int,
    db: Session = Depends(get_db)
):
    """
    Получить запись о настроении по ID
    """
    db_mood = crud_mood.get_mood(db, mood_id=mood_id, user_id=user_id)
    if db_mood is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Mood not found"
        )
    return db_mood


@router.put("/{mood_id}", response_model=Mood)
def update_mood(
    mood_id: int,
    mood: MoodUpdate,
    user_id: int,
    db: Session = Depends(get_db)
):
    """
    Обновить запись о настроении
    """
    db_mood = crud_mood.update_mood(db, mood_id=mood_id, mood=mood, user_id=user_id)
    if db_mood is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Mood not found"
        )
    return db_mood


@router.delete("/{mood_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_mood(
    mood_id: int,
    user_id: int,
    db: Session = Depends(get_db)
):
    """
    Удалить запись о настроении
    """
    success = crud_mood.delete_mood(db, mood_id=mood_id, user_id=user_id)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Mood not found"
        )
    return None
