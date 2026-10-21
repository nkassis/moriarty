"""Publish and consume with W3C trace context carried in AMQP headers."""

from collections.abc import Iterator
from contextlib import contextmanager

from aio_pika import DeliveryMode, Message
from aio_pika.abc import AbstractExchange, AbstractIncomingMessage
from opentelemetry import propagate, trace
from opentelemetry.trace import Span, SpanKind

tracer = trace.get_tracer("ship.bus")


def _attributes(destination: str, routing_key: str) -> dict[str, str]:
    return {
        "messaging.system": "rabbitmq",
        "messaging.destination.name": destination,
        "messaging.rabbitmq.destination.routing_key": routing_key,
    }


async def publish(exchange: AbstractExchange, routing_key: str, body: bytes) -> None:
    """Publish under a producer span; `traceparent` goes into the headers.
    Returns once the broker confirms."""
    with tracer.start_as_current_span(
        f"publish {exchange.name}",
        kind=SpanKind.PRODUCER,
        attributes=_attributes(exchange.name, routing_key),
    ):
        headers: dict[str, str] = {}
        propagate.inject(headers)
        message = Message(
            body,
            headers=headers,
            content_type="application/json",
            delivery_mode=DeliveryMode.PERSISTENT,
        )
        await exchange.publish(message, routing_key=routing_key)


@contextmanager
def consume_span(message: AbstractIncomingMessage, queue: str) -> Iterator[Span]:
    """A consumer span whose parent is the trace context in the message headers."""
    carrier = {key: str(value) for key, value in (message.headers or {}).items()}
    with tracer.start_as_current_span(
        f"consume {queue}",
        context=propagate.extract(carrier),
        kind=SpanKind.CONSUMER,
        attributes=_attributes(queue, message.routing_key or ""),
    ) as span:
        yield span
