"""Pydantic схемы для ресторанов"""

from pydantic import BaseModel, ConfigDict


class RestaurantResponse(BaseModel):
    """Схема ответа с информацией о ресторане"""

    id: int
    name: str
    address: str
    description: str | None = None

    model_config = ConfigDict(from_attributes=True)
