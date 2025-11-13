"""Kafka Producer для публикации событий"""
import json
import logging
from kafka import KafkaProducer as KafkaClient
from kafka.errors import KafkaError
from app.config import settings

logger = logging.getLogger(__name__)


class KafkaProducer:
    """Обертка для Kafka Producer"""

    def __init__(self):
        self.producer = None
        self.topic = settings.kafka_topic

    def connect(self):
        """Подключение к Kafka"""
        try:
            self.producer = KafkaClient(
                bootstrap_servers=settings.kafka_bootstrap_servers.split(','),
                value_serializer=lambda v: json.dumps(v).encode('utf-8'),
                retries=3,
                max_in_flight_requests_per_connection=1
            )
            logger.info(f"Connected to Kafka: {settings.kafka_bootstrap_servers}")
        except KafkaError as e:
            logger.error(f"Failed to connect to Kafka: {e}")
            raise

    def send_event(self, event_type: str, data: dict):
        """Отправка события в Kafka"""
        if not self.producer:
            self.connect()

        event = {
            "event_type": event_type,
            "data": data
        }

        try:
            future = self.producer.send(self.topic, event)
            future.get(timeout=10)
            logger.info(f"Event sent: {event_type}, booking_id: {data.get('booking_id')}")
        except KafkaError as e:
            logger.error(f"Failed to send event: {e}")
            raise

    def close(self):
        """Закрытие соединения"""
        if self.producer:
            self.producer.close()
            logger.info("Kafka producer closed")


# Singleton instance
kafka_producer = KafkaProducer()
