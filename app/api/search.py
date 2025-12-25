from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import datetime
from pydantic import BaseModel
from app.database import get_db
from app.models.note import Note
from app.models.task import Task
from sqlalchemy import or_

router = APIRouter(
    prefix="/search",
    tags=["search"]
)


class SearchResultItem(BaseModel):
    """
    Результат поиска - элемент
    """
    id: int
    type: str  # "note" или "task"
    title: str
    content: Optional[str] = None
    description: Optional[str] = None
    created_at: datetime
    updated_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True


class SearchResponse(BaseModel):
    """
    Ответ на поисковый запрос
    """
    query: str
    total_results: int
    notes_count: int
    tasks_count: int
    results: List[SearchResultItem]


@router.get("/", response_model=SearchResponse)
def search_content(
    user_id: int,
    q: str = Query(..., min_length=1, description="Поисковый запрос"),
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db)
):
    """
    Глобальный поиск по заметкам и задачам пользователя.
    Ищет по заголовкам, содержимому заметок и описанию задач.
    """
    search_pattern = f"%{q}%"
    
    # Поиск по заметкам
    notes = db.query(Note).filter(
        Note.user_id == user_id,
        or_(
            Note.title.ilike(search_pattern),
            Note.content.ilike(search_pattern)
        )
    ).all()
    
    # Поиск по задачам
    tasks = db.query(Task).filter(
        Task.user_id == user_id,
        or_(
            Task.title.ilike(search_pattern),
            Task.description.ilike(search_pattern)
        )
    ).all()
    
    # Формирование результатов
    results = []
    
    # Добавляем заметки
    for note in notes:
        results.append({
            "id": note.id,
            "type": "note",
            "title": note.title,
            "content": note.content,
            "description": None,
            "created_at": note.created_at,
            "updated_at": note.updated_at
        })
    
    # Добавляем задачи
    for task in tasks:
        results.append({
            "id": task.id,
            "type": "task",
            "title": task.title,
            "content": None,
            "description": task.description,
            "created_at": task.created_at,
            "updated_at": task.updated_at
        })
    
    # Сортируем по дате создания (новые первыми)
    results.sort(key=lambda x: x["created_at"], reverse=True)
    
    # Применяем пагинацию
    total_results = len(results)
    results = results[skip:skip + limit]
    
    # Преобразуем в модели Pydantic
    results = [SearchResultItem(**item) for item in results]
    
    return SearchResponse(
        query=q,
        total_results=total_results,
        notes_count=len(notes),
        tasks_count=len(tasks),
        results=results
    )
