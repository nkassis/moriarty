"""Session-scoped RabbitMQ and Postgres containers, in-memory spans, and bus helpers."""

import asyncio
from collections.abc import AsyncIterator, Callable, Iterator
from contextlib import asynccontextmanager
from dataclasses import dataclass, field

import aio_pika
import pytest
from aio_pika.abc import AbstractIncomingMessage, AbstractRobustConnection
from opentelemetry.sdk.trace.export.in_memory_span_exporter import InMemorySpanExporter
from testcontainers.community.postgres import PostgresContainer
from testcontainers.community.rabbitmq import RabbitMqContainer

from ship.bus.messaging import consume_span
from ship.bus.topology import SUBSPACE, Topology, declare_topology
from ship.relay import Relay
from ship.telemetry import setup_tracing

# The same images as infra/docker-compose.yml.
RABBITMQ_IMAGE = "rabbitmq:4.3.5-management"
POSTGRES_IMAGE = "pgvector/pgvector:0.8.7-pg18-trixie"
WAIT_SECONDS = 10.0


@pytest.fixture(scope="session")
def span_exporter() -> InMemorySpanExporter:
    exporter = InMemorySpanExporter()
    setup_tracing("moriarty-test", exporter=exporter)
    return exporter


@pytest.fixture
def spans(span_exporter: InMemorySpanExporter) -> InMemorySpanExporter:
    span_exporter.clear()
    return span_exporter


@pytest.fixture(scope="session")
def amqp_url() -> Iterator[str]:
    with RabbitMqContainer(RABBITMQ_IMAGE, username="test", password="test") as rabbitmq:
        host = rabbitmq.get_container_host_ip()
        port = rabbitmq.get_exposed_port(rabbitmq.port)
        yield f"amqp://test:test@{host}:{port}/"


@pytest.fixture(scope="session")
def database_url() -> Iterator[str]:
    with PostgresContainer(POSTGRES_IMAGE, driver=None) as postgres:
        yield postgres.get_connection_url()


@asynccontextmanager
async def connected(amqp_url: str) -> AsyncIterator[tuple[AbstractRobustConnection, Topology]]:
    connection = await aio_pika.connect_robust(amqp_url)
    async with connection:
        topology = await declare_topology(await connection.channel())
        yield connection, topology


@asynccontextmanager
async def running_relay(amqp_url: str) -> AsyncIterator[Relay]:
    async with connected(amqp_url) as (_, topology):
        relay = Relay(topology)
        await relay.start()
        yield relay


@dataclass
class Listener:
    """A crew-side stand-in: exclusive queues on `subspace` for alerts and clock ticks."""

    alert_queue: str = ""
    alerts: list[AbstractIncomingMessage] = field(default_factory=list)
    ticks: list[AbstractIncomingMessage] = field(default_factory=list)
    arrived: asyncio.Event = field(default_factory=asyncio.Event)

    async def on_alert(self, message: AbstractIncomingMessage) -> None:
        with consume_span(message, self.alert_queue):
            self.alerts.append(message)
            await message.ack()
        self.arrived.set()

    async def on_tick(self, message: AbstractIncomingMessage) -> None:
        self.ticks.append(message)
        await message.ack()
        self.arrived.set()

    async def until(self, condition: Callable[[], bool]) -> None:
        """Wait until `condition` holds, re-checking as each message arrives."""
        await wait_until(self.arrived, condition)


@asynccontextmanager
async def subspace_listener(amqp_url: str) -> AsyncIterator[Listener]:
    async with connected(amqp_url) as (connection, _):
        channel = await connection.channel()
        subspace = await channel.get_exchange(SUBSPACE)
        listener = Listener()
        alerts = await channel.declare_queue(exclusive=True)
        await alerts.bind(subspace, routing_key="alert.#")
        listener.alert_queue = alerts.name
        ticks = await channel.declare_queue(exclusive=True)
        await ticks.bind(subspace, routing_key="clock.tick")
        await alerts.consume(listener.on_alert)
        await ticks.consume(listener.on_tick)
        yield listener


async def wait_until(arrived: asyncio.Event, condition: Callable[[], bool]) -> None:
    """Wait until `condition` holds; `arrived` is set whenever it may have changed."""
    async with asyncio.timeout(WAIT_SECONDS):
        while not condition():
            arrived.clear()
            await arrived.wait()
