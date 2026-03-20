# Сервіс перевірки об'єктів нерухомості

Backend-сервіс для обробки заявок на перевірку об'єктів нерухомості.

## Запуск

1. Клонуйте репозиторій:
```bash
git clone <repo-url>
cd DjangoService
```

2. Скопіюйте `.env.example` в `.env` та налаштуйте змінні:
```bash
cp .env.example .env
```

3. Запустіть через Docker Compose:
```bash
docker-compose up --build
```

4. Застосуйте міграції:
```bash
docker-compose exec web python manage.py migrate
```

5. Створіть суперкористувача (за бажанням):
```bash
docker-compose exec web python manage.py createsuperuser
```

Сервіс доступний за адресою: http://localhost:8000

## API Endpoints

| Метод | URL | Опис |
|-------|-----|------|
| POST | `/api/requests/` | Створення заявки |
| GET | `/api/requests/` | Список заявок (фільтри: `status`, `source`; сортування: `created_at`) |
| GET | `/api/requests/<id>/` | Деталі заявки |
| PATCH | `/api/requests/<id>/status/` | Зміна статусу заявки |
| GET | `/api/requests/stats/` | Статистика заявок |
| WS | `ws://localhost:8000/ws/requests/` | WebSocket — оновлення статусу в реальному часі |

### Приклади запитів

**Створення заявки:**
```bash
curl -X POST http://localhost:8000/api/requests/ \
  -H "Content-Type: application/json" \
  -d '{"title": "Квартира на Хрещатику", "address": "вул. Хрещатик, 1", "phone": "+380501234567", "source": "olx"}'
```

**Список з фільтрами:**
```bash
curl "http://localhost:8000/api/requests/?status=new&source=olx&ordering=-created_at"
```

**Зміна статусу:**
```bash
curl -X PATCH http://localhost:8000/api/requests/1/status/ \
  -H "Content-Type: application/json" \
  -d '{"status": "in_progress"}'
```

**Статистика:**
```bash
curl http://localhost:8000/api/requests/stats/
```

## Структура проєкту

- `config/` — конфігурація Django, Celery, ASGI
- `verification/` — основний додаток (моделі, API, задачі, сервіси, WebSocket)
- `docker-compose.yml` — оркестрація сервісів (Django/Daphne, PostgreSQL, Redis, Celery Worker, Celery Beat)

## Фонові задачі

- **check_new_request** — через 2 хвилини після створення заявки перевіряє, чи статус досі `new`, і відправляє повідомлення в Telegram
- **check_stale_requests** (Celery Beat, кожну хвилину) — знаходить заявки у статусі `in_progress` без оновлення > 1 години та надсилає нагадування
