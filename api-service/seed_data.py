"""Скрипт для заполнения БД тестовыми данными"""
import asyncio
from sqlalchemy.ext.asyncio import AsyncSession
from app.db.database import async_session_maker, engine
from app.models import Restaurant, Base


async def seed_database():
    """Заполнение БД тестовыми данными"""
    async with engine.begin() as conn:
        # Создаем таблицы, если их нет
        await conn.run_sync(Base.metadata.create_all)

    async with async_session_maker() as db:
        # Проверяем, есть ли уже данные
        result = await db.execute("SELECT COUNT(*) FROM restaurants")
        count = result.scalar()

        if count > 0:
            print("База данных уже содержит данные. Пропускаем seed.")
            return

        # Создаем тестовые рестораны
        restaurants = [
            Restaurant(
                name="Итальянский Дворик",
                address="ул. Пушкина, д. 10, Москва",
                description="Аутентичная итальянская кухня в сердце Москвы"
            ),
            Restaurant(
                name="Суши Бар Токио",
                address="пр. Мира, д. 25, Москва",
                description="Свежие суши и роллы от японских мастеров"
            ),
            Restaurant(
                name="Грузинский Дом",
                address="ул. Арбат, д. 5, Москва",
                description="Традиционная грузинская кухня и гостеприимство"
            ),
            Restaurant(
                name="Французский Бистро",
                address="Тверская ул., д. 15, Москва",
                description="Изысканная французская кухня и винная карта"
            ),
            Restaurant(
                name="Пивная №1",
                address="Новый Арбат, д. 30, Москва",
                description="Широкий выбор крафтового пива и закусок"
            )
        ]

        for restaurant in restaurants:
            db.add(restaurant)

        await db.commit()
        print(f"Добавлено {len(restaurants)} ресторанов в базу данных")


if __name__ == "__main__":
    asyncio.run(seed_database())
