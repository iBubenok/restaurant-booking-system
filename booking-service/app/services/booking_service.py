"""Сервис для обработки бронирований"""
import logging
from datetime import datetime
from sqlalchemy import select, and_
from sqlalchemy.ext.asyncio import AsyncSession
from app.models import Booking, BookingStatus

logger = logging.getLogger(__name__)


class BookingService:
    """Сервис проверки доступности и обработки бронирований"""

    @staticmethod
    async def check_availability(
        db: AsyncSession,
        restaurant_id: int,
        booking_datetime: datetime
    ) -> bool:
        """
        Проверка доступности времени для бронирования.

        Возвращает True, если нет конфликтующих бронирований.
        """
        # Ищем бронирования на это же время в этом ресторане
        query = select(Booking).where(
            and_(
                Booking.restaurant_id == restaurant_id,
                Booking.booking_datetime == booking_datetime,
                Booking.status == BookingStatus.CONFIRMED
            )
        )

        result = await db.execute(query)
        existing_booking = result.scalar_one_or_none()

        return existing_booking is None

    @staticmethod
    async def process_booking(db: AsyncSession, booking_id: int):
        """
        Обработка бронирования: проверка доступности и обновление статуса.
        """
        # Получаем бронирование
        result = await db.execute(select(Booking).where(Booking.id == booking_id))
        booking = result.scalar_one_or_none()

        if not booking:
            logger.error(f"Booking {booking_id} not found")
            return

        # Обновляем статус на CHECKING_AVAILABILITY
        booking.status = BookingStatus.CHECKING_AVAILABILITY
        await db.commit()
        logger.info(f"Booking {booking_id}: status changed to CHECKING_AVAILABILITY")

        # Проверяем доступность
        is_available = await BookingService.check_availability(
            db,
            booking.restaurant_id,
            booking.booking_datetime
        )

        # Обновляем статус в зависимости от результата
        if is_available:
            booking.status = BookingStatus.CONFIRMED
            logger.info(f"Booking {booking_id}: CONFIRMED")
        else:
            booking.status = BookingStatus.REJECTED
            logger.info(f"Booking {booking_id}: REJECTED (time slot already booked)")

        await db.commit()
        logger.info(f"Booking {booking_id}: processing completed with status {booking.status}")
