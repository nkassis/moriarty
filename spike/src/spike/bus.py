"""RabbitMQ helpers: one topic exchange, plain JSON bodies."""

import json
import os
from collections.abc import Awaitable, Callable, Iterable
from dataclasses import dataclass
from datetime import UTC, datetime
from typing import Any
from urllib.parse import quote

import aio_pika
from aio_pika.abc import (
    AbstractIncomingMessage,
    AbstractRobustChannel,
    AbstractRobustConnection,
    AbstractRobustExchange,
)

EXCHANGE = "spike"
SENSORS = "sensors.readings"
ALERTS = "alerts"
COMMS = "comms"

type Handler = Callable[[str, dict[str, Any]], Awaitable[None]]


def now() -> str:
    """Return the current UTC time as an ISO 8601 string."""
    return datetime.now(UTC).isoformat()


def amqp_url() -> str:
    """Build the broker URL; host and port default to the compose stack as seen from the host."""
    user = quote(os.environ["RABBITMQ_USER"], safe="")
    password = quote(os.environ["RABBITMQ_PASSWORD"], safe="")
    host = os.environ.get("RABBITMQ_HOST", "localhost")
    port = os.environ.get("RABBITMQ_PORT", "5673")
    return f"amqp://{user}:{password}@{host}:{port}/"


@dataclass
class Bus:
    """An open connection with the exchange declared."""

    connection: AbstractRobustConnection
    channel: AbstractRobustChannel
    exchange: AbstractRobustExchange

    async def publish(self, routing_key: str, body: dict[str, Any]) -> None:
        """Publish one JSON message."""
        message = aio_pika.Message(json.dumps(body).encode(), content_type="application/json")
        await self.exchange.publish(message, routing_key=routing_key)

    async def subscribe(self, routing_keys: Iterable[str], handler: Handler) -> None:
        """Bind a temporary queue to the keys and pass each message to the handler."""
        queue = await self.channel.declare_queue(exclusive=True)
        for routing_key in routing_keys:
            await queue.bind(self.exchange, routing_key=routing_key)

        async def on_message(message: AbstractIncomingMessage) -> None:
            await handler(message.routing_key or "", json.loads(message.body))

        await queue.consume(on_message, no_ack=True)


async def connect() -> Bus:
    """Connect to the broker and declare the exchange."""
    connection = await aio_pika.connect_robust(amqp_url())
    channel = await connection.channel()
    exchange = await channel.declare_exchange(EXCHANGE, aio_pika.ExchangeType.TOPIC)
    return Bus(connection, channel, exchange)
