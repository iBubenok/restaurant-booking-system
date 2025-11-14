"""Интеграционные тесты API"""

import pytest
import pytest_asyncio
from datetime import datetime, timedelta
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import (
    AsyncSession,
    create_async_engine,
    async_sessionmaker,
)
from app.main import app
from app.db.database import get_db, Base
from app.models import Restaurant, Booking, BookingStatus

# Тестовая база данных
TEST_DATABASE_URL = (
    "postgresql+asyncpg://booking_user:booking_pass@localhost:5432/booking_db_test"
)


@pytest_asyncio.fixture(scope="function")
async def test_engine():
    """Фикстура для создания тестового engine"""
    engine = create_async_engine(TEST_DATABASE_URL, echo=False, poolclass=None)

    # Создаем таблицы
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    yield engine

    # Удаляем таблицы
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)

    await engine.dispose()


@pytest_asyncio.fixture(scope="function")
async def test_session_maker(test_engine):
    """Фикстура для создания session maker"""
    return async_sessionmaker(test_engine, class_=AsyncSession, expire_on_commit=False)


@pytest_asyncio.fixture(scope="function")
async def override_db(test_session_maker):
    """Фикстура для override get_db"""

    async def _override_get_db():
        async with test_session_maker() as session:
            try:
                yield session
            finally:
                await session.close()

    app.dependency_overrides[get_db] = _override_get_db
    yield
    app.dependency_overrides.clear()


@pytest_asyncio.fixture(scope="function")
async def test_restaurant(test_session_maker, override_db):
    """Фикстура для создания тестового ресторана"""
    async with test_session_maker() as session:
        restaurant = Restaurant(
            name="Тестовый ресторан",
            address="ул. Тестовая, д. 1",
            description="Тестовое описание",
        )
        session.add(restaurant)
        await session.commit()
        await session.refresh(restaurant)
        return restaurant


@pytest.mark.asyncio
async def test_create_booking(test_restaurant):
    """Тест создания бронирования"""
    async with AsyncClient(app=app, base_url="http://test") as client:
        booking_datetime = datetime.utcnow() + timedelta(days=1)
        response = await client.post(
            "/bookings",
            json={
                "restaurant_id": test_restaurant.id,
                "booking_datetime": booking_datetime.isoformat(),
                "guests_count": 4,
            },
        )

        assert response.status_code == 201
        data = response.json()
        assert data["restaurant_id"] == test_restaurant.id
        assert data["guests_count"] == 4
        assert data["status"] == "CREATED"


@pytest.mark.asyncio
async def test_get_booking(test_restaurant, test_session_maker):
    """Тест получения информации о бронировании"""
    # Создаем бронирование
    async with test_session_maker() as session:
        booking = Booking(
            restaurant_id=test_restaurant.id,
            booking_datetime=datetime.utcnow() + timedelta(days=1),
            guests_count=2,
            status=BookingStatus.CONFIRMED,
        )
        session.add(booking)
        await session.commit()
        await session.refresh(booking)
        booking_id = booking.id

    async with AsyncClient(app=app, base_url="http://test") as client:
        response = await client.get(f"/bookings/{booking_id}")

        assert response.status_code == 200
        data = response.json()
        assert data["id"] == booking_id
        assert data["status"] == "CONFIRMED"


@pytest.mark.asyncio
async def test_get_nonexistent_booking(override_db):
    """Тест получения несуществующего бронирования"""
    async with AsyncClient(app=app, base_url="http://test") as client:
        response = await client.get("/bookings/99999")

        assert response.status_code == 404
