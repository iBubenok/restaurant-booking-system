"""API эндпоинты для бронирований"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.db.database import get_db
from app.models.booking import Booking, BookingStatus
from app.schemas.booking import BookingCreate, BookingResponse
from app.kafka.producer import kafka_producer
import logging

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/bookings", tags=["Bookings"])


@router.post(
    "",
    response_model=BookingResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Создание нового бронирования",
    description="Создает новое бронирование и отправляет событие в Kafka для обработки",
)
async def create_booking(
    booking_data: BookingCreate, db: AsyncSession = Depends(get_db)
):
    """
    Создание нового бронирования столика.

    - **restaurant_id**: ID ресторана
    - **booking_datetime**: Дата и время бронирования
    - **guests_count**: Количество гостей
    """
    # Создаем запись о бронировании
    booking = Booking(
        restaurant_id=booking_data.restaurant_id,
        booking_datetime=booking_data.booking_datetime,
        guests_count=booking_data.guests_count,
        status=BookingStatus.CREATED,
    )

    db.add(booking)
    await db.commit()
    await db.refresh(booking)

    logger.info(f"Booking created: id={booking.id}")

    # Отправляем событие в Kafka
    try:
        kafka_producer.send_event(
            event_type="booking.created",
            data={
                "booking_id": booking.id,
                "restaurant_id": booking.restaurant_id,
                "booking_datetime": booking.booking_datetime.isoformat(),
                "guests_count": booking.guests_count,
            },
        )
    except Exception as e:
        logger.error(f"Failed to send Kafka event: {e}")
        # Не падаем, если Kafka недоступна

    return booking


@router.get(
    "/{booking_id}",
    response_model=BookingResponse,
    summary="Получение информации о бронировании",
    description="Возвращает информацию о бронировании по его ID",
)
async def get_booking(booking_id: int, db: AsyncSession = Depends(get_db)):
    """
    Получение информации о бронировании.

    - **booking_id**: ID бронирования
    """
    result = await db.execute(select(Booking).where(Booking.id == booking_id))
    booking = result.scalar_one_or_none()

    if not booking:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Бронирование с ID {booking_id} не найдено",
        )

    return booking
