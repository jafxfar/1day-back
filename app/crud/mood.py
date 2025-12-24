from sqlalchemy.orm import Session
from sqlalchemy import func
from typing import List, Optional
from datetime import date, datetime, timedelta
from app.models.mood import Mood, MoodLevel
from app.schemas.mood import MoodCreate, MoodUpdate


def get_mood(db: Session, mood_id: int, user_id: int) -> Optional[Mood]:
    """
    Получить запись настроения по ID
    """
    return db.query(Mood).filter(
        Mood.id == mood_id,
        Mood.user_id == user_id
    ).first()


def get_mood_by_date(db: Session, user_id: int, mood_date: date) -> Optional[Mood]:
    """
    Получить настроение за конкретную дату
    """
    return db.query(Mood).filter(
        Mood.user_id == user_id,
        Mood.mood_date == mood_date
    ).first()


def get_moods(db: Session, user_id: int, skip: int = 0, limit: int = 100) -> List[Mood]:
    """
    Получить список записей настроения пользователя
    """
    return db.query(Mood).filter(
        Mood.user_id == user_id
    ).order_by(Mood.mood_date.desc()).offset(skip).limit(limit).all()


def get_moods_by_date_range(db: Session, user_id: int, start_date: date, end_date: date) -> List[Mood]:
    """
    Получить записи настроения за период
    """
    return db.query(Mood).filter(
        Mood.user_id == user_id,
        Mood.mood_date >= start_date,
        Mood.mood_date <= end_date
    ).order_by(Mood.mood_date.asc()).all()


def get_moods_by_month(db: Session, user_id: int, year: int, month: int) -> List[Mood]:
    """
    Получить записи настроения за конкретный месяц
    """
    from calendar import monthrange
    
    # Получаем первый и последний день месяца
    first_day = date(year, month, 1)
    last_day_num = monthrange(year, month)[1]
    last_day = date(year, month, last_day_num)
    
    return db.query(Mood).filter(
        Mood.user_id == user_id,
        Mood.mood_date >= first_day,
        Mood.mood_date <= last_day
    ).order_by(Mood.mood_date.asc()).all()


def create_mood(db: Session, mood: MoodCreate, user_id: int) -> Mood:
    """
    Создать новую запись настроения
    """
    # Проверяем, есть ли уже запись за эту дату
    existing_mood = get_mood_by_date(db, user_id, mood.mood_date)
    if existing_mood:
        # Обновляем существующую запись
        for field, value in mood.model_dump().items():
            setattr(existing_mood, field, value)
        db.commit()
        db.refresh(existing_mood)
        return existing_mood
    
    # Создаем новую запись
    db_mood = Mood(
        **mood.model_dump(),
        user_id=user_id
    )
    db.add(db_mood)
    db.commit()
    db.refresh(db_mood)
    return db_mood


def update_mood(db: Session, mood_id: int, mood: MoodUpdate, user_id: int) -> Optional[Mood]:
    """
    Обновить запись настроения
    """
    db_mood = get_mood(db, mood_id, user_id)
    if not db_mood:
        return None
    
    # Обновляем только переданные поля
    update_data = mood.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(db_mood, field, value)
    
    db.commit()
    db.refresh(db_mood)
    return db_mood


def delete_mood(db: Session, mood_id: int, user_id: int) -> bool:
    """
    Удалить запись настроения
    """
    db_mood = get_mood(db, mood_id, user_id)
    if not db_mood:
        return False
    
    db.delete(db_mood)
    db.commit()
    return True


def get_mood_statistics(db: Session, user_id: int, days: int = 30) -> dict:
    """
    Получить статистику настроения за последние N дней
    """
    end_date = date.today()
    start_date = end_date - timedelta(days=days)
    
    moods = get_moods_by_date_range(db, user_id, start_date, end_date)
    
    if not moods:
        return {
            "average_mood": 0,
            "total_records": 0,
            "mood_distribution": {},
            "best_day": None,
            "worst_day": None
        }
    
    # Вычисляем среднее настроение
    mood_values = [mood.mood_level.value for mood in moods]
    average_mood = sum(mood_values) / len(mood_values)
    
    # Распределение настроений
    mood_distribution = {}
    for mood in moods:
        level_name = mood.mood_level.name
        mood_distribution[level_name] = mood_distribution.get(level_name, 0) + 1
    
    # Лучший и худший день
    best_mood = max(moods, key=lambda m: m.mood_level.value)
    worst_mood = min(moods, key=lambda m: m.mood_level.value)
    
    return {
        "average_mood": round(average_mood, 2),
        "total_records": len(moods),
        "mood_distribution": mood_distribution,
        "best_day": best_mood.mood_date,
        "worst_day": worst_mood.mood_date
    }