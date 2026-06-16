import logging

from kafka import KafkaProducer

from app.config import Settings, get_settings
from app.messaging.events import build_click_event

logger = logging.getLogger(__name__)

_producer: KafkaProducer | None = None


def init_kafka_producer(settings: Settings | None = None) -> KafkaProducer | None:
    """Create a shared Kafka producer at app startup."""
    global _producer

    settings = settings or get_settings()
    if not settings.kafka_enabled:
        return None

    import json

    _producer = KafkaProducer(
        bootstrap_servers=settings.kafka_bootstrap_servers,
        value_serializer=lambda value: json.dumps(value).encode("utf-8"),
        acks=1,
        retries=3,
        linger_ms=5,
    )
    return _producer


def get_kafka_producer() -> KafkaProducer | None:
    return _producer


def close_kafka_producer() -> None:
    global _producer
    if _producer is not None:
        _producer.flush(timeout=5)
        _producer.close()
        _producer = None


def publish_click_event(short_code: str, original_url: str, settings: Settings | None = None) -> None:
    """
    Fire-and-forget click analytics event.

    Does NOT block redirect — failures are logged, not raised.
    Interview: decouple analytics from the hot path via async messaging.
    """
    settings = settings or get_settings()
    producer = _producer

    if not settings.kafka_enabled or producer is None:
        return

    event = build_click_event(short_code, original_url)
    try:
        producer.send(settings.kafka_click_topic, value=event)
    except Exception:
        logger.exception("Failed to publish click event for short_code=%s", short_code)
