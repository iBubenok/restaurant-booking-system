# Система бронирования столиков

Event-driven система для бронирования столиков в ресторанах с использованием микросервисной архитектуры.

## Автор

Yan Bubenok
- Email: yan@bubenok.com
- Telegram: @iBubenok

## Технологический стек

- **Backend**: Python 3.11, FastAPI
- **База данных**: PostgreSQL 15
- **Брокер сообщений**: Apache Kafka
- **ORM**: SQLAlchemy (Async)
- **Миграции**: Alembic
- **Тестирование**: pytest, pytest-asyncio
- **CI/CD**: GitHub Actions
- **Деплой**: Render
- **Контейнеризация**: Docker, Docker Compose

## Архитектура

Система состоит из двух микросервисов:

1. **API Service** - HTTP-сервер для приема запросов и публикации событий
2. **Booking Service** - Worker для обработки событий бронирования

### Жизненный цикл бронирования

```
CREATED → CHECKING_AVAILABILITY → [CONFIRMED | REJECTED]
```

### Поток данных

1. Клиент создает бронирование через `POST /bookings`
2. API Service сохраняет бронирование в БД со статусом `CREATED`
3. API Service публикует событие `booking.created` в Kafka
4. Booking Service получает событие из Kafka
5. Booking Service проверяет доступность времени
6. Booking Service обновляет статус на `CONFIRMED` или `REJECTED`

## Структура проекта

```
restaurant-booking-system/
├── api-service/              # HTTP API сервис
│   ├── app/
│   │   ├── api/             # API endpoints
│   │   ├── db/              # Конфигурация БД
│   │   ├── kafka/           # Kafka producer
│   │   ├── models/          # SQLAlchemy модели
│   │   ├── schemas/         # Pydantic схемы
│   │   ├── config.py        # Настройки
│   │   └── main.py          # Точка входа
│   ├── alembic/             # Миграции БД
│   ├── tests/               # Тесты
│   ├── Dockerfile
│   └── requirements.txt
│
├── booking-service/         # Worker для обработки событий
│   ├── app/
│   │   ├── services/        # Бизнес-логика
│   │   ├── config.py
│   │   ├── consumer.py      # Kafka consumer
│   │   ├── database.py
│   │   └── models.py
│   ├── tests/
│   ├── Dockerfile
│   └── requirements.txt
│
├── .github/
│   └── workflows/
│       └── ci.yml           # GitHub Actions CI
│
├── docker-compose.yml       # Локальное окружение
├── render.yaml             # Конфигурация для деплоя
├── .env.example            # Пример переменных окружения
├── .gitignore
└── README.md
```

## Быстрый старт

### Предварительные требования

- Docker и Docker Compose
- Python 3.11+ (для локальной разработки)
- Git

### Локальный запуск

1. Клонируйте репозиторий:
```bash
git clone https://github.com/iBubenok/restaurant-booking-system.git
cd restaurant-booking-system
```

2. Создайте файл `.env` (скопируйте из `.env.example`):
```bash
cp .env.example .env
```

3. Запустите все сервисы через Docker Compose:
```bash
docker-compose up -d
```

4. Дождитесь запуска всех сервисов (это может занять 1-2 минуты при первом запуске)

5. Примените миграции и заполните БД тестовыми данными:
```bash
docker-compose exec api-service alembic upgrade head
docker-compose exec api-service python seed_data.py
```

6. API доступен по адресу: http://localhost:8000
7. Swagger UI документация: http://localhost:8000/docs

### Остановка сервисов

```bash
docker-compose down
```

Для полной очистки (включая volumes):
```bash
docker-compose down -v
```

## API Endpoints

### Создание бронирования

```http
POST /bookings
Content-Type: application/json

{
  "restaurant_id": 1,
  "booking_datetime": "2024-12-31T19:00:00",
  "guests_count": 4
}
```

Ответ:
```json
{
  "id": 1,
  "restaurant_id": 1,
  "booking_datetime": "2024-12-31T19:00:00",
  "guests_count": 4,
  "status": "CREATED",
  "created_at": "2024-01-01T10:00:00",
  "updated_at": "2024-01-01T10:00:00"
}
```

### Получение информации о бронировании

```http
GET /bookings/{booking_id}
```

Ответ:
```json
{
  "id": 1,
  "restaurant_id": 1,
  "booking_datetime": "2024-12-31T19:00:00",
  "guests_count": 4,
  "status": "CONFIRMED",
  "created_at": "2024-01-01T10:00:00",
  "updated_at": "2024-01-01T10:00:05"
}
```

## Тестирование

### Запуск тестов API Service

```bash
cd api-service
pytest tests/ -v
```

### Запуск тестов Booking Service

```bash
cd booking-service
pytest tests/ -v
```

### Запуск всех тестов через Docker

```bash
docker-compose exec api-service pytest tests/ -v
docker-compose exec booking-service pytest tests/ -v
```

## Разработка

### Локальная разработка без Docker

1. Создайте виртуальное окружение:
```bash
python -m venv venv
source venv/bin/activate  # Linux/Mac
# или
venv\Scripts\activate  # Windows
```

2. Установите зависимости:
```bash
cd api-service
pip install -r requirements.txt

cd ../booking-service
pip install -r requirements.txt
```

3. Запустите PostgreSQL и Kafka через Docker:
```bash
docker-compose up postgres kafka zookeeper -d
```

4. Запустите API Service:
```bash
cd api-service
uvicorn app.main:app --reload
```

5. В отдельном терминале запустите Booking Service:
```bash
cd booking-service
python -m app.consumer
```

### Создание новой миграции

```bash
cd api-service
alembic revision --autogenerate -m "Description"
alembic upgrade head
```

## CI/CD

Проект использует GitHub Actions для автоматической проверки кода:

- Линтинг (flake8)
- Проверка форматирования (black)
- Запуск тестов
- Сборка Docker образов

CI запускается автоматически при push и pull request в ветки `main`/`master`.

## Деплой на Render

1. Создайте аккаунт на [Render](https://render.com)

2. Подключите GitHub репозиторий

3. Настройте Kafka (рекомендуется [Upstash Kafka](https://upstash.com)):
   - Создайте Kafka кластер
   - Получите KAFKA_BOOTSTRAP_SERVERS

4. Render автоматически создаст сервисы согласно `render.yaml`:
   - PostgreSQL база данных
   - API Service (Web Service)
   - Booking Service (Worker)

5. Добавьте переменные окружения:
   - `KAFKA_BOOTSTRAP_SERVERS` - из Upstash
   - Остальные переменные подтянутся из render.yaml

6. После деплоя API будет доступен по HTTPS

## Мониторинг и логи

### Логи Docker Compose

```bash
# Все сервисы
docker-compose logs -f

# Только API
docker-compose logs -f api-service

# Только Worker
docker-compose logs -f booking-service
```

### Проверка здоровья сервисов

```bash
# API health check
curl http://localhost:8000/health

# PostgreSQL
docker-compose exec postgres pg_isready

# Kafka
docker-compose exec kafka kafka-broker-api-versions --bootstrap-server localhost:9092
```

## Возможные улучшения

См. файл `DECISIONS.md` для подробного описания архитектурных решений и возможных улучшений.

## Лицензия

MIT

## Контакты

По вопросам и предложениям:
- Email: yan@bubenok.com
- Telegram: @iBubenok
