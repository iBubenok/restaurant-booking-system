"""Модель бронирования"""
from datetime import datetime
from enum import Enum
from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Enum as SQLEnum
from sqlalchemy.orm import relationship
from app.db.database import Base


class BookingStatus(str, Enum):
    """Статусы бронирования"""
    CREATED = "CREATED"
    CHECKING_AVAILABILITY = "CHECKING_AVAILABILITY"
    CONFIRMED = "CONFIRMED"
    REJECTED = "REJECTED"


class Booking(Base):
    """Модель бронирования столика"""
    __tablename__ = "bookings"

    id = Column(Integer, primary_key=True, index=True)
    restaurant_id = Column(Integer, ForeignKey("restaurants.id"), nullable=False)
    booking_datetime = Column(DateTime, nullable=False)
    guests_count = Column(Integer, nullable=False)
    status = Column(SQLEnum(BookingStatus), default=BookingStatus.CREATED, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    # Связь с рестораном
    restaurant = relationship("Restaurant", back_populates="bookings")
