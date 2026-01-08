from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import datetime, date, timedelta
from app.models.habit import Habit, HabitCompletion, HabitFrequency
from app.schemas.habit import HabitCreate, HabitUpdate, HabitCompletionCreate


# ===== Habit CRUD =====

def get_habit(db: Session, habit_id: int, user_id: int) -> Optional[Habit]:
    """
    Получить привычку по ID
    """
    return db.query(Habit).filter(
        Habit.id == habit_id,
        Habit.user_id == user_id
    ).first()


def get_habits(db: Session, user_id: int, skip: int = 0, limit: int = 100, active_only: bool = False) -> List[Habit]:
    """
    Получить список привычек пользователя
    """
    query = db.query(Habit).filter(Habit.user_id == user_id)
    
    if active_only:
        query = query.filter(Habit.is_active == True)
    
    return query.order_by(Habit.created_at.desc()).offset(skip).limit(limit).all()


def create_habit(db: Session, habit: HabitCreate, user_id: int) -> Habit:
    """
    Создать новую привычку
    """
    db_habit = Habit(
        **habit.model_dump(),
        user_id=user_id
    )
    db.add(db_habit)
    db.commit()
    db.refresh(db_habit)
    return db_habit


def update_habit(db: Session, habit_id: int, habit: HabitUpdate, user_id: int) -> Optional[Habit]:
    """
    Обновить привычку
    """
    db_habit = get_habit(db, habit_id, user_id)
    if not db_habit:
        return None
    
    # Обновляем только переданные поля
    update_data = habit.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(db_habit, field, value)
    
    db.commit()
    db.refresh(db_habit)
    return db_habit


def delete_habit(db: Session, habit_id: int, user_id: int) -> bool:
    """
    Удалить привычку
    """
    db_habit = get_habit(db, habit_id, user_id)
    if not db_habit:
        return False
    
    db.delete(db_habit)
    db.commit()
    return True


# ===== HabitCompletion CRUD =====

def get_completion(db: Session, completion_id: int) -> Optional[HabitCompletion]:
    """
    Получить выполнение привычки по ID
    """
    return db.query(HabitCompletion).filter(
        HabitCompletion.id == completion_id
    ).first()


def get_completions_for_habit(
    db: Session, 
    habit_id: int, 
    user_id: int,
    skip: int = 0, 
    limit: int = 100
) -> List[HabitCompletion]:
    """
    Получить все выполнения конкретной привычки
    """
    # Проверяем, что привычка принадлежит пользователю
    habit = get_habit(db, habit_id, user_id)
    if not habit:
        return []
    
    return db.query(HabitCompletion).filter(
        HabitCompletion.habit_id == habit_id
    ).order_by(HabitCompletion.completed_at.desc()).offset(skip).limit(limit).all()


def get_completions_by_date(
    db: Session, 
    user_id: int, 
    target_date: date
) -> List[HabitCompletion]:
    """
    Получить все выполнения привычек пользователя за определенную дату
    """
    start_datetime = datetime.combine(target_date, datetime.min.time())
    end_datetime = datetime.combine(target_date, datetime.max.time())
    
    # Получаем ID привычек пользователя
    habit_ids = db.query(Habit.id).filter(Habit.user_id == user_id).all()
    habit_ids = [h[0] for h in habit_ids]
    
    return db.query(HabitCompletion).filter(
        HabitCompletion.habit_id.in_(habit_ids),
        HabitCompletion.completed_at >= start_datetime,
        HabitCompletion.completed_at <= end_datetime
    ).all()


def complete_habit(
    db: Session, 
    habit_id: int, 
    user_id: int,
    completion: HabitCompletionCreate
) -> Optional[HabitCompletion]:
    """
    Отметить привычку как выполненную
    """
    # Проверяем, что привычка существует и принадлежит пользователю
    habit = get_habit(db, habit_id, user_id)
    if not habit:
        return None
    
    # Создаем запись о выполнении
    db_completion = HabitCompletion(
        habit_id=habit_id,
        note=completion.note
    )
    db.add(db_completion)
    db.commit()
    db.refresh(db_completion)
    return db_completion


def uncomplete_habit(db: Session, completion_id: int, user_id: int) -> bool:
    """
    Удалить запись о выполнении привычки
    """
    db_completion = get_completion(db, completion_id)
    if not db_completion:
        return False
    
    # Проверяем, что привычка принадлежит пользователю
    habit = db.query(Habit).filter(
        Habit.id == db_completion.habit_id,
        Habit.user_id == user_id
    ).first()
    if not habit:
        return False
    
    db.delete(db_completion)
    db.commit()
    return True


def get_habit_streak(db: Session, habit_id: int, user_id: int) -> dict:
    """
    Получить статистику streak (серии выполнений) для привычки
    """
    habit = get_habit(db, habit_id, user_id)
    if not habit:
        return {
            "current_streak": 0,
            "longest_streak": 0,
            "total_completions": 0
        }
    
    # Получаем все выполнения привычки
    completions = db.query(HabitCompletion).filter(
        HabitCompletion.habit_id == habit_id
    ).order_by(HabitCompletion.completed_at.desc()).all()
    
    if not completions:
        return {
            "current_streak": 0,
            "longest_streak": 0,
            "total_completions": 0
        }
    
    # Считаем текущий streak
    current_streak = 0
    today = date.today()
    check_date = today
    
    completion_dates = set(c.completed_at.date() for c in completions)
    
    # Для daily привычек
    if habit.frequency == HabitFrequency.DAILY:
        while check_date in completion_dates:
            current_streak += 1
            check_date -= timedelta(days=1)
    
    # Считаем самый длинный streak
    longest_streak = 0
    temp_streak = 0
    sorted_dates = sorted(completion_dates, reverse=True)
    
    for i, comp_date in enumerate(sorted_dates):
        if i == 0:
            temp_streak = 1
        else:
            prev_date = sorted_dates[i - 1]
            if habit.frequency == HabitFrequency.DAILY:
                if (prev_date - comp_date).days == 1:
                    temp_streak += 1
                else:
                    longest_streak = max(longest_streak, temp_streak)
                    temp_streak = 1
    
    longest_streak = max(longest_streak, temp_streak)
    
    return {
        "current_streak": current_streak,
        "longest_streak": longest_streak,
        "total_completions": len(completions)
    }


def get_habits_for_date(db: Session, user_id: int, target_date: date) -> List[dict]:
    """
    Получить все активные привычки для конкретной даты с информацией о выполнении
    """
    # Получаем все активные привычки пользователя
    habits = get_habits(db, user_id=user_id, active_only=True, limit=1000)
    
    # Получаем выполнения за эту дату
    completions = get_completions_by_date(db, user_id=user_id, target_date=target_date)
    completion_map = {c.habit_id: c for c in completions}
    
    result = []
    weekday = target_date.weekday()  # 0 = Понедельник
    
    for habit in habits:
        # Проверяем, должна ли привычка быть в этот день
        should_show = False
        
        if habit.frequency == HabitFrequency.DAILY:
            should_show = True
        elif habit.frequency == HabitFrequency.WEEKLY:
            if habit.weekdays and weekday in habit.weekdays:
                should_show = True
        elif habit.frequency == HabitFrequency.CUSTOM:
            # Для custom нужна более сложная логика
            # Пока просто показываем
            should_show = True
        
        if should_show:
            completion = completion_map.get(habit.id)
            result.append({
                "habit": habit,
                "is_completed": completion is not None,
                "completion": completion
            })
    
    return result
