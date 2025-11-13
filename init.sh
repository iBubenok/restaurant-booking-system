#!/bin/bash

# Скрипт инициализации проекта

set -e

echo "🚀 Инициализация проекта..."

# Проверка Docker
if ! command -v docker &> /dev/null; then
    echo "❌ Docker не установлен. Установите Docker и попробуйте снова."
    exit 1
fi

if ! command -v docker-compose &> /dev/null; then
    echo "❌ Docker Compose не установлен. Установите Docker Compose и попробуйте снова."
    exit 1
fi

# Создание .env из .env.example если его нет
if [ ! -f .env ]; then
    echo "📝 Создание .env файла..."
    cp .env.example .env
fi

# Запуск сервисов
echo "🐳 Запуск Docker Compose..."
docker-compose up -d

# Ожидание готовности PostgreSQL
echo "⏳ Ожидание готовности PostgreSQL..."
sleep 10

# Применение миграций
echo "🔄 Применение миграций БД..."
docker-compose exec -T api-service alembic upgrade head

# Заполнение тестовыми данными
echo "📊 Заполнение БД тестовыми данными..."
docker-compose exec -T api-service python seed_data.py

echo ""
echo "✅ Инициализация завершена!"
echo ""
echo "📌 API доступен на: http://localhost:8000"
echo "📌 Swagger UI: http://localhost:8000/docs"
echo ""
echo "Для просмотра логов: docker-compose logs -f"
echo "Для остановки: docker-compose down"
