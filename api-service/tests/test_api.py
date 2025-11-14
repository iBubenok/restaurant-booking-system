"""Интеграционные тесты API"""
import pytest
from datetime import datetime, timedelta
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker
from app.main import app
from app.db.database import get_db, Base
from app.models import Restaurant, Booking, BookingStatus

# Тестовая база данных
TEST_DATABASE_URL = "postgresql+asyncpg://booking_user:booking_pass@localhost:5432/booking_db_test"
test_engine = create_async_engine(TEST_DATABASE_URL, echo=False)
test_session_maker = async_sessionmaker(test_engine, class_=AsyncSession, expire_on_commit=False)


async def override_get_db():
    """Override для тестовой БД"""
    async with test_session_maker() as session:
        try:
            yield session
        finally:
            await session.close()


app.dependency_overrides[get_db] = override_get_db


@pytest.fixture(scope="function", autouse=True)
async def db_session():
    """Фикстура для тестовой БД"""
    # Создаем таблицы
    async with test_engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    yield

    # Удаляем таблицы
    async with test_engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)


@pytest.fixture(scope="function")
async def test_restaurant():
    """Фикстура для создания тестового ресторана"""
    async with test_session_maker() as session:
        restaurant = Restaurant(
            name="Тестовый ресторан",
            address="ул. Тестовая, д. 1",
            description="Тестовое описание"
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
                "guests_count": 4
            }
        )

        assert response.status_code == 201
        data = response.json()
        assert data["restaurant_id"] == test_restaurant.id
        assert data["guests_count"] == 4
        assert data["status"] == "CREATED"


@pytest.mark.asyncio
async def test_get_booking(test_restaurant):
    """Тест получения информации о бронировании"""
    # Создаем бронирование
    async with test_session_maker() as session:
        booking = Booking(
            restaurant_id=test_restaurant.id,
            booking_datetime=datetime.utcnow() + timedelta(days=1),
            guests_count=2,
            status=BookingStatus.CONFIRMED
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
async def test_get_nonexistent_booking():
    """Тест получения несуществующего бронирования"""
    async with AsyncClient(app=app, base_url="http://test") as client:
        response = await client.get("/bookings/99999")

        assert response.status_code == 404
