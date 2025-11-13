"""Модель ресторана"""
from sqlalchemy import Column, Integer, String
from sqlalchemy.orm import relationship
from app.db.database import Base


class Restaurant(Base):
    """Модель ресторана"""
    __tablename__ = "restaurants"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    address = Column(String, nullable=False)
    description = Column(String, nullable=True)

    # Связь с бронированиями
    bookings = relationship("Booking", back_populates="restaurant")
