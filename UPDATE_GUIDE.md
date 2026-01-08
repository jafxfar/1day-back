# Обновление Backend с поддержкой привычек

## Что добавлено

✅ **Новая функциональность: Habits (Привычки)**

### Новые модели базы данных:
- `Habit` - Шаблон привычки (ежедневная медитация, чтение и т.д.)
- `HabitCompletion` - Факты выполнения привычки

### Новые API эндпоинты:
- `POST /api/v1/habits/` - Создать привычку
- `GET /api/v1/habits/` - Список привычек
- `GET /api/v1/habits/{id}` - Получить привычку
- `PUT /api/v1/habits/{id}` - Обновить привычку
- `DELETE /api/v1/habits/{id}` - Удалить привычку
- `POST /api/v1/habits/{id}/complete` - Отметить как выполненную
- `DELETE /api/v1/habits/completions/{id}` - Отменить выполнение
- `GET /api/v1/habits/{id}/completions` - История выполнений
- `GET /api/v1/habits/{id}/streak` - Статистика серий

### Обновленные эндпоинты:
- `GET /api/v1/moods/date/{date}` - Теперь включает привычки за день

## Как обновить Docker

### Вариант 1: Обновить только backend (быстро)
```bash
cd /c/Users/ASUS/Desktop/1day
docker-compose up -d --build backend
```

### Вариант 2: Полная пересборка
```bash
cd /c/Users/ASUS/Desktop/1day
docker-compose down
docker-compose build --no-cache backend
docker-compose up -d
```

## Обновление базы данных

При первом запуске обновленного backend автоматически создадутся новые таблицы:
- `habits`
- `habit_completions`

SQLAlchemy создаст их автоматически при старте приложения.

## Проверка работы

После обновления проверьте:

1. **Backend запустился:**
```bash
docker-compose logs backend
```

2. **API документация доступна:**
```
http://localhost:8000/api/v1/docs
```

3. **Новые эндпоинты появились:**
Откройте Swagger UI и найдите раздел "habits"

## Примеры использования

### 1. Создать привычку "Утренняя медитация"
```bash
curl -X POST "http://localhost:8000/api/v1/habits/?user_id=1" \
  -H "Content-Type: application/json" \
  -d '{
    "title": "5 минут медитации",
    "frequency": "daily",
    "target_time": "07:00:00",
    "duration_minutes": 5,
    "color": "#FF5733"
  }'
```

### 2. Получить активность за сегодня (с привычками)
```bash
curl "http://localhost:8000/api/v1/moods/date/$(date +%Y-%m-%d)?user_id=1"
```

Ответ будет включать:
- Настроение
- Задачи
- Заметки
- **Привычки** (новое!)

## Структура данных привычки

```json
{
  "habit_id": 1,
  "title": "5 минут медитации",
  "description": "Утренняя медитация",
  "target_time": "07:00:00",
  "duration_minutes": 5,
  "color": "#FF5733",
  "is_completed": true,
  "completion_id": 1,
  "completion_note": "Отличная сессия!"
}
```

## Типы повторений

- **daily** - Каждый день
- **weekly** - Определенные дни недели (массив: [0,2,4] = Пн, Ср, Пт)
- **custom** - Через N дней

## Troubleshooting

### Проблема: Таблицы не создались
```bash
# Перезапустите backend
docker-compose restart backend
```

### Проблема: Ошибка импорта моделей
```bash
# Полная пересборка
docker-compose down
docker volume rm 1day_mysql_data  # ВНИМАНИЕ: удалит все данные!
docker-compose up -d
```

### Проверка логов
```bash
docker-compose logs -f backend
```

## Frontend Integration

На фронтенде теперь можно:

1. Отображать привычки в календаре
2. Отмечать выполнение одним кликом
3. Показывать streak (серии выполнений)
4. Визуализировать прогресс

Пример запроса для получения дня с привычками:
```javascript
const response = await fetch(`/api/v1/moods/date/2026-01-08?user_id=1`);
const data = await response.json();

// data.habits содержит все привычки за день
data.habits.forEach(habit => {
  console.log(habit.title, habit.is_completed);
});
```
