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


@pytest.fixture(scope="function")
async def db_session():
    """Фикстура для тестовой БД"""
    async with test_engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    async with test_session_maker() as session:
        yield session

    async with test_engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)


@pytest.fixture(scope="function")
async def test_restaurant(db_session: AsyncSession):
    """Фикстура для создания тестового ресторана"""
    restaurant = Restaurant(
        name="Тестовый ресторан",
        address="ул. Тестовая, д. 1",
        description="Тестовое описание"
    )
    db_session.add(restaurant)
    await db_session.commit()
    await db_session.refresh(restaurant)
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
async def test_get_booking(test_restaurant, db_session):
    """Тест получения информации о бронировании"""
    # Создаем бронирование
    booking = Booking(
        restaurant_id=test_restaurant.id,
        booking_datetime=datetime.utcnow() + timedelta(days=1),
        guests_count=2,
        status=BookingStatus.CONFIRMED
    )
    db_session.add(booking)
    await db_session.commit()
    await db_session.refresh(booking)

    async with AsyncClient(app=app, base_url="http://test") as client:
        response = await client.get(f"/bookings/{booking.id}")

        assert response.status_code == 200
        data = response.json()
        assert data["id"] == booking.id
        assert data["status"] == "CONFIRMED"


@pytest.mark.asyncio
async def test_get_nonexistent_booking():
    """Тест получения несуществующего бронирования"""
    async with AsyncClient(app=app, base_url="http://test") as client:
        response = await client.get("/bookings/99999")

        assert response.status_code == 404
