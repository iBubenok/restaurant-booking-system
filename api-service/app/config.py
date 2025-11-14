"""Конфигурация приложения"""

from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Настройки приложения"""

    database_url: str = (
        "postgresql://booking_user:booking_pass@localhost:5432/booking_db"
    )
    kafka_bootstrap_servers: str = "localhost:9092"
    kafka_topic: str = "booking_events"
    api_host: str = "0.0.0.0"
    api_port: int = 8000

    class Config:
        env_file = ".env"
        case_sensitive = False


settings = Settings()
