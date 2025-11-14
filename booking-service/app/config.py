"""Конфигурация сервиса"""

import os
from dotenv import load_dotenv

load_dotenv()


class Settings:
    """Настройки приложения"""

    DATABASE_URL = os.getenv(
        "DATABASE_URL",
        "postgresql://booking_user:booking_pass@localhost:5432/booking_db",
    )
    KAFKA_BOOTSTRAP_SERVERS = os.getenv("KAFKA_BOOTSTRAP_SERVERS", "localhost:9092")
    KAFKA_TOPIC = os.getenv("KAFKA_TOPIC", "booking_events")
    KAFKA_GROUP_ID = os.getenv("KAFKA_GROUP_ID", "booking_service_group")


settings = Settings()
