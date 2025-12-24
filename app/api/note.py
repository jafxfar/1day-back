from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from app.database import get_db
from app.schemas.note import Note, NoteCreate, NoteUpdate
from app.crud import note as crud_note

router = APIRouter(
    prefix="/notes",
    tags=["notes"]
)


@router.post("/", response_model=Note, status_code=status.HTTP_201_CREATED)
def create_note(
    note: NoteCreate,
    user_id: int,
    db: Session = Depends(get_db)
):
    """
    Создать новую заметку
    """
    return crud_note.create_note(db=db, note=note, user_id=user_id)


@router.get("/", response_model=List[Note])
def read_notes(
    user_id: int,
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db)
):
    """
    Получить список заметок пользователя
    """
    return crud_note.get_notes(db, user_id=user_id, skip=skip, limit=limit)


@router.get("/{note_id}", response_model=Note)
def read_note(
    note_id: int,
    user_id: int,
    db: Session = Depends(get_db)
):
    """
    Получить заметку по ID
    """
    db_note = crud_note.get_note(db, note_id=note_id, user_id=user_id)
    if db_note is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Note not found"
        )
    return db_note


@router.put("/{note_id}", response_model=Note)
def update_note(
    note_id: int,
    note: NoteUpdate,
    user_id: int,
    db: Session = Depends(get_db)
):
    """
    Обновить заметку
    """
    db_note = crud_note.update_note(db, note_id=note_id, note=note, user_id=user_id)
    if db_note is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Note not found"
        )
    return db_note


@router.delete("/{note_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_note(
    note_id: int,
    user_id: int,
    db: Session = Depends(get_db)
):
    """
    Удалить заметку
    """
    success = crud_note.delete_note(db, note_id=note_id, user_id=user_id)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Note not found"
        )
    return None


@router.get("/search/", response_model=List[Note])
def search_notes(
    user_id: int,
    query: str,
    db: Session = Depends(get_db)
):
    """
    Поиск заметок по содержимому
    """
    return crud_note.search_notes(db, user_id=user_id, query=query)
