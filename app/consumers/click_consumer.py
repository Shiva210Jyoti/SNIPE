"""
Click analytics consumer.

Run manually:
    python -m app.consumers.click_consumer

In Docker:
    click-consumer service runs this automatically.
"""

import json
import logging
import sys
import time

from kafka import KafkaConsumer

from app.config import get_settings

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    stream=sys.stdout,
)
logger = logging.getLogger(__name__)


def run_consumer() -> None:
    settings = get_settings()

    if not settings.kafka_enabled:
        logger.error("KAFKA_ENABLED is false — consumer exiting")
        return

    logger.info(
        "Starting click consumer: topic=%s group=%s brokers=%s",
        settings.kafka_click_topic,
        settings.kafka_consumer_group,
        settings.kafka_bootstrap_servers,
    )

    while True:
        try:
            consumer = KafkaConsumer(
                settings.kafka_click_topic,
                bootstrap_servers=settings.kafka_bootstrap_servers,
                group_id=settings.kafka_consumer_group,
                auto_offset_reset="earliest",
                enable_auto_commit=True,
                value_deserializer=lambda message: json.loads(message.decode("utf-8")),
            )
            break
        except Exception as exc:
            logger.warning("Kafka not ready yet (%s) — retrying in 5 seconds...", exc)
            time.sleep(5)

    logger.info("Consumer connected — waiting for click events...")

    for message in consumer:
        event = message.value
        logger.info(
            "CLICK EVENT | short_code=%s | url=%s | clicked_at=%s | partition=%s | offset=%s",
            event.get("short_code"),
            event.get("original_url"),
            event.get("clicked_at"),
            message.partition,
            message.offset,
        )


if __name__ == "__main__":
    run_consumer()
