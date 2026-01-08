# API Документация: Привычки (Habits)

## Обзор

API для управления привычками позволяет пользователям создавать, отслеживать и анализировать свои ежедневные привычки.

## Типы повторений привычек

- **DAILY** - Каждый день
- **WEEKLY** - Определенные дни недели (например: Пн, Ср, Пт)
- **CUSTOM** - Кастомный интервал в днях

## Эндпоинты

### 1. Создать привычку
```http
POST /api/v1/habits/?user_id=1
Content-Type: application/json

{
  "title": "5 минут медитации",
  "description": "Утренняя медитация для ясности ума",
  "frequency": "daily",
  "target_time": "07:00:00",
  "duration_minutes": 5,
  "color": "#FF5733"
}
```

**Пример для weekly:**
```json
{
  "title": "Тренировка в зале",
  "frequency": "weekly",
  "weekdays": [0, 2, 4],  // Пн, Ср, Пт (0=Пн, 6=Вс)
  "target_time": "18:00:00",
  "duration_minutes": 60,
  "color": "#00FF00"
}
```

### 2. Получить все привычки пользователя
```http
GET /api/v1/habits/?user_id=1&active_only=true
```

**Ответ:**
```json
[
  {
    "id": 1,
    "title": "5 минут медитации",
    "description": "Утренняя медитация для ясности ума",
    "frequency": "daily",
    "target_time": "07:00:00",
    "duration_minutes": 5,
    "weekdays": null,
    "custom_interval_days": null,
    "is_active": true,
    "color": "#FF5733",
    "user_id": 1,
    "created_at": "2026-01-08T10:00:00Z",
    "updated_at": null
  }
]
```

### 3. Получить конкретную привычку
```http
GET /api/v1/habits/1?user_id=1
```

### 4. Обновить привычку
```http
PUT /api/v1/habits/1?user_id=1
Content-Type: application/json

{
  "title": "10 минут медитации",
  "duration_minutes": 10
}
```

### 5. Удалить привычку
```http
DELETE /api/v1/habits/1?user_id=1
```

### 6. Отметить привычку как выполненную
```http
POST /api/v1/habits/1/complete?user_id=1
Content-Type: application/json

{
  "note": "Отличная сессия медитации!"
}
```

**Ответ:**
```json
{
  "id": 1,
  "habit_id": 1,
  "completed_at": "2026-01-08T07:15:00Z",
  "note": "Отличная сессия медитации!"
}
```

### 7. Отменить выполнение привычки
```http
DELETE /api/v1/habits/completions/1?user_id=1
```

### 8. Получить историю выполнений привычки
```http
GET /api/v1/habits/1/completions?user_id=1&limit=30
```

**Ответ:**
```json
[
  {
    "id": 5,
    "habit_id": 1,
    "completed_at": "2026-01-08T07:15:00Z",
    "note": "Отличная сессия!"
  },
  {
    "id": 4,
    "habit_id": 1,
    "completed_at": "2026-01-07T07:10:00Z",
    "note": null
  }
]
```

### 9. Получить статистику streak (серии выполнений)
```http
GET /api/v1/habits/1/streak?user_id=1
```

**Ответ:**
```json
{
  "current_streak": 7,
  "longest_streak": 14,
  "total_completions": 45
}
```

### 10. Получить все выполнения за конкретную дату
```http
GET /api/v1/habits/date/2026-01-08/completions?user_id=1
```

### 11. Получить полную активность за день (включая привычки)
```http
GET /api/v1/moods/date/2026-01-08?user_id=1
```

**Ответ:**
```json
{
  "date": "2026-01-08",
  "mood": {
    "id": 1,
    "mood_level": 4,
    "note": "Отличный день!",
    ...
  },
  "tasks": [
    {
      "id": 1,
      "title": "Купить продукты",
      "status": "completed",
      ...
    }
  ],
  "notes": [
    {
      "id": 1,
      "title": "Дневниковая запись",
      "content": "Сегодня был продуктивный день",
      ...
    }
  ],
  "habits": [
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
    },
    {
      "habit_id": 2,
      "title": "10 минут чтения",
      "is_completed": false,
      "completion_id": null,
      "completion_note": null
    }
  ]
}
```

## Примеры использования

### Создание привычки "Ежедневное чтение"
```bash
curl -X POST "http://localhost:8000/api/v1/habits/?user_id=1" \
  -H "Content-Type: application/json" \
  -d '{
    "title": "10 минут чтения",
    "frequency": "daily",
    "duration_minutes": 10,
    "color": "#4CAF50"
  }'
```

### Отметить привычку как выполненную
```bash
curl -X POST "http://localhost:8000/api/v1/habits/1/complete?user_id=1" \
  -H "Content-Type: application/json" \
  -d '{
    "note": "Прочитал главу книги"
  }'
```

### Получить все привычки на сегодня
```bash
curl "http://localhost:8000/api/v1/moods/date/2026-01-08?user_id=1"
```

## Схема базы данных

### Таблица `habits`
- `id` - Идентификатор
- `title` - Название привычки
- `description` - Описание
- `frequency` - Частота (daily/weekly/custom)
- `target_time` - Целевое время выполнения
- `duration_minutes` - Продолжительность в минутах
- `weekdays` - Дни недели для weekly (JSON массив)
- `custom_interval_days` - Интервал для custom
- `is_active` - Активна ли привычка
- `color` - HEX цвет для отображения
- `user_id` - ID пользователя
- `created_at` - Дата создания
- `updated_at` - Дата обновления

### Таблица `habit_completions`
- `id` - Идентификатор
- `habit_id` - ID привычки
- `completed_at` - Время выполнения
- `note` - Заметка о выполнении

## Логика отображения привычек

При запросе `/api/v1/moods/date/{date}`:

1. **DAILY** привычки отображаются каждый день
2. **WEEKLY** привычки отображаются только в указанные дни недели
3. **CUSTOM** привычки отображаются согласно интервалу

Для каждой привычки указывается:
- Выполнена ли она в этот день (`is_completed`)
- ID выполнения (`completion_id`)
- Заметка о выполнении (`completion_note`)
