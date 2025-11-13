"""Kafka Consumer для обработки событий бронирования"""
import asyncio
import json
import logging
from datetime import datetime
from kafka import KafkaConsumer
from kafka.errors import KafkaError
from app.config import settings
from app.database import async_session_maker
from app.services.booking_service import BookingService

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class BookingEventConsumer:
    """Consumer для обработки событий бронирования"""

    def __init__(self):
        self.consumer = None
        self.running = False

    def connect(self):
        """Подключение к Kafka"""
        try:
            self.consumer = KafkaConsumer(
                settings.KAFKA_TOPIC,
                bootstrap_servers=settings.KAFKA_BOOTSTRAP_SERVERS.split(','),
                group_id=settings.KAFKA_GROUP_ID,
                auto_offset_reset='earliest',
                enable_auto_commit=True,
                value_deserializer=lambda m: json.loads(m.decode('utf-8'))
            )
            logger.info(f"Connected to Kafka: {settings.KAFKA_BOOTSTRAP_SERVERS}")
            logger.info(f"Subscribed to topic: {settings.KAFKA_TOPIC}")
        except KafkaError as e:
            logger.error(f"Failed to connect to Kafka: {e}")
            raise

    async def process_event(self, event: dict):
        """Обработка события"""
        event_type = event.get("event_type")
        data = event.get("data", {})

        logger.info(f"Processing event: {event_type}")

        if event_type == "booking.created":
            booking_id = data.get("booking_id")
            if not booking_id:
                logger.error("Missing booking_id in event data")
                return

            # Обрабатываем бронирование
            async with async_session_maker() as db:
                try:
                    await BookingService.process_booking(db, booking_id)
                except Exception as e:
                    logger.error(f"Error processing booking {booking_id}: {e}")
        else:
            logger.warning(f"Unknown event type: {event_type}")

    def start(self):
        """Запуск consumer"""
        self.connect()
        self.running = True

        logger.info("Booking Service started. Waiting for events...")

        try:
            for message in self.consumer:
                if not self.running:
                    break

                event = message.value
                logger.info(f"Received event: {event}")

                # Запускаем обработку события в asyncio
                asyncio.run(self.process_event(event))

        except KeyboardInterrupt:
            logger.info("Shutting down...")
        except Exception as e:
            logger.error(f"Error in consumer loop: {e}")
        finally:
            self.stop()

    def stop(self):
        """Остановка consumer"""
        self.running = False
        if self.consumer:
            self.consumer.close()
            logger.info("Consumer closed")


def main():
    """Главная функция"""
    consumer = BookingEventConsumer()
    consumer.start()


if __name__ == "__main__":
    main()
