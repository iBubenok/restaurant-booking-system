.PHONY: help up down restart logs clean test migrate seed

help:
	@echo "Доступные команды:"
	@echo "  make up         - Запустить все сервисы"
	@echo "  make down       - Остановить все сервисы"
	@echo "  make restart    - Перезапустить все сервисы"
	@echo "  make logs       - Показать логи всех сервисов"
	@echo "  make clean      - Удалить все контейнеры и volumes"
	@echo "  make test       - Запустить тесты"
	@echo "  make migrate    - Применить миграции БД"
	@echo "  make seed       - Заполнить БД тестовыми данными"

up:
	docker-compose up -d

down:
	docker-compose down

restart:
	docker-compose restart

logs:
	docker-compose logs -f

clean:
	docker-compose down -v
	docker system prune -f

test:
	docker-compose exec api-service pytest tests/ -v
	docker-compose exec booking-service pytest tests/ -v

migrate:
	docker-compose exec api-service alembic upgrade head

seed:
	docker-compose exec api-service python seed_data.py
