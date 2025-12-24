from pydantic import BaseModel, EmailStr, Field
from datetime import datetime
from typing import Optional


class UserBase(BaseModel):
    """
    Базовая схема пользователя
    """
    email: EmailStr
    username: str = Field(..., min_length=3, max_length=50)


class UserCreate(UserBase):
    """
    Схема для создания пользователя
    """
    password: str = Field(..., min_length=6, max_length=72)


class UserUpdate(BaseModel):
    """
    Схема для обновления пользователя
    """
    email: Optional[EmailStr] = None
    username: Optional[str] = Field(None, min_length=3, max_length=50)
    password: Optional[str] = Field(None, min_length=6, max_length=72)


class UserInDB(UserBase):
    """
    Схема пользователя в БД
    """
    id: int
    created_at: datetime
    updated_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True


class User(UserInDB):
    """
    Схема для возврата пользователя (публичная информация)
    """
    pass