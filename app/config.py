from pydantic_settings import BaseSettings, SettingsConfigDict
from typing import Optional
from urllib.parse import quote_plus
import os
from pathlib import Path


class Settings(BaseSettings):
    """
    Настройки приложения
    Значения загружаются из переменных окружения или .env файла
    """
    
    # Настройки приложения
    PROJECT_NAME: str = "Diary Tracker API"
    VERSION: str = "1.0.0"
    API_V1_STR: str = "/api/v1"
    
    # Настройки базы данных MySQL
    MYSQL_USER: str = "root"
    MYSQL_PASSWORD: str = ""
    MYSQL_SERVER: str = "localhost"
    MYSQL_PORT: str = "3306"
    MYSQL_DB: str = "1day_db"
    
    # Формирование DATABASE_URL
    @property
    def DATABASE_URL(self) -> str:
        # MySQL URL
        if self.MYSQL_PASSWORD:
            return f"mysql+pymysql://{self.MYSQL_USER}:{self.MYSQL_PASSWORD}@{self.MYSQL_SERVER}:{self.MYSQL_PORT}/{self.MYSQL_DB}?charset=utf8mb4"
        else:
            return f"mysql+pymysql://{self.MYSQL_USER}@{self.MYSQL_SERVER}:{self.MYSQL_PORT}/{self.MYSQL_DB}?charset=utf8mb4"
    
    # Настройки безопасности (для будущей авторизации в MVP)
    SECRET_KEY: str = "your-secret-key-change-in-production"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    
    # Настройки CORS
    BACKEND_CORS_ORIGINS: list = ["http://localhost:3000", "http://localhost:8000"]
    
    model_config = SettingsConfigDict(
        env_file=str(Path(__file__).parent.parent / ".env"),
        case_sensitive=True
    )


# Создаём экземпляр настроек
settings = Settings()