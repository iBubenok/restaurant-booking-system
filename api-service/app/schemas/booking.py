"""Pydantic схемы для бронирований"""

from datetime import datetime
from pydantic import BaseModel, Field, ConfigDict
from app.models.booking import BookingStatus


class BookingCreate(BaseModel):
    """Схема создания бронирования"""

    restaurant_id: int = Field(..., description="ID ресторана", gt=0)
    booking_datetime: datetime = Field(..., description="Дата и время бронирования")
    guests_count: int = Field(..., description="Количество гостей", gt=0)

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "restaurant_id": 1,
                "booking_datetime": "2024-12-31T19:00:00",
                "guests_count": 4,
            }
        }
    )


class BookingResponse(BaseModel):
    """Схема ответа с информацией о бронировании"""

    id: int
    restaurant_id: int
    booking_datetime: datetime
    guests_count: int
    status: BookingStatus
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)
