"""RabbitMQ topology. Declared in code; every declaration is idempotent."""

from dataclasses import dataclass

from aio_pika import ExchangeType
from aio_pika.abc import AbstractChannel, AbstractExchange, AbstractQueue

SUBSPACE = "subspace"  # topic exchange crews bind to
HOLODECK = "holodeck"  # internal: ticks and raw readings, Holodeck to relay only
LOST_HAIL = "lost-hail"  # dead-letter exchange and queue
RELAY_QUEUE = "holodeck.relay"
DELIVERY_LIMIT = 5


def quorum_args(*, single_active_consumer: bool = False) -> dict[str, object]:
    """Queue arguments: quorum, delivery limit 5, dead-lettered to `lost-hail`."""
    args: dict[str, object] = {
        "x-queue-type": "quorum",
        "x-delivery-limit": DELIVERY_LIMIT,
        "x-dead-letter-exchange": LOST_HAIL,
    }
    if single_active_consumer:
        args["x-single-active-consumer"] = True
    return args


@dataclass(frozen=True)
class Topology:
    subspace: AbstractExchange
    holodeck: AbstractExchange
    lost_hail: AbstractQueue
    relay: AbstractQueue


async def declare_topology(channel: AbstractChannel) -> Topology:
    """Declare the exchanges, the dead-letter queue and the relay's queue."""
    subspace = await channel.declare_exchange(SUBSPACE, ExchangeType.TOPIC, durable=True)
    holodeck = await channel.declare_exchange(HOLODECK, ExchangeType.TOPIC, durable=True)
    dead_letters = await channel.declare_exchange(LOST_HAIL, ExchangeType.FANOUT, durable=True)
    lost_hail = await channel.declare_queue(
        LOST_HAIL, durable=True, arguments={"x-queue-type": "quorum"}
    )
    await lost_hail.bind(dead_letters)
    # Declared here, not by the relay, so readings queue up even before the relay starts.
    relay = await channel.declare_queue(
        RELAY_QUEUE, durable=True, arguments=quorum_args(single_active_consumer=True)
    )
    await relay.bind(holodeck, routing_key="#")
    return Topology(subspace=subspace, holodeck=holodeck, lost_hail=lost_hail, relay=relay)
