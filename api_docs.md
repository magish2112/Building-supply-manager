# 🔌 API Документация - Управление снабжением v1.0

## Обзор

REST API для системы управления снабжением строительных объектов с поддержкой заявок, поставщиков и объектов строительства.

**Базовый URL:** `http://localhost:5000/api/v1`

## Аутентификация

API не требует аутентификации для базовых операций.

## Endpoints

### 📋 Заявки на снабжение

**GET** `/api/v1/requests`

Получить список всех заявок с фильтрацией и пагинацией.

#### Query параметры
- `page` (integer): Номер страницы (по умолчанию 1)
- `per_page` (integer): Количество элементов на страницу (по умолчанию 10)
- `status` (string): Фильтр по статусу (Новая, В работе, Ожидает поставки, Выполнена, Отменена)
- `priority` (string): Фильтр по приоритету (Низкий, Средний, Высокий, Критический)
- `supplier_id` (integer): Фильтр по поставщику
- `site_id` (integer): Фильтр по объекту
- `search` (string): Поиск по названию, описанию или материалу

#### Пример запроса
```bash
curl "http://localhost:5000/api/v1/requests?page=1&per_page=5&status=Новая"
```

#### Пример ответа
```json
{
  "success": true,
  "data": {
    "requests": [
      {
        "id": 1,
        "title": "Поставка цемента",
        "description": "Необходим цемент М500 для фундамента",
        "material_name": "Цемент М500",
        "quantity": "100",
        "unit": "тонн",
        "priority": "Высокий",
        "status": "Новая",
        "budget": 50000.0,
        "supplier_id": 1,
        "site_id": 2,
        "created_at": "2025-01-27T10:00:00",
        "updated_at": "2025-01-27T10:00:00",
        "deadline": "2025-02-01",
        "notes": "Срочная поставка"
      }
    ],
    "pagination": {
      "page": 1,
      "per_page": 5,
      "total": 25,
      "pages": 5
    }
  }
}
```

**GET** `/api/v1/requests/{id}`

Получить детальную информацию о заявке.

#### Пример ответа
```json
{
  "success": true,
  "data": {
    "id": 1,
    "title": "Поставка цемента",
    "supplier": {
      "id": 1,
      "name": "ООО Строительные материалы"
    },
    "site": {
      "id": 2,
      "name": "ЖК Солнечный"
    }
    // ... остальные поля
  }
}
```

**POST** `/api/v1/requests`

Создать новую заявку.

#### Тело запроса
```json
{
  "title": "Поставка кирпича",
  "description": "Красный кирпич для стен",
  "material_name": "Кирпич красный",
  "quantity": "10000",
  "unit": "штук",
  "priority": "Средний",
  "budget": 150000,
  "supplier_id": 1,
  "site_id": 2,
  "deadline": "2025-02-15",
  "notes": "Стандартное качество"
}
```

**PUT** `/api/v1/requests/{id}`

Обновить заявку.

**PUT** `/api/v1/requests/{id}/status`

Обновить статус заявки.

#### Тело запроса
```json
{
  "status": "В работе",
  "comment": "Начинаем обработку заявки"
}
```

**DELETE** `/api/v1/requests/{id}`

Удалить заявку.

### 🏢 Поставщики

**GET** `/api/v1/suppliers`

Получить список всех поставщиков.

#### Пример ответа
```json
{
  "success": true,
  "data": [
    {
      "id": 1,
      "name": "ООО Строительные материалы",
      "contact_person": "Иванов Иван",
      "phone": "+7 (495) 123-45-67",
      "email": "info@stroymat.ru",
      "address": "г. Москва, ул. Строителей, 10",
      "created_at": "2025-01-27T10:00:00"
    }
  ]
}
```

**GET** `/api/v1/suppliers/{id}`

Получить детальную информацию о поставщике (включая количество заявок).

**POST** `/api/v1/suppliers`

Создать нового поставщика.

### 🏗️ Объекты строительства

**GET** `/api/v1/sites`

