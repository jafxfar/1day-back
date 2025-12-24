from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
from app.config import settings
from app.database import engine, Base

# Импорт моделей (необходимо для создания таблиц)
from app.models import User, Note, Task, Mood

# Импорт роутеров
from app.api import user, note, task, mood


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Управление жизненным циклом приложения
    """
    # Startup: создание таблиц при запуске
    print("🚀 Запуск приложения...")
    try:
        Base.metadata.create_all(bind=engine)
        print("✅ Таблицы базы данных созданы успешно")
    except Exception as e:
        print(f"⚠️ Ошибка при создании таблиц: {e}")
    
    yield
    
    # Shutdown: действия при остановке
    print("🛑 Остановка приложения...")


# Инициализация FastAPI приложения
app = FastAPI(
    lifespan=lifespan,
    title=settings.PROJECT_NAME,
    version=settings.VERSION,
    description="API для дневника с трекером задач и настроения",
    docs_url=f"{settings.API_V1_STR}/docs",
    redoc_url=f"{settings.API_V1_STR}/redoc",
    openapi_url=f"{settings.API_V1_STR}/openapi.json"
)

# Настройка CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.BACKEND_CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Корневой endpoint
@app.get("/")
async def root():
    """
    Корневой endpoint для проверки работы API
    """
    return {
        "message": "Diary Tracker API",
        "version": settings.VERSION,
        "docs": f"{settings.API_V1_STR}/docs"
    }


# Health check endpoint
@app.get("/health")
async def health_check():
    """
    Проверка работоспособности API
    """
    return {
        "status": "healthy",
        "service": settings.PROJECT_NAME
    }


# Подключение роутеров
app.include_router(user.router, prefix=f"{settings.API_V1_STR}")
app.include_router(note.router, prefix=f"{settings.API_V1_STR}")
app.include_router(task.router, prefix=f"{settings.API_V1_STR}")
app.include_router(mood.router, prefix=f"{settings.API_V1_STR}")


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8000,
        reload=True  # Автоперезагрузка при изменении кода (только для разработки)
    )