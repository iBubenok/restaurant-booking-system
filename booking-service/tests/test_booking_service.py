"""Unit-тесты для BookingService"""
import pytest
from datetime import datetime, timedelta
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker
from app.database import Base
from app.models import Restaurant, Booking, BookingStatus
from app.services.booking_service import BookingService

# Тестовая база данных
TEST_DATABASE_URL = "postgresql+asyncpg://booking_user:booking_pass@localhost:5432/booking_db_test"
test_engine = create_async_engine(TEST_DATABASE_URL, echo=False)
test_session_maker = async_sessionmaker(test_engine, class_=AsyncSession, expire_on_commit=False)


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
        address="ул. Тестовая, д. 1"
    )
    db_session.add(restaurant)
    await db_session.commit()
    await db_session.refresh(restaurant)
    return restaurant


@pytest.mark.asyncio
async def test_check_availability_no_conflicts(test_restaurant, db_session):
    """Тест проверки доступности без конфликтов"""
    booking_datetime = datetime.utcnow() + timedelta(days=1)

    is_available = await BookingService.check_availability(
        db_session,
        test_restaurant.id,
        booking_datetime
    )

    assert is_available is True


@pytest.mark.asyncio
async def test_check_availability_with_conflict(test_restaurant, db_session):
    """Тест проверки доступности с конфликтом"""
    booking_datetime = datetime.utcnow() + timedelta(days=1)

    # Создаем подтвержденное бронирование
    existing_booking = Booking(
        restaurant_id=test_restaurant.id,
        booking_datetime=booking_datetime,
        guests_count=2,
        status=BookingStatus.CONFIRMED
    )
    db_session.add(existing_booking)
    await db_session.commit()

    # Проверяем доступность на то же время
    is_available = await BookingService.check_availability(
        db_session,
        test_restaurant.id,
        booking_datetime
    )

    assert is_available is False


@pytest.mark.asyncio
async def test_process_booking_confirmed(test_restaurant, db_session):
    """Тест обработки бронирования - подтверждение"""
    booking_datetime = datetime.utcnow() + timedelta(days=1)

    # Создаем новое бронирование
    booking = Booking(
        restaurant_id=test_restaurant.id,
        booking_datetime=booking_datetime,
        guests_count=4,
        status=BookingStatus.CREATED
    )
    db_session.add(booking)
    await db_session.commit()
    await db_session.refresh(booking)

    # Обрабатываем бронирование
    await BookingService.process_booking(db_session, booking.id)

    await db_session.refresh(booking)
    assert booking.status == BookingStatus.CONFIRMED


@pytest.mark.asyncio
async def test_process_booking_rejected(test_restaurant, db_session):
    """Тест обработки бронирования - отклонение"""
    booking_datetime = datetime.utcnow() + timedelta(days=1)

    # Создаем существующее подтвержденное бронирование
    existing_booking = Booking(
        restaurant_id=test_restaurant.id,
        booking_datetime=booking_datetime,
        guests_count=2,
        status=BookingStatus.CONFIRMED
    )
    db_session.add(existing_booking)
    await db_session.commit()

    # Создаем новое бронирование на то же время
    new_booking = Booking(
        restaurant_id=test_restaurant.id,
        booking_datetime=booking_datetime,
        guests_count=4,
        status=BookingStatus.CREATED
    )
    db_session.add(new_booking)
    await db_session.commit()
    await db_session.refresh(new_booking)

    # Обрабатываем новое бронирование
    await BookingService.process_booking(db_session, new_booking.id)

    await db_session.refresh(new_booking)
    assert new_booking.status == BookingStatus.REJECTED