Получить список всех объектов.

**GET** `/api/v1/sites/{id}`

Получить детальную информацию об объекте (включая количество заявок).

### 📊 Статистика

**GET** `/api/v1/stats`

Получить статистику приложения.

#### Пример ответа
```json
{
  "success": true,
  "data": {
    "requests": {
      "total": 25,
      "by_status": {
        "Новая": 5,
        "В работе": 8,
        "Ожидает поставки": 3,
        "Выполнена": 7,
        "Отменена": 2
      },
      "by_priority": {
        "Низкий": 10,
        "Средний": 8,
        "Высокий": 5,
        "Критический": 2
      },
      "recent": 3
    },
    "suppliers": {
      "total": 15
    },
    "sites": {
      "total": 8
    },
    "timestamp": "2025-01-27T12:00:00"
  }
}
```

### 💚 Проверка здоровья

**GET** `/api/v1/health`

Проверка работоспособности приложения.

#### Пример ответа
```json
{
  "status": "healthy",
  "timestamp": "2025-01-27T12:00:00",
  "version": "1.0.0",
  "database": "connected"
}
```

## Модели данных

### Заявка (SupplyRequest)
```json
{
  "id": "integer",
  "title": "string",
  "description": "string|null",
  "material_name": "string|null",
  "quantity": "string|null",
  "unit": "string|null",
  "priority": "Низкий|Средний|Высокий|Критический",
  "status": "Новая|В работе|Ожидает поставки|Выполнена|Отменена",
  "budget": "number|null",
  "supplier_id": "integer|null",
  "site_id": "integer|null",
  "created_at": "datetime",
  "updated_at": "datetime",
  "deadline": "date|null",
  "notes": "string|null"
}
```

### Поставщик (Supplier)
```json
{
  "id": "integer",
  "name": "string",
  "contact_person": "string|null",
  "phone": "string|null",
  "email": "string|null",
  "address": "string|null",
  "created_at": "datetime"
}
```

### Объект строительства (ConstructionSite)
```json
{
  "id": "integer",
  "name": "string",
  "address": "string|null",
  "manager": "string|null",
  "phone": "string|null",
  "created_at": "datetime"
}
```

## Коды ответов

- `200` - Успешный запрос
- `201` - Ресурс создан
- `400` - Ошибка в данных запроса
- `404` - Ресурс не найден
- `500` - Внутренняя ошибка сервера

## Примеры использования

### Python клиент
```python
import requests

# Получить все заявки
response = requests.get('http://localhost:5000/api/v1/requests')
requests_data = response.json()

# Создать новую заявку
new_request = {
    'title': 'Поставка арматуры',
    'material_name': 'Арматура А3',
    'quantity': '5',
    'unit': 'тонн',
    'priority': 'Высокий',
    'supplier_id': 1,
    'site_id': 2
}

response = requests.post('http://localhost:5000/api/v1/requests', json=new_request)
```

### JavaScript клиент
```javascript
// Получить статистику
fetch('/api/v1/stats')
  .then(res => res.json())
  .then(data => {
    console.log('Всего заявок:', data.data.requests.total);
  });

// Создать заявку
fetch('/api/v1/requests', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({
    title: 'Поставка бетона',
    material_name: 'Бетон М300',
    quantity: '50',
    unit: 'кубов',
    priority: 'Средний'
  })
})
.then(res => res.json())
.then(data => console.log('Заявка создана:', data));
```

## Ограничения

- Максимум 100 элементов на страницу
- Поиск работает по основным текстовым полям
- Все даты в формате ISO 8601
- Валюты в рублях (RUB)

## Обновления API

### v1.0.0 (текущая версия)
- Базовый функционал CRUD для заявок, поставщиков и объектов
- Фильтрация и поиск
- Статистика и health checks
- Полная интеграция с существующей бизнес-логикой

---

**Версия API:** v1
**Дата:** 2025
**Контакты:** Для вопросов по API обращайтесь к разработчику
