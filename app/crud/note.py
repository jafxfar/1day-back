from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import datetime, date
from app.models.note import Note
from app.schemas.note import NoteCreate, NoteUpdate


def get_note(db: Session, note_id: int, user_id: int) -> Optional[Note]:
    """
    Получить заметку по ID
    """
    return db.query(Note).filter(
        Note.id == note_id,
        Note.user_id == user_id
    ).first()


def get_notes(db: Session, user_id: int, skip: int = 0, limit: int = 100) -> List[Note]:
    """
    Получить список заметок пользователя с пагинацией
    """
    return db.query(Note).filter(
        Note.user_id == user_id
    ).offset(skip).limit(limit).all()


def create_note(db: Session, note: NoteCreate, user_id: int) -> Note:
    """
    Создать новую заметку
    """
    db_note = Note(
        **note.model_dump(),
        user_id=user_id
    )
    db.add(db_note)
    db.commit()
    db.refresh(db_note)
    return db_note


def update_note(db: Session, note_id: int, note: NoteUpdate, user_id: int) -> Optional[Note]:
    """
    Обновить заметку
    """
    db_note = get_note(db, note_id, user_id)
    if not db_note:
        return None
    
    # Обновляем только переданные поля
    update_data = note.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(db_note, field, value)
    
    db.commit()
    db.refresh(db_note)
    return db_note


def delete_note(db: Session, note_id: int, user_id: int) -> bool:
    """
    Удалить заметку
    """
    db_note = get_note(db, note_id, user_id)
    if not db_note:
        return False
    
    db.delete(db_note)
    db.commit()
    return True


def search_notes(db: Session, user_id: int, query: str, skip: int = 0, limit: int = 100) -> List[Note]:
    """
    Поиск заметок по заголовку или содержимому
    """
    search_pattern = f"%{query}%"
    return db.query(Note).filter(
        Note.user_id == user_id,
        (Note.title.ilike(search_pattern) | Note.content.ilike(search_pattern))
    ).offset(skip).limit(limit).all()


def get_notes_by_date(db: Session, user_id: int, target_date: date) -> List[Note]:
    """
    Получить заметки, созданные в определенную дату
    """
    start_datetime = datetime.combine(target_date, datetime.min.time())
    end_datetime = datetime.combine(target_date, datetime.max.time())
    
    return db.query(Note).filter(
        Note.user_id == user_id,
        Note.created_at >= start_datetime,
        Note.created_at <= end_datetime
    ).order_by(Note.created_at.desc()).all()