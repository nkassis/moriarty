"""The event relay (docs/decisions-m0.md, decision 4).

Consumes ticks and raw readings from the `holodeck` exchange in the Holodeck's order, forwards
ticks to `subspace` as `clock.tick`, and validates, verifies and stamps readings before
publishing them as events. Anything it cannot relay is rejected to `lost-hail`.
"""

import argparse
import asyncio
import logging
import os
import signal
from datetime import UTC, datetime
from uuid import UUID, uuid4

import aio_pika
from aio_pika.abc import AbstractIncomingMessage, AbstractRobustConnection
from opentelemetry import trace
from opentelemetry.trace import StatusCode
from pydantic import ValidationError

from ship.bus.messaging import consume_span, publish
from ship.bus.topology import Topology, declare_topology
from ship.contract.models import (
    CLOCK_TICK_ROUTING_KEY,
    ClockTick,
    Event,
    RawObservation,
    UnknownRoutingKeyError,
    parse_reading,
)
from ship.telemetry import setup_tracing

log = logging.getLogger(__name__)
tracer = trace.get_tracer("ship.relay")


class ShipTimeMismatchError(ValueError):
    """A reading stamped with a tick other than the current one: a Holodeck bug."""


class Relay:
    def __init__(self, topology: Topology) -> None:
        self.topology = topology
        self.current_tick = 0
        self.run_id: UUID | None = None

    async def start(self) -> None:
        await self.topology.relay.consume(self.handle)

    async def handle(self, message: AbstractIncomingMessage) -> None:
        routing_key = message.routing_key or ""
        with consume_span(message, self.topology.relay.name) as span:
            try:
                if routing_key == CLOCK_TICK_ROUTING_KEY:
                    with tracer.start_as_current_span("relay tick"):
                        await self._relay_tick(message.body)
                else:
                    with tracer.start_as_current_span("relay reading"):
                        await self._relay_reading(routing_key, message.body)
            except (ValidationError, UnknownRoutingKeyError, ShipTimeMismatchError) as exc:
                span.record_exception(exc)
                span.set_status(StatusCode.ERROR, type(exc).__name__)
                log.error("rejected %s to lost-hail: %s", routing_key, exc)
                await message.reject(requeue=False)
                return
        await message.ack()

    async def _relay_tick(self, body: bytes) -> None:
        tick = ClockTick.model_validate_json(body)
        self.current_tick = tick.ship_time
        self.run_id = tick.run_id
        await publish(self.topology.subspace, CLOCK_TICK_ROUTING_KEY, body)

    async def _relay_reading(self, routing_key: str, body: bytes) -> None:
        reading = parse_reading(routing_key, body)
        if self.run_id is None or reading.ship_time != self.current_tick:
            raise ShipTimeMismatchError(
                f"reading stamped {reading.ship_time} arrived under tick {self.current_tick}"
            )
        event = stamp(reading, self.run_id)
        await publish(self.topology.subspace, routing_key, event.model_dump_json().encode())


def stamp(reading: RawObservation, run_id: UUID) -> Event:
    """Turn a verified reading into an event: `event_id`, `run_id` and `wall_time` added."""
    return Event(
        event_id=uuid4(),
        run_id=run_id,
        wall_time=datetime.now(UTC),
        **reading.model_dump(),
    )


async def serve(amqp_url: str) -> None:
    connection: AbstractRobustConnection = await aio_pika.connect_robust(amqp_url)
    async with connection:
        channel = await connection.channel()
        relay = Relay(await declare_topology(channel))
        await relay.start()
        log.info("relay consuming %s", relay.topology.relay.name)
        stop = asyncio.Event()
        loop = asyncio.get_running_loop()
        for sig in (signal.SIGINT, signal.SIGTERM):
            loop.add_signal_handler(sig, stop.set)
        await stop.wait()


def main() -> None:
    parser = argparse.ArgumentParser(description="Run the event relay.")
    parser.parse_args()
    logging.basicConfig(level=logging.INFO)
    provider = setup_tracing("ship")
    asyncio.run(serve(os.environ["AMQP_URL"]))
    provider.shutdown()  # flush spans still in the batch


if __name__ == "__main__":
    main()
