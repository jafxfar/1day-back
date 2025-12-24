from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional


class NoteBase(BaseModel):
    """
    Базовая схема заметки
    """
    title: str = Field(..., min_length=1, max_length=255)
    content: str = Field(..., min_length=1)


class NoteCreate(NoteBase):
    """
    Схема для создания заметки
    """
    pass


class NoteUpdate(BaseModel):
    """
    Схема для обновления заметки
    """
    title: Optional[str] = Field(None, min_length=1, max_length=255)
    content: Optional[str] = Field(None, min_length=1)


class NoteInDB(NoteBase):
    """
    Схема заметки в БД
    """
    id: int
    user_id: int
    created_at: datetime
    updated_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True


class Note(NoteInDB):
    """
    Схема для возврата заметки
    """
    pass